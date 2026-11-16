import React, { useEffect, useState } from 'react'
import { Sparkles, Send, Flame, Clock } from 'lucide-react'
import { useJournalStore } from '../stores/useJournalStore'
import { useTelegram } from '../hooks/useTelegram'

const reflectionQuestions = [
  'Что у меня получилось хорошо сегодня?',
  'Что я мог бы сделать лучше?',
  'Чему новому я сегодня научился?',
  'Как я относился к людям вокруг?',
  'За что я сегодня искренне благодарен?',
  'Что главное мне стоит улучшить завтра?',
]

export const JournalPage: React.FC = () => {
  const { todayEntry, stats, saving, loadToday, saveEntry } = useJournalStore()
  const { impactOccurred } = useTelegram()

  const [activeTab, setActiveTab] = useState<'structured' | 'free'>('structured')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [freeText, setFreeText] = useState('')
  const [tomorrowIntentions, setTomorrowIntentions] = useState('')
  const [savedSuccess, setSavedSuccess] = useState(false)

  useEffect(() => {
    loadToday()
  }, [])

  useEffect(() => {
    if (todayEntry) {
      if (todayEntry.structured_answers) {
        setAnswers(todayEntry.structured_answers)
      }
      if (todayEntry.free_text) {
        setFreeText(todayEntry.free_text)
      }
      if (todayEntry.tomorrow_intentions) {
        setTomorrowIntentions(todayEntry.tomorrow_intentions)
      }
    }
  }, [todayEntry])

  const handleSave = async () => {
    impactOccurred('medium')
    const res = await saveEntry({
      structured_answers: answers,
      free_text: freeText,
      tomorrow_intentions: tomorrowIntentions,
    })
    if (res) {
      setSavedSuccess(true)
      setTimeout(() => setSavedSuccess(false), 2500)
    }
  }

  return (
    <div className="space-y-4 animate-fade-in pb-10">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Вечерний журнал</h2>
          <p className="text-xs text-[var(--text-secondary)]">
            Осознанность и честный разговор с собой
          </p>
        </div>
        {stats && (
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-500 text-xs font-semibold">
            <Flame className="w-3.5 h-3.5" />
            <span>{stats.streak_days} дн.</span>
          </div>
        )}
      </div>

      {/* Mode Switcher */}
      <div className="flex bg-[var(--bg-secondary)] p-1 rounded-xl text-xs">
        <button
          onClick={() => {
            impactOccurred('light')
            setActiveTab('structured')
          }}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-colors ${
            activeTab === 'structured'
              ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
              : 'text-[var(--text-secondary)]'
          }`}
        >
          6 вопросов дня
        </button>
        <button
          onClick={() => {
            impactOccurred('light')
            setActiveTab('free')
          }}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-colors ${
            activeTab === 'free'
              ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
              : 'text-[var(--text-secondary)]'
          }`}
        >
          Свободное письмо
        </button>
      </div>

      {/* Main Journal Input Area */}
      {activeTab === 'structured' ? (
        <div className="space-y-3">
          {reflectionQuestions.map((q, idx) => (
            <div
              key={idx}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3.5 shadow-sm space-y-1.5"
            >
              <label className="text-xs font-semibold text-[var(--text-primary)] block">
                {idx + 1}. {q}
              </label>
              <textarea
                rows={2}
                value={answers[String(idx)] || ''}
                onChange={(e) =>
                  setAnswers({ ...answers, [String(idx)]: e.target.value })
                }
                placeholder="Твои мысли и выводы..."
                className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
          <span className="text-xs font-semibold text-[var(--text-primary)] block">
            Свободный поток мыслей
          </span>
          <textarea
            rows={10}
            value={freeText}
            onChange={(e) => setFreeText(e.target.value)}
            placeholder="Пиши всё, что на душе сегодня: победы, сомнения, мысли, выводы..."
            className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-3 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
          />
        </div>
      )}

      {/* Tomorrow Intentions Card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-[var(--accent)] text-xs font-semibold">
          <Clock className="w-4 h-4" />
          <span>Планы и намерения на завтра</span>
        </div>
        <textarea
          rows={3}
          value={tomorrowIntentions}
          onChange={(e) => setTomorrowIntentions(e.target.value)}
          placeholder="Главный фокус на завтра, важные дела и настрой..."
          className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
        />
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-xs font-semibold shadow-md active:scale-[0.99] transition-all disabled:opacity-50"
      >
        {savedSuccess ? (
          <>
            <Sparkles className="w-4 h-4" />
            <span>Рефлексия сохранена! ✓</span>
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            <span>{saving ? 'Сохранение...' : 'Сохранить рефлексию дня'}</span>
          </>
        )}
      </button>
    </div>
  )
}
