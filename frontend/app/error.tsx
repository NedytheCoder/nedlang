"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { FaExclamationTriangle } from "react-icons/fa"
import { useTranslation } from "../i18n/LanguageProvider"

export default function Error({ reset }: { error: Error; reset: () => void }) {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center px-4 text-center">
      <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="max-w-md w-full">
        <div className="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-500/15 border border-red-200 dark:border-red-500/30 flex items-center justify-center mx-auto mb-6">
          <FaExclamationTriangle className="w-8 h-8 text-red-500 dark:text-red-400" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t("error_title")}</h1>
        <p className="text-slate-600 dark:text-gray-400 mb-8">{t("error_subtitle")}</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <motion.button onClick={reset} className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-xl text-sm shadow-lg shadow-indigo-500/20" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
            {t("error_try_again")}
          </motion.button>
          <Link href="/" className="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-white/8 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white font-medium rounded-xl text-sm transition-all text-center">
            {t("error_go_home")}
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
