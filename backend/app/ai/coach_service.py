"""
Full AI Coach orchestration service for Grow With Me.
Handles OpenAI API calls, function calling, token budgeting, conversation persistence,
and grounded local fallback when no API key is provided.
"""

from datetime import date, datetime, timedelta
import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.context import build_user_context
from app.ai.prompts import (
    COACH_BASE_PROMPT,
    TONE_MODIFIERS,
    WEEKLY_ANALYSIS_SYSTEM_PROMPT,
)
from app.ai.tools import AI_COACH_TOOLS, execute_ai_tool
from app.config import get_settings
from app.models.ai_conversation import AIConversation, AIMessage, AITokenUsage
from app.models.user import User
from app.schemas.ai import (
    AIAnalysisResponse,
    AIChatResponse,
    AIMessageResponse,
    AIUsageResponse,
)
from app.services.habit import HabitService
from app.services.journal import JournalService

logger = logging.getLogger(__name__)


class AICoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def get_or_create_conversation(self, user_id: int, context_type: str = "general") -> AIConversation:
        """Finds latest active conversation or creates a new one."""
        stmt = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.updated_at.desc())
        )
        res = await self.db.execute(stmt)
        conv = res.scalars().first()
        if not conv:
            conv = AIConversation(user_id=user_id, context_type=context_type, title="Диалог с коучем")
            self.db.add(conv)
            await self.db.flush()
        return conv

    async def get_history(self, user_id: int, limit: int = 30) -> List[AIMessageResponse]:
        """Returns message history for current active conversation."""
        conv = await self.get_or_create_conversation(user_id)
        stmt = (
            select(AIMessage)
            .where(AIMessage.conversation_id == conv.id, AIMessage.role.in_(["user", "assistant"]))
            .order_by(AIMessage.id.asc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        messages = list(res.scalars().all())
        return [AIMessageResponse.model_validate(m) for m in messages]

    async def clear_history(self, user_id: int) -> None:
        """Clears all messages in current conversation."""
        conv = await self.get_or_create_conversation(user_id)
        from sqlalchemy import delete
        await self.db.execute(delete(AIMessage).where(AIMessage.conversation_id == conv.id))
        await self.db.commit()

    async def record_token_usage(
        self, user_id: int, prompt_tokens: int, completion_tokens: int, model: str
    ) -> None:
        """Logs token consumption for budget tracking."""
        today = date.today()
        stmt = select(AITokenUsage).where(
            AITokenUsage.user_id == user_id,
            AITokenUsage.usage_date == today,
            AITokenUsage.model == model,
        )
        res = await self.db.execute(stmt)
        usage = res.scalars().first()
        if not usage:
            usage = AITokenUsage(
                user_id=user_id,
                usage_date=today,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=model,
            )
            self.db.add(usage)
        else:
            usage.prompt_tokens += prompt_tokens
            usage.completion_tokens += completion_tokens
            usage.total_tokens += prompt_tokens + completion_tokens
        await self.db.commit()

    async def get_token_usage_stats(self, user: User) -> AIUsageResponse:
        """Returns today and monthly token consumption stats."""
        today = date.today()
        first_day_month = today.replace(day=1)

        # Today
        today_stmt = select(func.coalesce(func.sum(AITokenUsage.total_tokens), 0)).where(
            AITokenUsage.user_id == user.id, AITokenUsage.usage_date == today
        )
        today_res = await self.db.execute(today_stmt)
        today_tokens = int(today_res.scalar() or 0)

        # Month
        month_stmt = select(func.coalesce(func.sum(AITokenUsage.total_tokens), 0)).where(
            AITokenUsage.user_id == user.id, AITokenUsage.usage_date >= first_day_month
        )
        month_res = await self.db.execute(month_stmt)
        month_tokens = int(month_res.scalar() or 0)

        daily_limit = (user.ai_preferences or {}).get(
            "max_daily_tokens", self.settings.openai_max_tokens_per_day
        )
        # GPT-4o-mini price estimation (~$0.15 per 1M input, $0.60 per 1M output => avg $0.30 / 1M)
        cost_usd = round((month_tokens / 1_000_000) * 0.35, 4)

        return AIUsageResponse(
            today_tokens=today_tokens,
            daily_limit=daily_limit,
            monthly_tokens=month_tokens,
            estimated_cost_usd=cost_usd,
            model=self.settings.openai_model,
        )

    async def chat(
        self, user: User, message: str, context_type: str = "general"
    ) -> AIChatResponse:
        """Main chat handler with tool calling and context injection."""
        conv = await self.get_or_create_conversation(user.id, context_type)

        # Save user message
        user_msg = AIMessage(
            conversation_id=conv.id,
            user_id=user.id,
            role="user",
            content=message,
        )
        self.db.add(user_msg)
        await self.db.commit()

        # Build prompts & context
        tone_key = (user.ai_preferences or {}).get("tone", "balanced")
        tone_instruction = TONE_MODIFIERS.get(tone_key, TONE_MODIFIERS["balanced"])
        user_ctx = await build_user_context(user, self.db, context_type)

        system_instruction = f"{COACH_BASE_PROMPT}\n{tone_instruction}\n{user_ctx}"

        tools_executed: List[str] = []
        tokens_used = 0

        # Check if OpenAI is enabled
        if self.settings.openai_api_key:
            try:
                client = AsyncOpenAI(api_key=self.settings.openai_api_key)

                # Fetch last 6 messages from DB for multi-turn history
                stmt = (
                    select(AIMessage)
                    .where(AIMessage.conversation_id == conv.id)
                    .order_by(AIMessage.created_at.desc())
                    .limit(8)
                )
                res = await self.db.execute(stmt)
                past_messages = list(reversed(res.scalars().all()))

                api_messages: List[Dict[str, Any]] = [
                    {"role": "system", "content": system_instruction}
                ]
                for pm in past_messages:
                    if pm.role in ["user", "assistant"]:
                        api_messages.append({"role": pm.role, "content": pm.content or ""})

                # Call OpenAI with tools
                response = await client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=api_messages,
                    tools=AI_COACH_TOOLS,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=1000,
                )

                choice = response.choices[0]
                total_prompt_tokens = response.usage.prompt_tokens if response.usage else 0
                total_comp_tokens = response.usage.completion_tokens if response.usage else 0
                tokens_used = total_prompt_tokens + total_comp_tokens

                # Check if model requested tool execution
                if choice.message.tool_calls:
                    api_messages.append(choice.message)

                    for tool_call in choice.message.tool_calls:
                        func_name = tool_call.function.name
                        try:
                            func_args = json.loads(tool_call.function.arguments or "{}")
                        except Exception:
                            func_args = {}

                        tools_executed.append(func_name)
                        tool_result_str = await execute_ai_tool(
                            tool_name=func_name,
                            args=func_args,
                            user_id=user.id,
                            user=user,
                            db=self.db,
                        )

                        api_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": func_name,
                                "content": tool_result_str,
                            }
                        )

                    # Follow up completion with tool results
                    second_resp = await client.chat.completions.create(
                        model=self.settings.openai_model,
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=1000,
                    )
                    reply_text = second_resp.choices[0].message.content or "Готово."
                    if second_resp.usage:
                        tokens_used += (
                            second_resp.usage.prompt_tokens + second_resp.usage.completion_tokens
                        )
                else:
                    reply_text = choice.message.content or "Я услышал тебя."

                # Log token usage
                await self.record_token_usage(
                    user.id, total_prompt_tokens, total_comp_tokens, self.settings.openai_model
                )

                # Save assistant response
                assistant_msg = AIMessage(
                    conversation_id=conv.id,
                    user_id=user.id,
                    role="assistant",
                    content=reply_text,
                    tokens_used=tokens_used,
                )
                self.db.add(assistant_msg)
                await self.db.commit()

                return AIChatResponse(
                    message=reply_text,
                    role="assistant",
                    tokens_used=tokens_used,
                    tools_used=tools_executed,
                    created_at=datetime.utcnow(),
                )

            except Exception as e:
                logger.warning(f"OpenAI chat call failed: {e}. Falling back to heuristic coach.")

        # Fallback intelligent grounded coach
        fallback_reply = await self._generate_heuristic_response(user, message)
        assistant_msg = AIMessage(
            conversation_id=conv.id,
            user_id=user.id,
            role="assistant",
            content=fallback_reply,
            tokens_used=0,
        )
        self.db.add(assistant_msg)
        await self.db.commit()

        return AIChatResponse(
            message=fallback_reply,
            role="assistant",
            tokens_used=0,
            tools_used=tools_executed,
            created_at=datetime.utcnow(),
        )

    async def _generate_heuristic_response(self, user: User, message: str) -> str:
        """High quality heuristic coaching response based on live user data and questions."""
        today = date.today()
        habit_service = HabitService(self.db)
        today_habits = await habit_service.get_today_habits(user.id, today)
        stats = await habit_service.get_stats(user.id, today)

        completed_count = sum(1 for h in today_habits if h.completed)
        pending = [h for h in today_habits if not h.completed]
        best_streak = max(stats.active_streaks.values(), default=0)

        msg_lower = message.lower()

        # 1. User wants status or weekly review
        if any(w in msg_lower for w in ["как дела", "статус", "недел", "прогресс", "обзор"]):
            pending_str = ", ".join(h.name for h in pending[:3]) if pending else "все привычки закрыты!"
            return (
                f"Смотрим на факты за сегодня:\n\n"
                f"• Выполнено привычек: **{completed_count} из {len(today_habits)}** ({stats.completion_percentage}%).\n"
                f"• Лучшая непрерывная серия: **{best_streak} дней**.\n"
                + (f"• Главный фокус сейчас: закрыть {pending_str}.\n\n" if pending else "• Отличная дисциплина сегодня, день закрыт на 100%.\n\n")
                + "Помни: стабильность держится на маленьких действиях без пропусков. Что из оставшегося сделаешь в ближайший час?"
            )

        # 2. User asks about weaknesses
        if any(w in msg_lower for w in ["слаб", "минус", "проблем", "ошибк", "улучш"]):
            if pending:
                first_pending = pending[0]
                return (
                    f"Главная зона внимания прямо сейчас — привычка **«{first_pending.name}»**.\n\n"
                    f"Она ещё не закрыта сегодня. В личной эффективности самое слабое место — откладывание простых действий на поздний вечер, когда падает сила воли.\n\n"
                    f"Сделай минимальную версию (правило 2 минут) прямо сейчас. Не жди идеального момента."
                )
            else:
                return (
                    "Сегодня у тебя закрыты все базовые привычки — дисциплина на высоте.\n\n"
                    "Следующий уровень роста — качество вечерней рефлексии: открой вкладку «Журнал» и честно ответь на вопрос: *«Что сегодня отняло больше всего энергии и как этого избежать завтра?»*"
                )

        # 3. User asks about tomorrow or planning
        if any(w in msg_lower for w in ["завтра", "план", "настрой"]):
            return (
                "Подготовка ко дню начинается с вечера:\n\n"
                "1. **Сон вовремя**: определи точное время отбоя без экрана за 30 минут.\n"
                "2. **Первое действие утра**: ранний подъём и стакан воды перед телефоном.\n"
                "3. **Правило 1 главной задачи**: выбери одну вещь, сделав которую, день уже можно считать успешным.\n\n"
                "Зафиксируй намерение на завтра во вкладке «Журнал», чтобы закрепить фокус."
            )

        # Default grounded response
        name = user.first_name or "друг"
        return (
            f"Я здесь, {name}. Твоя цель — становиться тем, кем ты гордишься, через дисциплину и честность перед собой.\n\n"
            f"Сейчас на сегодня закрыто **{completed_count}/{len(today_habits)} привычек**.\n"
            f"«Никогда не пропускай дважды» — главное правило системы. Какой конкретный шаг мы сделаем следующим?"
        )

    async def analyze_week(self, user: User) -> AIAnalysisResponse:
        """Deep weekly review of habits, consistency, and journal reflections."""
        today = date.today()
        start_date = today - timedelta(days=7)
        period_str = f"{start_date.strftime('%d.%m')} - {today.strftime('%d.%m.%Y')}"

        habit_service = HabitService(self.db)
        today_habits = await habit_service.get_today_habits(user.id, today)
        stats = await habit_service.get_stats(user.id, today)

        # Context assembly
        completed_habits = [h.name for h in today_habits if h.completed]
        high_streak_habits = [h.name for h in today_habits if h.streak >= 3]

        if self.settings.openai_api_key:
            try:
                client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                prompt = (
                    f"Пользователь: {user.first_name}\n"
                    f"Период: {period_str}\n"
                    f"Привычки со стабильной серией >=3 дней: {', '.join(high_streak_habits) or 'нет'}\n"
                    f"Сегодня выполнено: {len(completed_habits)} из {len(today_habits)}\n"
                    f"Общий процент выполнения: {stats.completion_rate_today}%\n"
                )
                response = await client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {"role": "system", "content": WEEKLY_ANALYSIS_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.6,
                )
                content = response.choices[0].message.content
                if content:
                    data = json.loads(content)
                    return AIAnalysisResponse(**data)
            except Exception as e:
                logger.warning(f"AI weekly analysis API failed: {e}. Using grounded fallback.")

        # Grounded calculated analysis
        strengths = []
        if high_streak_habits:
            strengths.append(f"Уверенно держатся привычки: {', '.join(high_streak_habits[:3])}")
        else:
            strengths.append("Сохраняется ежедневный вход в систему и фиксация прогресса")
        strengths.append("Стабильное следование базовым духовным и интеллектуальным блокам")

        weaknesses = []
        pending = [h.name for h in today_habits if not h.completed]
        if pending:
            weaknesses.append(f"Проседает регулярность в: {', '.join(pending[:2])}")
        else:
            weaknesses.append("Периодическое смещение времени выполнения на поздний вечер")
        weaknesses.append("Нужно больше внимания уделять фиксации итогов в вечернем журнале")

        score = max(5.0, min(9.5, round((stats.completion_percentage / 10) * 0.8 + 2.0, 1)))

        return AIAnalysisResponse(
            period=period_str,
            strengths=strengths,
            weaknesses=weaknesses,
            key_insight="Дисциплина строится не на мотивации, а на отсутствии компромиссов в первые 20 минут дня.",
            action_plan=[
                "Внедрить правило «Никогда не пропускай дважды» для проседающих привычек",
                "Делать самое тяжёлое действие до 12:00",
                "Фиксировать итоги дня в Журнале минимум 5 дней из 7",
            ],
            overall_score=score,
        )
