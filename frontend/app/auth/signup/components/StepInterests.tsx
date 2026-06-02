"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps } from "./types"

const PRESET_HOBBIES = [
  "Football", "Gaming", "Anime", "Cooking", "Fitness",
  "Reading", "Technology", "Music", "Photography",
  "Business", "Travel", "Movies",
]

const MAX = 3

export default function StepInterests({ data, onChange, errors }: StepProps) {
  const { t } = useTranslation()
  const [query, setQuery] = useState("")

  const selected = data.top_hobbies
  const canAdd = selected.length < MAX
  const isSelected = (h: string) => selected.includes(h)

  const toggle = (hobby: string) => {
    if (isSelected(hobby)) {
      onChange({ top_hobbies: selected.filter((h) => h !== hobby) })
    } else if (canAdd) {
      onChange({ top_hobbies: [...selected, hobby] })
    }
  }

  const addCustom = () => {
    const trimmed = query.trim()
    if (!trimmed || isSelected(trimmed) || !canAdd) return
    onChange({ top_hobbies: [...selected, trimmed] })
    setQuery("")
  }

  const filteredPresets = PRESET_HOBBIES.filter(
    (h) => h.toLowerCase().includes(query.toLowerCase()) && !PRESET_HOBBIES.includes(query)
  )

  const showAddButton =
    query.trim().length > 0 && !isSelected(query.trim()) && canAdd

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_interests_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_interests_subtitle")}</p>
      </div>

      <div className="bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-xl p-4">
        <p className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed">{t("onb_interests_note")}</p>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-500 dark:text-gray-400">
          {selected.length} / {MAX} {t("onb_interests_selected")}
        </p>
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-colors duration-200 ${
                i < selected.length ? "bg-indigo-500" : "bg-slate-200 dark:bg-slate-600"
              }`}
            />
          ))}
        </div>
      </div>

      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <AnimatePresence>
            {selected.map((hobby) => (
              <motion.button
                key={hobby}
                type="button"
                onClick={() => toggle(hobby)}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.15 }}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-indigo-600 text-white rounded-full shadow-sm shadow-indigo-500/20"
              >
                {hobby}
                <svg className="w-3 h-3 opacity-80" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      )}

      {errors.top_hobbies && <p className="text-xs text-red-500">{errors.top_hobbies}</p>}

      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustom())}
          placeholder={t("onb_interests_search")}
          className="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all"
        />
        {showAddButton && (
          <motion.button
            type="button"
            onClick={addCustom}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="px-4 py-2.5 text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-colors"
          >
            {t("onb_interests_add")}
          </motion.button>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {filteredPresets.map((hobby) => {
          const sel = isSelected(hobby)
          const disabled = !sel && !canAdd
          return (
            <button
              key={hobby}
              type="button"
              onClick={() => toggle(hobby)}
              disabled={disabled}
              className={`px-3 py-1.5 text-xs rounded-full border transition-all ${
                sel
                  ? "bg-indigo-600 border-indigo-600 text-white"
                  : disabled
                  ? "bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-white/8 text-slate-300 dark:text-gray-600 cursor-not-allowed"
                  : "bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-white/10 text-slate-600 dark:text-gray-400 hover:border-indigo-300 dark:hover:border-indigo-500/40 hover:text-indigo-700 dark:hover:text-indigo-300"
              }`}
            >
              {hobby}
            </button>
          )
        })}
      </div>
    </div>
  )
}
