import React from 'react'
import { NavLink } from 'react-router-dom'
import { Home, CheckSquare, TrendingUp, BookOpen, Bot, Settings } from 'lucide-react'
import { useTelegram } from '../../hooks/useTelegram'

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  { to: '/', label: 'Главная', icon: Home },
  { to: '/habits', label: 'Привычки', icon: CheckSquare },
  { to: '/growth', label: 'Рост', icon: TrendingUp },
  { to: '/journal', label: 'Журнал', icon: BookOpen },
  { to: '/ai', label: 'AI Коуч', icon: Bot },
  { to: '/settings', label: 'Профиль', icon: Settings },
]

export const BottomNav: React.FC = () => {
  const { selectionChanged } = useTelegram()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 bg-[var(--bg-card)]/90 backdrop-blur-md border-t border-[var(--border)] px-1 py-1 safe-area-pb">
      <div className="flex justify-around items-center max-w-lg mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => selectionChanged()}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center py-1.5 px-2 rounded-xl transition-all duration-150 ${
                  isActive
                    ? 'text-[var(--accent)] font-medium scale-105'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`
              }
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="text-[10px] tracking-tight">{item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}

