"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { FrameworkInfo } from "./frameworkUtils"

export default function FrameworkCard({ framework }: { framework: FrameworkInfo }) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl overflow-hidden shadow-sm"
    >
      {/* Header stripe */}
      <div className={`bg-gradient-to-r ${framework.gradient} p-5 sm:p-6`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-xs font-medium uppercase tracking-widest mb-1">
              {t("rec_framework_heading")}
            </p>
            <div className="flex items-center gap-3">
              <span className="text-3xl">{framework.flag}</span>
              <div>
                <h2 className="text-white text-2xl font-bold">{t(framework.nameKey)}</h2>
                <p className="text-white/80 text-sm">{t(framework.rangeKey)}</p>
              </div>
            </div>
          </div>
          {/* Animated glow badge */}
          <motion.div
            animate={{ boxShadow: ["0 0 12px rgba(255,255,255,0.2)", "0 0 28px rgba(255,255,255,0.5)", "0 0 12px rgba(255,255,255,0.2)"] }}
            transition={{ repeat: Infinity, duration: 2.5 }}
            className="w-14 h-14 rounded-2xl bg-white/20 border border-white/30 flex items-center justify-center"
          >
            <span className="text-white text-xs font-bold text-center leading-tight px-1">
              {framework.id}
            </span>
          </motion.div>
        </div>

        {/* Level chips */}
        <div className="flex flex-wrap gap-2 mt-5">
          {framework.levels.map((lvl, i) => (
            <motion.span
              key={lvl}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.25 + i * 0.06 }}
              className="px-3 py-1 bg-white/20 border border-white/30 rounded-full text-white text-xs font-semibold"
            >
              {lvl}
            </motion.span>
          ))}
        </div>
      </div>

      {/* Body */}
      <div className="p-5 sm:p-6 space-y-4">
        {/* Description */}
        <div className="flex gap-3">
          <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 text-sm">
            📋
          </div>
          <p className="text-sm text-slate-700 dark:text-gray-300 leading-relaxed">{t(framework.descKey)}</p>
        </div>

        {/* Why this framework */}
        <div className="flex gap-3">
          <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 text-sm">
            🌍
          </div>
          <p className="text-sm text-slate-600 dark:text-gray-400 leading-relaxed">{t(framework.whyKey)}</p>
        </div>

        {/* AI note */}
        <div className="bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-xl p-4 flex gap-3">
          <span className="text-lg flex-shrink-0">🤖</span>
          <p className="text-sm text-indigo-700 dark:text-indigo-300 leading-relaxed">{t("rec_framework_ai_note")}</p>
        </div>
      </div>
    </motion.div>
  )
}
