import { create } from 'zustand'
import type { UserProfile } from '../types/user'
import { fetchProfile, updateProfile } from '../api/profile'

interface UserState {
  profile: UserProfile | null
  loading: boolean
  error: string | null
  loadProfile: () => Promise<void>
  saveProfile: (data: Partial<UserProfile>) => Promise<void>
}

export const useUserStore = create<UserState>((set) => ({
  profile: null,
  loading: false,
  error: null,

  loadProfile: async () => {
    set({ loading: true, error: null })
    try {
      const data = await fetchProfile()
      set({ profile: data, loading: false })
    } catch (err: any) {
      set({ error: err.message || 'Ошибка загрузки профиля', loading: false })
    }
  },

  saveProfile: async (data: Partial<UserProfile>) => {
    set({ loading: true, error: null })
    try {
      const updated = await updateProfile(data)
      set({ profile: updated, loading: false })
    } catch (err: any) {
      set({ error: err.message || 'Ошибка обновления профиля', loading: false })
    }
  },
}))
