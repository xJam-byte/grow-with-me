from datetime import date
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_knowledge import DailyKnowledge
from app.repositories.base import BaseRepository


class DailyKnowledgeRepository(BaseRepository[DailyKnowledge]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyKnowledge, db)

    async def get_by_date(
        self, user_id: int, target_date: date
    ) -> Optional[DailyKnowledge]:
        stmt = select(DailyKnowledge).where(
            DailyKnowledge.user_id == user_id,
            DailyKnowledge.knowledge_date == target_date,
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_recent_titles(self, user_id: int, limit: int = 50) -> List[str]:
        stmt = (
            select(DailyKnowledge.topic_title)
            .where(DailyKnowledge.user_id == user_id)
            .order_by(desc(DailyKnowledge.knowledge_date))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_history(
        self, user_id: int, limit: int = 30, offset: int = 0
    ) -> List[DailyKnowledge]:
        stmt = (
            select(DailyKnowledge)
            .where(DailyKnowledge.user_id == user_id)
            .order_by(desc(DailyKnowledge.knowledge_date))
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
