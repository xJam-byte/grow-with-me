from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AllahNameBase(BaseModel):
    number: int
    arabic_name: str
    transliteration: str
    meaning_ru: str
    explanation: str
    life_reflection: str
    source_reference: Optional[str] = None


class AllahNameResponse(AllahNameBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DailySpiritualResponse(BaseModel):
    id: int
    display_date: date
    name: AllahNameResponse
    user_reflection: Optional[str] = None
    is_favorite: bool

    model_config = ConfigDict(from_attributes=True)


class SpiritualReflectionUpdate(BaseModel):
    reflection: str

