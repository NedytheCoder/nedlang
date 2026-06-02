"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockErrors } from "./mockData"

type Tab = "vocab" | "grammar" | "structure" | "skills"

const TABS: { key: Tab; labelKey: string; icon: string }[] = [
  { key: "vocab", labelKey: "dash_error_vocab", icon: "📚" },
  { key: "grammar", labelKey: "dash_error_grammar", icon: "📝" },
  { key: "structure", labelKey: "dash_error_structure", icon: "🔗" },
  { key: "skills", labelKey: "dash_error_skills", icon: "🎯" },
]

const SKILL_KEYS: Record<string, string> = {
  reading: "dash_error_reading",
  listening: "dash_error_listening",
  speaking: "dash_error_speaking",
  writing: "dash_error_writing",
}

export default function ErrorAnalysis() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<Tab>("vocab")

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-base">🔍</span>
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_error_title")}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
        {TABS.map(({ key, labelKey, icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex-1 flex items-center justify-center gap-1 py-1.5 text-xs font-medium rounded-lg transition-all ${
              tab === key
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-gray-500 hover:text-slate-700 dark:hover:text-gray-300"
            }`}
          >
            <span className="hidden sm:inline">{icon}</span>
            <span className="truncate">{t(labelKey)}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          transition={{ duration: 0.15 }}
        >
          {tab === "vocab" && (
            <div className="space-y-2">
              {mockErrors.vocabulary.map((e, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium text-slate-900 dark:text-white">{e.word}</span>
                    <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400">
                      {t(e.typeKey)}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 flex-shrink-0">{e.count}× {t("dash_error_times")}</span>
                </div>
              ))}
            </div>
          )}

          {tab === "grammar" && (
            <div className="space-y-2">
              {mockErrors.grammar.map((e, i) => {
                const maxCount = Math.max(...mockErrors.grammar.map((x) => x.count))
                return (
                  <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-slate-700 dark:text-gray-300 truncate">{e.topic}</p>
                      <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full mt-1.5 overflow-hidden">
                        <div className="h-full bg-red-400 rounded-full" style={{ width: `${(e.count / maxCount) * 100}%` }} />
                      </div>
                    </div>
                    <span className="text-xs font-semibold text-red-500 flex-shrink-0">{e.count}</span>
                  </div>
                )
              })}
            </div>
          )}

          {tab === "structure" && (
            <div className="space-y-2">
              {mockErrors.sentenceStructure.map((e, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-xl">
                  <div className="flex-1">
                    <p className="text-xs font-medium text-slate-700 dark:text-gray-300">{e.pattern}</p>
                  </div>
                  <span className="text-xs font-semibold text-amber-500 flex-shrink-0">{e.count}× {t("dash_error_times")}</span>
                </div>
              ))}
            </div>
          )}

          {tab === "skills" && (
            <div className="grid grid-cols-1 gap-3">
              {(["reading", "listening", "speaking", "writing"] as const).map((skill) => (
                <div key={skill}>
                  <p className="text-xs font-semibold text-slate-700 dark:text-gray-300 mb-1.5 capitalize">
                    {t(SKILL_KEYS[skill])}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {mockErrors.skills[skill].map((w) => (
                      <span key={w} className="px-2 py-1 text-xs bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300 rounded-lg border border-amber-100 dark:border-amber-500/20">
                        {w}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
