"use client"

import { useState } from "react"

// Maps ISO 639-1 codes to BCP 47 locales for Web Speech API
const LANG_LOCALE: Record<string, string> = {
  fr: "fr-FR",
  de: "de-DE",
  zh: "zh-CN",
  en: "en-US",
  es: "es-ES",
  pt: "pt-BR",
  it: "it-IT",
  nl: "nl-NL",
  ja: "ja-JP",
  ko: "ko-KR",
  ar: "ar-SA",
  ru: "ru-RU",
}

interface Props {
  text: string
  lang?: string      // ISO 639-1 code; falls back to nedlang_target_lang in localStorage
  className?: string
}

export default function SpeakButton({ text, lang, className = "" }: Props) {
  const [speaking, setSpeaking] = useState(false)

  const speak = () => {
    if (typeof window === "undefined" || !window.speechSynthesis) return
    if (speaking) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
      return
    }
    const resolvedLang = lang || localStorage.getItem("nedlang_target_lang") || ""
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = LANG_LOCALE[resolvedLang] ?? resolvedLang
    utterance.rate = 0.9
    utterance.onstart = () => setSpeaking(true)
    utterance.onend   = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }

  return (
    <button
      type="button"
      onClick={speak}
      title={speaking ? "Stop" : "Listen"}
      className={`flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-md transition-all ${
        speaking
          ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/15"
          : "text-slate-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-500/10"
      } ${className}`}
    >
      {speaking ? (
        <svg className="w-3.5 h-3.5 animate-pulse" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="4" width="4" height="16" rx="1" />
          <rect x="14" y="4" width="4" height="16" rx="1" />
        </svg>
      ) : (
        <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
        </svg>
      )}
    </button>
  )
}
