from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Structured reflection: dict of question_index -> answer text
    structured_answers: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSONB, nullable=True, default=dict
    )

    # Freeform writing
    free_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tomorrow's intentions
    tomorrow_intentions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True, default=list)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "entry_date", name="uq_user_journal_date"),
    )
