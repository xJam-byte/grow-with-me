from datetime import date
from typing import Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DailyKnowledge(Base, TimestampMixin):
    __tablename__ = "daily_knowledge"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    knowledge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    topic_title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # psychology, philosophy, science, tech, etc.

    introduction: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    facts: Mapped[str] = mapped_column(Text, nullable=False)
    practical_application: Mapped[str] = mapped_column(Text, nullable=False)
    reflection_question: Mapped[str] = mapped_column(Text, nullable=False)
    additional_resources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_date", name="uq_user_knowledge_date"),
    )

