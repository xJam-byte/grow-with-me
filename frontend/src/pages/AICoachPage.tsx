import React, { useEffect, useRef, useState } from 'react'
import {
  Bot,
  Send,
  Sparkles,
  User as UserIcon,
  Trash2,
  BarChart3,
  Settings2,
  X,
  CheckCircle2,
  AlertCircle,
  Shield,
  Zap,
} from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'
import { useAIStore } from '../stores/useAIStore'
import { useUserStore } from '../stores/useUserStore'

export const AICoachPage: React.FC = () => {
  const {
    messages,
    usage,
    analysis,
    loading,
    analyzing,
    loadHistory,
    sendMessage,
    clearHistory,
    loadUsage,
    runWeeklyAnalysis,
    updatePreferences,
  } = useAIStore()

  const { profile, loadProfile } = useUserStore()
  const { impactOccurred } = useTelegram()

  const [input, setInput] = useState('')
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)

  // Local settings state
  const [tone, setTone] = useState<'strict' | 'balanced' | 'gentle'>('balanced')
  const [allowJournal, setAllowJournal] = useState(true)
  const [allowNotes, setAllowNotes] = useState(true)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadHistory()
    loadUsage()
    loadProfile()
  }, [])

  useEffect(() => {
    if (profile?.ai_preferences) {
      if (profile.ai_preferences.tone) setTone(profile.ai_preferences.tone)
      if (typeof profile.ai_preferences.allow_journal_access === 'boolean') {
        setAllowJournal(profile.ai_preferences.allow_journal_access)
      }
      if (typeof profile.ai_preferences.allow_notes_access === 'boolean') {
        setAllowNotes(profile.ai_preferences.allow_notes_access)
      }
    }
  }, [profile?.ai_preferences])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const quickPrompts = [
    'Как у меня дела на этой неделе?',
    'В чём моя слабая сторона?',
    'Помоги настроиться на завтра',
    'Что мне улучшить в привычках?',
  ]

  const handleSend = (textToSend?: string) => {
    const text = textToSend || input
    if (!text.trim() || loading) return

    impactOccurred('light')
    setInput('')
    sendMessage(text.trim())
  }

  const handleClear = () => {
    if (confirm('Очистить историю диалога с коучем?')) {
      impactOccurred('medium')
      clearHistory()
    }
  }

  const handleOpenAnalysis = () => {
    impactOccurred('light')
    setShowAnalysisModal(true)
    if (!analysis) {
      runWeeklyAnalysis()
    }
  }

  const handleSavePreferences = () => {
    impactOccurred('medium')
    updatePreferences({
      tone,
      allow_journal_access: allowJournal,
      allow_notes_access: allowNotes,
    })
    setShowSettingsModal(false)
  }

  const formatToolBadge = (toolName: string) => {
    switch (toolName) {
      case 'get_habits_today':
        return '🎯 Привычки сегодня'
      case 'get_habits_stats':
        return '📊 Статистика'
      case 'get_recent_journal':
        return '📝 Журнал'
      case 'search_notes':
        return '🔍 Заметки'
      case 'mark_habit_completed':
        return '✅ Отметил привычку'
      case 'add_quick_note':
        return '📌 Сохранил заметку'
      default:
        return '⚙️ ' + toolName
    }
  }

  // Simple Markdown renderer for chat messages
  const renderFormattedText = (content: string) => {
    const lines = content.split('\n')
    return (
      <div className="space-y-1.5">
        {lines.map((line, idx) => {
          if (!line.trim()) return <div key={idx} className="h-1" />

          // Bold parsing
          const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g)
          return (
            <p key={idx} className="leading-relaxed">
              {parts.map((part, pIdx) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return (
                    <strong key={pIdx} className="font-semibold text-[var(--text-primary)]">
                      {part.slice(2, -2)}
                    </strong>
                  )
                }
                if (part.startsWith('*') && part.endsWith('*')) {
                  return (
                    <em key={pIdx} className="italic text-[var(--text-secondary)]">
                      {part.slice(1, -1)}
                    </em>
                  )
                }
                return part
              })}
            </p>
          )
        })}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] animate-fade-in relative">
      {/* Top Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-[var(--border)] mb-2">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500 to-amber-400 flex items-center justify-center text-white shadow-sm">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
              <span>AI Коуч</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse" />
            </h2>
            <p className="text-[10px] text-[var(--text-secondary)]">
              {tone === 'strict'
                ? 'Строгий режим • Дисциплина'
                : tone === 'gentle'
                ? 'Мягкий режим • Поддержка'
                : 'Сбалансированный • Факты'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={handleOpenAnalysis}
            title="Анализ недели"
            className="p-1.5 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-secondary)] rounded-lg transition-colors flex items-center space-x-1"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[10px]">Анализ</span>
          </button>
          <button
            onClick={() => setShowSettingsModal(true)}
            title="Настройки AI"
            className="p-1.5 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-secondary)] rounded-lg transition-colors"
          >
            <Settings2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleClear}
            title="Очистить историю"
            className="p-1.5 text-xs text-[var(--text-secondary)] hover:text-red-500 bg-[var(--bg-secondary)] rounded-lg transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 py-1">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex items-start space-x-2 ${
              m.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {m.role === 'assistant' && (
              <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-orange-500 to-amber-400 text-white flex items-center justify-center shrink-0 text-xs mt-0.5 shadow-sm">
                <Sparkles className="w-3 h-3" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-3 text-xs shadow-sm ${
                m.role === 'user'
                  ? 'bg-[var(--accent)] text-white rounded-tr-none'
                  : 'bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-primary)] rounded-tl-none'
              }`}
            >
              {/* Tool calling indicators */}
              {m.tools_used && m.tools_used.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2 pb-2 border-b border-[var(--border)]">
                  {m.tools_used.map((tool, tIdx) => (
                    <span
                      key={tIdx}
                      className="text-[10px] px-1.5 py-0.5 rounded-md bg-[var(--bg-secondary)] text-[var(--accent)] font-medium"
                    >
                      {formatToolBadge(tool)}
                    </span>
                  ))}
                </div>
              )}

              {renderFormattedText(m.content)}
            </div>

            {m.role === 'user' && (
              <div className="w-6 h-6 rounded-full bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--border)] flex items-center justify-center shrink-0 text-xs mt-0.5">
                <UserIcon className="w-3 h-3" />
              </div>
            )}
          </div>
        ))}

        {/* Loading bubble */}
        {loading && (
          <div className="flex items-start space-x-2 justify-start">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-orange-500 to-amber-400 text-white flex items-center justify-center shrink-0 text-xs mt-0.5">
              <Sparkles className="w-3 h-3 animate-spin" />
            </div>
            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl rounded-tl-none p-3 shadow-sm flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full animate-bounce [animation-delay:-0.3s]" />
              <span className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full animate-bounce [animation-delay:-0.15s]" />
              <span className="w-1.5 h-1.5 bg-[var(--accent)] rounded-full animate-bounce" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="flex items-center space-x-1.5 overflow-x-auto py-2 no-scrollbar">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            disabled={loading}
            className="text-[11px] whitespace-nowrap bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent)] px-3 py-1.5 rounded-full transition-all shrink-0 shadow-sm disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input bar */}
      <div className="pt-2 flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Спроси коуча о прогрессе или дне..."
          disabled={loading}
          className="flex-1 text-xs bg-[var(--bg-card)] border border-[var(--border)] rounded-xl px-3 py-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] disabled:opacity-60"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          aria-label="Send"
          className="p-2.5 rounded-xl bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      {/* MODAL 1: Weekly Analysis */}
      {showAnalysisModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl w-full max-w-md max-h-[85vh] overflow-y-auto p-5 shadow-xl space-y-4 animate-scale-in">
            <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-[var(--accent)]" />
                <h3 className="text-sm font-bold text-[var(--text-primary)]">Анализ недели</h3>
              </div>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="p-1 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {analyzing ? (
              <div className="py-12 flex flex-col items-center justify-center space-y-3">
                <Sparkles className="w-6 h-6 text-[var(--accent)] animate-spin" />
                <p className="text-xs text-[var(--text-secondary)]">Анализируем прогресс недели...</p>
              </div>
            ) : analysis ? (
              <div className="space-y-4">
                {/* Score Banner */}
                <div className="bg-gradient-to-r from-orange-500/10 to-amber-500/10 border border-orange-500/20 rounded-xl p-3 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-[var(--accent)] tracking-wider">
                      {analysis.period}
                    </span>
                    <h4 className="text-xs font-semibold text-[var(--text-primary)] mt-0.5">
                      Оценка стабильности
                    </h4>
                  </div>
                  <div className="text-xl font-black text-[var(--accent)]">
                    {analysis.overall_score} <span className="text-xs text-[var(--text-secondary)]">/ 10</span>
                  </div>
                </div>

                {/* Key Insight */}
                <div className="bg-[var(--bg-secondary)] rounded-xl p-3 border-l-2 border-[var(--accent)]">
                  <span className="text-[10px] text-[var(--text-secondary)] uppercase font-semibold">
                    Главный инсайт
                  </span>
                  <p className="text-xs text-[var(--text-primary)] italic mt-1 leading-relaxed">
                    «{analysis.key_insight}»
                  </p>
                </div>

                {/* Strengths */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-emerald-500 flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Сильные стороны:</span>
                  </span>
                  <ul className="space-y-1">
                    {analysis.strengths.map((s, idx) => (
                      <li key={idx} className="text-xs text-[var(--text-secondary)] pl-2 border-l border-emerald-500/30">
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-amber-500 flex items-center space-x-1">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>Узкие места:</span>
                  </span>
                  <ul className="space-y-1">
                    {analysis.weaknesses.map((w, idx) => (
                      <li key={idx} className="text-xs text-[var(--text-secondary)] pl-2 border-l border-amber-500/30">
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action plan */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-[var(--accent)] flex items-center space-x-1">
                    <Zap className="w-3.5 h-3.5" />
                    <span>План действий на следующую неделю:</span>
                  </span>
                  <ul className="space-y-1.5">
                    {analysis.action_plan.map((a, idx) => (
                      <li
                        key={idx}
                        className="text-xs text-[var(--text-primary)] bg-[var(--bg-secondary)] p-2 rounded-lg flex items-start space-x-2"
                      >
                        <span className="font-bold text-[var(--accent)] text-[10px] mt-0.5">{idx + 1}.</span>
                        <span>{a}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <button
                  onClick={() => runWeeklyAnalysis()}
                  className="px-4 py-2 bg-[var(--accent)] text-white text-xs rounded-xl"
                >
                  Сформировать анализ
                </button>
              </div>
            )}

            <button
              onClick={() => setShowAnalysisModal(false)}
              className="w-full py-2.5 rounded-xl bg-[var(--bg-secondary)] hover:bg-[var(--border)] text-xs font-semibold text-[var(--text-primary)] transition-colors"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}

      {/* MODAL 2: Settings & Preferences */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl w-full max-w-md p-5 shadow-xl space-y-4 animate-scale-in">
            <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
              <div className="flex items-center space-x-2">
                <Settings2 className="w-5 h-5 text-[var(--accent)]" />
                <h3 className="text-sm font-bold text-[var(--text-primary)]">Настройки AI Коуча</h3>
              </div>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="p-1 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Tone Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-[var(--text-primary)]">
                Тон общения коуча:
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(
                  [
                    { key: 'strict', label: 'Строгий', desc: 'Дисциплина' },
                    { key: 'balanced', label: 'Баланс', desc: 'Факты' },
                    { key: 'gentle', label: 'Мягкий', desc: 'Поддержка' },
                  ] as const
                ).map((t) => (
                  <button
                    key={t.key}
                    onClick={() => setTone(t.key)}
                    className={`p-2 rounded-xl border text-center transition-all ${
                      tone === t.key
                        ? 'border-[var(--accent)] bg-[var(--accent)]/10 text-[var(--accent)] font-semibold'
                        : 'border-[var(--border)] bg-[var(--bg-secondary)] text-[var(--text-secondary)]'
                    }`}
                  >
                    <div className="text-xs">{t.label}</div>
                    <div className="text-[9px] opacity-80">{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Privacy switches */}
            <div className="space-y-2.5 pt-2 border-t border-[var(--border)]">
              <label className="text-xs font-semibold text-[var(--text-primary)] flex items-center space-x-1.5">
                <Shield className="w-3.5 h-3.5 text-[var(--accent)]" />
                <span>Приватность данных:</span>
              </label>

              <label className="flex items-center justify-between text-xs p-2.5 rounded-xl bg-[var(--bg-secondary)] cursor-pointer">
                <span>Разрешить доступ к Журналу рефлексии</span>
                <input
                  type="checkbox"
                  checked={allowJournal}
                  onChange={(e) => setAllowJournal(e.target.checked)}
                  className="rounded text-[var(--accent)] focus:ring-[var(--accent)]"
                />
              </label>

              <label className="flex items-center justify-between text-xs p-2.5 rounded-xl bg-[var(--bg-secondary)] cursor-pointer">
                <span>Разрешить доступ к Заметкам</span>
                <input
                  type="checkbox"
                  checked={allowNotes}
                  onChange={(e) => setAllowNotes(e.target.checked)}
                  className="rounded text-[var(--accent)] focus:ring-[var(--accent)]"
                />
              </label>
            </div>

            {/* Token usage info */}
            {usage && (
              <div className="p-3 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border)] space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-[var(--text-secondary)]">Лимит токенов сегодня:</span>
                  <span className="font-mono text-[var(--text-primary)] font-semibold">
                    {usage.today_tokens.toLocaleString()} / {usage.daily_limit.toLocaleString()}
                  </span>
                </div>
                <div className="w-full bg-[var(--border)] h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[var(--accent)] h-full transition-all"
                    style={{
                      width: `${Math.min(100, Math.round((usage.today_tokens / usage.daily_limit) * 100))}%`,
                    }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-[var(--text-secondary)] pt-1">
                  <span>Модель: {usage.model}</span>
                  <span>Расход: ~${usage.estimated_cost_usd}</span>
                </div>
              </div>
            )}

            <div className="flex items-center space-x-2 pt-2">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-[var(--bg-secondary)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSavePreferences}
                className="flex-1 py-2.5 rounded-xl bg-[var(--accent)] text-white text-xs font-semibold hover:bg-[var(--accent-hover)] transition-colors"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
