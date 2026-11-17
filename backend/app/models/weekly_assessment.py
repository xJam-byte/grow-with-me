from datetime import date
from typing import Any, Dict, Optional
from sqlalchemy import Date, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class WeeklyAssessment(Base, TimestampMixin):
    __tablename__ = "weekly_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)

    # 5 Areas Subjective Scores (1 to 5)
    score_spirituality: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    score_intellectual: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    score_physical: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    score_mental: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    score_academic: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Subjective Reflection Questions
    went_well: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    went_wrong: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulties: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_week_priorities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Generated AI Report
    ai_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

