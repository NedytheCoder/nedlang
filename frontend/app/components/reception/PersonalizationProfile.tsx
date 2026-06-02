"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { ReceptionUser } from "./receptionMockData"

export default function PersonalizationProfile({ user }: { user: ReceptionUser }) {
  const { t } = useTranslation()

  const rows = [
    { icon: "🗣️", labelKey: "rec_persona_native", value: `${user.nativeLanguage.flag} ${user.nativeLanguage.name}` },
    { icon: "🎯", labelKey: "rec_persona_target", value: `${user.targetLanguage.flag} ${user.targetLanguage.name}` },
    { icon: "📖", labelKey: "rec_persona_style", value: user.learningStyle },
    { icon: "⏱️", labelKey: "rec_persona_daily", value: `${user.dailyGoalMinutes} ${t("rec_persona_min")}` },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.55 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-7"
    >
      <div className="flex items-center gap-3 mb-5">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-base flex-shrink-0">
          🧠
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white">{t("rec_persona_title")}</h2>
          <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">{t("rec_persona_subtitle")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
        {rows.map(({ icon, labelKey, value }) => (
          <div key={labelKey} className="flex items-center gap-3 bg-slate-50 dark:bg-slate-800 rounded-xl px-4 py-3">
            <span className="text-base flex-shrink-0">{icon}</span>
            <div>
              <p className="text-[10px] font-medium text-slate-400 dark:text-gray-500 uppercase tracking-wide">{t(labelKey)}</p>
              <p className="text-sm font-semibold text-slate-900 dark:text-white mt-0.5">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Learning goal */}
      <div className="bg-slate-50 dark:bg-slate-800 rounded-xl px-4 py-3 mb-4">
        <p className="text-[10px] font-medium text-slate-400 dark:text-gray-500 uppercase tracking-wide mb-1">
          {t("rec_persona_goal")}
        </p>
        <p className="text-sm font-medium text-slate-900 dark:text-white leading-snug">{user.learningGoal}</p>
      </div>

      {/* Hobbies */}
      <div className="mb-5">
        <p className="text-[10px] font-medium text-slate-400 dark:text-gray-500 uppercase tracking-wide mb-2">
          {t("rec_persona_hobbies")}
        </p>
        <div className="flex flex-wrap gap-2">
          {user.hobbies.map((h, i) => (
            <motion.span
              key={h}
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + i * 0.07 }}
              className="px-3 py-1.5 text-xs font-medium bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-100 dark:border-indigo-500/20 rounded-full"
            >
              {h}
            </motion.span>
          ))}
        </div>
      </div>

      {/* Note */}
      <div className="flex gap-3 bg-violet-50 dark:bg-violet-500/10 border border-violet-100 dark:border-violet-500/20 rounded-xl p-4">
        <span className="text-lg flex-shrink-0">💡</span>
        <p className="text-xs text-violet-700 dark:text-violet-300 leading-relaxed">{t("rec_persona_note")}</p>
      </div>
    </motion.div>
  )
}
