import React, { useEffect } from 'react'
import { Shield, Bell, Key, Sparkles, Check, User } from 'lucide-react'
import { useUserStore } from '../stores/useUserStore'
import { useTelegram } from '../hooks/useTelegram'

export const SettingsPage: React.FC = () => {
  const { profile, loadProfile } = useUserStore()
  const { user } = useTelegram()

  useEffect(() => {
    loadProfile()
  }, [])

  const principles = [
    'Держи своё слово.',
    'Бери на себя ответственность.',
    'Будь добрым, но не слабым.',
    'Оставайся скромным.',
    'Никогда не прекращай учиться.',
    'Уважай своё тело.',
    'Выбирай долгосрочную пользу вместо сиюминутного удовольствия.',
    'Никогда не пропускай дважды.',
  ]

  return (
    <div className="space-y-4 animate-fade-in pb-6">
      <div>
        <h2 className="text-lg font-bold text-[var(--text-primary)]">Профиль и настройки</h2>
        <p className="text-xs text-[var(--text-secondary)]">Твоя идентичность и конфигурация системы</p>
      </div>

      {/* User Info Header */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm flex items-center space-x-3">
        <div className="w-10 h-10 rounded-full bg-[var(--accent)] text-white flex items-center justify-center font-bold text-sm">
          <User className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            {profile?.first_name || user?.first_name || 'Пользователь'}
          </h3>
          <p className="text-[11px] text-[var(--text-secondary)] font-mono">
            @{profile?.username || user?.username || 'user'} • ID: {profile?.telegram_id || user?.id || 'Dev'}
          </p>
        </div>
      </div>

      {/* Identity Card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)]">
          <Sparkles className="w-4 h-4" />
          <h3 className="text-xs font-semibold uppercase tracking-wider">
            Идентичность (Identity Statement)
          </h3>
        </div>
        <p className="text-xs text-[var(--text-primary)] font-medium leading-relaxed">
          «Я становлюсь дисциплинированным, образованным, сострадательным, духовно развитым, физически здоровым и ментально сильным человеком.»
        </p>
      </div>

      {/* Principles */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)]">
          <Key className="w-4 h-4" />
          <h3 className="text-xs font-semibold uppercase tracking-wider">
            Главные правила и принципы
          </h3>
        </div>
        <div className="space-y-1.5">
          {principles.map((p, idx) => (
            <div key={idx} className="flex items-center space-x-2 text-xs text-[var(--text-secondary)]">
              <Check className="w-3.5 h-3.5 text-[var(--accent)] shrink-0" />
              <span>{p}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)]">
          <Bell className="w-4 h-4" />
          <h3 className="text-xs font-semibold uppercase tracking-wider">
            Уведомления
          </h3>
        </div>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center py-1">
            <span className="text-[var(--text-primary)]">Утреннее приветствие</span>
            <span className="text-[var(--text-secondary)] font-mono">07:30</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-[var(--text-primary)]">Тема дня (Daily Knowledge)</span>
            <span className="text-[var(--text-secondary)] font-mono">09:00</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-[var(--text-primary)]">Вечерняя рефлексия</span>
            <span className="text-[var(--text-secondary)] font-mono">21:30</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-[var(--text-primary)]">Напоминание о сне</span>
            <span className="text-[var(--text-secondary)] font-mono">23:00</span>
          </div>
        </div>
      </div>

      {/* Privacy & Security */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-emerald-500">
          <Shield className="w-4 h-4" />
          <h3 className="text-xs font-semibold uppercase tracking-wider">
            Приватность и безопасность
          </h3>
        </div>
        <p className="text-[11px] text-[var(--text-secondary)]">
          Все данные привязаны к твоему Telegram ID. Доступ защищён криптографической подписью initData.
        </p>
      </div>
    </div>
  )
}
