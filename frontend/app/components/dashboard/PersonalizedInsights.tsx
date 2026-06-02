"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockInsights, Insight } from "./mockData"

const TYPE_STYLES: Record<Insight["type"], { bg: string; border: string; label: string; labelKey: string }> = {
  strength:    { bg: "bg-emerald-50 dark:bg-emerald-500/10",   border: "border-emerald-100 dark:border-emerald-500/20",   label: "Strength",    labelKey: "dash_insights_strength"    },
  improvement: { bg: "bg-blue-50 dark:bg-blue-500/10",         border: "border-blue-100 dark:border-blue-500/20",         label: "Improvement", labelKey: "dash_insights_improvement" },
  weakness:    { bg: "bg-amber-50 dark:bg-amber-500/10",       border: "border-amber-100 dark:border-amber-500/20",       label: "Focus Area",  labelKey: "dash_insights_weakness"    },
  habit:       { bg: "bg-violet-50 dark:bg-violet-500/10",     border: "border-violet-100 dark:border-violet-500/20",     label: "Pattern",     labelKey: "dash_insights_habit"       },
}

const TYPE_TEXT_COLORS: Record<Insight["type"], string> = {
  strength:    "text-emerald-700 dark:text-emerald-300",
  improvement: "text-blue-700 dark:text-blue-300",
  weakness:    "text-amber-700 dark:text-amber-300",
  habit:       "text-violet-700 dark:text-violet-300",
}

export default function PersonalizedInsights() {
  const { t } = useTranslation()

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-sm">
          ✨
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_insights_title")}</p>
          <p className="text-xs text-slate-500 dark:text-gray-400">{t("dash_insights_subtitle")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {mockInsights.map((insight, i) => {
          const style = TYPE_STYLES[insight.type]
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className={`${style.bg} border ${style.border} rounded-xl p-4`}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl flex-shrink-0">{insight.icon}</span>
                <div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${TYPE_TEXT_COLORS[insight.type]}`}>
                    {t(style.labelKey)}
                  </span>
                  <p className="text-xs text-slate-700 dark:text-gray-300 mt-1 leading-relaxed">
                    {t(insight.textKey)}
                  </p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
