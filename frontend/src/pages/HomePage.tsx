import React from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, BookOpen, Compass, ChevronRight, Zap, Target } from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'

export const HomePage: React.FC = () => {
  const { user } = useTelegram()

  const todayStr = new Intl.DateTimeFormat('ru-RU', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(new Date())

  // Sample habits for preview
  const sampleHabits = [
    { name: 'Подъём в одно время', completed: true, icon: '⏰' },
    { name: 'Утренняя рефлексия', completed: true, icon: '🤲' },
    { name: 'Чтение книги (10 стр.)', completed: false, icon: '📖' },
    { name: 'Deep Work (60 мин)', completed: false, icon: '💻' },
    { name: 'Английский (20 мин)', completed: false, icon: '🇬🇧' },
  ]

  const completedCount = sampleHabits.filter((h) => h.completed).length

  return (
    <div className="space-y-4 animate-fade-in">
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
            Все (10) <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </Link>
        </div>

        {/* Progress bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-[var(--text-secondary)]">Прогресс дня</span>
            <span className="font-semibold text-[var(--text-primary)]">
              {completedCount} из {sampleHabits.length} ({Math.round((completedCount / sampleHabits.length) * 100)}%)
            </span>
          </div>
          <div className="w-full h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--accent)] rounded-full transition-all duration-300"
              style={{ width: `${(completedCount / sampleHabits.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Quick habit list */}
        <div className="space-y-1.5">
          {sampleHabits.slice(0, 4).map((h, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-2 rounded-xl bg-[var(--bg-secondary)] text-xs"
            >
              <div className="flex items-center space-x-2">
                <span>{h.icon}</span>
                <span className={h.completed ? 'line-through text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'}>
                  {h.name}
                </span>
              </div>
              <CheckCircle2
                className={`w-4 h-4 ${
                  h.completed ? 'text-[var(--success)]' : 'text-[var(--text-secondary)]'
                }`}
              />
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

      {/* Daily Knowledge & Spiritual Teasers */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3.5 shadow-sm">
          <div className="flex items-center space-x-1.5 text-[var(--accent)] mb-1.5">
            <BookOpen className="w-4 h-4" />
            <span className="text-[11px] font-semibold">Тема дня</span>
          </div>
          <h4 className="text-xs font-semibold text-[var(--text-primary)] line-clamp-1">
            Когнитивные искажения
          </h4>
          <p className="text-[11px] text-[var(--text-secondary)] line-clamp-2 mt-0.5">
            Эффект привязки (Anchoring effect) в принятии решений.
          </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3.5 shadow-sm">
          <div className="flex items-center space-x-1.5 text-emerald-500 mb-1.5">
            <Compass className="w-4 h-4" />
            <span className="text-[11px] font-semibold">Имя Аллаха</span>
          </div>
          <h4 className="text-xs font-semibold text-[var(--text-primary)]">
            Аль-Алим (العليم)
          </h4>
          <p className="text-[11px] text-[var(--text-secondary)] line-clamp-2 mt-0.5">
            Всезнающий, ведающий обо всём сущем.
          </p>
        </div>
      </div>
    </div>
  )
}
