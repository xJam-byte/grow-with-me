from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    completion_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    actual_value: Mapped[int] = mapped_column(Integer, default=1)
    completion_level: Mapped[str] = mapped_column(String(50), default="target")  # min, target, bonus
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    habit = relationship("Habit", back_populates="completions")

    __table_args__ = (
        UniqueConstraint("habit_id", "completion_date", name="uq_habit_date"),
    )

