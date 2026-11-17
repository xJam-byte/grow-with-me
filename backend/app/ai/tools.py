"""
OpenAI function calling definitions and execution engine for Grow With Me AI Coach.
"""

from datetime import date
import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_principle import PersonalPrinciple
from app.models.user import User
from app.services.habit import HabitService
from app.services.journal import JournalService
from app.services.knowledge import DailyKnowledgeService
from app.services.note import NoteService
from app.services.spiritual import SpiritualService
from app.schemas.note import NoteCreate

logger = logging.getLogger(__name__)

AI_COACH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Получить профиль пользователя: идентичность, ценности, вижн и личные принципы.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_habits_today",
            "description": "Получить список привычек пользователя на сегодня со статусом выполнения и текущими сериями (streaks).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_habits_stats",
            "description": "Получить общую статистику привычек: % выполнения, лучшие серии, активные дни.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_journal",
            "description": "Получить последние вечерние рефлексии пользователя (итоги дня, ответы на вопросы, планы на завтра).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Количество записей (по умолчанию 3)",
                        "default": 3,
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Поиск по личным заметкам пользователя (мысли, идеи, конспекты книг).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос или ключевые слова",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_knowledge_today",
            "description": "Получить тему сегодняшнего образовательного блока (Daily Knowledge).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spiritual_practice_today",
            "description": "Получить сегодняшнее Имя Аллаха для размышления и практики.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_habit_completed",
            "description": "Отметить выполнение привычки, если пользователь в диалоге сообщил, что сделал её (например, 'я прочитал книгу' или 'сделал тренировку').",
            "parameters": {
                "type": "object",
                "properties": {
                    "habit_id": {
                        "type": "integer",
                        "description": "ID привычки (если известен)",
                    },
                    "habit_name": {
                        "type": "string",
                        "description": "Название или ключевое слово привычки (например 'чтение', 'спорт', 'сон')",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_quick_note",
            "description": "Сохранить важную мысль, решение или инсайт пользователя в его личные заметки.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Заголовок заметки",
                    },
                    "content": {
                        "type": "string",
                        "description": "Содержимое заметки",
                    },
                    "category": {
                        "type": "string",
                        "description": "Категория (ideas, quick_notes, learning, goals)",
                        "default": "quick_notes",
                    },
                },
                "required": ["title", "content"],
            },
        },
    },
]


