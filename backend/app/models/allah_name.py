from typing import Optional
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AllahName(Base):
    __tablename__ = "allah_names"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    arabic_name: Mapped[str] = mapped_column(String(100), nullable=False)
    transliteration: Mapped[str] = mapped_column(String(100), nullable=False)
    meaning_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    life_reflection: Mapped[str] = mapped_column(Text, nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
