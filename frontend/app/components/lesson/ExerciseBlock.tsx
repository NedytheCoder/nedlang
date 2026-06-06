"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import type { Exercise } from "./types"

interface Props {
  exercises: Exercise[]
}

const TYPE_ICON: Record<string, string> = {
  fill_in_blank: "✏️",
  translation:   "🔄",
  construction:  "🏗️",
  matching:      "🔗",
}

const TYPE_LABEL: Record<string, string> = {
  fill_in_blank: "Fill in the blank",
  translation:   "Translation",
  construction:  "Construction",
  matching:      "Matching",
}

function ExerciseItem({ exercise, index }: { exercise: Exercise; index: number }) {
  const { t } = useTranslation()
  const [showAnswer, setShowAnswer] = useState(false)
  const [value, setValue] = useState("")

  return (
    <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-white/8">
        <div className="flex items-center gap-2">
          <span className="text-sm">{TYPE_ICON[exercise.type] ?? "📋"}</span>
          <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">
            {TYPE_LABEL[exercise.type] ?? exercise.type}
          </span>
        </div>
        <span className="text-[10px] font-bold text-slate-400 dark:text-gray-500 tabular-nums">
          {String(index + 1).padStart(2, "0")}
        </span>
      </div>

      <div className="px-4 py-4 space-y-3">
        {/* Instruction */}
        <p className="text-xs text-slate-500 dark:text-gray-400">{exercise.instruction}</p>

        {/* Prompt */}
        <p className="text-sm font-medium text-slate-800 dark:text-gray-100 leading-relaxed">
          {exercise.prompt}
        </p>

        {/* Input */}
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t("lesson_exercise_placeholder")}
          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all"
        />

        {/* Answer reveal */}
        <div>
          <button
            type="button"
            onClick={() => setShowAnswer((v) => !v)}
            className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors flex items-center gap-1"
          >
            <svg
              className={`w-3.5 h-3.5 transition-transform ${showAnswer ? "rotate-180" : ""}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
            </svg>
            {showAnswer ? t("lesson_answer_hide") : t("lesson_answer_show")}
          </button>

          <AnimatePresence>
            {showAnswer && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-2 px-3.5 py-2.5 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
                  <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-0.5 uppercase tracking-wide">
                    {t("lesson_answer_label")}
                  </p>
                  <p className="text-sm text-emerald-800 dark:text-emerald-200">{exercise.answer}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

export default function ExerciseBlock({ exercises }: Props) {
  const { t } = useTranslation()

  if (!exercises?.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-lg bg-orange-100 dark:bg-orange-500/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">🎯</span>
        </div>
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
          {t("lesson_exercises_label")}
        </h2>
      </div>

      <div className="space-y-3">
        {exercises.map((ex, i) => (
          <ExerciseItem key={i} exercise={ex} index={i} />
        ))}
      </div>
    </motion.div>
  )
}
