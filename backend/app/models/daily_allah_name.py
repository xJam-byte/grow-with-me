from datetime import date
from typing import Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DailyAllahName(Base, TimestampMixin):
    __tablename__ = "daily_allah_names"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    allah_name_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("allah_names.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    user_reflection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relationships
    name_details = relationship("AllahName")

    __table_args__ = (
        UniqueConstraint("user_id", "display_date", name="uq_user_daily_allah_name"),
    )

