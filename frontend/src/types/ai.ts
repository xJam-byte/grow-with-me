export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant'
  content: string
  created_at?: string
  tools_used?: string[]
}

export interface AIPreferences {
  tone: 'strict' | 'balanced' | 'gentle'
  allow_journal_access: boolean
  allow_notes_access: boolean
  max_daily_tokens: number
}

export interface AIUsage {
  today_tokens: number
  daily_limit: number
  monthly_tokens: number
  estimated_cost_usd: number
  model: string
}

export interface AIAnalysis {
  period: string
  strengths: string[]
  weaknesses: string[]
  key_insight: string
  action_plan: string[]
  overall_score: number
}

