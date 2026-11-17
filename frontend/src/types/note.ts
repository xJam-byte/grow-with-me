export interface NoteItem {
  id: number;
  user_id: number;
  title: string;
  content: string;
  category: string;
  tags?: string[] | null;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}
