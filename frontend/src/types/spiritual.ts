export interface AllahName {
  id: number
  number: number
  arabic_name: string
  transliteration: string
  meaning_ru: string
  explanation: string
  life_reflection: string
  source_reference?: string | null
}

export interface DailySpiritual {
  id: number
  display_date: string
  name: AllahName
  user_reflection?: string | null
  is_favorite: boolean
}
