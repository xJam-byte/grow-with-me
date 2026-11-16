import React, { useState } from 'react'
import { Sparkles, Send } from 'lucide-react'
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
  const [activeTab, setActiveTab] = useState<'structured' | 'free'>('structured')
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [freeText, setFreeText] = useState('')
  const [saved, setSaved] = useState(false)
  const { impactOccurred } = useTelegram()

  const handleSave = () => {
    impactOccurred('medium')
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Вечерний журнал</h2>
          <p className="text-xs text-[var(--text-secondary)]">
            Осознанность и честный разговор с собой
          </p>
        </div>
        <div className="flex bg-[var(--bg-secondary)] p-1 rounded-xl text-xs">
          <button
            onClick={() => setActiveTab('structured')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
              activeTab === 'structured'
                ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                : 'text-[var(--text-secondary)]'
            }`}
          >
            Вопросы
          </button>
          <button
            onClick={() => setActiveTab('free')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
              activeTab === 'free'
                ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                : 'text-[var(--text-secondary)]'
            }`}
          >
            Свободно
          </button>
        </div>
      </div>

      {activeTab === 'structured' ? (
        <div className="space-y-3">
          {reflectionQuestions.map((q, idx) => (
            <div
              key={idx}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3.5 shadow-sm space-y-2"
            >
              <label className="text-xs font-semibold text-[var(--text-primary)] block">
                {idx + 1}. {q}
              </label>
              <textarea
                rows={2}
                value={answers[idx] || ''}
                onChange={(e) => setAnswers({ ...answers, [idx]: e.target.value })}
                placeholder="Твои мысли..."
                className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
          <textarea
            rows={10}
            value={freeText}
            onChange={(e) => setFreeText(e.target.value)}
            placeholder="Пиши всё, что на душе сегодня: победы, сомнения, мысли, выводы..."
            className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-3 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-none"
          />
        </div>
      )}

      {/* Save Button */}
      <button
        onClick={handleSave}
        className="w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-xs font-semibold shadow-md active:scale-[0.99] transition-all"
      >
        {saved ? (
          <>
            <Sparkles className="w-4 h-4" />
            <span>Запись сохранена! ✨</span>
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            <span>Сохранить рефлексию</span>
          </>
        )}
      </button>
    </div>
  )
}
