"use client"

import { useEffect, useState } from "react"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps } from "./types"
import { CJK, isMotivationValid } from "./motivationUtils"

interface Motivation { label: string; localizedLabel: string }

export default function StepMotivation({ data, onChange, errors }: StepProps) {
  const { t, lang } = useTranslation()
  const [motivations, setMotivations] = useState<Motivation[]>([])
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  useEffect(() => {
    fetch(`${backendUrl}/motivations?ui_lang=${lang}`)
      .then((r) => r.json())
      .then(setMotivations)
  }, [lang])

  const selected = data.selected_motivations

  const toggleChip = (label: string) => {
    if (selected.includes(label)) {
      onChange({ selected_motivations: selected.filter((m) => m !== label) })
    } else {
      onChange({ selected_motivations: [...selected, label] })
    }
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
        <p className="text-xs font-medium text-slate-500 dark:text-gray-400 mb-2">{t("onb_motiv_examples")}</p>
        <div className="flex flex-wrap gap-2">
          {motivations.map(({ label, localizedLabel }) => {
            const isSelected = selected.includes(label)
            return (
              <button
                key={label}
                type="button"
                onClick={() => toggleChip(label)}
                className={`px-3 py-1.5 text-xs rounded-full border transition-all ${
                  isSelected
                    ? "bg-indigo-600 border-indigo-600 text-white"
                    : "bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 hover:text-indigo-700 dark:hover:text-indigo-300 border-slate-200 dark:border-white/8 hover:border-indigo-200 dark:hover:border-indigo-500/30 text-slate-600 dark:text-gray-400"
                }`}
              >
                {localizedLabel}
              </button>
            )
          })}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
          {t("onb_motiv_label")}
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
          {data.learning_goal.trim() && (
            <span className={`text-xs ml-auto ${isMotivationValid(data.learning_goal) ? "text-green-600 dark:text-green-400" : "text-slate-400 dark:text-gray-500"}`}>
              {CJK.test(data.learning_goal.trim())
                ? `${data.learning_goal.trim().length} / 5+`
                : `${data.learning_goal.trim().split(/\s+/).filter(Boolean).length} / 3+ words`}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
