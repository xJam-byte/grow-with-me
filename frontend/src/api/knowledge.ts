import { apiClient } from './client'
import type { KnowledgeTopic } from '../types/knowledge'

export async function fetchTodayKnowledge(): Promise<KnowledgeTopic> {
  const response = await apiClient.get<KnowledgeTopic>('/knowledge/today')
  return response.data
}

export async function markKnowledgeRead(id: number): Promise<KnowledgeTopic> {
  const response = await apiClient.post<KnowledgeTopic>(`/knowledge/${id}/read`)
  return response.data
}

export async function toggleKnowledgeFavorite(id: number): Promise<{ id: number; is_favorite: boolean }> {
  const response = await apiClient.post<{ id: number; is_favorite: boolean }>(`/knowledge/${id}/favorite`)
  return response.data
}

export async function updateKnowledgeNotes(id: number, notes: string): Promise<KnowledgeTopic> {
  const response = await apiClient.put<KnowledgeTopic>(`/knowledge/${id}/notes`, { notes })
  return response.data
}

export async function askTopicQuestion(
  id: number,
  question: string
): Promise<{ question: string; answer: string }> {
  const response = await apiClient.post<{ question: string; answer: string }>(`/knowledge/${id}/ask`, { question })
  return response.data
}

export async function fetchKnowledgeHistory(): Promise<KnowledgeTopic[]> {
  const response = await apiClient.get<KnowledgeTopic[]>('/knowledge/history')
  return response.data
}
