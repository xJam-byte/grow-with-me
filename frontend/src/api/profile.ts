import { apiClient } from './client'
import type { UserProfile } from '../types/user'

export async function fetchProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/profile')
  return response.data
}

export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  const response = await apiClient.put<UserProfile>('/profile', data)
  return response.data
}
