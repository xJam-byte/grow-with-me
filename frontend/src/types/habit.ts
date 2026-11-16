export interface HabitItem {
  id: number
  user_id: number
  name: string
  description?: string | null
  icon: string
  category: string
  target_type: string
  target_value: number
  target_unit?: string | null
  min_value?: number | null
  bonus_value?: number | null
  sort_order: number
  is_active: boolean
  completed: boolean
  actual_value?: number | null
  streak: number
  created_at: string
}

export interface HabitStats {
  today_completed: number
  today_total: number
  completion_percentage: number
  weekly_completion_percentage: number
  active_streaks: Record<number, number>
}
