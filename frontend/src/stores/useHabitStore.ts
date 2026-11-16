import { create } from 'zustand'
import type { HabitItem, HabitStats } from '../types/habit'
import { fetchHabitStats, fetchTodayHabits, toggleHabitApi } from '../api/habits'

interface HabitState {
  habits: HabitItem[]
  stats: HabitStats | null
  loading: boolean
  error: string | null
  loadHabits: () => Promise<void>
  toggleHabit: (id: number) => Promise<void>
}

export const useHabitStore = create<HabitState>((set, get) => ({
  habits: [],
  stats: null,
  loading: false,
  error: null,

  loadHabits: async () => {
    set({ loading: true, error: null })
    try {
      const [habitsData, statsData] = await Promise.all([
        fetchTodayHabits(),
        fetchHabitStats().catch(() => null),
      ])
      set({ habits: habitsData, stats: statsData, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки привычек',
        loading: false,
      })
    }
  },

  toggleHabit: async (id: number) => {
    const currentHabits = get().habits
    const target = currentHabits.find((h) => h.id === id)
    if (!target) return

    const previousCompleted = target.completed
    const nextCompleted = !previousCompleted
    const streakDelta = nextCompleted ? 1 : -1

    // 1. Optimistic UI update
    set({
      habits: currentHabits.map((h) =>
        h.id === id
          ? {
              ...h,
              completed: nextCompleted,
              streak: Math.max(0, h.streak + streakDelta),
            }
          : h
      ),
    })

    // 2. Call backend
    try {
      const result = await toggleHabitApi(id)
      // Sync exact streak from backend
      set({
        habits: get().habits.map((h) =>
          h.id === id
            ? { ...h, completed: result.completed, streak: result.streak }
            : h
        ),
      })
      // Refresh stats in background
      fetchHabitStats()
        .then((s) => set({ stats: s }))
        .catch(() => {})
    } catch (err: any) {
      // Rollback on failure
      set({
        habits: currentHabits,
        error: 'Не удалось обновить статус привычки',
      })
    }
  },
}))
