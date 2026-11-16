from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class KnowledgeBase(BaseModel):
    topic_title: str
    category: str
    introduction: str
    explanation: str
    facts: str
    practical_application: str
    reflection_question: str
    additional_resources: Optional[str] = None


class KnowledgeResponse(KnowledgeBase):
    id: int
    user_id: int
    knowledge_date: date
    is_read: bool
    is_favorite: bool
    user_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeNoteUpdate(BaseModel):
    notes: str


class KnowledgeAskRequest(BaseModel):
    question: str


class KnowledgeAskResponse(BaseModel):
    question: str
    answer: str
