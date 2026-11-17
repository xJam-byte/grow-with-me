import React, { useEffect, useState } from 'react'
import {
  Shield,
  Bell,
  Key,
  Sparkles,
  Check,
  User,
  Plus,
  Trash2,
  Download,
  AlertTriangle,
  Moon,
  Sun,
  Edit2,
  CheckCircle2,
} from 'lucide-react'
import { useUserStore } from '../stores/useUserStore'
import { useThemeStore } from '../stores/useThemeStore'
import { useTelegram } from '../hooks/useTelegram'
import type { NotificationSettings } from '../types/user'

export const SettingsPage: React.FC = () => {
  const {
    profile,
    principles,
    saving,
    loadProfile,
    saveProfile,
    loadPrinciples,
    addPrinciple,
    editPrinciple,
    removePrinciple,
    exportData,
    resetData,
  } = useUserStore()

  const { theme, toggleTheme } = useThemeStore()
  const { user, impactOccurred } = useTelegram()

  // Principles state
  const [newPrincipleText, setNewPrincipleText] = useState('')

  // Identity editing state
  const [editingIdentity, setEditingIdentity] = useState(false)
  const [identityVision, setIdentityVision] = useState('')

  // Notification state
  const [notifications, setNotifications] = useState<NotificationSettings>({
    morning_greeting: { enabled: true, time: '07:30' },
    daily_knowledge: { enabled: true, time: '09:00' },
    spiritual_name: { enabled: true, time: '12:00' },
    evening_reflection: { enabled: true, time: '21:30' },
    sleep_reminder: { enabled: true, time: '23:00' },
    weekly_review: { enabled: true, day: 'sunday', time: '19:00' },
  })

  // Reset confirmation
  const [showResetConfirm, setShowResetConfirm] = useState(false)
  const [toastMsg, setToastMsg] = useState<string | null>(null)

  useEffect(() => {
    loadProfile()
    loadPrinciples()
  }, [])

  useEffect(() => {
    if (profile?.identity_statement?.vision) {
      setIdentityVision(profile.identity_statement.vision)
    }
    if (profile?.notification_settings) {
      setNotifications(profile.notification_settings)
    }
  }, [profile])

  const showToast = (msg: string) => {
    setToastMsg(msg)
    setTimeout(() => setToastMsg(null), 3000)
  }

  const handleAddPrinciple = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPrincipleText.trim()) return
    impactOccurred('medium')
    await addPrinciple(newPrincipleText.trim())
    setNewPrincipleText('')
    showToast('Принцип добавлен!')
  }

  const handleTogglePrinciple = async (id: number, currentActive: boolean) => {
    impactOccurred('light')
    await editPrinciple(id, { is_active: !currentActive })
  }

  const handleDeletePrinciple = async (id: number) => {
    impactOccurred('medium')
    await removePrinciple(id)
    showToast('Принцип удалён')
  }

  const handleSaveIdentity = async () => {
    impactOccurred('medium')
    const currentIdentity = profile?.identity_statement || {
      title: 'Личность',
      values: [],
      vision: '',
    }
    await saveProfile({
      identity_statement: {
        ...currentIdentity,
        vision: identityVision,
      },
    })
    setEditingIdentity(false)
    showToast('Вижн идентичности сохранён!')
  }

  const handleToggleNotification = async (
    key: keyof NotificationSettings,
    field: 'enabled' | 'time',
    value: any
  ) => {
    impactOccurred('light')
    const updated = {
      ...notifications,
      [key]: {
        ...notifications[key],
        [field]: value,
      },
    }
    setNotifications(updated)
    await saveProfile({ notification_settings: updated })
  }

  const handleExport = async () => {
    impactOccurred('light')
    const data = await exportData()
    if (!data) {
      showToast('Ошибка при экспорте данных')
      return
    }

    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute(
      'download',
      `grow_with_me_backup_${new Date().toISOString().slice(0, 10)}.json`
    )
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
    showToast('Резервная копия скачана!')
  }

  const handleReset = async () => {
    impactOccurred('medium')
    const ok = await resetData()
    setShowResetConfirm(false)
    if (ok) {
      showToast('Прогресс успешно сброшен')
      loadProfile()
    } else {
      showToast('Ошибка сброса')
    }
  }

  return (
    <div className="space-y-4 animate-fade-in pb-10 relative">
      {/* Toast Notification */}
      {toastMsg && (
        <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-[var(--bg-card)] border border-[var(--accent)] text-[var(--accent)] px-4 py-2 rounded-xl text-xs font-semibold shadow-lg animate-fade-in flex items-center space-x-1.5">
          <CheckCircle2 className="w-4 h-4" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-[var(--text-primary)]">Профиль и Настройки</h2>
        <p className="text-xs text-[var(--text-secondary)]">
          Идентичность, личные правила, расписание и управление данными
        </p>
      </div>

      {/* 1. User Info Header Card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm flex items-center space-x-3">
        <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-orange-500 to-amber-400 text-white flex items-center justify-center font-bold text-base shadow-sm">
          <User className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-[var(--text-primary)] truncate">
            {profile?.first_name || user?.first_name || 'Пользователь'}
          </h3>
          <p className="text-[11px] text-[var(--text-secondary)] font-mono truncate">
            @{profile?.username || user?.username || 'user'} • ID: {profile?.telegram_id || user?.id || 'Dev'}
          </p>
        </div>
        <button
          onClick={toggleTheme}
          aria-label="Сменить тему"
          className="p-2 rounded-xl bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>

      {/* 2. Identity Statement Card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-[var(--accent)]">
            <Sparkles className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider">
              Идентичность (Identity Statement)
            </h3>
          </div>
          <button
            onClick={() => setEditingIdentity(!editingIdentity)}
            className="text-[11px] text-[var(--accent)] hover:underline font-semibold flex items-center space-x-1"
          >
            <Edit2 className="w-3 h-3" />
            <span>{editingIdentity ? 'Отмена' : 'Изменить'}</span>
          </button>
        </div>

        {editingIdentity ? (
          <div className="space-y-2">
            <textarea
              value={identityVision}
              onChange={(e) => setIdentityVision(e.target.value)}
              rows={3}
              className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-3 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] leading-relaxed"
              placeholder="Каким человеком ты становишься?"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={handleSaveIdentity}
                disabled={saving}
                className="px-3 py-1.5 bg-[var(--accent)] text-white text-xs font-semibold rounded-xl hover:bg-[var(--accent-hover)] transition-colors shadow-sm"
              >
                Сохранить вижн
              </button>
            </div>
          </div>
        ) : (
          <blockquote className="border-l-2 border-[var(--accent)] pl-3 text-xs text-[var(--text-primary)] italic leading-relaxed">
            «{profile?.identity_statement?.vision || identityVision || 'Стань тем, кем ты гордишься. Каждый день — это шаг вперёд.'}»
          </blockquote>
        )}

        {/* Core Values */}
        {profile?.identity_statement?.values && profile.identity_statement.values.length > 0 && (
          <div className="pt-2 border-t border-[var(--border)]">
            <span className="text-[10px] text-[var(--text-secondary)] uppercase font-semibold">
              Ключевые ценности:
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {profile.identity_statement.values.map((v: string, idx: number) => (
                <span
                  key={idx}
                  className="text-[11px] px-2.5 py-1 rounded-lg bg-[var(--bg-secondary)] text-[var(--text-secondary)] font-medium border border-[var(--border)]"
                >
                  {v}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. Personal Principles Management */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)]">
          <Key className="w-4 h-4" />
          <h3 className="text-xs font-bold uppercase tracking-wider">
            Личные правила и принципы ({principles.filter((p) => p.is_active).length})
          </h3>
        </div>

        {/* Add Principle Form */}
        <form onSubmit={handleAddPrinciple} className="flex items-center space-x-2">
          <input
            type="text"
            value={newPrincipleText}
            onChange={(e) => setNewPrincipleText(e.target.value)}
            placeholder="Новое правило (напр: 'Никогда не пропускай дважды')..."
            className="flex-1 text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl px-3 py-2 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          />
          <button
            type="submit"
            disabled={!newPrincipleText.trim()}
            className="p-2 rounded-xl bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors shadow-sm disabled:opacity-40"
          >
            <Plus className="w-4 h-4" />
          </button>
        </form>

        {/* List of Principles */}
        <div className="space-y-1.5 pt-1">
          {principles.map((p) => (
            <div
              key={p.id}
              className={`p-2.5 rounded-xl border flex items-center justify-between transition-all ${
                p.is_active
                  ? 'bg-[var(--bg-secondary)] border-[var(--border)] text-[var(--text-primary)]'
                  : 'bg-[var(--bg-secondary)]/50 border-transparent text-[var(--text-secondary)] opacity-50 line-through'
              }`}
            >
              <div
                onClick={() => handleTogglePrinciple(p.id, p.is_active)}
                className="flex items-center space-x-2 flex-1 cursor-pointer"
              >
                <div
                  className={`w-4 h-4 rounded-md flex items-center justify-center border text-white text-[10px] ${
                    p.is_active
                      ? 'bg-[var(--accent)] border-[var(--accent)]'
                      : 'border-[var(--text-secondary)]'
                  }`}
                >
                  {p.is_active && <Check className="w-3 h-3" />}
                </div>
                <span className="text-xs font-medium">{p.text}</span>
              </div>
              <button
                onClick={() => handleDeletePrinciple(p.id)}
                className="p-1 text-[var(--text-secondary)] hover:text-red-500 rounded-lg transition-colors ml-2"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Notification Schedules */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-[var(--accent)]">
          <Bell className="w-4 h-4" />
          <h3 className="text-xs font-bold uppercase tracking-wider">
            Расписание уведомлений бота
          </h3>
        </div>

        <div className="space-y-2 text-xs divide-y divide-[var(--border)]">
          {[
            { key: 'morning_greeting', label: 'Утреннее приветствие и привычки' },
            { key: 'daily_knowledge', label: 'Тема дня (Daily Knowledge)' },
            { key: 'spiritual_name', label: 'Имя Аллаха и рефлексия' },
            { key: 'evening_reflection', label: 'Вечерняя рефлексия (Журнал)' },
            { key: 'sleep_reminder', label: 'Напоминание о подготовке ко сну' },
          ].map((item) => {
            const notifKey = item.key as keyof NotificationSettings
            const notif = notifications[notifKey] as { enabled: boolean; time: string }
            if (!notif) return null

            return (
              <div key={item.key} className="flex items-center justify-between pt-2 first:pt-0">
                <span className="text-[var(--text-primary)] font-medium pr-2">{item.label}</span>
                <div className="flex items-center space-x-2 shrink-0">
                  <input
                    type="time"
                    value={notif.time || '08:00'}
                    onChange={(e) =>
                      handleToggleNotification(notifKey, 'time', e.target.value)
                    }
                    disabled={!notif.enabled}
                    className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs font-mono text-[var(--text-primary)] focus:outline-none disabled:opacity-40"
                  />
                  <input
                    type="checkbox"
                    checked={notif.enabled}
                    onChange={(e) =>
                      handleToggleNotification(notifKey, 'enabled', e.target.checked)
                    }
                    className="rounded text-[var(--accent)] focus:ring-[var(--accent)] w-4 h-4 cursor-pointer"
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 5. Data Management, Export & Privacy */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-emerald-500">
          <Shield className="w-4 h-4" />
          <h3 className="text-xs font-bold uppercase tracking-wider">
            Данные, Экспорт и Безопасность
          </h3>
        </div>

        <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">
          Все твои данные принадлежат только тебе. Ты можешь скачать полный архив в формате JSON в любой момент.
        </p>

        <div className="pt-2 flex flex-col sm:flex-row items-center gap-2">
          <button
            onClick={handleExport}
            className="w-full sm:w-auto flex-1 py-2.5 px-4 bg-[var(--bg-secondary)] border border-[var(--border)] hover:bg-[var(--border)] text-xs font-semibold text-[var(--text-primary)] rounded-xl flex items-center justify-center space-x-2 transition-colors shadow-sm"
          >
            <Download className="w-4 h-4 text-[var(--accent)]" />
            <span>Скачать архив данных (JSON)</span>
          </button>

          <button
            onClick={() => setShowResetConfirm(true)}
            className="w-full sm:w-auto py-2.5 px-4 bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-xs font-semibold text-red-500 rounded-xl flex items-center justify-center space-x-1.5 transition-colors"
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Сбросить прогресс</span>
          </button>
        </div>
      </div>

      {/* MODAL: Reset Progress Confirmation */}
      {showResetConfirm && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl w-full max-w-sm p-5 shadow-xl space-y-4 animate-scale-in text-center">
            <div className="w-12 h-12 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <h3 className="text-sm font-bold text-[var(--text-primary)]">
                Сбросить отметки привычек?
              </h3>
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                Это действие очистит историю отметок и записей журнала, но сохранит твои привычки, принципы и настройки.
              </p>
            </div>

            <div className="flex items-center space-x-2 pt-2">
              <button
                onClick={() => setShowResetConfirm(false)}
                className="flex-1 py-2.5 rounded-xl bg-[var(--bg-secondary)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] font-semibold transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleReset}
                className="flex-1 py-2.5 rounded-xl bg-red-500 text-white text-xs font-semibold hover:bg-red-600 transition-colors shadow-sm"
              >
                Да, сбросить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
