"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockCertification } from "./mockData"

export default function CertificationProgress() {
  const { t } = useTranslation()
  const { name, targetExam, readiness, estimatedReadyDate, strongest, weakest } = mockCertification

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <span className="text-base">🏅</span>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_cert_title")}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500 dark:text-gray-400">{t("dash_cert_target")}</p>
          <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">{targetExam}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Readiness circle */}
        <div className="flex flex-col items-center gap-2">
          <div className="relative w-28 h-28">
            <svg className="w-28 h-28 -rotate-90" viewBox="0 0 112 112">
              <circle cx="56" cy="56" r="46" fill="none" stroke="currentColor" strokeWidth="8" className="text-slate-100 dark:text-slate-800" />
              <motion.circle
                cx="56" cy="56" r="46"
                fill="none"
                stroke="url(#certGrad)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 46}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 46 }}
                animate={{ strokeDashoffset: 2 * Math.PI * 46 * (1 - readiness / 100) }}
                transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
              />
              <defs>
                <linearGradient id="certGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="rgb(99,102,241)" />
                  <stop offset="100%" stopColor="rgb(139,92,246)" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{readiness}%</span>
              <span className="text-xs text-slate-500 dark:text-gray-400">{t("dash_cert_readiness")}</span>
            </div>
          </div>
          <p className="text-xs text-slate-500 dark:text-gray-400 text-center">
            {t("dash_cert_est_ready")}: <span className="font-semibold text-slate-700 dark:text-gray-300">{estimatedReadyDate}</span>
          </p>
        </div>

        {/* Strongest areas */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide">{t("dash_cert_strongest")}</p>
          </div>
          <div className="space-y-2">
            {strongest.map((area) => (
              <div key={area} className="flex items-center gap-2 p-2.5 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-100 dark:border-emerald-500/20 rounded-xl">
                <span className="text-emerald-500 text-sm">✓</span>
                <span className="text-xs text-emerald-700 dark:text-emerald-300 font-medium">{area}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weakest areas */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide">{t("dash_cert_weakest")}</p>
          </div>
          <div className="space-y-2">
            {weakest.map((area) => (
              <div key={area} className="flex items-center gap-2 p-2.5 bg-amber-50 dark:bg-amber-500/10 border border-amber-100 dark:border-amber-500/20 rounded-xl">
                <span className="text-amber-500 text-sm">↗</span>
                <span className="text-xs text-amber-700 dark:text-amber-300 font-medium">{area}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
