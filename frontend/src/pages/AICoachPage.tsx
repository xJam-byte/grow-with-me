import React, { useState } from 'react'
import { Bot, Send, Sparkles, User as UserIcon } from 'lucide-react'
import { useTelegram } from '../hooks/useTelegram'

interface ChatMsg {
  sender: 'ai' | 'user'
  text: string
}

export const AICoachPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      sender: 'ai',
      text: 'Ассаляму алейкум! Я твой личный коуч в Grow With Me. Я опираюсь на твои привычки, цели и рефлексию. Буду честным и помогу держать фокус. О чём хочешь поговорить?',
    },
  ])
  const [input, setInput] = useState('')
  const { impactOccurred } = useTelegram()

  const quickPrompts = [
    'Как у меня дела на этой неделе?',
    'В чём моя слабая сторона сейчас?',
    'Помоги настроиться на завтра',
  ]

  const handleSend = (textToSend?: string) => {
    const text = textToSend || input
    if (!text.trim()) return

    impactOccurred('light')
    const nextMsgs: ChatMsg[] = [...messages, { sender: 'user', text }]
    setMessages(nextMsgs)
    setInput('')

    // Simulated thoughtful coach response
    setTimeout(() => {
      setMessages([
        ...nextMsgs,
        {
          sender: 'ai',
          text: `Отличный вопрос. Глядя на твои привычки за последние дни: ты отлично держишь подъём и чтение (серия 12 дней!), но физическая активность проседает. Помни правило: «Никогда не пропускай дважды». Давай запланируем короткую 20-минутную активность на завтра?`,
        },
      ])
    }, 600)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] animate-fade-in">
      <div className="flex items-center space-x-2 pb-3 border-b border-[var(--border)] mb-3">
        <div className="p-1.5 rounded-lg bg-[var(--accent)] text-white">
          <Bot className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-xs font-bold text-[var(--text-primary)]">AI Персональный Коуч</h2>
          <p className="text-[10px] text-[var(--text-secondary)]">Честный, конструктивный, без пустой мотивации</p>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex items-start space-x-2 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'ai' && (
              <div className="w-6 h-6 rounded-full bg-[var(--accent)] text-white flex items-center justify-center shrink-0 text-xs mt-0.5">
                <Sparkles className="w-3 h-3" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl p-3 text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-[var(--accent)] text-white rounded-tr-none'
                  : 'bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-primary)] rounded-tl-none shadow-sm'
              }`}
            >
              {m.text}
            </div>
            {m.sender === 'user' && (
              <div className="w-6 h-6 rounded-full bg-[var(--bg-secondary)] text-[var(--text-secondary)] flex items-center justify-center shrink-0 text-xs mt-0.5">
                <UserIcon className="w-3 h-3" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Prompts */}
      <div className="flex items-center space-x-1.5 overflow-x-auto py-2 no-scrollbar">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="text-[11px] whitespace-nowrap bg-[var(--bg-secondary)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] px-2.5 py-1 rounded-full transition-colors"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="pt-2 flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Спроси коуча..."
          className="flex-1 text-xs bg-[var(--bg-card)] border border-[var(--border)] rounded-xl px-3 py-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
        />
        <button
          onClick={() => handleSend()}
          aria-label="Send"
          className="p-2.5 rounded-xl bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