async def execute_ai_tool(
    tool_name: str,
    args: Dict[str, Any],
    user_id: int,
    user: User,
    db: AsyncSession,
) -> str:
    """Executes a requested tool function and returns a stringified JSON result."""
    today = date.today()
    ai_prefs = user.ai_preferences or {}

    try:
        if tool_name == "get_user_profile":
            principles_stmt = (
                select(PersonalPrinciple.text)
                .where(PersonalPrinciple.user_id == user_id, PersonalPrinciple.is_active == True)
                .order_by(PersonalPrinciple.sort_order.asc())
            )
            res = await db.execute(principles_stmt)
            principles = list(res.scalars().all())

            return json.dumps(
                {
                    "first_name": user.first_name,
                    "identity_statement": user.identity_statement,
                    "principles": principles,
                },
                ensure_ascii=False,
            )

        elif tool_name == "get_habits_today":
            service = HabitService(db)
            today_habits = await service.get_today_habits(user_id, today)
            data = [
                {
                    "id": h.id,
                    "name": h.name,
                    "category": h.category,
                    "target": f"{h.target_value} {h.target_unit or ''}".strip(),
                    "completed": h.completed,
                    "streak_days": h.streak,
                }
                for h in today_habits
            ]
            return json.dumps({"habits": data}, ensure_ascii=False)

        elif tool_name == "get_habits_stats":
            service = HabitService(db)
            stats = await service.get_stats(user_id, today)
            best_streak = max(stats.active_streaks.values(), default=0)
            return json.dumps(
                {
                    "total_habits": stats.today_total,
                    "completed_today": stats.today_completed,
                    "completion_rate_today_percent": stats.completion_percentage,
                    "weekly_completion_percentage": stats.weekly_completion_percentage,
                    "best_streak": best_streak,
                    "active_streaks_count": len([s for s in stats.active_streaks.values() if s > 0]),
                },
                ensure_ascii=False,
            )

        elif tool_name == "get_recent_journal":
            if not ai_prefs.get("allow_journal_access", True):
                return json.dumps(
                    {"status": "restricted", "message": "Пользователь ограничил доступ к журналу в настройках приватности."},
                    ensure_ascii=False,
                )
            service = JournalService(db)
            limit = args.get("limit", 3)
            entries = await service.get_history(user_id, limit=limit)
            data = [
                {
                    "date": str(e.entry_date),
                    "answers": e.structured_answers,
                    "free_text": e.free_text,
                    "tomorrow_intentions": e.tomorrow_intentions,
                }
                for e in entries
            ]
            return json.dumps({"journal_entries": data}, ensure_ascii=False)

        elif tool_name == "search_notes":
            if not ai_prefs.get("allow_notes_access", True):
                return json.dumps(
                    {"status": "restricted", "message": "Пользователь ограничил доступ к заметкам в настройках приватности."},
                    ensure_ascii=False,
                )
            service = NoteService(db)
            query = args.get("query", "")
            notes = await service.list_notes(user_id, limit=5)
            # Filter matches
            matches = [
                {"id": n.id, "title": n.title, "content": n.content[:200], "category": n.category}
                for n in notes
                if query.lower() in n.title.lower() or query.lower() in n.content.lower()
            ]
            return json.dumps({"notes": matches}, ensure_ascii=False)

        elif tool_name == "get_daily_knowledge_today":
            service = DailyKnowledgeService(db)
            k = await service.get_or_create_daily(user_id, today)
            return json.dumps(
                {
                    "topic_title": k.topic_title,
                    "category": k.category,
                    "introduction": k.introduction,
                    "explanation": k.explanation,
                    "practical_application": k.practical_application,
                    "reflection_question": k.reflection_question,
                },
                ensure_ascii=False,
            )

        elif tool_name == "get_spiritual_practice_today":
            service = SpiritualService(db)
            s = await service.get_today_name(user_id, today)
            return json.dumps(
                {
                    "arabic_name": s.name.arabic_name,
                    "transliteration": s.name.transliteration,
                    "meaning_ru": s.name.meaning_ru,
                    "explanation": s.name.explanation,
                    "life_reflection": s.name.life_reflection,
                },
                ensure_ascii=False,
            )

        elif tool_name == "mark_habit_completed":
            habit_id = args.get("habit_id")
            habit_name = args.get("habit_name", "").lower()
            service = HabitService(db)
            today_habits = await service.get_today_habits(user_id, today)

            target = None
            if habit_id:
                target = next((h for h in today_habits if h.id == habit_id), None)
            if not target and habit_name:
                target = next((h for h in today_habits if habit_name in h.name.lower()), None)

            if target:
                if not target.completed:
                    await service.toggle_habit(user_id, target.id, today)
                    return json.dumps(
                        {"status": "success", "message": f"Привычка '{target.name}' успешно отмечена как выполненная."},
                        ensure_ascii=False,
                    )
                else:
                    return json.dumps(
                        {"status": "already_completed", "message": f"Привычка '{target.name}' уже была выполнена сегодня."},
                        ensure_ascii=False,
                    )
            else:
                return json.dumps(
                    {"status": "not_found", "message": f"Не удалось найти привычку по запросу '{habit_name or habit_id}'."},
                    ensure_ascii=False,
                )

        elif tool_name == "add_quick_note":
            title = args.get("title", "Заметка от коуча")
            content = args.get("content", "")
            category = args.get("category", "quick_notes")
            service = NoteService(db)
            created = await service.create_note(
                user_id,
                NoteCreate(title=title, content=content, category=category, tags=["ai-coach"]),
            )
            return json.dumps(
                {"status": "success", "note_id": created.id, "title": created.title},
                ensure_ascii=False,
            )

        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    except Exception as e:
        logger.error(f"Error executing AI tool {tool_name}: {e}", exc_info=True)
        return json.dumps({"error": str(e)})
