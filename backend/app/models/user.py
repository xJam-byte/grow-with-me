from typing import Any, Dict, Optional
from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Personal identity & statements
    identity_statement: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {
            "title": "Disciplined, knowledgeable, spiritually grounded individual",
            "values": [
                "Integrity",
                "Compassion",
                "Spirituality",
                "Intellectual curiosity",
                "Discipline",
                "Physical health",
                "Emotional intelligence",
                "Lifelong learning",
            ],
            "vision": "Become someone you are proud of through consistent daily action.",
        },
    )

    # Preferences & AI configs
    ai_preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {
            "tone": "balanced",  # strict, balanced, gentle
            "allow_journal_access": True,
            "allow_notes_access": True,
            "max_daily_tokens": 50000,
        },
    )

    # Notification schedules (e.g., morning 07:00, evening reflection 21:00)
    notification_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {
            "morning_greeting": {"enabled": True, "time": "07:30"},
            "daily_knowledge": {"enabled": True, "time": "09:00"},
            "spiritual_name": {"enabled": True, "time": "12:00"},
            "evening_reflection": {"enabled": True, "time": "21:30"},
            "sleep_reminder": {"enabled": True, "time": "23:00"},
            "weekly_review": {"enabled": True, "day": "sunday", "time": "19:00"},
        },
    )

    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ru", nullable=False)
    theme: Mapped[str] = mapped_column(String(10), default="dark", nullable=False)

