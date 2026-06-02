"use client"

import { motion } from "framer-motion"
import { FaBolt } from "react-icons/fa"
import { useTranslation } from "../i18n/LanguageProvider"

export default function Loading() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center gap-6">
      <motion.div
        className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-xl shadow-indigo-500/30"
        animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      >
        <FaBolt className="w-6 h-6 text-white" />
      </motion.div>
      <motion.p className="text-sm text-slate-600 dark:text-gray-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        {t("loading_message")}
      </motion.p>
    </div>
  )
}
