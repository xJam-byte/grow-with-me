from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weekly_assessment import WeeklyAssessment
from app.repositories.base import BaseRepository


class WeeklyAssessmentRepository(BaseRepository[WeeklyAssessment]):
    def __init__(self, db: AsyncSession):
        super().__init__(WeeklyAssessment, db)

    async def get_by_week(self, user_id: int, week_start: date) -> Optional[WeeklyAssessment]:
        stmt = select(WeeklyAssessment).where(
            WeeklyAssessment.user_id == user_id,
            WeeklyAssessment.week_start == week_start,
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_latest(self, user_id: int) -> Optional[WeeklyAssessment]:
        stmt = (
            select(WeeklyAssessment)
            .where(WeeklyAssessment.user_id == user_id)
            .order_by(WeeklyAssessment.week_start.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_history(self, user_id: int, limit: int = 12) -> List[WeeklyAssessment]:
        stmt = (
            select(WeeklyAssessment)
            .where(WeeklyAssessment.user_id == user_id)
            .order_by(WeeklyAssessment.week_start.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def save_or_update(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
        scores: Dict[str, int],
        went_well: Optional[str] = None,
        went_wrong: Optional[str] = None,
        difficulties: Optional[str] = None,
        achievements: Optional[str] = None,
        learned: Optional[str] = None,
        next_week_priorities: Optional[str] = None,
    ) -> WeeklyAssessment:
        record = await self.get_by_week(user_id, week_start)
        if record:
            record.week_end = week_end
            record.score_spirituality = scores.get("spirituality", 3)
            record.score_intellectual = scores.get("intellectual", 3)
            record.score_physical = scores.get("physical", 3)
            record.score_mental = scores.get("mental", 3)
            record.score_academic = scores.get("academic", 3)
            record.went_well = went_well
            record.went_wrong = went_wrong
            record.difficulties = difficulties
            record.achievements = achievements
            record.learned = learned
            record.next_week_priorities = next_week_priorities
        else:
            record = WeeklyAssessment(
                user_id=user_id,
                week_start=week_start,
                week_end=week_end,
                score_spirituality=scores.get("spirituality", 3),
                score_intellectual=scores.get("intellectual", 3),
                score_physical=scores.get("physical", 3),
                score_mental=scores.get("mental", 3),
                score_academic=scores.get("academic", 3),
                went_well=went_well,
                went_wrong=went_wrong,
                difficulties=difficulties,
                achievements=achievements,
                learned=learned,
                next_week_priorities=next_week_priorities,
            )
            self.db.add(record)

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def update_ai_report(
        self, assessment_id: int, user_id: int, report: Dict[str, Any]
    ) -> Optional[WeeklyAssessment]:
        stmt = select(WeeklyAssessment).where(
            WeeklyAssessment.id == assessment_id, WeeklyAssessment.user_id == user_id
        )
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        if record:
            record.ai_report = report
            await self.db.commit()
            await self.db.refresh(record)
        return record
