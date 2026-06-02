"use client"

import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockStats } from "./mockData"

export default function LearningStats() {
  const { t } = useTranslation()

  const statCards = [
    { value: `${mockStats.totalHours}`, unit: t("dash_stats_hours"), labelKey: "dash_stats_total_hours", icon: "⏱️", color: "text-indigo-600 dark:text-indigo-400" },
    { value: `${mockStats.thisWeekHours}`, unit: t("dash_stats_hours"), labelKey: "dash_stats_this_week", icon: "📅", color: "text-blue-600 dark:text-blue-400" },
    { value: `${mockStats.thisMonthHours}`, unit: t("dash_stats_hours"), labelKey: "dash_stats_this_month", icon: "📆", color: "text-violet-600 dark:text-violet-400" },
    { value: `${mockStats.avgDailyMinutes}`, unit: t("dash_stats_min"), labelKey: "dash_stats_avg_daily", icon: "🎯", color: "text-emerald-600 dark:text-emerald-400" },
    { value: `${mockStats.lessonsCompleted}`, unit: "", labelKey: "dash_stats_lessons", icon: "📖", color: "text-orange-600 dark:text-orange-400" },
    { value: `${mockStats.assessmentsCompleted}`, unit: "", labelKey: "dash_stats_assessments", icon: "🎓", color: "text-pink-600 dark:text-pink-400" },
    { value: `${mockStats.conversationsCompleted}`, unit: "", labelKey: "dash_stats_conversations", icon: "💬", color: "text-teal-600 dark:text-teal-400" },
  ]

  const maxHours = Math.max(...mockStats.weeklyHoursData)

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-base">📊</span>
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_stats_title")}</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
        {statCards.map(({ value, unit, labelKey, icon, color }) => (
          <div key={labelKey} className="bg-slate-50 dark:bg-slate-800 rounded-xl p-3 text-center">
            <span className="text-lg">{icon}</span>
            <p className={`text-lg font-bold mt-1 ${color}`}>
              {value}<span className="text-xs font-normal text-slate-400 ml-0.5">{unit}</span>
            </p>
            <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5 leading-tight">{t(labelKey)}</p>
          </div>
        ))}
      </div>

      {/* Weekly bar chart */}
      <div>
        <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide mb-3">{t("dash_stats_weekly_activity")}</p>
        <div className="flex items-end gap-2 h-28">
          {mockStats.weeklyHoursData.map((hours, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
              <span className="text-[10px] text-slate-500 dark:text-gray-400">{hours}h</span>
              <div className="w-full relative" style={{ height: `${(hours / maxHours) * 80}px` }}>
                <div
                  className="absolute inset-0 bg-gradient-to-t from-indigo-600 to-violet-500 rounded-t-md"
                />
              </div>
              <span className="text-[10px] text-slate-400 dark:text-gray-500">{mockStats.weekLabels[i]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
