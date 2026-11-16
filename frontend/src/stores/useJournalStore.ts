import { create } from 'zustand'
import type { JournalEntry, JournalStats } from '../types/journal'
import {
  fetchJournalHistory,
  fetchJournalStats,
  fetchTodayJournal,
  saveJournalApi,
} from '../api/journal'

interface JournalState {
  todayEntry: JournalEntry | null
  history: JournalEntry[]
  stats: JournalStats | null
  loading: boolean
  saving: boolean
  error: string | null
  loadToday: () => Promise<void>
  loadHistory: () => Promise<void>
  saveEntry: (data: {
    structured_answers?: Record<string, string>
    free_text?: string
    tomorrow_intentions?: string
    mood?: string
    tags?: string[]
  }) => Promise<JournalEntry | null>
}

export const useJournalStore = create<JournalState>((set) => ({
  todayEntry: null,
  history: [],
  stats: null,
  loading: false,
  saving: false,
  error: null,

  loadToday: async () => {
    set({ loading: true, error: null })
    try {
      const [entry, stats] = await Promise.all([
        fetchTodayJournal(),
        fetchJournalStats().catch(() => null),
      ])
      set({ todayEntry: entry, stats, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки журнала',
        loading: false,
      })
    }
  },

  loadHistory: async () => {
    try {
      const history = await fetchJournalHistory()
      set({ history })
    } catch (err) {
      console.error(err)
    }
  },

  saveEntry: async (data) => {
    set({ saving: true, error: null })
    try {
      const saved = await saveJournalApi(data)
      set({ todayEntry: saved, saving: false })
      // Refresh stats
      fetchJournalStats()
        .then((s) => set({ stats: s }))
        .catch(() => {})
      return saved
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Не удалось сохранить запись',
        saving: false,
      })
      return null
    }
  },
}))

