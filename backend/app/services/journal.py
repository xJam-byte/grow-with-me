from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import JournalEntry
from app.repositories.journal import JournalRepository
from app.schemas.journal import JournalResponse, JournalSaveRequest, JournalStatsResponse


class JournalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = JournalRepository(db)

    async def get_by_date(self, user_id: int, target_date: date) -> Optional[JournalResponse]:
        entry = await self.repo.get_by_date(user_id, target_date)
        if not entry:
            return None
        return JournalResponse.model_validate(entry)

    async def save_journal(
        self, user_id: int, payload: JournalSaveRequest
    ) -> JournalResponse:
        target_date = payload.entry_date or date.today()
        entry = await self.repo.save_or_update(
            user_id=user_id,
            entry_date=target_date,
            structured_answers=payload.structured_answers,
            free_text=payload.free_text,
            tomorrow_intentions=payload.tomorrow_intentions,
            mood=payload.mood,
            tags=payload.tags,
        )
        return JournalResponse.model_validate(entry)

    async def get_history(
        self, user_id: int, limit: int = 30, offset: int = 0
    ) -> List[JournalResponse]:
        records = await self.repo.get_history(user_id, limit=limit, offset=offset)
        return [JournalResponse.model_validate(r) for r in records]

    async def get_stats(self, user_id: int, today: date) -> JournalStatsResponse:
        total = await self.repo.get_total_count(user_id)
        streak = await self.repo.calculate_streak(user_id, today)
        return JournalStatsResponse(total_entries=total, streak_days=streak)

