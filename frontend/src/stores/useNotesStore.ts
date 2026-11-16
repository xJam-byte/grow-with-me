import { create } from 'zustand'
import type { NoteItem } from '../types/note'
import {
  createNoteApi,
  deleteNoteApi,
  fetchNotes,
  searchNotesApi,
  toggleNoteFavoriteApi,
  updateNoteApi,
} from '../api/notes'

interface NotesState {
  notes: NoteItem[]
  loading: boolean
  error: string | null
  activeCategory: string
  searchQuery: string
  setCategory: (category: string) => void
  setSearchQuery: (query: string) => void
  loadNotes: () => Promise<void>
  search: (query: string) => Promise<void>
  addNote: (data: { title: string; content: string; category?: string; tags?: string[] }) => Promise<void>
  updateNote: (id: number, data: Partial<NoteItem>) => Promise<void>
  removeNote: (id: number) => Promise<void>
  toggleFavorite: (id: number) => Promise<void>
}

export const useNotesStore = create<NotesState>((set, get) => ({
  notes: [],
  loading: false,
  error: null,
  activeCategory: 'all',
  searchQuery: '',

  setCategory: (category: string) => {
    set({ activeCategory: category })
    get().loadNotes()
  },

  setSearchQuery: (query: string) => {
    set({ searchQuery: query })
    if (!query.trim()) {
      get().loadNotes()
    } else {
      get().search(query)
    }
  },

  loadNotes: async () => {
    set({ loading: true, error: null })
    const { activeCategory } = get()
    try {
      const data = await fetchNotes({
        category: activeCategory === 'all' ? undefined : activeCategory,
      })
      set({ notes: data, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка загрузки заметок',
        loading: false,
      })
    }
  },

  search: async (query: string) => {
    set({ loading: true, error: null })
    try {
      const data = await searchNotesApi(query)
      set({ notes: data, loading: false })
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || err.message || 'Ошибка поиска',
        loading: false,
      })
    }
  },

  addNote: async (data) => {
    try {
      const created = await createNoteApi(data)
      set({ notes: [created, ...get().notes] })
    } catch (err) {
      console.error(err)
    }
  },

  updateNote: async (id: number, data: Partial<NoteItem>) => {
    try {
      const updated = await updateNoteApi(id, data)
      set({
        notes: get().notes.map((n) => (n.id === id ? updated : n)),
      })
    } catch (err) {
      console.error(err)
    }
  },

  removeNote: async (id: number) => {
    try {
      await deleteNoteApi(id)
      set({ notes: get().notes.filter((n) => n.id !== id) })
    } catch (err) {
      console.error(err)
    }
  },

  toggleFavorite: async (id: number) => {
    const current = get().notes
    const target = current.find((n) => n.id === id)
    if (!target) return
    const prev = target.is_favorite

    set({
      notes: current.map((n) =>
        n.id === id ? { ...n, is_favorite: !prev } : n
      ),
    })

    try {
      const res = await toggleNoteFavoriteApi(id)
      set({
        notes: get().notes.map((n) =>
          n.id === id ? { ...n, is_favorite: res.is_favorite } : n
        ),
      })
    } catch (err) {
      set({
        notes: current.map((n) =>
          n.id === id ? { ...n, is_favorite: prev } : n
        ),
      })
    }
  },
}))

