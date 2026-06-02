"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { useTranslation } from "../i18n/LanguageProvider"

export default function NotFound() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center px-4 text-center">
      <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="max-w-md w-full">
        <motion.div
          className="text-8xl font-black bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400 bg-clip-text text-transparent mb-6 leading-none"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          404
        </motion.div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">{t("not_found_title")}</h1>
        <p className="text-slate-600 dark:text-gray-400 mb-8">{t("not_found_subtitle")}</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/">
            <motion.div className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-xl text-sm shadow-lg shadow-indigo-500/20 inline-block" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
              {t("not_found_home")}
            </motion.div>
          </Link>
          <motion.button onClick={() => window.history.back()} className="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-white/8 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white font-medium rounded-xl text-sm transition-all" whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
            {t("not_found_back")}
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}
