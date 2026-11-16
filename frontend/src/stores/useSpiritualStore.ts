import { create } from 'zustand'
import type { AllahName, DailySpiritual } from '../types/spiritual'
import {
  fetchAllAllahNames,
  fetchTodaySpiritual,
  saveSpiritualReflection,
  toggleSpiritualFavorite,
} from '../api/spiritual'

interface SpiritualState {
  daily: DailySpiritual | null
  allNames: AllahName[]
  loading: boolean
  error: string | null
  loadTodaySpiritual: () => Promise<void>
  loadAllNames: () => Promise<void>
  saveReflection: (reflection: string) => Promise<void>
  toggleFavorite: () => Promise<void>
}

export const useSpiritualStore = create<SpiritualState>((set, get) => ({
  daily: null,
  allNames: [],
  loading: false,
  error: null,

  loadTodaySpiritual: async () => {
    set({ loading: true, error: null })
    try {
      const data = await fetchTodaySpiritual()
      set({ daily: data, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки имени Аллаха',
        loading: false,
      })
    }
  },

  loadAllNames: async () => {
    try {
      const names = await fetchAllAllahNames()
      set({ allNames: names })
    } catch (err) {
      console.error(err)
    }
  },

  saveReflection: async (reflection: string) => {
    const d = get().daily
    if (!d) return
    try {
      const updated = await saveSpiritualReflection(d.id, reflection)
      set({ daily: updated })
    } catch (err) {
      console.error(err)
    }
  },

  toggleFavorite: async () => {
    const d = get().daily
    if (!d) return
    const prev = d.is_favorite
    set({ daily: { ...d, is_favorite: !prev } })
    try {
      const res = await toggleSpiritualFavorite(d.id)
      set({ daily: { ...d, is_favorite: res.is_favorite } })
    } catch (err) {
      set({ daily: { ...d, is_favorite: prev } })
    }
  },
}))
