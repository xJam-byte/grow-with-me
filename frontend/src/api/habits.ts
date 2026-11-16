import { apiClient } from './client'
import type { HabitItem, HabitStats } from '../types/habit'

export async function fetchTodayHabits(): Promise<HabitItem[]> {
  const response = await apiClient.get<HabitItem[]>('/habits/today')
  return response.data
}

export async function toggleHabitApi(
  habitId: number,
  actualValue?: number,
  note?: string
): Promise<{ habit_id: number; target_date: string; completed: boolean; streak: number }> {
  const response = await apiClient.post(`/habits/${habitId}/toggle`, {
    actual_value: actualValue,
    note: note,
  })
  return response.data
}

export async function fetchHabitStats(): Promise<HabitStats> {
  const response = await apiClient.get<HabitStats>('/habits/stats')
  return response.data
}
