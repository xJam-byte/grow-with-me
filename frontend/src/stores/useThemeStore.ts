import { create } from 'zustand'

interface ThemeState {
  theme: 'dark' | 'light'
  setTheme: (theme: 'dark' | 'light') => void
  toggleTheme: () => void
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: 'dark',
  setTheme: (theme) => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    set({ theme })
  },
  toggleTheme: () => {
    set((state) => {
      const nextTheme = state.theme === 'dark' ? 'light' : 'dark'
      document.documentElement.classList.toggle('dark', nextTheme === 'dark')
      return { theme: nextTheme }
    })
  },
}))
