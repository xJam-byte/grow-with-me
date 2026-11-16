import React, { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Flame, Sparkles, AlertCircle, RefreshCw, TrendingUp } from 'lucide-react'
import { useHabitStore } from '../stores/useHabitStore'
import { useTelegram } from '../hooks/useTelegram'

export const HabitsPage: React.FC = () => {
  const { habits, stats, loading, error, loadHabits, toggleHabit } = useHabitStore()
  const { impactOccurred } = useTelegram()
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    loadHabits()
  }, [])

  const handleToggle = (id: number) => {
    impactOccurred('medium')
    toggleHabit(id)
  }

  const categories = [
    { key: 'all', label: 'Все' },
    { key: 'spirituality', label: 'Духовность' },
    { key: 'intellectual', label: 'Интеллект' },
    { key: 'physical', label: 'Тело' },
    { key: 'mental', label: 'Ментальность' },
    { key: 'academic', label: 'Учёба' },
  ]

  const filteredHabits = habits.filter((h) => {
    if (selectedCategory === 'all') return true
    return h.category.toLowerCase() === selectedCategory.toLowerCase()
  })

  const completedCount = habits.filter((h) => h.completed).length
  const totalCount = habits.length

  return (
    <div className="space-y-4 animate-fade-in pb-4">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Трекер привычек</h2>
          <p className="text-xs text-[var(--text-secondary)]">
            Принцип: «Никогда не пропускай дважды»
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => loadHabits()}
            disabled={loading}
            aria-label="Refresh habits"
            className="p-1.5 rounded-full hover:bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[var(--accent)]/10 text-[var(--accent)] text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>
              {completedCount} / {totalCount}
            </span>
          </div>
        </div>
      </div>

      {/* Stats summary if available */}
      {stats && (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3 flex items-center justify-between text-xs shadow-sm">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)]">
              <TrendingUp className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="text-[var(--text-secondary)] block text-[10px]">Недельный темп</span>
              <span className="font-bold text-[var(--text-primary)]">
                {stats.weekly_completion_percentage}% выполнено
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[var(--text-secondary)] block text-[10px]">Сегодня</span>
            <span className="font-bold text-[var(--accent)]">
              {stats.completion_percentage}%
            </span>
          </div>
        </div>
      )}

      {/* Category Pills */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => {
              impactOccurred('light')
              setSelectedCategory(cat.key)
            }}
            className={`text-xs px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              selectedCategory === cat.key
                ? 'bg-[var(--accent)] text-white shadow-sm'
                : 'bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Error display */}
      {error && (
        <div className="flex items-center space-x-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Habit List */}
      <div className="space-y-2">
        {filteredHabits.map((habit) => (
          <div
            key={habit.id}
            onClick={() => handleToggle(habit.id)}
            className={`flex items-center justify-between p-3.5 rounded-2xl border transition-all duration-200 cursor-pointer select-none active:scale-[0.98] ${
              habit.completed
                ? 'bg-[var(--bg-card)] border-emerald-500/30 shadow-sm'
                : 'bg-[var(--bg-card)] border-[var(--border)] hover:border-[var(--accent)]/40'
            }`}
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{habit.icon}</span>
              <div>
                <h4
                  className={`text-xs font-medium ${
                    habit.completed
                      ? 'line-through text-[var(--text-secondary)]'
                      : 'text-[var(--text-primary)] font-semibold'
                  }`}
                >
                  {habit.name}
                </h4>
                <div className="flex items-center space-x-2 text-[11px] text-[var(--text-secondary)] mt-0.5">
                  <span>
                    Цель: {habit.target_value} {habit.target_unit || ''}
                  </span>
                  <span>•</span>
                  <span className="flex items-center text-amber-500">
                    <Flame className="w-3 h-3 mr-0.5" />
                    {habit.streak} дн.
                  </span>
                </div>
              </div>
            </div>

            <button
              aria-label="Toggle completion"
              className="p-1 focus:outline-none"
            >
              {habit.completed ? (
                <CheckCircle2 className="w-6 h-6 text-[var(--success)] transition-transform duration-200 scale-110" />
              ) : (
                <Circle className="w-6 h-6 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors" />
              )}
            </button>
          </div>
        ))}

        {filteredHabits.length === 0 && !loading && (
          <div className="text-center py-10 text-[var(--text-secondary)] text-xs">
            Нет привычек в этой категории
          </div>
        )}
      </div>
    </div>
  )
}
