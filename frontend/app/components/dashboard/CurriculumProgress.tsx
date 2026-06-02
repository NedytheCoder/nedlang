"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockCurriculum, CurriculumModule } from "./mockData"

const STATUS_STYLES: Record<CurriculumModule["status"], { icon: string; ring: string; bg: string; text: string }> = {
  completed: { icon: "✓", ring: "ring-2 ring-emerald-400", bg: "bg-emerald-400", text: "text-emerald-600 dark:text-emerald-400" },
  current:   { icon: "▶", ring: "ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-slate-900", bg: "bg-indigo-600", text: "text-indigo-600 dark:text-indigo-400" },
  locked:    { icon: "🔒", ring: "ring-1 ring-slate-200 dark:ring-slate-700", bg: "bg-slate-200 dark:bg-slate-700", text: "text-slate-400 dark:text-gray-500" },
}

export default function CurriculumProgress() {
  const { t } = useTranslation()

  const completedCount = mockCurriculum.filter((m) => m.status === "completed").length
  const totalLessons = mockCurriculum.reduce((s, m) => s + m.lessons, 0)
  const completedLessons = mockCurriculum.reduce((s, m) => s + m.completedLessons, 0)

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <span className="text-base">🗺️</span>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_curriculum_title")}</p>
        </div>
        <span className="text-xs text-slate-500 dark:text-gray-400">
          {completedLessons} / {totalLessons} {t("dash_curriculum_lessons")}
        </span>
      </div>

      {/* Module road */}
      <div className="relative">
        {/* Connecting line */}
        <div className="absolute left-5 top-5 bottom-5 w-0.5 bg-slate-200 dark:bg-slate-700" />

        <div className="space-y-3">
          {mockCurriculum.map((module, i) => {
            const style = STATUS_STYLES[module.status]
            const pct = module.lessons > 0 ? (module.completedLessons / module.lessons) * 100 : 0

            return (
              <motion.div
                key={module.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`relative flex gap-4 p-4 rounded-xl border transition-all ${
                  module.status === "current"
                    ? "bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/30"
                    : module.status === "completed"
                    ? "bg-slate-50 dark:bg-slate-800 border-slate-100 dark:border-white/6"
                    : "bg-slate-50/50 dark:bg-slate-800/30 border-slate-100 dark:border-white/4 opacity-60"
                }`}
              >
                {/* Status node */}
                <div className={`relative z-10 w-10 h-10 rounded-full ${style.bg} ${style.ring} flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}>
                  {module.status === "completed" ? "✓" : module.status === "current" ? module.id : <span className="text-xs">🔒</span>}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className={`text-sm font-semibold ${module.status === "locked" ? "text-slate-400 dark:text-gray-500" : "text-slate-900 dark:text-white"}`}>
                        {t("dash_curriculum_module")} {module.id}: {module.title}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
                        {module.completedLessons}/{module.lessons} {t("dash_curriculum_lessons")}
                      </p>
                    </div>
                    {module.status === "current" && (
                      <span className="flex-shrink-0 px-2 py-0.5 bg-indigo-600 text-white text-[10px] font-bold rounded-full uppercase tracking-wide">
                        {t("dash_curriculum_current")}
                      </span>
                    )}
                    {module.status === "completed" && (
                      <span className="flex-shrink-0 text-emerald-500 text-sm font-bold">✓</span>
                    )}
                  </div>

                  {module.status !== "locked" && (
                    <div className="mt-2 w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div className={`h-full ${module.status === "completed" ? "bg-emerald-400" : "bg-indigo-500"} rounded-full`} style={{ width: `${pct}%` }} />
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
