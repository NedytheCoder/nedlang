"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

export interface RecommendedAction {
  id: number
  type: "review" | "lesson" | "assessment" | "practice" | "grammar"
  icon: string
  titleKey: string
  priority: "high" | "medium" | "low"
  estimatedMinutes: number
}

const PRIORITY_STYLES: Record<RecommendedAction["priority"], { badge: string; border: string }> = {
  high:   { badge: "bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400",     border: "border-red-100 dark:border-red-500/20" },
  medium: { badge: "bg-amber-100 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400", border: "border-amber-100 dark:border-amber-500/20" },
  low:    { badge: "bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-gray-400",  border: "border-slate-100 dark:border-white/8" },
}

const PRIORITY_KEYS: Record<RecommendedAction["priority"], string> = {
  high: "dash_actions_high",
  medium: "dash_actions_medium",
  low: "dash_actions_low",
}

interface Props {
  actions: RecommendedAction[]
}

export default function RecommendedActions({ actions }: Props) {
  const { t } = useTranslation()

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-sm">
          🚀
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_actions_title")}</p>
          <p className="text-xs text-slate-500 dark:text-gray-400">{t("dash_actions_subtitle")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
        {actions.map((action, i) => {
          const style = PRIORITY_STYLES[action.priority]
          return (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className={`relative flex flex-col gap-3 p-4 bg-slate-50 dark:bg-slate-800 border ${style.border} rounded-xl hover:shadow-md transition-all group`}
            >
              <div className="flex items-start justify-between">
                <span className="text-2xl">{action.icon}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide ${style.badge}`}>
                  {t(PRIORITY_KEYS[action.priority])}
                </span>
              </div>

              <p className="text-xs font-medium text-slate-800 dark:text-gray-200 leading-snug flex-1">
                {t(action.titleKey)}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-400 dark:text-gray-500">
                  ~{action.estimatedMinutes} {t("dash_actions_min")}
                </span>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 transition-colors"
                >
                  {t("dash_actions_start")} →
                </motion.button>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
