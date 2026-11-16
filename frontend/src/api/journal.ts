import { apiClient } from './client'
import type { JournalEntry, JournalStats } from '../types/journal'

export async function fetchTodayJournal(): Promise<JournalEntry | null> {
  const response = await apiClient.get<JournalEntry | null>('/journal/today')
  return response.data
}

export async function saveJournalApi(data: {
  entry_date?: string
  structured_answers?: Record<string, string>
  free_text?: string
  tomorrow_intentions?: string
  mood?: string
  tags?: string[]
}): Promise<JournalEntry> {
  const response = await apiClient.post<JournalEntry>('/journal', data)
  return response.data
}

export async function fetchJournalHistory(limit: number = 30): Promise<JournalEntry[]> {
  const response = await apiClient.get<JournalEntry[]>('/journal/history', {
    params: { limit },
  })
  return response.data
}

export async function fetchJournalStats(): Promise<JournalStats> {
  const response = await apiClient.get<JournalStats>('/journal/stats')
  return response.data
}
