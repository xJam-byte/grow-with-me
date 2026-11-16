from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: str = "🎯"
    category: str = "other"
    target_type: str = "boolean"
    target_value: int = 1
    target_unit: Optional[str] = None
    min_value: Optional[int] = None
    bonus_value: Optional[int] = None
    reminder_settings: Optional[Dict[str, Any]] = None


class HabitCreate(HabitBase):
    sort_order: int = 0


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[int] = None
    target_unit: Optional[str] = None
    min_value: Optional[int] = None
    bonus_value: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    reminder_settings: Optional[Dict[str, Any]] = None


class HabitResponse(HabitBase):
    id: int
    user_id: int
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitTodayItem(HabitResponse):
    completed: bool
    actual_value: Optional[int] = None
    streak: int = 0


class HabitToggleRequest(BaseModel):
    target_date: Optional[date] = None
    actual_value: Optional[int] = None
    note: Optional[str] = None


class HabitToggleResponse(BaseModel):
    habit_id: int
    target_date: date
    completed: bool
    streak: int


class HabitStatsResponse(BaseModel):
    today_completed: int
    today_total: int
    completion_percentage: float
    weekly_completion_percentage: float
    active_streaks: Dict[int, int]  # habit_id -> streak days
