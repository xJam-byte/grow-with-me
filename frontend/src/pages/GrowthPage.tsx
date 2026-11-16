import React from 'react'
import { HeartHandshake, Brain, Activity, ShieldCheck, GraduationCap } from 'lucide-react'

interface AreaItem {
  name: string
  subtitle: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  objectiveStats: string
  subjectiveScore: number // 1-5
}

const areas: AreaItem[] = [
  {
    name: 'Духовность и характер',
    subtitle: 'Практики, имена Аллаха, благодарность, добрые дела',
    icon: HeartHandshake,
    color: 'from-emerald-500/20 to-emerald-500/5 text-emerald-500 border-emerald-500/30',
    objectiveStats: '14/14 практик выполнено на этой неделе',
    subjectiveScore: 4,
  },
  {
    name: 'Интеллектуальное развитие',
    subtitle: 'Психология, философия, наука, технологии, чтение',
    icon: Brain,
    color: 'from-blue-500/20 to-blue-500/5 text-blue-500 border-blue-500/30',
    objectiveStats: '110 прочитанных страниц, 6 тем изучено',
    subjectiveScore: 5,
  },
  {
    name: 'Физическое развитие',
    subtitle: 'Тренировки, ходьба, режим сна, восстановление',
    icon: Activity,
    color: 'from-orange-500/20 to-orange-500/5 text-orange-500 border-orange-500/30',
    objectiveStats: '4 тренировки, среднее время сна: 7.5ч',
    subjectiveScore: 3,
  },
  {
    name: 'Ментальное развитие',
    subtitle: 'Эмоциональный баланс, рефлексия, стрессоустойчивость',
    icon: ShieldCheck,
    color: 'from-purple-500/20 to-purple-500/5 text-purple-500 border-purple-500/30',
    objectiveStats: '6 вечерних рефлексий за неделю',
    subjectiveScore: 4,
  },
  {
    name: 'Академическое и карьера',
    subtitle: 'Университет, диплом, IELTS, программирование',
    icon: GraduationCap,
    color: 'from-amber-500/20 to-amber-500/5 text-amber-500 border-amber-500/30',
    objectiveStats: '18 часов Deep Work, 5 практик английского',
    subjectiveScore: 4,
  },
]

export const GrowthPage: React.FC = () => {
  return (
    <div className="space-y-4 animate-fade-in">
      <div>
        <h2 className="text-lg font-bold text-[var(--text-primary)]">Области развития</h2>
        <p className="text-xs text-[var(--text-secondary)]">
          5 ключевых сфер твоего жизненного баланса
        </p>
      </div>

      <div className="space-y-3">
        {areas.map((area, idx) => {
          const Icon = area.icon
          return (
            <div
              key={idx}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2.5 rounded-xl border ${area.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-[var(--text-primary)]">
                      {area.name}
                    </h3>
                    <p className="text-[11px] text-[var(--text-secondary)] line-clamp-1 mt-0.5">
                      {area.subtitle}
                    </p>
                  </div>
                </div>

                {/* Score */}
                <div className="text-right">
                  <span className="text-xs font-bold text-[var(--text-primary)]">
                    {area.subjectiveScore} / 5
                  </span>
                  <div className="text-[10px] text-[var(--text-secondary)]">оценка</div>
                </div>
              </div>

              {/* Stats */}
              <div className="pt-2 border-t border-[var(--border)] flex items-center justify-between text-[11px]">
                <span className="text-[var(--text-secondary)]">Объективные данные:</span>
                <span className="font-medium text-[var(--text-primary)]">
                  {area.objectiveStats}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

