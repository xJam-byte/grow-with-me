import { apiClient } from './client'
import type { AIAnalysis, ChatMessage, AIPreferences, AIUsage } from '../types/ai'

export async function sendChatMessage(
  message: string,
  context_type: string = 'general'
): Promise<{ message: string; role: string; tokens_used: number; tools_used: string[] }> {
  const res = await apiClient.post('/ai/chat', { message, context_type })
  return res.data
}

export async function fetchChatHistory(): Promise<ChatMessage[]> {
  const res = await apiClient.get<ChatMessage[]>('/ai/history')
  return res.data
}

export async function clearChatHistoryApi(): Promise<void> {
  await apiClient.delete('/ai/history')
}

export async function fetchWeeklyAnalysisApi(): Promise<AIAnalysis> {
  const res = await apiClient.post<AIAnalysis>('/ai/analyze/week')
  return res.data
}

export async function fetchAIUsageApi(): Promise<AIUsage> {
  const res = await apiClient.get<AIUsage>('/ai/usage')
  return res.data
}

export async function updateAIPreferencesApi(
  prefs: Partial<AIPreferences>
): Promise<{ status: string; ai_preferences: AIPreferences }> {
  const res = await apiClient.put('/ai/preferences', prefs)
  return res.data
}

