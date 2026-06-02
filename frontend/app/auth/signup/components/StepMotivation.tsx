"use client"

import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps } from "./types"

const EXAMPLE_KEYS = [
  "onb_motiv_ex_career",
  "onb_motiv_ex_travel",
  "onb_motiv_ex_reloc",
  "onb_motiv_ex_study",
  "onb_motiv_ex_biz",
  "onb_motiv_ex_movies",
  "onb_motiv_ex_family",
  "onb_motiv_ex_personal",
]

export default function StepMotivation({ data, onChange, errors }: StepProps) {
  const { t } = useTranslation()

  const handleExampleClick = (text: string) => {
    const current = data.learning_goal.trim()
    const appended = current ? `${current}\n${text}` : text
    onChange({ learning_goal: appended })
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_motiv_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_motiv_subtitle")}</p>
      </div>

      <div className="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl p-4">
        <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">{t("onb_motiv_note")}</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
          {t("onb_motiv_label")} <span className="text-red-500">*</span>
        </label>
        <textarea
          rows={5}
          placeholder={t("onb_motiv_ph")}
          value={data.learning_goal}
          onChange={(e) => onChange({ learning_goal: e.target.value })}
          className={`w-full bg-slate-50 dark:bg-slate-800 border ${
            errors.learning_goal
              ? "border-red-400 dark:border-red-500 focus:ring-red-400/20"
              : "border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:ring-indigo-500/20"
          } focus:outline-none focus:ring-2 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all resize-none`}
        />
        <div className="flex items-center justify-between mt-1">
          {errors.learning_goal ? (
            <p className="text-xs text-red-500">{errors.learning_goal}</p>
          ) : (
            <span />
          )}
          <span className={`text-xs ml-auto ${data.learning_goal.trim().length >= 20 ? "text-green-600 dark:text-green-400" : "text-slate-400 dark:text-gray-500"}`}>
            {data.learning_goal.trim().length} / 20+
          </span>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-slate-500 dark:text-gray-400 mb-2">{t("onb_motiv_examples")}</p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_KEYS.map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => handleExampleClick(t(key))}
              className="px-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 hover:text-indigo-700 dark:hover:text-indigo-300 border border-slate-200 dark:border-white/8 hover:border-indigo-200 dark:hover:border-indigo-500/30 text-slate-600 dark:text-gray-400 rounded-full transition-all"
            >
              {t(key)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
