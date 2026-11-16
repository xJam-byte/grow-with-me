from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.knowledge_generator import answer_topic_question, generate_daily_knowledge_topic
from app.models.daily_knowledge import DailyKnowledge
from app.repositories.knowledge import DailyKnowledgeRepository
from app.schemas.knowledge import KnowledgeAskResponse, KnowledgeResponse


class DailyKnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DailyKnowledgeRepository(db)

    async def get_or_create_daily(
        self, user_id: int, target_date: date
    ) -> KnowledgeResponse:
        existing = await self.repo.get_by_date(user_id, target_date)
        if existing:
            return KnowledgeResponse.model_validate(existing)

        # Generate topic excluding recent ones
        recent_titles = await self.repo.get_recent_titles(user_id, limit=30)
        topic_data = await generate_daily_knowledge_topic(
            target_date=target_date,
            excluded_topics=recent_titles,
        )

        record = DailyKnowledge(
            user_id=user_id,
            knowledge_date=target_date,
            topic_title=topic_data["topic_title"],
            category=topic_data["category"],
            introduction=topic_data["introduction"],
            explanation=topic_data["explanation"],
            facts=topic_data["facts"],
            practical_application=topic_data["practical_application"],
            reflection_question=topic_data["reflection_question"],
            additional_resources=topic_data.get("additional_resources"),
            is_read=False,
            is_favorite=False,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return KnowledgeResponse.model_validate(record)

    async def mark_as_read(self, user_id: int, knowledge_id: int) -> KnowledgeResponse:
        record = await self.repo.get_by_id(knowledge_id)
        if not record or record.user_id != user_id:
            raise ValueError("Topic not found")

        record.is_read = True
        await self.db.flush()
        await self.db.refresh(record)
        return KnowledgeResponse.model_validate(record)

    async def toggle_favorite(self, user_id: int, knowledge_id: int) -> bool:
        record = await self.repo.get_by_id(knowledge_id)
        if not record or record.user_id != user_id:
            raise ValueError("Topic not found")

        record.is_favorite = not record.is_favorite
        await self.db.flush()
        return record.is_favorite

    async def update_notes(
        self, user_id: int, knowledge_id: int, notes: str
    ) -> KnowledgeResponse:
        record = await self.repo.get_by_id(knowledge_id)
        if not record or record.user_id != user_id:
            raise ValueError("Topic not found")

        record.user_notes = notes
        await self.db.flush()
        await self.db.refresh(record)
        return KnowledgeResponse.model_validate(record)

    async def get_history(self, user_id: int, limit: int = 30) -> List[KnowledgeResponse]:
        records = await self.repo.get_history(user_id, limit=limit)
        return [KnowledgeResponse.model_validate(r) for r in records]

    async def ask_question(
        self, user_id: int, knowledge_id: int, question: str
    ) -> KnowledgeAskResponse:
        record = await self.repo.get_by_id(knowledge_id)
        if not record or record.user_id != user_id:
            raise ValueError("Topic not found")

        answer = await answer_topic_question(
            topic_title=record.topic_title,
            explanation=record.explanation,
            user_question=question,
        )
        return KnowledgeAskResponse(question=question, answer=answer)

