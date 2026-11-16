import React from 'react'
import { Sun, Moon, Sparkles } from 'lucide-react'
import { useThemeStore } from '../../stores/useThemeStore'
import { useTelegram } from '../../hooks/useTelegram'

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore()
  const { user, impactOccurred } = useTelegram()

  const handleThemeToggle = () => {
    impactOccurred('light')
    toggleTheme()
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-[var(--bg-card)]/80 backdrop-blur-md border-b border-[var(--border)] transition-colors">
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 rounded-lg bg-[var(--accent)] flex items-center justify-center text-white shadow-sm">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h1 className="text-sm font-semibold tracking-tight text-[var(--text-primary)]">
            Grow With Me
          </h1>
          <p className="text-[11px] text-[var(--text-secondary)]">
            {user?.first_name || 'Personal OS'}
          </p>
        </div>
      </div>

      <button
        onClick={handleThemeToggle}
        aria-label="Toggle theme"
        className="w-8 h-8 rounded-full flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-secondary)] transition-colors"
      >
        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  )
}
