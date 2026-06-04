"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  current: number
  total: number
}

export default function ProgressTracker({ current, total }: Props) {
  const { t } = useTranslation()
  const pct = Math.round((current / total) * 100)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-500 dark:text-gray-400">
        <span className="font-medium">
          {t("assess_question_label")} {current} {t("assess_question_of")} {total}
        </span>
        <span>{pct}{t("assess_complete")}</span>
      </div>
      <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-indigo-500 to-violet-600 rounded-full"
          initial={false}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>
    </div>
  )
}
