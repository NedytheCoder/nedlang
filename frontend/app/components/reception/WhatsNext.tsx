"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

const STEPS = [
  { icon: "📊", titleKey: "rec_next_1_title", descKey: "rec_next_1_desc", color: "from-blue-400 to-indigo-500" },
  { icon: "🤖", titleKey: "rec_next_2_title", descKey: "rec_next_2_desc", color: "from-violet-400 to-purple-500" },
  { icon: "✨", titleKey: "rec_next_3_title", descKey: "rec_next_3_desc", color: "from-purple-400 to-pink-500" },
  { icon: "🚀", titleKey: "rec_next_4_title", descKey: "rec_next_4_desc", color: "from-pink-400 to-rose-500" },
]

export default function WhatsNext() {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.45 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-7"
    >
      <div className="mb-6">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">{t("rec_next_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400 mt-1">{t("rec_next_subtitle")}</p>
      </div>

      <div className="relative">
        {/* Connecting line — desktop only */}
        <div className="hidden sm:block absolute top-7 left-7 right-7 h-0.5 border-t-2 border-dashed border-slate-200 dark:border-slate-700" />

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-5">
          {STEPS.map(({ icon, titleKey, descKey, color }, i) => (
            <motion.div
              key={titleKey}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
              className="relative flex sm:flex-col gap-4 sm:gap-0"
            >
              {/* Icon circle */}
              <div className="flex-shrink-0">
                <div className={`relative z-10 w-14 h-14 rounded-2xl bg-gradient-to-br ${color} flex items-center justify-center shadow-lg`}>
                  <span className="text-2xl">{icon}</span>
                </div>
              </div>

              <div className="sm:mt-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-slate-400 dark:text-gray-500">0{i + 1}</span>
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{t(titleKey)}</h3>
                </div>
                <p className="text-xs text-slate-500 dark:text-gray-400 leading-relaxed">{t(descKey)}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
