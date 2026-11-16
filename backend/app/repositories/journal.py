from datetime import date, timedelta
from typing import Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import JournalEntry
from app.repositories.base import BaseRepository


class JournalRepository(BaseRepository[JournalEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(JournalEntry, db)

    async def get_by_date(
        self, user_id: int, entry_date: date
    ) -> Optional[JournalEntry]:
        stmt = select(JournalEntry).where(
            JournalEntry.user_id == user_id,
            JournalEntry.entry_date == entry_date,
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def save_or_update(
        self,
        user_id: int,
        entry_date: date,
        structured_answers: Optional[Dict[str, str]] = None,
        free_text: Optional[str] = None,
        tomorrow_intentions: Optional[str] = None,
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> JournalEntry:
        existing = await self.get_by_date(user_id, entry_date)
        if existing:
            if structured_answers is not None:
                existing.structured_answers = structured_answers
            if free_text is not None:
                existing.free_text = free_text
            if tomorrow_intentions is not None:
                existing.tomorrow_intentions = tomorrow_intentions
            if mood is not None:
                existing.mood = mood
            if tags is not None:
                existing.tags = tags
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            entry = JournalEntry(
                user_id=user_id,
                entry_date=entry_date,
                structured_answers=structured_answers or {},
                free_text=free_text,
                tomorrow_intentions=tomorrow_intentions,
                mood=mood,
                tags=tags or [],
            )
            self.db.add(entry)
            await self.db.flush()
            await self.db.refresh(entry)
            return entry

    async def get_history(
        self, user_id: int, limit: int = 30, offset: int = 0
    ) -> List[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(desc(JournalEntry.entry_date))
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_total_count(self, user_id: int) -> int:
        stmt = select(func.count(JournalEntry.id)).where(JournalEntry.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar() or 0

    async def calculate_streak(self, user_id: int, reference_date: date) -> int:
        stmt = (
            select(JournalEntry.entry_date)
            .where(JournalEntry.user_id == user_id, JournalEntry.entry_date <= reference_date)
            .order_by(desc(JournalEntry.entry_date))
        )
        res = await self.db.execute(stmt)
        dates = set(res.scalars().all())

        if not dates:
            return 0

        streak = 0
        check_date = reference_date
        if check_date not in dates:
            check_date -= timedelta(days=1)
            if check_date not in dates:
                return 0

        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak
