from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.development_area import DevelopmentArea
from app.models.habit import Habit
from app.models.personal_principle import PersonalPrinciple

DEFAULT_AREAS = [
    {
        "name": "Духовность и характер",
        "slug": "spirituality",
        "icon": "🤲",
        "color": "#10B981",
        "sort_order": 1,
    },
    {
        "name": "Интеллектуальное развитие",
        "slug": "intellectual",
        "icon": "🧠",
        "color": "#3B82F6",
        "sort_order": 2,
    },
    {
        "name": "Физическое развитие",
        "slug": "physical",
        "icon": "🏃",
        "color": "#F97316",
        "sort_order": 3,
    },
    {
        "name": "Ментальное развитие",
        "slug": "mental",
        "icon": "🛡️",
        "color": "#8B5CF6",
        "sort_order": 4,
    },
    {
        "name": "Академическое и карьера",
        "slug": "academic",
        "icon": "🎓",
        "color": "#F59E0B",
        "sort_order": 5,
    },
]

DEFAULT_HABITS = [
  {
      "name": "Подъём в одно время",
      "description": "Просыпаться в фиксированное время каждое утро для стабильного циркадного ритма.",
      "category": "physical",
      "icon": "⏰",
      "target_type": "boolean",
      "target_value": 1,
      "sort_order": 1,
  },
  {
      "name": "Утренняя духовная практика / рефлексия",
      "description": "Молитва, благодарность, осознанность и настройка на день.",
      "category": "spirituality",
      "icon": "🤲",
      "target_type": "duration",
      "target_value": 10,
      "target_unit": "мин",
      "sort_order": 2,
  },
  {
      "name": "Чтение книги",
      "description": "Качественное чтение полезной литературы, минимум 10 страниц в день.",
      "category": "intellectual",
      "icon": "📖",
      "target_type": "number",
      "target_value": 10,
      "target_unit": "стр.",
      "min_value": 10,
      "sort_order": 3,
  },
  {
      "name": "Deep Work / учёба",
      "description": "Глубокая сфокусированная работа без телефона и отвлечений минимум 60 минут.",
      "category": "academic",
      "icon": "💻",
      "target_type": "duration",
      "target_value": 60,
      "target_unit": "мин",
      "min_value": 60,
      "sort_order": 4,
  },
  {
      "name": "Практика английского",
      "description": "IELTS подготовка, аудирование, словарь или разговорная практика.",
      "category": "academic",
      "icon": "🇬🇧",
      "target_type": "duration",
      "target_value": 20,
      "target_unit": "мин",
      "min_value": 20,
      "sort_order": 5,
  },
  {
      "name": "Физическая активность",
      "description": "Силовая тренировка, зарядка или активная прогулка на свежем воздухе.",
      "category": "physical",
      "icon": "🏃",
      "target_type": "duration",
      "target_value": 30,
      "target_unit": "мин",
      "sort_order": 6,
  },
  {
      "name": "Узнать что-то новое",
      "description": "Изучить концепт из психологии, науки, философии, экономики или технологий.",
      "category": "intellectual",
      "icon": "💡",
      "target_type": "duration",
      "target_value": 20,
      "target_unit": "мин",
      "min_value": 20,
      "sort_order": 7,
  },
  {
      "name": "Сделать одно доброе дело",
      "description": "Помочь кому-то, проявить искреннее внимание, сказать доброе слово или дать садака.",
      "category": "spirituality",
      "icon": "🤝",
      "target_type": "boolean",
      "target_value": 1,
      "sort_order": 8,
  },
  {
      "name": "Вечерний журнал / рефлексия",
      "description": "Честный разбор прошедшего дня: победы, ошибки, выводы и благодарность.",
      "category": "mental",
      "icon": "📝",
      "target_type": "boolean",
      "target_value": 1,
      "sort_order": 9,
  },
  {
      "name": "Сон вовремя",
      "description": "Лечь спать вовремя для полноценного восстановления сил и ясного ума.",
      "category": "physical",
      "icon": "🌙",
      "target_type": "boolean",
      "target_value": 1,
      "sort_order": 10,
  },
]

DEFAULT_PRINCIPLES = [
    "Держи своё слово.",
    "Бери на себя ответственность.",
    "Будь добрым, но не слабым.",
    "Оставайся скромным.",
    "Уважай каждого.",
    "Контролируй свои эмоции.",
    "Никогда не прекращай учиться.",
    "Уважай своё тело.",
    "Выбирай долгосрочную пользу вместо сиюминутного удовольствия.",
    "Будь полезным для других.",
    "Без телефона первые 30 минут после пробуждения.",
    "Без телефона во время Deep Work.",
    "Избегай бесцельного скроллинга.",
    "Поддерживай стабильный режим сна.",
    "Никогда не пропускай дважды.",
]


async def seed_user_defaults(user_id: int, db: AsyncSession) -> None:
    """Populates user with 5 core areas, 10 initial habits, and 15 principles if they don't exist yet."""
    # 1. Areas
    area_res = await db.execute(select(DevelopmentArea).where(DevelopmentArea.user_id == user_id))
    existing_areas = area_res.scalars().all()
    area_map = {a.slug: a.id for a in existing_areas}
    for area_data in DEFAULT_AREAS:
        if area_data["slug"] not in area_map:
            area = DevelopmentArea(user_id=user_id, **area_data)
            db.add(area)
            await db.flush()
            area_map[area.slug] = area.id

    # 2. Habits (deduplicate by name)
    habit_res = await db.execute(select(Habit.name).where(Habit.user_id == user_id))
    existing_habit_names = set(habit_res.scalars().all())
    for habit_data in DEFAULT_HABITS:
        if habit_data["name"] in existing_habit_names:
            continue
        category = habit_data["category"]
        area_id = area_map.get(category)
        habit = Habit(
            user_id=user_id,
            area_id=area_id,
            **habit_data,
        )
        db.add(habit)
        existing_habit_names.add(habit_data["name"])

    # 3. Principles (deduplicate by text)
    principle_res = await db.execute(select(PersonalPrinciple.text).where(PersonalPrinciple.user_id == user_id))
    existing_principles = set(principle_res.scalars().all())
    for idx, text in enumerate(DEFAULT_PRINCIPLES, start=1):
        if text in existing_principles:
            continue
        principle = PersonalPrinciple(
            user_id=user_id,
            text=text,
            sort_order=idx,
        )
        db.add(principle)
        existing_principles.add(text)

    await db.flush()

