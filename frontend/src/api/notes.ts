import { apiClient } from './client'
import type { NoteItem } from '../types/note'

export async function fetchNotes(params?: {
  category?: string
  is_favorite?: boolean
}): Promise<NoteItem[]> {
  const response = await apiClient.get<NoteItem[]>('/notes', { params })
  return response.data
}

export async function createNoteApi(data: {
  title: string
  content: string
  category?: string
  tags?: string[]
  is_favorite?: boolean
}): Promise<NoteItem> {
  const response = await apiClient.post<NoteItem>('/notes', data)
  return response.data
}

export async function updateNoteApi(
  id: number,
  data: Partial<NoteItem>
): Promise<NoteItem> {
  const response = await apiClient.put<NoteItem>(`/notes/${id}`, data)
  return response.data
}

export async function deleteNoteApi(id: number): Promise<void> {
  await apiClient.delete(`/notes/${id}`)
}

export async function toggleNoteFavoriteApi(id: number): Promise<{ id: number; is_favorite: boolean }> {
  const response = await apiClient.post<{ id: number; is_favorite: boolean }>(`/notes/${id}/favorite`)
  return response.data
}

export async function searchNotesApi(q: string): Promise<NoteItem[]> {
  const response = await apiClient.get<NoteItem[]>('/notes/search', {
    params: { q },
  })
  return response.data
}

