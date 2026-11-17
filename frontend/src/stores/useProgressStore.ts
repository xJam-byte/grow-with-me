import { create } from 'zustand'
import type {
  AreaProgressItem,
  DashboardProgressResponse,
  WeeklyAssessment,
  WeeklyAssessmentCreate,
} from '../types/progress'
import {
  fetchAreasProgress,
  fetchDashboardProgress,
  fetchLatestAssessment,
  generateWeeklyReportApi,
  saveWeeklyAssessmentApi,
} from '../api/progress'

interface ProgressState {
  dashboard: DashboardProgressResponse | null
  areas: AreaProgressItem[]
  latestAssessment: WeeklyAssessment | null
  loading: boolean
  savingAssessment: boolean
  generatingReport: boolean
  error: string | null

  loadProgressData: () => Promise<void>
  saveAssessment: (payload: WeeklyAssessmentCreate) => Promise<WeeklyAssessment | null>
  generateReport: (assessmentId: number) => Promise<WeeklyAssessment | null>
}

export const useProgressStore = create<ProgressState>((set) => ({
  dashboard: null,
  areas: [],
  latestAssessment: null,
  loading: false,
  savingAssessment: false,
  generatingReport: false,
  error: null,

  loadProgressData: async () => {
    set({ loading: true, error: null })
    try {
      const [dash, areasData, assessment] = await Promise.all([
        fetchDashboardProgress(),
        fetchAreasProgress(),
        fetchLatestAssessment().catch(() => null),
      ])
      set({
        dashboard: dash,
        areas: areasData,
        latestAssessment: assessment,
        loading: false,
      })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки данных аналитики',
        loading: false,
      })
    }
  },

  saveAssessment: async (payload: WeeklyAssessmentCreate) => {
    set({ savingAssessment: true, error: null })
    try {
      const saved = await saveWeeklyAssessmentApi(payload)
      set({ latestAssessment: saved, savingAssessment: false })
      // Refresh areas progress as subjective scores updated
      const areasData = await fetchAreasProgress()
      set({ areas: areasData })
      return saved
    } catch (err: any) {
      set({
        savingAssessment: false,
        error: err.response?.data?.detail || 'Не удалось сохранить самооценку',
      })
      return null
    }
  },

  generateReport: async (assessmentId: number) => {
    set({ generatingReport: true, error: null })
    try {
      const updated = await generateWeeklyReportApi(assessmentId)
      set({ latestAssessment: updated, generatingReport: false })
      return updated
    } catch (err: any) {
      set({
        generatingReport: false,
        error: err.response?.data?.detail || 'Не удалось сформировать AI-отчёт недели',
      })
      return null
    }
  },
}))
