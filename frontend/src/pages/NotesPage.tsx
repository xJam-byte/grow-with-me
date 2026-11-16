import React, { useEffect, useState } from 'react'
import {
  Search,
  Plus,
  Star,
  Trash2,
  Check,
  X,
  FileText,
} from 'lucide-react'
import { useNotesStore } from '../stores/useNotesStore'
import { useTelegram } from '../hooks/useTelegram'

const categories = [
  { key: 'all', label: 'Все' },
  { key: 'quick_notes', label: 'Быстрые' },
  { key: 'ideas', label: 'Идеи' },
  { key: 'book_notes', label: 'Книги' },
  { key: 'quotes', label: 'Цитаты' },
  { key: 'learning', label: 'Обучение' },
  { key: 'goals', label: 'Цели' },
]

export const NotesPage: React.FC = () => {
  const {
    notes,
    loading,
    activeCategory,
    searchQuery,
    setCategory,
    setSearchQuery,
    loadNotes,
    addNote,
    removeNote,
    toggleFavorite,
  } = useNotesStore()
  const { impactOccurred } = useTelegram()

  const [isCreating, setIsCreating] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newContent, setNewContent] = useState('')
  const [newCategory, setNewCategory] = useState('quick_notes')

  useEffect(() => {
    loadNotes()
  }, [loadNotes])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || !newContent.trim()) return
    impactOccurred('medium')
    await addNote({
      title: newTitle.trim(),
      content: newContent.trim(),
      category: newCategory,
    })
    setNewTitle('')
    setNewContent('')
    setIsCreating(false)
  }

  const handleDelete = (id: number) => {
    impactOccurred('medium')
    if (window.confirm('Удалить эту заметку?')) {
      removeNote(id)
    }
  }

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">База знаний и заметки</h2>
          <p className="text-xs text-[var(--text-secondary)]">Твои идеи, инсайты и выводы</p>
        </div>
        <button
          onClick={() => {
            impactOccurred('light')
            setIsCreating(!isCreating)
          }}
          className="px-3 py-1.5 rounded-xl bg-[var(--accent)] text-white text-xs font-semibold hover:bg-[var(--accent-hover)] transition-colors flex items-center space-x-1 shadow-sm"
        >
          {isCreating ? <X className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
          <span>{isCreating ? 'Отмена' : 'Создать'}</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-[var(--text-secondary)] absolute left-3 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Поиск по заметкам и мыслям..."
          className="w-full text-xs bg-[var(--bg-card)] border border-[var(--border)] rounded-xl pl-9 pr-3 py-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
        />
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => {
              impactOccurred('light')
              setCategory(cat.key)
            }}
            className={`text-xs px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              activeCategory === cat.key
                ? 'bg-[var(--accent)] text-white shadow-sm'
                : 'bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Create Note Form */}
      {isCreating && (
        <form
          onSubmit={handleCreate}
          className="bg-[var(--bg-card)] border border-[var(--accent)]/40 rounded-2xl p-4 shadow-md space-y-3 animate-fade-in"
        >
          <span className="text-xs font-semibold text-[var(--text-primary)] block">
            Новая заметка
          </span>

          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Заголовок заметки..."
            className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl px-3 py-2 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          />

          <textarea
            rows={4}
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Текст мысли, инсайта или цитаты..."
            className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
          />

          <div className="flex items-center justify-between pt-1">
            <select
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl px-2.5 py-1.5 text-[var(--text-primary)] focus:outline-none"
            >
              <option value="quick_notes">Быстрые</option>
              <option value="ideas">Идеи</option>
              <option value="book_notes">Книги</option>
              <option value="quotes">Цитаты</option>
              <option value="learning">Обучение</option>
              <option value="goals">Цели</option>
            </select>

            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-[var(--accent)] text-white text-xs font-semibold hover:bg-[var(--accent-hover)] transition-colors shadow-sm flex items-center space-x-1"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Сохранить</span>
            </button>
          </div>
        </form>
      )}

      {/* Notes List */}
      <div className="space-y-2.5">
        {notes.map((note) => (
          <div
            key={note.id}
            className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm hover:border-[var(--accent)]/30 transition-all space-y-2"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] uppercase font-semibold text-[var(--accent)] tracking-wider">
                  {categories.find((c) => c.key === note.category)?.label || note.category}
                </span>
                <h3 className="text-xs font-bold text-[var(--text-primary)] mt-0.5">
                  {note.title}
                </h3>
              </div>

              <div className="flex items-center space-x-1">
                <button
                  onClick={() => {
                    impactOccurred('light')
                    toggleFavorite(note.id)
                  }}
                  aria-label="Favorite"
                  className="p-1 text-[var(--text-secondary)] hover:text-amber-500 transition-colors"
                >
                  <Star
                    className={`w-3.5 h-3.5 ${
                      note.is_favorite ? 'fill-amber-500 text-amber-500' : ''
                    }`}
                  />
                </button>
                <button
                  onClick={() => handleDelete(note.id)}
                  aria-label="Delete"
                  className="p-1 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <p className="text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-line">
              {note.content}
            </p>

            <div className="pt-2 border-t border-[var(--border)] flex items-center justify-between text-[10px] text-[var(--text-secondary)]">
              <span>
                {new Intl.DateTimeFormat('ru-RU', {
                  day: 'numeric',
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit',
                }).format(new Date(note.created_at))}
              </span>
              {note.tags && note.tags.length > 0 && (
                <div className="flex space-x-1">
                  {note.tags.map((t, idx) => (
                    <span key={idx} className="px-1.5 py-0.5 rounded bg-[var(--bg-secondary)]">
                      #{t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {notes.length === 0 && !loading && (
          <div className="text-center py-16 space-y-2">
            <FileText className="w-8 h-8 text-[var(--text-secondary)]/50 mx-auto" />
            <p className="text-xs text-[var(--text-secondary)]">
              {searchQuery ? 'Ничего не найдено по вашему запросу' : 'У вас пока нет заметок в этой категории'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
