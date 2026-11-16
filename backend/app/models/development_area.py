from typing import Optional
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DevelopmentArea(Base, TimestampMixin):
    __tablename__ = "development_areas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)  # spirituality, intellectual, physical, mental, academic
    icon: Mapped[str] = mapped_column(String(50), default="🌟")
    color: Mapped[str] = mapped_column(String(50), default="#F97316")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    habits = relationship("Habit", back_populates="development_area", cascade="all, delete-orphan")
