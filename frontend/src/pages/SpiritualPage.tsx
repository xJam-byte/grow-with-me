import React, { useEffect, useState } from 'react'
import { Compass, Heart, Sparkles, Send, BookOpen, ChevronRight } from 'lucide-react'
import { useSpiritualStore } from '../stores/useSpiritualStore'
import { useTelegram } from '../hooks/useTelegram'

export const SpiritualPage: React.FC = () => {
  const { daily, allNames, loading, error, loadTodaySpiritual, loadAllNames, saveReflection, toggleFavorite } =
    useSpiritualStore()
  const { impactOccurred } = useTelegram()

  const [reflection, setReflection] = useState('')
  const [saved, setSaved] = useState(false)
  const [showCatalog, setShowCatalog] = useState(false)

  useEffect(() => {
    loadTodaySpiritual()
    loadAllNames()
  }, [loadTodaySpiritual, loadAllNames])

  useEffect(() => {
    if (daily?.user_reflection) {
      setReflection(daily.user_reflection)
    }
  }, [daily?.user_reflection])

  const handleSaveReflection = () => {
    impactOccurred('medium')
    saveReflection(reflection)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  if (loading && !daily) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-3">
        <Sparkles className="w-6 h-6 text-emerald-500 animate-spin" />
        <p className="text-xs text-[var(--text-secondary)]">Загружаем духовную практику...</p>
      </div>
    )
  }

  if (error || !daily) {
    return (
      <div className="p-4 rounded-2xl bg-red-500/10 text-red-500 text-xs">
        {error || 'Не удалось загрузить духовную практику'}
      </div>
    )
  }

  const { name } = daily

  return (
    <div className="space-y-4 animate-fade-in pb-10">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Духовный рост</h2>
          <p className="text-xs text-[var(--text-secondary)]">Прекрасные Имена Аллаха (Асма уль-Хусна)</p>
        </div>
        <button
          onClick={() => {
            impactOccurred('light')
            setShowCatalog(!showCatalog)
          }}
          className="text-xs px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-500 font-semibold hover:bg-emerald-500/20 transition-colors flex items-center"
        >
          {showCatalog ? 'Имя дня' : 'Все 99'}
          <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
        </button>
      </div>

      {!showCatalog ? (
        <>
          {/* Main Calligraphy Card */}
          <div className="bg-gradient-to-br from-emerald-950/40 via-[var(--bg-card)] to-[var(--bg-card)] border border-emerald-500/30 rounded-3xl p-6 text-center shadow-lg relative overflow-hidden">
            <div className="absolute top-4 right-4">
              <button
                onClick={() => {
                  impactOccurred('light')
                  toggleFavorite()
                }}
                aria-label="Favorite"
                className="p-2 rounded-full bg-[var(--bg-card)]/80 text-[var(--text-secondary)] hover:text-red-500 transition-colors"
              >
                <Heart
                  className={`w-4 h-4 ${
                    daily.is_favorite ? 'fill-red-500 text-red-500' : ''
                  }`}
                />
              </button>
            </div>

            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-500 inline-block mb-3">
              Имя #{name.number} из 99
            </span>

            {/* Arabic calligraphy */}
            <div className="py-2">
              <span className="text-4xl md:text-5xl font-serif text-emerald-400 tracking-wider font-bold">
                {name.arabic_name}
              </span>
            </div>

            {/* Transliteration & Russian meaning */}
            <h1 className="text-lg font-bold text-[var(--text-primary)] mt-1">
              {name.transliteration}
            </h1>
            <p className="text-sm font-medium text-emerald-500/90 mt-0.5">
              «{name.meaning_ru}»
            </p>
          </div>

          {/* Explanation */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-emerald-500 font-semibold text-xs">
              <Compass className="w-4 h-4" />
              <span>Толкование значения</span>
            </div>
            <p className="text-xs text-[var(--text-primary)] leading-relaxed whitespace-pre-line">
              {name.explanation}
            </p>
          </div>

          {/* Character & Life reflection */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
            <div className="flex items-center space-x-2 text-amber-500 font-semibold text-xs">
              <Sparkles className="w-4 h-4" />
              <span>Связь с характером и жизнью</span>
            </div>
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
              {name.life_reflection}
            </p>
          </div>

          {/* Reference */}
          {name.source_reference && (
            <div className="flex items-center space-x-2 text-[11px] text-[var(--text-secondary)] px-1">
              <BookOpen className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
              <span>Источник: {name.source_reference}</span>
            </div>
          )}

          {/* User Personal Reflection */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-primary)]">
                Моя рефлексия и намерение
              </span>
              {saved && (
                <span className="text-[11px] text-[var(--success)] font-medium">Сохранено! ✓</span>
              )}
            </div>
            <textarea
              rows={3}
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
              placeholder="Как понимание этого имени меняет мои поступки сегодня?"
              className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500 resize-none"
            />
            <button
              onClick={handleSaveReflection}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition-colors flex items-center justify-center space-x-1.5 shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Сохранить рефлексию</span>
            </button>
          </div>
        </>
      ) : (
        /* 99 Names Catalog View */
        <div className="space-y-2 animate-fade-in">
          <div className="text-xs text-[var(--text-secondary)] mb-1 px-1">
            Каталог 99 прекрасных имён Аллаха:
          </div>
          <div className="grid grid-cols-1 gap-2">
            {allNames.map((n) => (
              <div
                key={n.id}
                className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-3 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-3">
                  <span className="w-6 h-6 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center text-[10px] font-bold">
                    {n.number}
                  </span>
                  <div>
                    <h4 className="font-semibold text-[var(--text-primary)]">
                      {n.transliteration}
                    </h4>
                    <p className="text-[11px] text-[var(--text-secondary)]">{n.meaning_ru}</p>
                  </div>
                </div>
                <span className="text-lg font-serif text-emerald-400 font-bold">
                  {n.arabic_name}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
