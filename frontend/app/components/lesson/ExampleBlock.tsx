"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import type { Example } from "./types"

interface Props {
  examples: Example[]
}

export default function ExampleBlock({ examples }: Props) {
  const { t } = useTranslation()

  if (!examples?.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-lg bg-emerald-100 dark:bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">📝</span>
        </div>
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
          {t("lesson_examples_label")}
        </h2>
      </div>

      <div className="space-y-3">
        {examples.map((ex, i) => (
          <div
            key={i}
            className="group bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-3.5 hover:border-emerald-300 dark:hover:border-emerald-500/40 transition-colors"
          >
            {/* Index + sentence */}
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 text-[10px] font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0 space-y-1.5">
                <p className="text-sm sm:text-base font-medium text-slate-800 dark:text-gray-100 leading-relaxed">
                  {ex.sentence}
                </p>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-gray-400 leading-relaxed">
                  {ex.translation}
                </p>
                {ex.note && (
                  <p className="text-xs text-indigo-600 dark:text-indigo-400 italic">
                    {t("lesson_note_label")}: {ex.note}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
