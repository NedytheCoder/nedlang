"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { TOTAL_STEPS } from "./types"

const STEP_KEYS = [
  "onb_step_account",
  "onb_step_language",
  "onb_step_motivation",
  "onb_step_interests",
  "onb_step_preferences",
  "onb_step_summary",
]

export default function ProgressBar({ currentStep }: { currentStep: number }) {
  const { t } = useTranslation()
  const progress = ((currentStep + 1) / TOTAL_STEPS) * 100

  return (
    <div className="mb-7">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-500 dark:text-gray-400">
          {t("onb_step_label")} {currentStep + 1} {t("onb_of")} {TOTAL_STEPS}
        </span>
        <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
          {t(STEP_KEYS[currentStep])}
        </span>
      </div>
      <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
          initial={false}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>
      <div className="hidden sm:flex justify-between mt-2 px-0.5">
        {STEP_KEYS.map((_, i) => (
          <motion.div
            key={i}
            className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
              i <= currentStep ? "bg-indigo-500" : "bg-slate-200 dark:bg-slate-600"
            }`}
            animate={{ scale: i === currentStep ? 1.3 : 1 }}
            transition={{ duration: 0.2 }}
          />
        ))}
      </div>
    </div>
  )
}
