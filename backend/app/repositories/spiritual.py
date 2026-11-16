from datetime import date
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.allah_name import AllahName
from app.models.daily_allah_name import DailyAllahName
from app.repositories.base import BaseRepository
from app.services.seed_allah_names import seed_allah_names


class SpiritualRepository(BaseRepository[DailyAllahName]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyAllahName, db)

    async def get_daily_by_date(
        self, user_id: int, target_date: date
    ) -> Optional[DailyAllahName]:
        stmt = (
            select(DailyAllahName)
            .options(selectinload(DailyAllahName.name_details))
            .where(
                DailyAllahName.user_id == user_id,
                DailyAllahName.display_date == target_date,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_all_allah_names(self) -> List[AllahName]:
        await seed_allah_names(self.db)
        stmt = select(AllahName).order_by(AllahName.number.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_or_create_daily(
        self, user_id: int, target_date: date
    ) -> DailyAllahName:
        existing = await self.get_daily_by_date(user_id, target_date)
        if existing:
            return existing

        await seed_allah_names(self.db)
        names = await self.get_all_allah_names()
        if not names:
            raise ValueError("No Allah names found in database")

        # Pick name cyclically based on date
        idx = target_date.toordinal() % len(names)
        chosen_name = names[idx]

        daily = DailyAllahName(
            user_id=user_id,
            allah_name_id=chosen_name.id,
            display_date=target_date,
            is_favorite=False,
        )
        self.db.add(daily)
        await self.db.flush()
        await self.db.refresh(daily)

        # Reload with name_details relationship
        return await self.get_daily_by_date(user_id, target_date)  # type: ignore
