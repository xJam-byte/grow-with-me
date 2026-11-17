import { create } from 'zustand'
import type { PersonalPrincipleItem, UserDataExport, UserProfile } from '../types/user'
import {
  createPrincipleApi,
  deletePrincipleApi,
  exportUserDataApi,
  fetchPrinciples,
  fetchProfile,
  resetUserDataApi,
  updatePrincipleApi,
  updateProfile,
} from '../api/profile'

interface UserState {
  profile: UserProfile | null
  principles: PersonalPrincipleItem[]
  loading: boolean
  saving: boolean
  error: string | null

  loadProfile: () => Promise<void>
  saveProfile: (data: Partial<UserProfile>) => Promise<void>
  loadPrinciples: () => Promise<void>
  addPrinciple: (text: string, category?: string) => Promise<void>
  editPrinciple: (id: number, data: Partial<PersonalPrincipleItem>) => Promise<void>
  removePrinciple: (id: number) => Promise<void>
  exportData: () => Promise<UserDataExport | null>
  resetData: () => Promise<boolean>
}

export const useUserStore = create<UserState>((set) => ({
  profile: null,
  principles: [],
  loading: false,
  saving: false,
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
    set({ saving: true, error: null })
    try {
      const updated = await updateProfile(data)
      set({ profile: updated, saving: false })
    } catch (err: any) {
      set({ error: err.message || 'Ошибка обновления профиля', saving: false })
    }
  },

  loadPrinciples: async () => {
    try {
      const data = await fetchPrinciples()
      set({ principles: data })
    } catch (err: any) {
      console.error('Failed to load principles', err)
    }
  },

  addPrinciple: async (text: string, category: string = 'general') => {
    try {
      const created = await createPrincipleApi({ text, category })
      set((state) => ({ principles: [...state.principles, created] }))
    } catch (err: any) {
      set({ error: err.message || 'Ошибка создания принципа' })
    }
  },

  editPrinciple: async (id: number, data: Partial<PersonalPrincipleItem>) => {
    try {
      const updated = await updatePrincipleApi(id, data)
      set((state) => ({
        principles: state.principles.map((p) => (p.id === id ? updated : p)),
      }))
    } catch (err: any) {
      set({ error: err.message || 'Ошибка обновления принципа' })
    }
  },

  removePrinciple: async (id: number) => {
    try {
      await deletePrincipleApi(id)
      set((state) => ({
        principles: state.principles.filter((p) => p.id !== id),
      }))
    } catch (err: any) {
      set({ error: err.message || 'Ошибка удаления принципа' })
    }
  },

  exportData: async () => {
    try {
      return await exportUserDataApi()
    } catch (err: any) {
      set({ error: err.message || 'Ошибка экспорта данных' })
      return null
    }
  },

  resetData: async () => {
    try {
      await resetUserDataApi()
      return true
    } catch (err: any) {
      set({ error: err.message || 'Ошибка сброса данных' })
      return false
    }
  },
}))
