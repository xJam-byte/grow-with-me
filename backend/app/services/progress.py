from datetime import date, datetime, timedelta
import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.habit import Habit
from app.models.habit_completion import HabitCompletion
from app.models.weekly_assessment import WeeklyAssessment
from app.repositories.habit import HabitRepository
from app.repositories.weekly_assessment import WeeklyAssessmentRepository
from app.schemas.progress import (
    AreaProgressItem,
    DailyHeatmapItem,
    DashboardProgressResponse,
    HabitStreakItem,
    WeeklyAssessmentCreate,
    WeeklyAssessmentResponse,
)
from app.services.seed import seed_user_defaults

logger = logging.getLogger(__name__)

AREAS_CONFIG = [
    {
        "slug": "spirituality",
        "name": "Духовность и характер",
        "icon": "HeartHandshake",
        "color": "#10B981",
    },
    {
        "slug": "intellectual",
        "name": "Интеллектуальное развитие",
        "icon": "Brain",
        "color": "#3B82F6",
    },
    {
        "slug": "physical",
        "name": "Физическое развитие",
        "icon": "Activity",
        "color": "#F97316",
    },
    {
        "slug": "mental",
        "name": "Ментальное развитие",
        "icon": "ShieldCheck",
        "color": "#A855F7",
    },
    {
        "slug": "academic",
        "name": "Академическое и карьера",
        "icon": "GraduationCap",
        "color": "#F59E0B",
    },
]


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.habit_repo = HabitRepository(db)
        self.assessment_repo = WeeklyAssessmentRepository(db)
        self.settings = get_settings()

    async def get_dashboard(self, user_id: int) -> DashboardProgressResponse:
        await seed_user_defaults(user_id, self.db)
        today = date.today()

        habits = await self.habit_repo.get_user_habits(user_id, active_only=True)
        total_habits = len(habits) or 1

        # 1. Today completions
        today_completions = await self.habit_repo.get_user_completions_for_date(user_id, today)
        today_completed = len(today_completions)
        today_rate = round((today_completed / total_habits) * 100, 1)

        # 2. Last 30 days completions lookup
        start_30 = today - timedelta(days=29)
        completions_30_stmt = select(
            HabitCompletion.completion_date, func.count(HabitCompletion.id)
        ).where(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date >= start_30,
            HabitCompletion.completion_date <= today,
        ).group_by(HabitCompletion.completion_date)

        res = await self.db.execute(completions_30_stmt)
        date_counts: Dict[date, int] = {r[0]: r[1] for r in res.all()}

        # 3. Monthly heatmap (last 30 days)
        monthly_heatmap: List[DailyHeatmapItem] = []
        total_month_completions = 0
        for i in range(30):
            d = start_30 + timedelta(days=i)
            count = date_counts.get(d, 0)
            total_month_completions += count
            monthly_heatmap.append(
                DailyHeatmapItem(
                    date=d.isoformat(),
                    completed_count=count,
                    total_count=total_habits,
                    completion_rate=round((count / total_habits) * 100, 1),
                )
            )

        # 4. Weekly chart (last 7 days)
        weekly_chart = monthly_heatmap[-7:]
        weekly_sum = sum(item.completed_count for item in weekly_chart)
        weekly_possible = total_habits * 7
        weekly_rate = round((weekly_sum / weekly_possible) * 100, 1) if weekly_possible else 0.0

        monthly_possible = total_habits * 30
        monthly_rate = (
            round((total_month_completions / monthly_possible) * 100, 1) if monthly_possible else 0.0
        )

        # 5. Streaks per habit
        streaks: List[HabitStreakItem] = []
        best_active_streak = 0
        for h in habits:
            streak = await self.habit_repo.calculate_streak(h.id, user_id, today)
            if streak > best_active_streak:
                best_active_streak = streak
            streaks.append(
                HabitStreakItem(
                    id=h.id,
                    name=h.name,
                    icon=h.icon,
                    category=h.category,
                    streak=streak,
                )
            )

        return DashboardProgressResponse(
            today_completion_rate=today_rate,
            today_completed=today_completed,
            today_total=total_habits,
            weekly_completion_rate=weekly_rate,
            monthly_completion_rate=monthly_rate,
            total_completions_month=total_month_completions,
            best_active_streak=best_active_streak,
            weekly_chart=weekly_chart,
            monthly_heatmap=monthly_heatmap,
            streaks=streaks,
        )

    async def get_areas_progress(self, user_id: int) -> List[AreaProgressItem]:
        await seed_user_defaults(user_id, self.db)
        today = date.today()
        week_start = today - timedelta(days=6)

        habits = await self.habit_repo.get_user_habits(user_id, active_only=True)

        # Group habits by category slug
        habits_by_area: Dict[str, List[Habit]] = {area["slug"]: [] for area in AREAS_CONFIG}
        for h in habits:
            slug = h.category.lower()
            if slug in habits_by_area:
                habits_by_area[slug].append(h)
            else:
                # Map or default
                if slug in ["academic", "career"]:
                    habits_by_area["academic"].append(h)
                else:
                    habits_by_area["mental"].append(h)

        # Fetch completions in last 7 days
        stmt = (
            select(HabitCompletion.habit_id, func.count(HabitCompletion.id))
            .where(
                HabitCompletion.user_id == user_id,
                HabitCompletion.completion_date >= week_start,
                HabitCompletion.completion_date <= today,
            )
            .group_by(HabitCompletion.habit_id)
        )
        res = await self.db.execute(stmt)
        habit_completions_map: Dict[int, int] = {r[0]: r[1] for r in res.all()}

        # Latest 2 assessments for subjective score & trend
        history = await self.assessment_repo.get_history(user_id, limit=2)
        latest_assessment = history[0] if len(history) > 0 else None
        prev_assessment = history[1] if len(history) > 1 else None

        items: List[AreaProgressItem] = []
        for area in AREAS_CONFIG:
            slug = area["slug"]
            area_habits = habits_by_area[slug]
            habits_count = len(area_habits)

            objective_target = habits_count * 7
            objective_completions = sum(
                habit_completions_map.get(h.id, 0) for h in area_habits
            )
            obj_pct = (
                round((objective_completions / objective_target) * 100, 1)
                if objective_target > 0
                else 0.0
            )

            # Subjective score
            score_attr = f"score_{slug}"
            current_score = (
                getattr(latest_assessment, score_attr, 3) if latest_assessment else 3
            )
            prev_score = getattr(prev_assessment, score_attr, None) if prev_assessment else None

            if prev_score is None or current_score == prev_score:
                trend = "stable"
            elif current_score > prev_score:
                trend = "up"
            else:
                trend = "down"

            items.append(
                AreaProgressItem(
                    slug=slug,
                    name=area["name"],
                    icon=area["icon"],
                    color=area["color"],
                    objective_completions=objective_completions,
                    objective_target=objective_target,
                    objective_percentage=obj_pct,
                    subjective_score=current_score,
                    trend=trend,
                    habits_count=habits_count,
                )
            )

        return items

    async def save_assessment(
        self, user_id: int, payload: WeeklyAssessmentCreate
    ) -> WeeklyAssessmentResponse:
        today = date.today()
        # Default to current week Monday-Sunday
        start = payload.week_start or (today - timedelta(days=today.weekday()))
        end = payload.week_end or (start + timedelta(days=6))

        scores = {
            "spirituality": payload.score_spirituality,
            "intellectual": payload.score_intellectual,
            "physical": payload.score_physical,
            "mental": payload.score_mental,
            "academic": payload.score_academic,
        }

        record = await self.assessment_repo.save_or_update(
            user_id=user_id,
            week_start=start,
            week_end=end,
            scores=scores,
            went_well=payload.went_well,
            went_wrong=payload.went_wrong,
            difficulties=payload.difficulties,
            achievements=payload.achievements,
            learned=payload.learned,
            next_week_priorities=payload.next_week_priorities,
        )
        return WeeklyAssessmentResponse.model_validate(record)

    async def get_latest_assessment(self, user_id: int) -> Optional[WeeklyAssessmentResponse]:
        record = await self.assessment_repo.get_latest(user_id)
        if not record:
            return None
        return WeeklyAssessmentResponse.model_validate(record)

    async def get_assessment_history(
        self, user_id: int, limit: int = 12
    ) -> List[WeeklyAssessmentResponse]:
        records = await self.assessment_repo.get_history(user_id, limit=limit)
        return [WeeklyAssessmentResponse.model_validate(r) for r in records]

    async def generate_ai_report(
        self, user_id: int, assessment_id: int
    ) -> WeeklyAssessmentResponse:
        record = await self.assessment_repo.get_by_id(assessment_id)
        if not record or record.user_id != user_id:
            raise ValueError("Weekly assessment not found")

        # Gather weekly habit stats
        habits = await self.habit_repo.get_user_habits(user_id, active_only=True)
        stmt = (
            select(HabitCompletion.habit_id, func.count(HabitCompletion.id))
            .where(
                HabitCompletion.user_id == user_id,
                HabitCompletion.completion_date >= record.week_start,
                HabitCompletion.completion_date <= record.week_end,
            )
            .group_by(HabitCompletion.habit_id)
        )
        res = await self.db.execute(stmt)
        habit_counts = {r[0]: r[1] for r in res.all()}

        total_done = sum(habit_counts.values())
        max_possible = len(habits) * 7
        actual_pct = round((total_done / max_possible) * 100, 1) if max_possible else 0.0

        scores_summary = (
            f"Духовность: {record.score_spirituality}/5, "
            f"Интеллект: {record.score_intellectual}/5, "
            f"Тело: {record.score_physical}/5, "
            f"Ментальность: {record.score_mental}/5, "
            f"Академическое: {record.score_academic}/5"
        )

        user_input_summary = (
            f"Получилось: {record.went_well or 'не указано'}\n"
            f"Не получилось: {record.went_wrong or 'не указано'}\n"
            f"Трудности: {record.difficulties or 'не указаны'}\n"
            f"Уроки: {record.learned or 'не указаны'}\n"
            f"Приоритеты: {record.next_week_priorities or 'не указаны'}"
        )

        # Generate report via OpenAI if available
        if self.settings.openai_api_key:
            try:
                client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                prompt = (
                    f"Период: {record.week_start} - {record.week_end}\n"
                    f"Объективная статистика: {total_done} из {max_possible} выполнений привычек ({actual_pct}%)\n"
                    f"Субъективные оценки по 5 областям: {scores_summary}\n"
                    f"Рефлексия пользователя:\n{user_input_summary}\n\n"
                    "Сгенерируй подробный, честный и структурированный отчёт недели в формате JSON:\n"
                    "{\n"
                    '  "overall_evaluation": "Общий вывод о неделе (2 предложения)",\n'
                    '  "objective_facts": ["Факт 1", "Факт 2"],\n'
                    '  "subjective_insights": ["Инсайт 1", "Инсайт 2"],\n'
                    '  "strongest_area": "Название самой сильной области и почему",\n'
                    '  "focus_area": "Область требующая срочного внимания и конкретное узкое место",\n'
                    '  "recommendations": ["Рекомендация 1", "Рекомендация 2", "Рекомендация 3"],\n'
                    '  "priorities": ["Приоритет 1 на новую неделю", "Приоритет 2"]\n'
                    "}"
                )
                response = await client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты персональный коуч по развитию в Grow With Me. Выдавай только валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                )
                content = response.choices[0].message.content
                if content:
                    report_data = json.loads(content)
                    updated = await self.assessment_repo.update_ai_report(
                        assessment_id, user_id, report_data
                    )
                    return WeeklyAssessmentResponse.model_validate(updated)
            except Exception as e:
                logger.warning(f"Failed to generate OpenAI weekly report: {e}. Using fallback.")

        # Grounded structured fallback report
        scores_map = {
            "Духовность и характер": record.score_spirituality,
            "Интеллектуальное развитие": record.score_intellectual,
            "Физическое развитие": record.score_physical,
            "Ментальное развитие": record.score_mental,
            "Академическое и карьера": record.score_academic,
        }
        best_area = max(scores_map, key=scores_map.get)
        worst_area = min(scores_map, key=scores_map.get)

        report_data = {
            "overall_evaluation": (
                f"Неделя завершена с объективным выполнением {actual_pct}% привычек ({total_done}/{max_possible}). "
                f"Наибольшая стабильность проявилась в области «{best_area}»."
            ),
            "objective_facts": [
                f"Выполнено привычек: {total_done} из {max_possible} возможных за 7 дней",
                f"Средняя субъективная оценка по областям: {round(sum(scores_map.values()) / 5, 1)} / 5",
            ],
            "subjective_insights": [
                f"Главное достижение недели: {record.achievements or 'стабильное следование системе'}",
                f"Ключевой урок: {record.learned or 'дисциплина важнее сиюминутной мотивации'}",
            ],
            "strongest_area": f"{best_area} (оценка {scores_map[best_area]}/5)",
            "focus_area": f"{worst_area} (оценка {scores_map[worst_area]}/5) — требует внедрения правила «Никогда не пропускай дважды»",
            "recommendations": [
                "Сфокусируйся на самом уязвимом действии в первые 2 часа после пробуждения",
                "Если наступает спад сил, выполняй минимальную планку привычки вместо полного пропуска",
                "Фиксируй итоги дня в Журнале ежедневно, не накапливая на конец недели",
            ],
            "priorities": [
                record.next_week_priorities or "Поднять регулярность физической активности",
                "Держать непрерывную серию в ключевых привычках",
            ],
        }

        updated = await self.assessment_repo.update_ai_report(assessment_id, user_id, report_data)
        return WeeklyAssessmentResponse.model_validate(updated)

