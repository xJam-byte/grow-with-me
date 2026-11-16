from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class JournalSaveRequest(BaseModel):
    entry_date: Optional[date] = None
    structured_answers: Optional[Dict[str, str]] = None
    free_text: Optional[str] = None
    tomorrow_intentions: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None


class JournalResponse(BaseModel):
    id: int
    user_id: int
    entry_date: date
    structured_answers: Optional[Dict[str, str]] = None
    free_text: Optional[str] = None
    tomorrow_intentions: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalStatsResponse(BaseModel):
    total_entries: int
    streak_days: int

