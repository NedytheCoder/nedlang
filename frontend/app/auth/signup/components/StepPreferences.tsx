"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps, LearningStyle } from "./types"

const STYLES: { value: LearningStyle; key: string; icon: string }[] = [
  { value: "reading", key: "onb_style_reading", icon: "📖" },
  { value: "listening", key: "onb_style_listening", icon: "🎧" },
  { value: "speaking", key: "onb_style_speaking", icon: "🗣️" },
  { value: "writing", key: "onb_style_writing", icon: "✍️" },
  { value: "mixed", key: "onb_style_mixed", icon: "⚡" },
]

const GOALS: { value: number; key: string; accent: boolean }[] = [
  { value: 5, key: "onb_goal_5", accent: false },
  { value: 10, key: "onb_goal_10", accent: false },
  { value: 15, key: "onb_goal_15", accent: true },
  { value: 30, key: "onb_goal_30", accent: false },
  { value: 60, key: "onb_goal_60", accent: false },
]

export default function StepPreferences({ data, onChange, errors }: StepProps) {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_prefs_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_prefs_subtitle")}</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-3">
          {t("onb_style_label")} <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {STYLES.map(({ value, key, icon }) => {
            const active = data.preferred_learning_style === value
            return (
              <motion.button
                key={value}
                type="button"
                onClick={() => onChange({ preferred_learning_style: value })}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all text-center ${
                  active
                    ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300"
                    : "border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-gray-400 hover:border-slate-300 dark:hover:border-white/20"
                }`}
              >
                <span className="text-2xl">{icon}</span>
                <span className="text-xs font-medium">{t(key)}</span>
              </motion.button>
            )
          })}
        </div>
        {errors.preferred_learning_style && (
          <p className="mt-1.5 text-xs text-red-500">{errors.preferred_learning_style}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-3">
          {t("onb_daily_label")} <span className="text-red-500">*</span>
        </label>
        <div className="flex flex-wrap gap-2">
          {GOALS.map(({ value, key, accent }) => {
            const active = data.daily_goal_minutes === value
            return (
              <motion.button
                key={value}
                type="button"
                onClick={() => onChange({ daily_goal_minutes: value })}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`px-4 py-2 text-sm rounded-xl border-2 font-medium transition-all ${
                  active
                    ? "border-indigo-500 bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
                    : accent
                    ? "border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 hover:border-indigo-400 dark:hover:border-indigo-500/60"
                    : "border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-gray-400 hover:border-slate-300 dark:hover:border-white/20"
                }`}
              >
                {t(key)}
              </motion.button>
            )
          })}
        </div>
        {errors.daily_goal_minutes && (
          <p className="mt-1.5 text-xs text-red-500">{errors.daily_goal_minutes}</p>
        )}
      </div>
    </div>
  )
}
