export interface JournalEntry {
  id: number
  user_id: number
  entry_date: string
  structured_answers?: Record<string, string> | null
  free_text?: string | null
  tomorrow_intentions?: string | null
  mood?: string | null
  tags?: string[] | null
  ai_summary?: string | null
  created_at: string
  updated_at: string
}

export interface JournalStats {
  total_entries: number
  streak_days: number
}

