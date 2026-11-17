import { apiClient } from './client'
import type { PersonalPrincipleItem, UserDataExport, UserProfile } from '../types/user'

export async function fetchProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/profile')
  return response.data
}

export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  const response = await apiClient.put<UserProfile>('/profile', data)
  return response.data
}

export async function fetchPrinciples(): Promise<PersonalPrincipleItem[]> {
  const response = await apiClient.get<PersonalPrincipleItem[]>('/profile/principles')
  return response.data
}

export async function createPrincipleApi(payload: {
  text: string
  category?: string
  sort_order?: number
}): Promise<PersonalPrincipleItem> {
  const response = await apiClient.post<PersonalPrincipleItem>('/profile/principles', payload)
  return response.data
}

export async function updatePrincipleApi(
  id: number,
  payload: Partial<PersonalPrincipleItem>
): Promise<PersonalPrincipleItem> {
  const response = await apiClient.put<PersonalPrincipleItem>(`/profile/principles/${id}`, payload)
  return response.data
}

export async function deletePrincipleApi(id: number): Promise<void> {
  await apiClient.delete(`/profile/principles/${id}`)
}

export async function exportUserDataApi(): Promise<UserDataExport> {
  const response = await apiClient.get<UserDataExport>('/profile/export')
  return response.data
}

export async function resetUserDataApi(): Promise<void> {
  await apiClient.post('/profile/reset')
}
