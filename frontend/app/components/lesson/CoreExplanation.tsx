"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  core_explanation: string
}

export default function CoreExplanation({ core_explanation }: Props) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-500/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">💡</span>
        </div>
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
          {t("lesson_explanation_label")}
        </h2>
      </div>

      {/* Explanation text — supports long-form paragraphs */}
      <div className="prose prose-sm dark:prose-invert max-w-none">
        {core_explanation.split("\n").filter(Boolean).map((para, i) => (
          <p
            key={i}
            className="text-sm sm:text-base text-slate-700 dark:text-gray-200 leading-relaxed mb-3 last:mb-0"
          >
            {para}
          </p>
        ))}
      </div>
    </motion.div>
  )
}
