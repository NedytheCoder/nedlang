"use client"

import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockVocab } from "./mockData"

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300",
  medium: "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300",
  hard: "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300",
}

export default function VocabularyAnalytics() {
  const { t } = useTranslation()

  const stats = [
    { value: mockVocab.total.toLocaleString(), labelKey: "dash_vocab_total", color: "text-indigo-600 dark:text-indigo-400" },
    { value: mockVocab.active.toLocaleString(), labelKey: "dash_vocab_active", color: "text-emerald-600 dark:text-emerald-400" },
    { value: `${mockVocab.retentionRate}%`, labelKey: "dash_vocab_retention", color: "text-violet-600 dark:text-violet-400" },
    { value: `+${mockVocab.newPerWeek}`, labelKey: "dash_vocab_per_week", color: "text-blue-600 dark:text-blue-400" },
  ]

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-base">📖</span>
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_vocab_title")}</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        {stats.map(({ value, labelKey, color }) => (
          <div key={labelKey} className="bg-slate-50 dark:bg-slate-800 rounded-xl p-3">
            <p className={`text-xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">{t(labelKey)}</p>
          </div>
        ))}
      </div>

      {/* Recently learned */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide mb-2">{t("dash_vocab_recent")}</p>
        <div className="space-y-1.5">
          {mockVocab.recent.slice(0, 4).map((w) => (
            <div key={w.word} className="flex items-center justify-between py-1.5 px-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span className="text-sm font-medium text-slate-900 dark:text-white">{w.word}</span>
              <span className="text-xs text-slate-500 dark:text-gray-400">{w.translation}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Needs review */}
      <div>
        <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide mb-2">{t("dash_vocab_review")}</p>
        <div className="flex flex-wrap gap-1.5">
          {mockVocab.review.map((w) => (
            <span key={w.word} className={`px-2 py-1 text-xs rounded-lg font-medium ${DIFFICULTY_COLORS[w.difficulty ?? "medium"]}`}>
              {w.word}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
