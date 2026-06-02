"use client"

import { useTranslation } from "../../../../i18n/LanguageProvider"
import { OnboardingData } from "./types"
import { getLangByCode } from "./languages"

const STYLE_ICONS: Record<string, string> = {
  reading: "📖",
  listening: "🎧",
  speaking: "🗣️",
  writing: "✍️",
  mixed: "⚡",
}

const STYLE_KEYS: Record<string, string> = {
  reading: "onb_style_reading",
  listening: "onb_style_listening",
  speaking: "onb_style_speaking",
  writing: "onb_style_writing",
  mixed: "onb_style_mixed",
}

function SummaryRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-3 py-3 border-b border-slate-100 dark:border-white/6 last:border-0">
      <span className="text-xs font-medium text-slate-500 dark:text-gray-400 w-28 flex-shrink-0 pt-0.5">{label}</span>
      <div className="flex-1">{children}</div>
    </div>
  )
}

export default function StepSummary({ data }: { data: OnboardingData }) {
  const { t } = useTranslation()

  const nativeLang = getLangByCode(data.native_language)
  const targetLang = getLangByCode(data.target_language)
  const dailyGoalKey = `onb_goal_${data.daily_goal_minutes === 60 ? "60" : data.daily_goal_minutes}`

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_summary_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_summary_subtitle")}</p>
      </div>

      <div className="bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
        <SummaryRow label={t("onb_summary_native")}>
          {nativeLang ? (
            <span className="text-sm text-slate-900 dark:text-white font-medium">
              {nativeLang.flag} {nativeLang.name}
            </span>
          ) : <span className="text-sm text-slate-400">—</span>}
        </SummaryRow>

        <SummaryRow label={t("onb_summary_target")}>
          {targetLang ? (
            <span className="text-sm text-slate-900 dark:text-white font-medium">
              {targetLang.flag} {targetLang.name}
            </span>
          ) : <span className="text-sm text-slate-400">—</span>}
        </SummaryRow>

        <SummaryRow label={t("onb_summary_goal")}>
          <p className="text-sm text-slate-700 dark:text-gray-300 leading-relaxed line-clamp-3">
            {data.learning_goal || "—"}
          </p>
        </SummaryRow>

        <SummaryRow label={t("onb_summary_hobbies")}>
          <div className="flex flex-wrap gap-1.5">
            {data.top_hobbies.length > 0
              ? data.top_hobbies.map((h) => (
                  <span key={h} className="px-2.5 py-1 text-xs bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 rounded-full border border-indigo-100 dark:border-indigo-500/20 font-medium">
                    {h}
                  </span>
                ))
              : <span className="text-sm text-slate-400">—</span>}
          </div>
        </SummaryRow>

        <SummaryRow label={t("onb_summary_style")}>
          {data.preferred_learning_style ? (
            <span className="text-sm text-slate-900 dark:text-white font-medium">
              {STYLE_ICONS[data.preferred_learning_style]} {t(STYLE_KEYS[data.preferred_learning_style])}
            </span>
          ) : <span className="text-sm text-slate-400">—</span>}
        </SummaryRow>

        <SummaryRow label={t("onb_summary_daily")}>
          {data.daily_goal_minutes ? (
            <span className="text-sm text-slate-900 dark:text-white font-medium">
              {t(dailyGoalKey)}
            </span>
          ) : <span className="text-sm text-slate-400">—</span>}
        </SummaryRow>
      </div>

      <div className="bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-xl p-4">
        <div className="flex gap-3">
          <div className="w-8 h-8 flex-shrink-0 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-sm">
            ✨
          </div>
          <p className="text-sm text-indigo-700 dark:text-indigo-300 leading-relaxed">
            {t("onb_summary_ai_note")}
          </p>
        </div>
      </div>
    </div>
  )
}
