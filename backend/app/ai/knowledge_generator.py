import json
import logging
from datetime import date
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from app.config import get_settings
from app.data.curated_knowledge import CURATED_KNOWLEDGE_TOPICS

logger = logging.getLogger(__name__)


async def generate_daily_knowledge_topic(
    target_date: date,
    excluded_topics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generates an educational daily knowledge topic using OpenAI GPT-4o-mini,
    or falls back to curated verified topics if no API key is provided.
    """
    settings = get_settings()
    excluded = set(excluded_topics or [])

    if settings.openai_api_key:
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            prompt = (
                "Ты — экспертный преподаватель в системе личного развития Grow With Me.\n"
                "Выбери глубокую, точную и практически полезную тему из одной из категорий: "
                "Психология, Философия, Наука, Экономика, Технологии/AI, Критическое мышление.\n"
                "НЕ используй пустые мотивационные штампы. Приводи реальные научные факты, исследования и практическую пользу.\n"
                f"Не выбирай следующие ранее изученные темы: {', '.join(list(excluded)[:20])}.\n\n"
                "Верни ответ СТРОГО в формате JSON со следующими полями:\n"
                "{\n"
                '  "category": "Название категории",\n'
                '  "topic_title": "Чёткое название темы",\n'
                '  "introduction": "Краткое введение (2-3 предложения)",\n'
                '  "explanation": "Подробное, ясное объяснение сути концепта (2-3 абзаца)",\n'
                '  "facts": "Интересный исторический или научный эксперимент/факт",\n'
                '  "practical_application": "Как применить это знание в жизни или работе сегодня",\n'
                '  "reflection_question": "Один глубокий вопрос для личной рефлексии",\n'
                '  "additional_resources": "Рекомендуемая авторитетная книга или статья"\n'
                "}"
            )

            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                logger.info(f"Generated new AI topic: {data.get('topic_title')}")
                return data
        except Exception as e:
            logger.warning(f"OpenAI topic generation error: {e}. Falling back to curated catalog.")

    # Fallback to curated topics
    available = [t for t in CURATED_KNOWLEDGE_TOPICS if t["topic_title"] not in excluded]
    if not available:
        available = CURATED_KNOWLEDGE_TOPICS

    idx = target_date.toordinal() % len(available)
    return available[idx]


async def answer_topic_question(
    topic_title: str,
    explanation: str,
    user_question: str,
) -> str:
    """Answers a user's follow-up question regarding a daily knowledge topic."""
    settings = get_settings()
    if settings.openai_api_key:
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            prompt = (
                f"Тема: {topic_title}\n"
                f"Материал: {explanation}\n\n"
                f"Вопрос пользователя: {user_question}\n\n"
                f"Ответь кратко, ясно, доброжелательно и по существу, приводя понятные примеры."
            )
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "Ты персональный образовательный ассистент."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.7,
            )
            return response.choices[0].message.content or "Не удалось получить ответ от AI."
        except Exception as e:
            logger.warning(f"OpenAI question error: {e}")
            return f"AI временно недоступен ({e}). Попробуйте позже."

    return (
        f"Ответ на вопрос «{user_question}»: Концепт «{topic_title}» показывает, "
        "как важно осознанно анализировать входящую информацию и не действовать на автопилоте."
    )

