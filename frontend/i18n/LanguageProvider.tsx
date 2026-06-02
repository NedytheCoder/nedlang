"use client"

import React, { createContext, useContext, useEffect, useMemo, useState } from "react"
import translations from "./translations"

type Lang = "en" | "fr" | "de" | "zh"

const STORAGE_KEY = "fc_ui_lang"

type I18nContext = {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string) => string
}

const defaultLang: Lang = "en"

const I18nContext = createContext<I18nContext>({
  lang: defaultLang,
  setLang: () => {},
  t: (k: string) => k,
})

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(defaultLang)

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as Lang | null
      if (stored && Object.keys(translations).includes(stored)) {
        setLangState(stored)
        return
      }
      // fallback to navigator language if available
      const nav = typeof navigator !== "undefined" ? navigator.language : undefined
      if (nav) {
        const short = nav.split("-")[0]
        if (short === "fr" || short === "de" || short === "zh") setLangState(short as Lang)
      }
    } catch (e) {
      // ignore
    }
  }, [])

  const setLang = (l: Lang) => {
    setLangState(l)
    try {
      localStorage.setItem(STORAGE_KEY, l)
    } catch (e) {}
  }

  const t = (key: string) => {
    const dict = translations[lang] || translations[defaultLang]
    return dict[key] ?? translations[defaultLang][key] ?? key
  }

  const value = useMemo(() => ({ lang, setLang, t }), [lang])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useTranslation() {
  return useContext(I18nContext)
}

export type { Lang }
