from typing import Any, Dict, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    area_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("development_areas.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(50), default="🎯")
    category: Mapped[str] = mapped_column(String(50), default="other")  # spirituality, intellectual, physical, mental, academic

    # Measurement & targets
    target_type: Mapped[str] = mapped_column(String(50), default="boolean")  # boolean, number, duration
    target_value: Mapped[int] = mapped_column(Integer, default=1)
    target_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g. "стр.", "мин."
    min_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bonus_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Reminder settings (e.g., {"enabled": True, "time": "08:00"})
    reminder_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    development_area = relationship("DevelopmentArea", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

