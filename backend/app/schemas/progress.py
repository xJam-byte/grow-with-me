from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WeeklyAssessmentCreate(BaseModel):
    week_start: Optional[date] = None
    week_end: Optional[date] = None
    score_spirituality: int = Field(3, ge=1, le=5)
    score_intellectual: int = Field(3, ge=1, le=5)
    score_physical: int = Field(3, ge=1, le=5)
    score_mental: int = Field(3, ge=1, le=5)
    score_academic: int = Field(3, ge=1, le=5)
    went_well: Optional[str] = None
    went_wrong: Optional[str] = None
    difficulties: Optional[str] = None
    achievements: Optional[str] = None
    learned: Optional[str] = None
    next_week_priorities: Optional[str] = None


class WeeklyAssessmentResponse(BaseModel):
    id: int
    user_id: int
    week_start: date
    week_end: date
    score_spirituality: int
    score_intellectual: int
    score_physical: int
    score_mental: int
    score_academic: int
    went_well: Optional[str] = None
    went_wrong: Optional[str] = None
    difficulties: Optional[str] = None
    achievements: Optional[str] = None
    learned: Optional[str] = None
    next_week_priorities: Optional[str] = None
    ai_report: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AreaProgressItem(BaseModel):
    slug: str
    name: str
    icon: str
    color: str
    objective_completions: int
    objective_target: int
    objective_percentage: float
    subjective_score: int  # 1 to 5
    trend: str  # "up", "down", "stable"
    habits_count: int


class DailyHeatmapItem(BaseModel):
    date: str
    completed_count: int
    total_count: int
    completion_rate: float


class HabitStreakItem(BaseModel):
    id: int
    name: str
    icon: str
    category: str
    streak: int


class DashboardProgressResponse(BaseModel):
    today_completion_rate: float
    today_completed: int
    today_total: int
    weekly_completion_rate: float
    monthly_completion_rate: float
    total_completions_month: int
    best_active_streak: int
    weekly_chart: List[DailyHeatmapItem]
    monthly_heatmap: List[DailyHeatmapItem]
    streaks: List[HabitStreakItem]
