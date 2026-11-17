export interface AreaProgressItem {
  slug: string
  name: string
  icon: string
  color: string
  objective_completions: number
  objective_target: number
  objective_percentage: number
  subjective_score: number // 1 to 5
  trend: 'up' | 'down' | 'stable'
  habits_count: number
}

export interface DailyHeatmapItem {
  date: string
  completed_count: number
  total_count: number
  completion_rate: number
}

export interface HabitStreakItem {
  id: number
  name: string
  icon: string
  category: string
  streak: number
}

export interface DashboardProgressResponse {
  today_completion_rate: number
  today_completed: number
  today_total: number
  weekly_completion_rate: number
  monthly_completion_rate: number
  total_completions_month: number
  best_active_streak: number
  weekly_chart: DailyHeatmapItem[]
  monthly_heatmap: DailyHeatmapItem[]
  streaks: HabitStreakItem[]
}

export interface WeeklyAIReport {
  overall_evaluation: string
  objective_facts: string[]
  subjective_insights: string[]
  strongest_area: string
  focus_area: string
  recommendations: string[]
  priorities: string[]
}

export interface WeeklyAssessment {
  id: number
  user_id: number
  week_start: string
  week_end: string
  score_spirituality: number
  score_intellectual: number
  score_physical: number
  score_mental: number
  score_academic: number
  went_well?: string
  went_wrong?: string
  difficulties?: string
  achievements?: string
  learned?: string
  next_week_priorities?: string
  ai_report?: WeeklyAIReport
  created_at: string
}

export interface WeeklyAssessmentCreate {
  week_start?: string
  week_end?: string
  score_spirituality: number
  score_intellectual: number
  score_physical: number
  score_mental: number
  score_academic: number
  went_well?: string
  went_wrong?: string
  difficulties?: string
  achievements?: string
  learned?: string
  next_week_priorities?: string
}
