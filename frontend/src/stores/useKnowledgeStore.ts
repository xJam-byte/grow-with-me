import { create } from 'zustand'
import type { KnowledgeTopic } from '../types/knowledge'
import {
  askTopicQuestion,
  fetchTodayKnowledge,
  markKnowledgeRead,
  toggleKnowledgeFavorite,
  updateKnowledgeNotes,
} from '../api/knowledge'

interface KnowledgeState {
  topic: KnowledgeTopic | null
  loading: boolean
  error: string | null
  aiAnswer: string | null
  aiLoading: boolean
  loadTodayTopic: () => Promise<void>
  markRead: () => Promise<void>
  toggleFavorite: () => Promise<void>
  saveNotes: (notes: string) => Promise<void>
  askAI: (question: string) => Promise<void>
}

export const useKnowledgeStore = create<KnowledgeState>((set, get) => ({
  topic: null,
  loading: false,
  error: null,
  aiAnswer: null,
  aiLoading: false,

  loadTodayTopic: async () => {
    set({ loading: true, error: null })
    try {
      const data = await fetchTodayKnowledge()
      set({ topic: data, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки темы дня',
        loading: false,
      })
    }
  },

  markRead: async () => {
    const t = get().topic
    if (!t) return
    try {
      const updated = await markKnowledgeRead(t.id)
      set({ topic: updated })
    } catch (err) {
      console.error(err)
    }
  },

  toggleFavorite: async () => {
    const t = get().topic
    if (!t) return
    const prev = t.is_favorite
    set({ topic: { ...t, is_favorite: !prev } })
    try {
      const res = await toggleKnowledgeFavorite(t.id)
      set({ topic: { ...t, is_favorite: res.is_favorite } })
    } catch (err) {
      set({ topic: { ...t, is_favorite: prev } })
    }
  },

  saveNotes: async (notes: string) => {
    const t = get().topic
    if (!t) return
    try {
      const updated = await updateKnowledgeNotes(t.id, notes)
      set({ topic: updated })
    } catch (err) {
      console.error(err)
    }
  },

  askAI: async (question: string) => {
    const t = get().topic
    if (!t) return
    set({ aiLoading: true, aiAnswer: null })
    try {
      const res = await askTopicQuestion(t.id, question)
      set({ aiAnswer: res.answer, aiLoading: false })
    } catch (err: any) {
      set({
        aiAnswer: 'Не удалось получить ответ. Попробуйте позже.',
        aiLoading: false,
      })
    }
  },
}))

