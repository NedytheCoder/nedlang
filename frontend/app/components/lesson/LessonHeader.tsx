"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  title: string
  level?: string
  topic?: string
  framework?: string
  progressCompleted?: number
  progressTotal?: number
}

function levelColor(level: string): string {
  const l = level.toUpperCase()
  if (["A1", "A2", "N5", "N4", "HSK1", "HSK2", "TOPIK1", "TOPIK2"].some((v) => l === v))
    return "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30"
  if (["B1", "B2", "N3", "HSK3", "HSK4", "TOPIK3", "TOPIK4"].some((v) => l === v))
    return "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30"
  return "bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30"
}

export default function LessonHeader({ title, level, topic, framework, progressCompleted = 0, progressTotal = 0 }: Props) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      {/* Top row: back link + badges */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors mr-1"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          {t("dash_nav_dashboard")}
        </Link>

        {level && (
          <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full border ${levelColor(level)}`}>
            {framework ? `${framework} · ` : ""}{level}
          </span>
        )}

        {topic && (
          <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
            {topic}
          </span>
        )}
      </div>

      {/* Title */}
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white leading-snug mb-5">
        {title}
      </h1>

      {/* Curriculum progress */}
      {progressTotal > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-500 dark:text-gray-400">
              {t("dash_hero_progress")}
            </span>
            <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400">
              {progressCompleted} / {progressTotal} {t("lesson_lessons")}
            </span>
          </div>
          <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.round((progressCompleted / progressTotal) * 100)}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="h-full bg-indigo-600 dark:bg-indigo-500 rounded-full"
            />
          </div>
        </div>
      )}
    </motion.div>
  )
}
