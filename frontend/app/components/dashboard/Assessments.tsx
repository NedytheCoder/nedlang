"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockAssessments } from "./mockData"

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 85 ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10" :
    score >= 70 ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-500/10" :
    "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10"
  return (
    <span className={`px-2 py-0.5 text-xs font-bold rounded-lg ${color}`}>{score}%</span>
  )
}

export default function Assessments() {
  const { t } = useTranslation()

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-base">🎯</span>
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_assess_title")}</p>
      </div>

      {/* Upcoming */}
      <div className="mb-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide">{t("dash_assess_upcoming")}</p>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 transition-colors"
          >
            + {t("dash_assess_schedule")}
          </motion.button>
        </div>
        <div className="space-y-2">
          {mockAssessments.upcoming.map((a, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <div className="w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-slate-900 dark:text-white truncate">{a.title}</p>
                <p className="text-xs text-slate-400 dark:text-gray-500">{t(a.typeKey)} · {a.date}</p>
              </div>
              <span className="text-xs text-slate-400 dark:text-gray-500 flex-shrink-0">{a.duration} {t("dash_assess_min")}</span>
            </div>
          ))}
        </div>
      </div>

      {/* History */}
      <div>
        <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide mb-3">{t("dash_assess_history")}</p>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left">
                <th className="pb-2 font-medium text-slate-400 dark:text-gray-500">{t("dash_assess_date")}</th>
                <th className="pb-2 font-medium text-slate-400 dark:text-gray-500">{t("dash_assess_type")}</th>
                <th className="pb-2 font-medium text-slate-400 dark:text-gray-500">{t("dash_assess_level")}</th>
                <th className="pb-2 font-medium text-slate-400 dark:text-gray-500 text-right">{t("dash_assess_score")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/6">
              {mockAssessments.history.map((r, i) => (
                <tr key={i}>
                  <td className="py-2 text-slate-600 dark:text-gray-400">{r.date}</td>
                  <td className="py-2 text-slate-700 dark:text-gray-300">{t(r.typeKey)}</td>
                  <td className="py-2">
                    <span className="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 rounded font-medium">
                      {r.level}
                    </span>
                  </td>
                  <td className="py-2 text-right">
                    <ScoreBadge score={r.score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
