import { apiClient } from './client'
import type { AllahName, DailySpiritual } from '../types/spiritual'

export async function fetchTodaySpiritual(): Promise<DailySpiritual> {
  const response = await apiClient.get<DailySpiritual>('/spiritual/today')
  return response.data
}

export async function fetchAllAllahNames(): Promise<AllahName[]> {
  const response = await apiClient.get<AllahName[]>('/spiritual/names')
  return response.data
}

export async function saveSpiritualReflection(
  dailyId: number,
  reflection: string
): Promise<DailySpiritual> {
  const response = await apiClient.post<DailySpiritual>(`/spiritual/${dailyId}/reflection`, { reflection })
  return response.data
}

export async function toggleSpiritualFavorite(
  dailyId: number
): Promise<{ id: number; is_favorite: boolean }> {
  const response = await apiClient.post<{ id: number; is_favorite: boolean }>(`/spiritual/${dailyId}/favorite`)
  return response.data
}

