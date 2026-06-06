"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  summary: string
}

export default function SummaryBlock({ summary }: Props) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4, ease: "easeOut" }}
      className="bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl p-5 sm:p-6 shadow-xl shadow-indigo-500/20"
    >
      <div className="flex items-start gap-3.5 mb-5">
        <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center mt-0.5">
          <span className="text-base">🎉</span>
        </div>
        <div>
          <p className="text-xs font-semibold text-indigo-200 uppercase tracking-wider mb-1.5">
            {t("lesson_summary_label")}
          </p>
          <p className="text-sm sm:text-base text-white leading-relaxed">
            {summary}
          </p>
        </div>
      </div>

      <Link
        href="/dashboard"
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-indigo-600 font-semibold text-sm rounded-xl hover:bg-indigo-50 transition-colors shadow-md shadow-indigo-900/20"
      >
        {t("lesson_continue")}
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
        </svg>
      </Link>
    </motion.div>
  )
}
