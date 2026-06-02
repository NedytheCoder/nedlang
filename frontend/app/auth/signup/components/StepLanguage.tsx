"use client"

import { useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps } from "./types"
import { LANGUAGES, getLangByCode } from "./languages"

interface ComboboxProps {
  value: string
  onChange: (code: string) => void
  placeholder: string
  error?: string
  excludeCode?: string
  label: string
  description: string
}

function LanguageCombobox({ value, onChange, placeholder, error, excludeCode, label, description }: ComboboxProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = LANGUAGES.filter(
    (l) =>
      l.code !== excludeCode &&
      (l.name.toLowerCase().includes(query.toLowerCase()) ||
        l.nativeName.toLowerCase().includes(query.toLowerCase()))
  )

  const selected = getLangByCode(value)

  const handleSelect = (code: string) => {
    onChange(code)
    setOpen(false)
    setQuery("")
  }

  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1">{label}</label>
      <p className="text-xs text-slate-500 dark:text-gray-500 mb-2">{description}</p>
      <div className="relative">
        {open && (
          <div className="fixed inset-0 z-10" onClick={() => { setOpen(false); setQuery("") }} />
        )}

        <button
          type="button"
          onClick={() => { setOpen(true); setTimeout(() => inputRef.current?.focus(), 50) }}
          className={`w-full flex items-center gap-2 px-4 py-2.5 text-sm rounded-xl border transition-all text-left ${
            error
              ? "border-red-400 dark:border-red-500"
              : "border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20"
          } bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white`}
        >
          {selected ? (
            <>
              <span className="text-base">{selected.flag}</span>
              <span className="flex-1">{selected.name}</span>
              <span className="text-xs text-slate-400 dark:text-gray-500">{selected.nativeName}</span>
            </>
          ) : (
            <span className="text-slate-400 dark:text-gray-500 flex-1">{placeholder}</span>
          )}
          <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.15 }}
              className="absolute z-20 top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl shadow-xl overflow-hidden"
            >
              <div className="p-2 border-b border-slate-100 dark:border-white/8">
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search..."
                  className="w-full bg-slate-50 dark:bg-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
                />
              </div>
              <div className="max-h-44 overflow-y-auto">
                {filtered.length === 0 ? (
                  <div className="px-4 py-3 text-sm text-slate-400 dark:text-gray-500 text-center">No results</div>
                ) : (
                  filtered.map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => handleSelect(lang.code)}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left hover:bg-indigo-50 dark:hover:bg-indigo-500/10 transition-colors ${
                        lang.code === value ? "bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300" : "text-slate-700 dark:text-gray-300"
                      }`}
                    >
                      <span className="text-base">{lang.flag}</span>
                      <span className="flex-1 font-medium">{lang.name}</span>
                      <span className="text-xs text-slate-400 dark:text-gray-500">{lang.nativeName}</span>
                    </button>
                  ))
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  )
}

const PREVIEW_PAIRS = [
  { native: "de", target: "es" },
  { native: "en", target: "ja" },
  { native: "fr", target: "zh" },
]

export default function StepLanguage({ data, onChange, errors }: StepProps) {
  const { t } = useTranslation()

  const nativeLang = getLangByCode(data.native_language)
  const targetLang = getLangByCode(data.target_language)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_lang_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_lang_subtitle")}</p>
      </div>

      <LanguageCombobox
        value={data.native_language}
        onChange={(code) => onChange({ native_language: code })}
        placeholder={t("onb_lang_select")}
        error={errors.native_language}
        excludeCode={data.target_language}
        label={t("onb_native_label")}
        description={t("onb_native_desc")}
      />

      <LanguageCombobox
        value={data.target_language}
        onChange={(code) => onChange({ target_language: code })}
        placeholder={t("onb_lang_select")}
        error={errors.target_language}
        excludeCode={data.native_language}
        label={t("onb_target_label")}
        description={t("onb_target_desc")}
      />

      {nativeLang && targetLang ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-xl p-4"
        >
          <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400 mb-2">{t("onb_lang_preview_label")}</p>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{nativeLang.flag}</span>
            <div className="flex-1">
              <p className="text-sm font-semibold text-slate-900 dark:text-white">
                {nativeLang.name} <span className="text-slate-400 dark:text-gray-500 font-normal">{t("onb_lang_speaker")}</span> {targetLang.name}
              </p>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
                {nativeLang.nativeName} → {targetLang.nativeName}
              </p>
            </div>
            <span className="text-2xl">{targetLang.flag}</span>
          </div>
        </motion.div>
      ) : (
        <div className="border border-dashed border-slate-200 dark:border-slate-700 rounded-xl p-4">
          <p className="text-xs text-slate-400 dark:text-gray-500 text-center mb-3">{t("onb_lang_preview_label")}</p>
          <div className="space-y-1.5">
            {PREVIEW_PAIRS.map(({ native, target }) => {
              const n = getLangByCode(native)!
              const tg = getLangByCode(target)!
              return (
                <p key={`${native}-${target}`} className="text-xs text-center text-slate-400 dark:text-gray-500">
                  {n.flag} {n.name} → {tg.flag} {tg.name}
                </p>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
