from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Сообщение пользователя для коуча")
    context_type: str = Field("general", description="Тип контекста: general, habits, reflection, analysis")


class AIMessageResponse(BaseModel):
    id: int
    role: str
    content: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIChatResponse(BaseModel):
    message: str
    role: str = "assistant"
    tokens_used: int = 0
    tools_used: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIUsageResponse(BaseModel):
    today_tokens: int
    daily_limit: int
    monthly_tokens: int
    estimated_cost_usd: float
    model: str


class AIPreferencesUpdate(BaseModel):
    tone: Optional[str] = Field(None, description="strict | balanced | gentle")
    allow_journal_access: Optional[bool] = None
    allow_notes_access: Optional[bool] = None
    max_daily_tokens: Optional[int] = Field(None, ge=1000, le=200000)


class AIAnalysisResponse(BaseModel):
    period: str
    strengths: List[str]
    weaknesses: List[str]
    key_insight: str
    action_plan: List[str]
    overall_score: float

