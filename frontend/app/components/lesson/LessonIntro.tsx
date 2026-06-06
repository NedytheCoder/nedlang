"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  introduction: string
}

export default function LessonIntro({ introduction }: Props) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.05, ease: "easeOut" }}
      className="bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-start gap-3.5">
        <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/25 mt-0.5">
          <span className="text-base">👋</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-1.5">
            {t("lesson_intro_label")}
          </p>
          <p className="text-sm sm:text-base text-slate-700 dark:text-gray-200 leading-relaxed">
            {introduction}
          </p>
        </div>
      </div>
    </motion.div>
  )
}
