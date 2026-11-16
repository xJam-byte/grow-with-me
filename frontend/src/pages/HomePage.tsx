import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, Circle, BookOpen, Compass, ChevronRight, Zap, Target } from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'
import { useHabitStore } from '../stores/useHabitStore'
import { useKnowledgeStore } from '../stores/useKnowledgeStore'
import { useSpiritualStore } from '../stores/useSpiritualStore'

export const HomePage: React.FC = () => {
  const { user, impactOccurred } = useTelegram()
  const { habits, loadHabits, toggleHabit } = useHabitStore()
  const { topic, loadTodayTopic } = useKnowledgeStore()
  const { daily, loadTodaySpiritual } = useSpiritualStore()

  useEffect(() => {
    loadHabits()
    loadTodayTopic()
    loadTodaySpiritual()
  }, [])

  const todayStr = new Intl.DateTimeFormat('ru-RU', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(new Date())

  const completedCount = habits.filter((h) => h.completed).length
  const totalCount = habits.length || 10
  const percentage = Math.round((completedCount / totalCount) * 100)

  const handleQuickToggle = (id: number, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    impactOccurred('medium')
    toggleHabit(id)
  }

  return (
    <div className="space-y-4 animate-fade-in pb-4">
      {/* Greeting card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs uppercase tracking-wider text-[var(--accent)] font-semibold">
            Grow With Me OS
          </span>
          <span className="text-xs text-[var(--text-secondary)] capitalize">
            {todayStr}
          </span>
        </div>
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          Привет, {user?.first_name || 'друг'}! 👋
        </h2>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          «Стань тем, кем ты гордишься. Каждый день — это шаг вперёд.»
        </p>
      </div>

      {/* Habit Tracker Quick Card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Target className="w-4 h-4 text-[var(--accent)]" />
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              Привычки сегодня
            </h3>
          </div>
          <Link
            to="/habits"
            className="text-xs text-[var(--accent)] hover:text-[var(--accent-hover)] font-medium flex items-center"
          >
            Все ({habits.length}) <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </Link>
        </div>

        {/* Progress bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-[var(--text-secondary)]">Прогресс дня</span>
            <span className="font-semibold text-[var(--text-primary)]">
              {completedCount} из {totalCount} ({percentage}%)
            </span>
          </div>
          <div className="w-full h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--accent)] rounded-full transition-all duration-300"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {/* Quick habit list (top 4) */}
        <div className="space-y-1.5">
          {habits.slice(0, 4).map((h) => (
            <div
              key={h.id}
              onClick={(e) => handleQuickToggle(h.id, e)}
              className="flex items-center justify-between p-2.5 rounded-xl bg-[var(--bg-secondary)] text-xs cursor-pointer hover:bg-[var(--bg-secondary)]/80 transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="text-base">{h.icon}</span>
                <span
                  className={
                    h.completed
                      ? 'line-through text-[var(--text-secondary)]'
                      : 'text-[var(--text-primary)] font-medium'
                  }
                >
                  {h.name}
                </span>
              </div>
              <button aria-label="Toggle habit">
                {h.completed ? (
                  <CheckCircle2 className="w-4 h-4 text-[var(--success)] transition-transform scale-105" />
                ) : (
                  <Circle className="w-4 h-4 text-[var(--text-secondary)]" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Principle */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm flex items-start space-x-3">
        <div className="p-2 rounded-xl bg-[var(--accent)]/10 text-[var(--accent)] shrink-0">
          <Zap className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <span className="text-[11px] font-semibold text-[var(--text-secondary)] uppercase tracking-wider">
            Принцип дня
          </span>
          <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">
            «Никогда не пропускай дважды. Ошибка — случайность, повторение ошибки — выбор.»
          </p>
        </div>
      </div>

      {/* Daily Knowledge & Spiritual Teasers with Real Links */}
      <div className="grid grid-cols-2 gap-3">
        {/* Daily Knowledge Card */}
        <Link
          to="/knowledge"
          className="bg-[var(--bg-card)] border border-[var(--border)] hover:border-[var(--accent)]/50 rounded-2xl p-3.5 shadow-sm transition-all duration-200 block select-none active:scale-[0.98]"
        >
          <div className="flex items-center space-x-1.5 text-[var(--accent)] mb-1.5">
            <BookOpen className="w-4 h-4" />
            <span className="text-[11px] font-semibold">Тема дня</span>
          </div>
          <h4 className="text-xs font-semibold text-[var(--text-primary)] line-clamp-1">
            {topic?.topic_title || 'Когнитивные искажения'}
          </h4>
          <p className="text-[11px] text-[var(--text-secondary)] line-clamp-2 mt-0.5">
            {topic?.introduction || 'Эффект привязки в принятии решений.'}
          </p>
          <div className="mt-2 text-[10px] text-[var(--accent)] font-medium flex items-center">
            Читать <ChevronRight className="w-3 h-3 ml-0.5" />
          </div>
        </Link>

        {/* Daily Spiritual Card */}
        <Link
          to="/spiritual"
          className="bg-[var(--bg-card)] border border-[var(--border)] hover:border-emerald-500/50 rounded-2xl p-3.5 shadow-sm transition-all duration-200 block select-none active:scale-[0.98]"
        >
          <div className="flex items-center space-x-1.5 text-emerald-500 mb-1.5">
            <Compass className="w-4 h-4" />
            <span className="text-[11px] font-semibold">Имя Аллаха</span>
          </div>
          <h4 className="text-xs font-semibold text-[var(--text-primary)]">
            {daily?.name?.transliteration || 'Аль-Алим'}{' '}
            <span className="font-serif text-emerald-400">
              ({daily?.name?.arabic_name || 'العليم'})
            </span>
          </h4>
          <p className="text-[11px] text-[var(--text-secondary)] line-clamp-2 mt-0.5">
            {daily?.name?.meaning_ru || 'Всезнающий, ведающий обо всём сущем.'}
          </p>
          <div className="mt-2 text-[10px] text-emerald-500 font-medium flex items-center">
            Изучить <ChevronRight className="w-3 h-3 ml-0.5" />
          </div>
        </Link>
      </div>
    </div>
  )
}
