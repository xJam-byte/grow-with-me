import { create } from 'zustand'
import type { AIAnalysis, ChatMessage, AIPreferences, AIUsage } from '../types/ai'
import {
  clearChatHistoryApi,
  fetchAIUsageApi,
  fetchChatHistory,
  fetchWeeklyAnalysisApi,
  sendChatMessage,
  updateAIPreferencesApi,
} from '../api/ai'

const DEFAULT_WELCOME_MSG: ChatMessage = {
  role: 'assistant',
  content:
    'Ассаляму алейкум! Я твой персональный AI-коуч в Grow With Me. Я опираюсь на твои реальные привычки, цели и принципы. Никаких пустых лозунгов — только факты, честность и фокус на главном. О чём хочешь поговорить?',
}

interface AIState {
  messages: ChatMessage[]
  usage: AIUsage | null
  analysis: AIAnalysis | null
  loading: boolean
  analyzing: boolean
  error: string | null

  loadHistory: () => Promise<void>
  sendMessage: (text: string, contextType?: string) => Promise<void>
  clearHistory: () => Promise<void>
  loadUsage: () => Promise<void>
  runWeeklyAnalysis: () => Promise<void>
  updatePreferences: (prefs: Partial<AIPreferences>) => Promise<void>
}

export const useAIStore = create<AIState>((set, get) => ({
  messages: [DEFAULT_WELCOME_MSG],
  usage: null,
  analysis: null,
  loading: false,
  analyzing: false,
  error: null,

  loadHistory: async () => {
    try {
      const history = await fetchChatHistory()
      if (history && history.length > 0) {
        set({ messages: history })
      } else {
        set({ messages: [DEFAULT_WELCOME_MSG] })
      }
    } catch {
      // Keep default welcome message on offline/error
    }
  },

  sendMessage: async (text: string, contextType: string = 'general') => {
    const current = get().messages
    const userMsg: ChatMessage = { role: 'user', content: text }

    // 1. Optimistic append of user message
    set({
      messages: [...current, userMsg],
      loading: true,
      error: null,
    })

    try {
      const res = await sendChatMessage(text, contextType)
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.message,
        tools_used: res.tools_used,
      }
      set((state) => ({
        messages: [...state.messages, assistantMsg],
        loading: false,
      }))
      // Refresh token usage in background
      get().loadUsage()
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || err.message || 'Не удалось получить ответ от коуча'
      set((state) => ({
        messages: [
          ...state.messages,
          {
            role: 'assistant',
            content: `⚠️ ${errorMsg}. Проверь подключение к бэкенду.`,
          },
        ],
        loading: false,
      }))
    }
  },

  clearHistory: async () => {
    try {
      await clearChatHistoryApi()
      set({ messages: [DEFAULT_WELCOME_MSG] })
    } catch {
      set({ messages: [DEFAULT_WELCOME_MSG] })
    }
  },

  loadUsage: async () => {
    try {
      const usage = await fetchAIUsageApi()
      set({ usage })
    } catch {
      // Ignore background usage fetch error
    }
  },

  runWeeklyAnalysis: async () => {
    set({ analyzing: true, error: null })
    try {
      const analysis = await fetchWeeklyAnalysisApi()
      set({ analysis, analyzing: false })
    } catch (err: any) {
      set({
        analyzing: false,
        error: err.response?.data?.detail || 'Не удалось составить анализ недели',
      })
    }
  },

  updatePreferences: async (prefs: Partial<AIPreferences>) => {
    try {
      await updateAIPreferencesApi(prefs)
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Ошибка обновления настроек AI' })
    }
  },
}))

