from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    title: str
    content: str
    category: str = "quick_notes"  # quick_notes, ideas, book_notes, quotes, learning, goals
    tags: Optional[List[str]] = None
    is_favorite: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None


class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
