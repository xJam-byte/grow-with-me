from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allah_name import AllahName
from app.models.daily_allah_name import DailyAllahName
from app.repositories.spiritual import SpiritualRepository
from app.schemas.spiritual import AllahNameResponse, DailySpiritualResponse


class SpiritualService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SpiritualRepository(db)

    async def get_today_name(self, user_id: int, today: date) -> DailySpiritualResponse:
        daily = await self.repo.get_or_create_daily(user_id, today)
        name = daily.name_details
        return DailySpiritualResponse(
            id=daily.id,
            display_date=daily.display_date,
            user_reflection=daily.user_reflection,
            is_favorite=daily.is_favorite,
            name=AllahNameResponse(
                id=name.id,
                number=name.number,
                arabic_name=name.arabic_name,
                transliteration=name.transliteration,
                meaning_ru=name.meaning_ru,
                explanation=name.explanation,
                life_reflection=name.life_reflection,
                source_reference=name.source_reference,
            ),
        )

    async def get_all_names(self) -> List[AllahNameResponse]:
        names = await self.repo.get_all_allah_names()
        return [
            AllahNameResponse(
                id=n.id,
                number=n.number,
                arabic_name=n.arabic_name,
                transliteration=n.transliteration,
                meaning_ru=n.meaning_ru,
                explanation=n.explanation,
                life_reflection=n.life_reflection,
                source_reference=n.source_reference,
            )
            for n in names
        ]

    async def update_reflection(
        self, user_id: int, daily_id: int, reflection: str
    ) -> DailySpiritualResponse:
        daily = await self.repo.get_by_id(daily_id)
        if not daily or daily.user_id != user_id:
            raise ValueError("Daily spiritual record not found")

        daily.user_reflection = reflection
        await self.db.flush()
        await self.db.refresh(daily)
        return await self.get_today_name(user_id, daily.display_date)

    async def toggle_favorite(self, user_id: int, daily_id: int) -> bool:
        daily = await self.repo.get_by_id(daily_id)
        if not daily or daily.user_id != user_id:
            raise ValueError("Daily spiritual record not found")

        daily.is_favorite = not daily.is_favorite
        await self.db.flush()
        return daily.is_favorite
