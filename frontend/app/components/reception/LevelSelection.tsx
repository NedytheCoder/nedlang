"use client"

import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { FrameworkInfo } from "./frameworkUtils"

export type StartMode = "placement" | "manual"

interface Props {
  framework: FrameworkInfo
  mode: StartMode
  selectedLevel: string | null
  onModeChange: (m: StartMode) => void
  onLevelChange: (lvl: string) => void
}

export default function LevelSelection({ framework, mode, selectedLevel, onModeChange, onLevelChange }: Props) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t("rec_level_title")}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

        {/* Option A — Placement test */}
        <button
          type="button"
          onClick={() => onModeChange("placement")}
          className={`relative text-left rounded-2xl border-2 p-5 transition-all ${
            mode === "placement"
              ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10 shadow-md shadow-emerald-500/10"
              : "border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-white/20"
          }`}
        >
          {/* Recommended badge */}
          <span className="absolute top-4 right-4 px-2.5 py-0.5 bg-emerald-500 text-white text-[10px] font-bold rounded-full uppercase tracking-wide">
            {t("rec_level_placement_badge")}
          </span>

          <div className="flex items-center gap-2 mb-3">
            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
              mode === "placement" ? "border-emerald-500 bg-emerald-500" : "border-slate-300 dark:border-slate-600"
            }`}>
              {mode === "placement" && (
                <motion.svg initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </motion.svg>
              )}
            </div>
            <span className="text-base font-bold text-slate-900 dark:text-white">{t("rec_level_placement_title")}</span>
          </div>
          <p className="text-sm text-slate-600 dark:text-gray-400 mb-4 leading-relaxed pr-16">{t("rec_level_placement_desc")}</p>
          <ul className="space-y-1.5">
            {["rec_level_placement_b1", "rec_level_placement_b2", "rec_level_placement_b3"].map((key) => (
              <li key={key} className="flex items-center gap-2 text-xs text-slate-600 dark:text-gray-400">
                <span className="text-emerald-500 font-bold">✓</span>
                {t(key)}
              </li>
            ))}
          </ul>
        </button>

        {/* Option B — Manual */}
        <div>
          <button
            type="button"
            onClick={() => onModeChange("manual")}
            className={`w-full text-left rounded-2xl border-2 p-5 transition-all ${
              mode === "manual"
                ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10 shadow-md shadow-indigo-500/10"
                : "border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-white/20"
            }`}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                mode === "manual" ? "border-indigo-500 bg-indigo-500" : "border-slate-300 dark:border-slate-600"
              }`}>
                {mode === "manual" && (
                  <motion.svg initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </motion.svg>
                )}
              </div>
              <span className="text-base font-bold text-slate-900 dark:text-white">{t("rec_level_manual_title")}</span>
            </div>
            <p className="text-sm text-slate-600 dark:text-gray-400 leading-relaxed">{t("rec_level_manual_desc")}</p>
          </button>

          {/* Level picker — expands when manual is selected */}
          <AnimatePresence>
            {mode === "manual" && (
              <motion.div
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: "auto", marginTop: 12 }}
                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                transition={{ duration: 0.25 }}
                className="overflow-hidden"
              >
                <p className="text-xs font-medium text-slate-500 dark:text-gray-400 mb-2">{t("rec_level_select_prompt")}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {framework.levels.map((lvl) => (
                    <motion.button
                      key={lvl}
                      type="button"
                      onClick={() => onLevelChange(lvl)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`px-4 py-2 text-sm font-semibold rounded-xl border-2 transition-all ${
                        selectedLevel === lvl
                          ? "border-indigo-500 bg-indigo-600 text-white shadow-md shadow-indigo-500/25"
                          : "border-slate-200 dark:border-white/10 text-slate-600 dark:text-gray-400 hover:border-indigo-300 dark:hover:border-indigo-500/40"
                      }`}
                    >
                      {lvl}
                    </motion.button>
                  ))}
                </div>
                {/* Warning */}
                <div className="flex gap-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/25 rounded-xl p-3">
                  <span className="text-sm flex-shrink-0">⚠️</span>
                  <p className="text-xs text-amber-700 dark:text-amber-300 leading-relaxed">{t("rec_level_manual_warning")}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}
