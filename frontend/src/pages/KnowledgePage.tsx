import React, { useEffect, useState } from 'react'
import {
  BookOpen,
  CheckCircle2,
  Heart,
  Lightbulb,
  Sparkles,
  HelpCircle,
  Send,
  Bookmark,
} from 'lucide-react'
import { useKnowledgeStore } from '../stores/useKnowledgeStore'
import { useTelegram } from '../hooks/useTelegram'

export const KnowledgePage: React.FC = () => {
  const { topic, loading, error, aiAnswer, aiLoading, loadTodayTopic, markRead, toggleFavorite, saveNotes, askAI } =
    useKnowledgeStore()
  const { impactOccurred } = useTelegram()

  const [notes, setNotes] = useState('')
  const [question, setQuestion] = useState('')
  const [notesSaved, setNotesSaved] = useState(false)

  useEffect(() => {
    loadTodayTopic()
  }, [])

  useEffect(() => {
    if (topic?.user_notes) {
      setNotes(topic.user_notes)
    }
  }, [topic?.user_notes])

  const handleSaveNotes = () => {
    impactOccurred('medium')
    saveNotes(notes)
    setNotesSaved(true)
    setTimeout(() => setNotesSaved(false), 2000)
  }

  const handleAskAI = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return
    impactOccurred('light')
    askAI(question)
  }

  if (loading && !topic) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-3">
        <Sparkles className="w-6 h-6 text-[var(--accent)] animate-spin" />
        <p className="text-xs text-[var(--text-secondary)]">Готовим тему дня...</p>
      </div>
    )
  }

  if (error || !topic) {
    return (
      <div className="p-4 rounded-2xl bg-red-500/10 text-red-500 text-xs">
        {error || 'Не удалось загрузить тему дня'}
      </div>
    )
  }

  return (
    <div className="space-y-4 animate-fade-in pb-10">
      {/* Category & Title */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="px-2.5 py-1 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)] text-[11px] font-semibold uppercase tracking-wider">
            {topic.category}
          </span>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => {
                impactOccurred('light')
                toggleFavorite()
              }}
              aria-label="Favorite"
              className="p-1.5 rounded-full hover:bg-[var(--bg-secondary)] text-[var(--text-secondary)] transition-colors"
            >
              <Heart
                className={`w-4 h-4 ${
                  topic.is_favorite ? 'fill-red-500 text-red-500' : ''
                }`}
              />
            </button>
            <button
              onClick={() => {
                impactOccurred('medium')
                markRead()
              }}
              aria-label="Mark as read"
              className={`p-1.5 rounded-full hover:bg-[var(--bg-secondary)] transition-colors ${
                topic.is_read ? 'text-[var(--success)]' : 'text-[var(--text-secondary)]'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <h1 className="text-base font-bold text-[var(--text-primary)] leading-snug">
          {topic.topic_title}
        </h1>

        <p className="text-xs text-[var(--text-secondary)] leading-relaxed italic border-l-2 border-[var(--accent)] pl-2.5 py-0.5">
          {topic.introduction}
        </p>
      </div>

      {/* Main Explanation */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-[var(--text-primary)] font-semibold text-xs">
          <BookOpen className="w-4 h-4 text-[var(--accent)]" />
          <span>Подробный разбор</span>
        </div>
        <p className="text-xs text-[var(--text-primary)] leading-relaxed whitespace-pre-line">
          {topic.explanation}
        </p>
      </div>

      {/* Interesting Facts */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-amber-500 font-semibold text-xs">
          <Lightbulb className="w-4 h-4" />
          <span>Научный факт / Эксперимент</span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {topic.facts}
        </p>
      </div>

      {/* Practical Application */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-emerald-500 font-semibold text-xs">
          <Sparkles className="w-4 h-4" />
          <span>Практическое применение</span>
        </div>
        <p className="text-xs text-[var(--text-primary)] leading-relaxed">
          {topic.practical_application}
        </p>
      </div>

      {/* Reflection Question */}
      <div className="bg-[var(--bg-card)] border border-[var(--accent)]/30 rounded-2xl p-4 shadow-sm space-y-2 bg-[var(--accent)]/5">
        <div className="flex items-center space-x-2 text-[var(--accent)] font-semibold text-xs">
          <HelpCircle className="w-4 h-4" />
          <span>Вопрос для рефлексии</span>
        </div>
        <p className="text-xs font-medium text-[var(--text-primary)] leading-relaxed">
          «{topic.reflection_question}»
        </p>
      </div>

      {/* Recommended Resource */}
      {topic.additional_resources && (
        <div className="flex items-center space-x-2 text-[11px] text-[var(--text-secondary)] px-1">
          <Bookmark className="w-3.5 h-3.5 text-[var(--accent)] shrink-0" />
          <span>Источник: {topic.additional_resources}</span>
        </div>
      )}

      {/* AI Q&A Section */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)] font-semibold text-xs">
          <Sparkles className="w-4 h-4" />
          <span>Спросить AI по этой теме</span>
        </div>

        <form onSubmit={handleAskAI} className="flex space-x-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Что именно непонятно в этой теме?"
            className="flex-1 text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl px-3 py-2 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          />
          <button
            type="submit"
            disabled={aiLoading}
            aria-label="Ask"
            className="px-3 py-2 rounded-xl bg-[var(--accent)] text-white text-xs font-semibold hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50"
          >
            {aiLoading ? <Sparkles className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>

        {aiAnswer && (
          <div className="p-3 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border)] text-xs text-[var(--text-primary)] leading-relaxed animate-fade-in">
            <span className="font-semibold block text-[11px] text-[var(--accent)] mb-1">
              Ответ AI-ассистента:
            </span>
            {aiAnswer}
          </div>
        )}
      </div>

      {/* User Notes */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-[var(--text-primary)]">
            Мои заметки и выводы
          </span>
          {notesSaved && (
            <span className="text-[11px] text-[var(--success)] font-medium">Сохранено! ✓</span>
          )}
        </div>
        <textarea
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Запиши свои инсайты или как это связано с твоими планами..."
          className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
        />
        <button
          onClick={handleSaveNotes}
          className="w-full py-2 rounded-xl bg-[var(--bg-secondary)] hover:bg-[var(--border)] text-xs font-medium text-[var(--text-primary)] transition-colors"
        >
          Сохранить заметку
        </button>
      </div>
    </div>
  )
}
