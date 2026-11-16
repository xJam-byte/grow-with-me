export interface KnowledgeTopic {
  id: number
  user_id: number
  knowledge_date: string
  topic_title: string
  category: string
  introduction: string
  explanation: string
  facts: string
  practical_application: string
  reflection_question: string
  additional_resources?: string | null
  is_read: boolean
  is_favorite: boolean
  user_notes?: string | null
  created_at: string
}
