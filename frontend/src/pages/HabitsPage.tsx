import React, { useState } from 'react'
import { CheckCircle2, Circle, Flame, Sparkles } from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'

interface HabitItem {
  id: number
  name: string
  category: string
  icon: string
  target: string
  streak: number
  completed: boolean
}

const initialHabits: HabitItem[] = [
  { id: 1, name: 'Подъём в одно время', category: 'Physical', icon: '⏰', target: '07:00', streak: 5, completed: true },
  { id: 2, name: 'Утренняя духовная практика / рефлексия', category: 'Spirituality', icon: '🤲', target: '10 мин', streak: 4, completed: true },
  { id: 3, name: 'Чтение книги', category: 'Intellectual', icon: '📖', target: 'мин. 10 стр.', streak: 12, completed: false },
  { id: 4, name: 'Deep Work / учёба', category: 'Academic', icon: '💻', target: 'мин. 60 мин', streak: 3, completed: false },
  { id: 5, name: 'Практика английского', category: 'Academic', icon: '🇬🇧', target: 'мин. 20 мин', streak: 8, completed: false },
  { id: 6, name: 'Физическая активность (тренировка / ходьба)', category: 'Physical', icon: '🏃', target: '30 мин', streak: 2, completed: false },
  { id: 7, name: 'Узнать что-то новое', category: 'Intellectual', icon: '💡', target: 'мин. 20 мин', streak: 9, completed: false },
  { id: 8, name: 'Сделать одно доброе дело', category: 'Spirituality', icon: '🤝', target: '1 действие', streak: 6, completed: false },
  { id: 9, name: 'Вечерний журнал / рефлексия', category: 'Mental', icon: '📝', target: '10 мин', streak: 11, completed: false },
  { id: 10, name: 'Сон вовремя', category: 'Physical', icon: '🌙', target: '23:30', streak: 7, completed: false },
]

export const HabitsPage: React.FC = () => {
  const [habits, setHabits] = useState<HabitItem[]>(initialHabits)
  const { impactOccurred } = useTelegram()

  const toggleHabit = (id: number) => {
    impactOccurred('medium')
    setHabits((prev) =>
      prev.map((h) => {
        if (h.id === id) {
          const nextState = !h.completed
          return {
            ...h,
            completed: nextState,
            streak: nextState ? h.streak + 1 : Math.max(0, h.streak - 1),
          }
        }
        return h
      })
    )
  }

  const completedCount = habits.filter((h) => h.completed).length

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Трекер привычек</h2>
          <p className="text-xs text-[var(--text-secondary)]">
            Принцип: «Никогда не пропускай дважды»
          </p>
        </div>
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[var(--accent)]/10 text-[var(--accent)] text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>{completedCount} / {habits.length}</span>
        </div>
      </div>

      {/* Habit Cards */}
      <div className="space-y-2">
        {habits.map((habit) => (
          <div
            key={habit.id}
            onClick={() => toggleHabit(habit.id)}
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
                  <span>Цель: {habit.target}</span>
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
      </div>
    </div>
  )
}
