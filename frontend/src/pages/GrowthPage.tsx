import React, { useEffect, useState } from 'react'
import {
  HeartHandshake,
  Brain,
  Activity,
  ShieldCheck,
  GraduationCap,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  Flame,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Zap,
  BarChart2,
  FileText,
  X,
  Star,
  RefreshCw,
} from 'lucide-react'
import { useProgressStore } from '../stores/useProgressStore'
import { useTelegram } from '../hooks/useTelegram'
import type { WeeklyAssessmentCreate } from '../types/progress'

export const GrowthPage: React.FC = () => {
  const {
    dashboard,
    areas,
    latestAssessment,
    loading,
    savingAssessment,
    generatingReport,
    loadProgressData,
    saveAssessment,
    generateReport,
  } = useProgressStore()

  const { impactOccurred } = useTelegram()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'areas' | 'assessment'>('dashboard')
  const [showAssessmentModal, setShowAssessmentModal] = useState(false)

  // Assessment form state
  const [scores, setScores] = useState({
    spirituality: 4,
    intellectual: 4,
    physical: 3,
    mental: 4,
    academic: 3,
  })
  const [wentWell, setWentWell] = useState('')
  const [wentWrong, setWentWrong] = useState('')
  const [difficulties, setDifficulties] = useState('')
  const [achievements, setAchievements] = useState('')
  const [learned, setLearned] = useState('')
  const [priorities, setPriorities] = useState('')

  useEffect(() => {
    loadProgressData()
  }, [])

  useEffect(() => {
    if (latestAssessment) {
      setScores({
        spirituality: latestAssessment.score_spirituality,
        intellectual: latestAssessment.score_intellectual,
        physical: latestAssessment.score_physical,
        mental: latestAssessment.score_mental,
        academic: latestAssessment.score_academic,
      })
      if (latestAssessment.went_well) setWentWell(latestAssessment.went_well)
      if (latestAssessment.went_wrong) setWentWrong(latestAssessment.went_wrong)
      if (latestAssessment.difficulties) setDifficulties(latestAssessment.difficulties)
      if (latestAssessment.achievements) setAchievements(latestAssessment.achievements)
      if (latestAssessment.learned) setLearned(latestAssessment.learned)
      if (latestAssessment.next_week_priorities) setPriorities(latestAssessment.next_week_priorities)
    }
  }, [latestAssessment])

  const getAreaIcon = (iconName: string) => {
    switch (iconName) {
      case 'HeartHandshake':
        return HeartHandshake
      case 'Brain':
        return Brain
      case 'Activity':
        return Activity
      case 'ShieldCheck':
        return ShieldCheck
      case 'GraduationCap':
        return GraduationCap
      default:
        return Sparkles
    }
  }

  const handleSaveAssessment = async () => {
    impactOccurred('medium')
    const payload: WeeklyAssessmentCreate = {
      score_spirituality: scores.spirituality,
      score_intellectual: scores.intellectual,
      score_physical: scores.physical,
      score_mental: scores.mental,
      score_academic: scores.academic,
      went_well: wentWell,
      went_wrong: wentWrong,
      difficulties: difficulties,
      achievements: achievements,
      learned: learned,
      next_week_priorities: priorities,
    }

    const saved = await saveAssessment(payload)
    if (saved) {
      setShowAssessmentModal(false)
      // Auto-trigger AI report generation
      await generateReport(saved.id)
      setActiveTab('assessment')
    }
  }

  const handleGenerateReport = async () => {
    if (!latestAssessment) return
    impactOccurred('light')
    await generateReport(latestAssessment.id)
  }

  return (
    <div className="space-y-4 animate-fade-in pb-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Аналитика и Рост</h2>
          <p className="text-xs text-[var(--text-secondary)]">
            Объективные факты, 5 сфер развития и недельная самооценка
          </p>
        </div>
        <button
          onClick={() => {
            impactOccurred('light')
            loadProgressData()
          }}
          disabled={loading}
          aria-label="Обновить аналитику"
          className="p-2 rounded-xl bg-[var(--bg-secondary)] hover:bg-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex p-1 bg-[var(--bg-secondary)] rounded-2xl border border-[var(--border)]">
        <button
          onClick={() => {
            impactOccurred('light')
            setActiveTab('dashboard')
          }}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-xl transition-all ${
            activeTab === 'dashboard'
              ? 'bg-[var(--bg-card)] text-[var(--accent)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          Дашборд
        </button>
        <button
          onClick={() => {
            impactOccurred('light')
            setActiveTab('areas')
          }}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-xl transition-all ${
            activeTab === 'areas'
              ? 'bg-[var(--bg-card)] text-[var(--accent)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          5 Областей
        </button>
        <button
          onClick={() => {
            impactOccurred('light')
            setActiveTab('assessment')
          }}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-xl transition-all ${
            activeTab === 'assessment'
              ? 'bg-[var(--bg-card)] text-[var(--accent)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          AI-Отчёт
        </button>
      </div>

      {/* TAB 1: DASHBOARD */}
      {activeTab === 'dashboard' && dashboard && (
        <div className="space-y-4">
          {/* Top 3 KPI metrics */}
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3 shadow-sm text-center">
              <span className="text-[10px] text-[var(--text-secondary)] uppercase font-semibold">
                Сегодня
              </span>
              <div className="text-lg font-black text-[var(--text-primary)] mt-1">
                {dashboard.today_completion_rate}%
              </div>
              <p className="text-[10px] text-[var(--text-secondary)]">
                {dashboard.today_completed}/{dashboard.today_total} выполнено
              </p>
            </div>

            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3 shadow-sm text-center">
              <span className="text-[10px] text-[var(--text-secondary)] uppercase font-semibold">
                За 7 дней
              </span>
              <div className="text-lg font-black text-emerald-500 mt-1">
                {dashboard.weekly_completion_rate}%
              </div>
              <p className="text-[10px] text-[var(--text-secondary)]">недельная норма</p>
            </div>

            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-3 shadow-sm text-center">
              <span className="text-[10px] text-[var(--text-secondary)] uppercase font-semibold">
                Макс. серия
              </span>
              <div className="text-lg font-black text-orange-500 mt-1 flex items-center justify-center space-x-1">
                <Flame className="w-4 h-4 fill-orange-500" />
                <span>{dashboard.best_active_streak}д</span>
              </div>
              <p className="text-[10px] text-[var(--text-secondary)]">непрерывно</p>
            </div>
          </div>

          {/* Weekly Progress Bar Chart */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
                <BarChart2 className="w-4 h-4 text-[var(--accent)]" />
                <span>График за последние 7 дней</span>
              </h3>
              <span className="text-[11px] font-semibold text-[var(--text-secondary)]">
                {dashboard.weekly_completion_rate}% среднее
              </span>
            </div>

            <div className="flex items-end justify-between h-28 pt-4 pb-1 px-1">
              {dashboard.weekly_chart.map((day, idx) => {
                const dateObj = new Date(day.date)
                const dayName = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][dateObj.getDay()]
                const heightPct = Math.max(8, day.completion_rate)
                const isToday = idx === dashboard.weekly_chart.length - 1

                return (
                  <div key={idx} className="flex flex-col items-center flex-1 space-y-1.5 group">
                    <span className="text-[9px] font-mono text-[var(--text-secondary)] opacity-0 group-hover:opacity-100 transition-opacity">
                      {day.completed_count}
                    </span>
                    <div className="w-6 sm:w-8 bg-[var(--bg-secondary)] rounded-t-lg h-20 flex items-end overflow-hidden p-0.5">
                      <div
                        className={`w-full rounded-t-md transition-all duration-500 ${
                          isToday
                            ? 'bg-gradient-to-t from-orange-500 to-amber-400'
                            : day.completion_rate >= 70
                            ? 'bg-emerald-500'
                            : day.completion_rate > 0
                            ? 'bg-[var(--accent)]'
                            : 'bg-transparent'
                        }`}
                        style={{ height: `${heightPct}%` }}
                      />
                    </div>
                    <span
                      className={`text-[10px] font-semibold ${
                        isToday ? 'text-[var(--accent)] font-bold' : 'text-[var(--text-secondary)]'
                      }`}
                    >
                      {dayName}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 30-Day Activity Heatmap */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
                <Calendar className="w-4 h-4 text-[var(--accent)]" />
                <span>Тепловая карта дисциплины (30 дней)</span>
              </h3>
              <span className="text-[10px] text-[var(--text-secondary)]">
                {dashboard.total_completions_month} отметок
              </span>
            </div>

            <div className="grid grid-cols-10 gap-1.5 pt-1">
              {dashboard.monthly_heatmap.map((item, idx) => {
                let bgClass = 'bg-[var(--bg-secondary)] border-[var(--border)]'
                if (item.completion_rate >= 80) {
                  bgClass = 'bg-emerald-500 border-emerald-600'
                } else if (item.completion_rate >= 50) {
                  bgClass = 'bg-emerald-500/60 border-emerald-500/80'
                } else if (item.completion_rate > 0) {
                  bgClass = 'bg-emerald-500/25 border-emerald-500/40'
                }

                return (
                  <div
                    key={idx}
                    title={`${item.date}: ${item.completed_count}/${item.total_count} (${item.completion_rate}%)`}
                    className={`aspect-square rounded-md border transition-transform hover:scale-110 cursor-pointer ${bgClass}`}
                  />
                )
              })}
            </div>

            <div className="flex items-center justify-end space-x-2 text-[10px] text-[var(--text-secondary)] pt-1">
              <span>0%</span>
              <div className="w-2.5 h-2.5 rounded bg-[var(--bg-secondary)] border border-[var(--border)]" />
              <div className="w-2.5 h-2.5 rounded bg-emerald-500/25 border border-emerald-500/40" />
              <div className="w-2.5 h-2.5 rounded bg-emerald-500/60 border border-emerald-500/80" />
              <div className="w-2.5 h-2.5 rounded bg-emerald-500 border border-emerald-600" />
              <span>100%</span>
            </div>
          </div>

          {/* Active Streaks List */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
              <Flame className="w-4 h-4 text-orange-500" />
              <span>Серии непрерывности</span>
            </h3>

            <div className="grid grid-cols-2 gap-2">
              {dashboard.streaks.map((h) => (
                <div
                  key={h.id}
                  className="p-2.5 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border)] flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2 truncate">
                    <span className="text-sm">{h.icon}</span>
                    <span className="text-xs text-[var(--text-primary)] truncate font-medium">
                      {h.name}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-orange-500 shrink-0 font-mono font-bold text-xs pl-1">
                    <Flame className="w-3.5 h-3.5 fill-orange-500" />
                    <span>{h.streak}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: 5 DEVELOPMENT AREAS */}
      {activeTab === 'areas' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs text-[var(--text-secondary)]">
              Объективное выполнение vs Твоя самооценка
            </span>
            <button
              onClick={() => {
                impactOccurred('light')
                setShowAssessmentModal(true)
              }}
              className="text-xs text-[var(--accent)] font-semibold hover:underline"
            >
              Оценить неделю
            </button>
          </div>

          {areas.map((area) => {
            const Icon = getAreaIcon(area.icon)
            return (
              <div
                key={area.slug}
                className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3 transition-all hover:border-[var(--accent)]"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div
                      className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-sm"
                      style={{ backgroundColor: area.color }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-xs font-bold text-[var(--text-primary)]">{area.name}</h3>
                      <p className="text-[11px] text-[var(--text-secondary)]">
                        {area.habits_count} привычек в сфере
                      </p>
                    </div>
                  </div>

                  {/* Subjective rating badge */}
                  <div className="flex items-center space-x-1.5 bg-[var(--bg-secondary)] border border-[var(--border)] px-2.5 py-1 rounded-xl">
                    <div className="flex items-center text-amber-500">
                      <Star className="w-3.5 h-3.5 fill-amber-500" />
                      <span className="text-xs font-bold ml-1">{area.subjective_score}</span>
                      <span className="text-[10px] text-[var(--text-secondary)]">/5</span>
                    </div>
                    {area.trend === 'up' && <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />}
                    {area.trend === 'down' && <TrendingDown className="w-3.5 h-3.5 text-red-500" />}
                    {area.trend === 'stable' && <Minus className="w-3.5 h-3.5 text-gray-400" />}
                  </div>
                </div>

                {/* Objective progress bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[var(--text-secondary)]">
                      Выполнено: {area.objective_completions} из {area.objective_target}
                    </span>
                    <span className="font-semibold text-[var(--text-primary)]">
                      {area.objective_percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-[var(--bg-secondary)] h-2 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(100, area.objective_percentage)}%`,
                        backgroundColor: area.color,
                      }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* TAB 3: WEEKLY ASSESSMENT & AI REPORT */}
      {activeTab === 'assessment' && (
        <div className="space-y-4">
          {/* Card: Weekly Assessment Overview */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
                  <FileText className="w-4 h-4 text-[var(--accent)]" />
                  <span>Недельная рефлексия</span>
                </h3>
                {latestAssessment ? (
                  <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">
                    Период: {latestAssessment.week_start} — {latestAssessment.week_end}
                  </p>
                ) : (
                  <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">
                    Самооценка за эту неделю ещё не заполнена
                  </p>
                )}
              </div>

              <button
                onClick={() => {
                  impactOccurred('light')
                  setShowAssessmentModal(true)
                }}
                className="px-3 py-1.5 bg-[var(--accent)] text-white text-xs font-semibold rounded-xl hover:bg-[var(--accent-hover)] transition-colors shadow-sm"
              >
                {latestAssessment ? 'Редактировать' : 'Заполнить'}
              </button>
            </div>

            {latestAssessment && (
              <div className="grid grid-cols-5 gap-1.5 pt-1 text-center">
                {[
                  { label: 'Дух.', val: latestAssessment.score_spirituality },
                  { label: 'Инт.', val: latestAssessment.score_intellectual },
                  { label: 'Тело', val: latestAssessment.score_physical },
                  { label: 'Мент.', val: latestAssessment.score_mental },
                  { label: 'Акад.', val: latestAssessment.score_academic },
                ].map((item, idx) => (
                  <div key={idx} className="bg-[var(--bg-secondary)] rounded-xl p-2 border border-[var(--border)]">
                    <span className="text-[10px] text-[var(--text-secondary)]">{item.label}</span>
                    <div className="text-xs font-bold text-amber-500 mt-0.5">{item.val}/5</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Report Card */}
          {latestAssessment?.ai_report ? (
            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-4 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-orange-500" />
                  <h3 className="text-xs font-bold text-[var(--text-primary)]">
                    Глубокий AI-Отчёт Недели
                  </h3>
                </div>
                <button
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="text-[11px] text-[var(--accent)] font-semibold hover:underline flex items-center space-x-1"
                >
                  <RefreshCw className={`w-3 h-3 ${generatingReport ? 'animate-spin' : ''}`} />
                  <span>Обновить</span>
                </button>
              </div>

              {/* Overall Evaluation */}
              <div className="bg-gradient-to-r from-orange-500/10 to-amber-500/10 border border-orange-500/20 rounded-xl p-3">
                <span className="text-[10px] font-bold text-[var(--accent)] uppercase tracking-wider">
                  Общий вывод недели
                </span>
                <p className="text-xs text-[var(--text-primary)] leading-relaxed mt-1">
                  {latestAssessment.ai_report.overall_evaluation}
                </p>
              </div>

              {/* Strongest & Focus Areas */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <span className="text-[10px] font-bold text-emerald-500 uppercase flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Сильная область:</span>
                  </span>
                  <p className="text-xs text-[var(--text-primary)] font-medium mt-1">
                    {latestAssessment.ai_report.strongest_area}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                  <span className="text-[10px] font-bold text-amber-500 uppercase flex items-center space-x-1">
                    <AlertCircle className="w-3 h-3" />
                    <span>Фокус внимания:</span>
                  </span>
                  <p className="text-xs text-[var(--text-primary)] font-medium mt-1">
                    {latestAssessment.ai_report.focus_area}
                  </p>
                </div>
              </div>

              {/* Recommendations */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-[var(--text-primary)] flex items-center space-x-1">
                  <Zap className="w-3.5 h-3.5 text-[var(--accent)]" />
                  <span>Практические рекомендации:</span>
                </span>
                <ul className="space-y-1">
                  {latestAssessment.ai_report.recommendations.map((r, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-[var(--text-secondary)] bg-[var(--bg-secondary)] p-2 rounded-lg flex items-start space-x-2"
                    >
                      <span className="font-bold text-[var(--accent)] text-[10px] mt-0.5">•</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Priorities for Next Week */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-[var(--text-primary)]">
                  🎯 Приоритеты на следующую неделю:
                </span>
                <ul className="space-y-1">
                  {latestAssessment.ai_report.priorities.map((p, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-[var(--text-primary)] bg-[var(--bg-secondary)] p-2 rounded-lg font-medium"
                    >
                      {idx + 1}. {p}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : latestAssessment ? (
            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-6 text-center space-y-3">
              <Sparkles className="w-8 h-8 text-[var(--accent)] mx-auto" />
              <h4 className="text-xs font-bold text-[var(--text-primary)]">
                Самооценка сохранена, сформировать AI-отчёт?
              </h4>
              <p className="text-xs text-[var(--text-secondary)] max-w-xs mx-auto">
                AI проанализирует соотношение твоих объективных привычек и субъективных оценок.
              </p>
              <button
                onClick={handleGenerateReport}
                disabled={generatingReport}
                className="px-4 py-2 bg-[var(--accent)] text-white text-xs font-semibold rounded-xl hover:bg-[var(--accent-hover)] transition-colors shadow-sm disabled:opacity-50"
              >
                {generatingReport ? 'Генерируем отчёт...' : 'Сформировать AI-отчёт'}
              </button>
            </div>
          ) : null}
        </div>
      )}

      {/* MODAL: Weekly Assessment Form */}
      {showAssessmentModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-5 shadow-xl space-y-4 animate-scale-in">
            <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
              <div>
                <h3 className="text-sm font-bold text-[var(--text-primary)]">
                  Недельная самооценка
                </h3>
                <p className="text-[11px] text-[var(--text-secondary)]">
                  Оцени прогресс по 5 сферам от 1 до 5
                </p>
              </div>
              <button
                onClick={() => setShowAssessmentModal(false)}
                className="p-1 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* 5 Area Rating Sliders */}
            <div className="space-y-3">
              {[
                { key: 'spirituality', label: '1. Духовность и характер' },
                { key: 'intellectual', label: '2. Интеллектуальное развитие' },
                { key: 'physical', label: '3. Физическое развитие' },
                { key: 'mental', label: '4. Ментальное развитие' },
                { key: 'academic', label: '5. Академическое и карьера' },
              ].map((area) => (
                <div key={area.key} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-[var(--text-primary)]">{area.label}</span>
                    <span className="font-bold text-[var(--accent)]">
                      {scores[area.key as keyof typeof scores]} / 5
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="1"
                    value={scores[area.key as keyof typeof scores]}
                    onChange={(e) =>
                      setScores({
                        ...scores,
                        [area.key]: parseInt(e.target.value),
                      })
                    }
                    className="w-full accent-[var(--accent)] cursor-pointer"
                  />
                </div>
              ))}
            </div>

            {/* Questions */}
            <div className="space-y-3 pt-2 border-t border-[var(--border)]">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-[var(--text-primary)]">
                  Что получилось особенно хорошо?
                </label>
                <input
                  type="text"
                  value={wentWell}
                  onChange={(e) => setWentWell(e.target.value)}
                  placeholder="Стабильный ранний подъём, закрыл книгу..."
                  className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-[var(--text-primary)]">
                  Что пошло не так или где был срыв?
                </label>
                <input
                  type="text"
                  value={wentWrong}
                  onChange={(e) => setWentWrong(e.target.value)}
                  placeholder="Пропустил спорт, залип в телефоне..."
                  className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-[var(--text-primary)]">
                  Главный урок недели?
                </label>
                <input
                  type="text"
                  value={learned}
                  onChange={(e) => setLearned(e.target.value)}
                  placeholder="Никогда не пропускать дважды..."
                  className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-[var(--text-primary)]">
                  Главные приоритеты на следующую неделю:
                </label>
                <input
                  type="text"
                  value={priorities}
                  onChange={(e) => setPriorities(e.target.value)}
                  placeholder="Закрыть 4 тренировки, сдать проект..."
                  className="w-full text-xs bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2.5 text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2 pt-2">
              <button
                onClick={() => setShowAssessmentModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-[var(--bg-secondary)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSaveAssessment}
                disabled={savingAssessment}
                className="flex-1 py-2.5 rounded-xl bg-[var(--accent)] text-white text-xs font-semibold hover:bg-[var(--accent-hover)] transition-colors shadow-sm disabled:opacity-50"
              >
                {savingAssessment ? 'Сохранение...' : 'Сохранить и анализ'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
