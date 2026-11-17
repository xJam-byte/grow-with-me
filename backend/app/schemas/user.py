from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str = "UTC"
    language: str = "ru"
    theme: str = "dark"


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    identity_statement: Optional[Dict[str, Any]] = None
    ai_preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    id: int
    identity_statement: Optional[Dict[str, Any]] = None
    ai_preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonalPrincipleCreate(BaseModel):
    text: str = Field(..., min_length=2, max_length=500)
    category: str = Field("general", max_length=50)
    sort_order: int = 0


class PersonalPrincipleUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=2, max_length=500)
    category: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class PersonalPrincipleResponse(BaseModel):
    id: int
    user_id: int
    text: str
    category: str
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDataExportResponse(BaseModel):
    export_date: str
    user: Dict[str, Any]
    principles: List[Dict[str, Any]]
    habits: List[Dict[str, Any]]
    journal_entries: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]
    weekly_assessments: List[Dict[str, Any]]
