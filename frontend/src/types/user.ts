export interface IdentityStatement {
  title: string
  values: string[]
  vision: string
}

export interface NotificationSettings {
  morning_greeting: { enabled: boolean; time: string }
  daily_knowledge: { enabled: boolean; time: string }
  spiritual_name: { enabled: boolean; time: string }
  evening_reflection: { enabled: boolean; time: string }
  sleep_reminder: { enabled: boolean; time: string }
  weekly_review: { enabled: boolean; day: string; time: string }
}

export interface AIPreferences {
  tone: 'strict' | 'balanced' | 'gentle'
  allow_journal_access: boolean
  allow_notes_access: boolean
  max_daily_tokens: number
}

export interface PersonalPrincipleItem {
  id: number
  text: string
  category: string
  sort_order: number
  is_active: boolean
  created_at: string
}

export interface UserDataExport {
  export_date: string
  user: Record<string, any>
  principles: Array<Record<string, any>>
  habits: Array<Record<string, any>>
  journal_entries: Array<Record<string, any>>
  notes: Array<Record<string, any>>
  weekly_assessments: Array<Record<string, any>>
}
export interface UserProfile {
  id: number
  telegram_id: number
  username?: string | null
  first_name?: string | null
  last_name?: string | null
  identity_statement?: IdentityStatement | null
  ai_preferences?: AIPreferences | null
  notification_settings?: NotificationSettings | null
  timezone: string
  language: string
  theme: string
  created_at: string
  updated_at: string
}

