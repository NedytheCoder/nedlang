"use client"

import { useTranslation } from "../../../i18n/LanguageProvider"

const HEAT_COLORS = [
  "bg-slate-100 dark:bg-slate-800",
  "bg-indigo-200 dark:bg-indigo-900/70",
  "bg-indigo-400 dark:bg-indigo-700",
  "bg-indigo-600 dark:bg-indigo-500",
  "bg-indigo-800 dark:bg-indigo-300",
]

interface Props {
  streak: { currentStreak: number; longestStreak: number; totalStudyDays: number; weeklyConsistency: number }
  heatmapData: number[]
}

export default function StreakCard({ streak, heatmapData }: Props) {
  const { t } = useTranslation()
  const { currentStreak, longestStreak, totalStudyDays, weeklyConsistency } = streak

  const stats = [
    { valueKey: currentStreak, labelKey: "dash_streak_current", accent: true },
    { valueKey: longestStreak, labelKey: "dash_streak_longest", accent: false },
    { valueKey: totalStudyDays, labelKey: "dash_streak_total_days", accent: false },
  ]

  // Build heatmap: 53 weeks × 7 days
  const weeks = 53

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_streak_title")}</p>
        <div className="flex items-center gap-1.5">
          <span className="text-lg">🔥</span>
          <span className="text-sm font-bold text-orange-500">{currentStreak} {t("dash_streak_days")}</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        {stats.map(({ valueKey, labelKey, accent }) => (
          <div key={labelKey} className={`text-center py-3 rounded-xl ${accent ? "bg-orange-50 dark:bg-orange-500/10 border border-orange-100 dark:border-orange-500/20" : "bg-slate-50 dark:bg-slate-800"}`}>
            <p className={`text-xl font-bold ${accent ? "text-orange-500" : "text-slate-900 dark:text-white"}`}>{valueKey}</p>
            <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">{t(labelKey)}</p>
          </div>
        ))}
      </div>

      {/* Weekly consistency */}
      <div className="flex items-center gap-3 mb-5 px-1">
        <span className="text-xs text-slate-500 dark:text-gray-400 whitespace-nowrap">{t("dash_streak_weekly_score")}</span>
        <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full" style={{ width: `${weeklyConsistency}%` }} />
        </div>
        <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">{weeklyConsistency}%</span>
      </div>

      {/* Heatmap */}
      <div>
        <p className="text-xs text-slate-500 dark:text-gray-400 mb-2">{t("dash_streak_heatmap_title")}</p>
        <div className="overflow-x-auto">
          <div className="flex gap-0.5" style={{ minWidth: "max-content" }}>
            {/* Day labels */}
            <div className="flex flex-col gap-0.5 mr-0.5">
              {[0, 1, 2, 3, 4, 5, 6].map((d) => (
                <div key={d} className="w-3 h-3 flex items-center justify-center">
                  <span className="text-[8px] text-slate-400">
                    {d === 0 ? t("dash_streak_day_mon") : d === 2 ? t("dash_streak_day_wed") : d === 4 ? t("dash_streak_day_fri") : ""}
                  </span>
                </div>
              ))}
            </div>
            {Array.from({ length: weeks }, (_, week) => (
              <div key={week} className="flex flex-col gap-0.5">
                {Array.from({ length: 7 }, (_, day) => {
                  const idx = week * 7 + day
                  const level = idx < heatmapData.length ? heatmapData[idx] : 0
                  return (
                    <div
                      key={day}
                      className={`w-3 h-3 rounded-[2px] ${HEAT_COLORS[level as 0|1|2|3|4]}`}
                      title={`Level ${level}`}
                    />
                  )
                })}
              </div>
            ))}
          </div>
        </div>
        {/* Legend */}
        <div className="flex items-center gap-1.5 mt-2 justify-end">
          <span className="text-[10px] text-slate-400">{t("dash_streak_less")}</span>
          {[0, 1, 2, 3, 4].map((l) => (
            <div key={l} className={`w-2.5 h-2.5 rounded-sm ${HEAT_COLORS[l as 0|1|2|3|4]}`} />
          ))}
          <span className="text-[10px] text-slate-400">{t("dash_streak_more")}</span>
        </div>
      </div>
    </div>
  )
}
