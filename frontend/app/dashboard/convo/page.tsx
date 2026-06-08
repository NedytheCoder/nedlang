"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface SessionInfo {
  level: string
  target_language: string
  native_language: string
}

const BEGINNER_LEVELS = ["A1", "A2"]

export default function ConvoSelectorPage() {
  const router = useRouter()
  const { t }  = useTranslation()

  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null)

  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) { router.replace("/auth/signup"); return }

    fetch(`${BACKEND_URL}/convo/session?user_id=${encodeURIComponent(userId)}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json() })
      .then(setSessionInfo)
      .catch(() => {})
  }, [])

  const recommendChat = sessionInfo ? BEGINNER_LEVELS.includes(sessionInfo.level) : false
  const recommendCall = sessionInfo ? !BEGINNER_LEVELS.includes(sessionInfo.level) : false

  const cards = [
    {
      id:         "chat",
      href:       "/dashboard/convo/chat",
      recommended: recommendChat,
      gradient:   "from-emerald-500 to-teal-600",
      shadowColor:"shadow-emerald-500/20",
      ringColor:  "ring-emerald-500/40",
      badgeColor: "bg-emerald-100 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
      ctaClass:   "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/30",
      diffColor:  "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-gray-400",
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      titleKey:    "convo_chat_title",
      subtitleKey: "convo_chat_subtitle",
      features:    ["convo_chat_f1", "convo_chat_f2", "convo_chat_f3", "convo_chat_f4"],
      diffKey:     "convo_chat_difficulty",
      bestForKey:  "convo_chat_best_for",
      ctaKey:      "convo_chat_cta",
    },
    {
      id:         "call",
      href:       "/dashboard/convo/call",
      recommended: recommendCall,
      gradient:   "from-indigo-500 to-violet-600",
      shadowColor:"shadow-indigo-500/20",
      ringColor:  "ring-indigo-500/40",
      badgeColor: "bg-indigo-100 dark:bg-indigo-500/15 text-indigo-700 dark:text-indigo-300",
      ctaClass:   "bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/30",
      diffColor:  "bg-amber-100 dark:bg-amber-500/15 text-amber-700 dark:text-amber-400",
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
      ),
      titleKey:    "convo_call_title",
      subtitleKey: "convo_call_subtitle",
      features:    ["convo_call_f1", "convo_call_f2", "convo_call_f3", "convo_call_f4"],
      diffKey:     "convo_call_difficulty",
      bestForKey:  "convo_call_best_for",
      ctaKey:      "convo_call_cta",
    },
  ]

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-white/8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/30">
                <GiEarthAfricaEurope className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                NedLang
              </span>
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 text-sm font-medium text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              {t("convo_back")}
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12 flex flex-col gap-8">

        {/* Hero */}
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {sessionInfo && (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 text-xs font-medium text-indigo-600 dark:text-indigo-400 mb-4">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                {sessionInfo.target_language} · {t("convo_level_label")} {sessionInfo.level}
              </div>
            )}
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {t("convo_select_title")}
            </h1>
            <p className="text-sm sm:text-base text-slate-500 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
              {t("convo_select_subtitle")}
            </p>
          </motion.div>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
          {cards.map((card, i) => (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.08 }}
              whileHover={{ y: -3 }}
              className={`relative bg-white dark:bg-slate-900 border rounded-2xl flex flex-col overflow-hidden transition-shadow duration-200 ${
                card.recommended
                  ? `border-transparent ring-2 ${card.ringColor} shadow-xl ${card.shadowColor}`
                  : "border-slate-200 dark:border-white/8 shadow-sm hover:shadow-lg"
              }`}
            >
              {/* Recommended badge */}
              {card.recommended && (
                <div className={`absolute top-4 right-4 px-2.5 py-1 rounded-full text-xs font-semibold ${card.badgeColor}`}>
                  {t("convo_select_recommended")}
                </div>
              )}

              {/* Card top — gradient icon area */}
              <div className={`bg-gradient-to-br ${card.gradient} px-6 py-6 flex items-start gap-4`}>
                <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center flex-shrink-0 shadow-sm">
                  {card.icon}
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white leading-tight">{t(card.titleKey)}</h2>
                  <p className="text-sm text-white/75 mt-0.5">{t(card.subtitleKey)}</p>
                </div>
              </div>

              {/* Card body */}
              <div className="flex flex-col flex-1 p-6 gap-5">

                {/* Feature list */}
                <ul className="space-y-2.5 flex-1">
                  {card.features.map(key => (
                    <li key={key} className="flex items-start gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <svg className="w-3 h-3 text-slate-500 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                        </svg>
                      </span>
                      <span className="text-sm text-slate-600 dark:text-gray-300 leading-snug">{t(key)}</span>
                    </li>
                  ))}
                </ul>

                {/* Difficulty + best for */}
                <div className="flex flex-wrap items-center gap-2 py-4 border-t border-slate-100 dark:border-white/8">
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${card.diffColor}`}>
                    {t(card.diffKey)}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-gray-400">{t(card.bestForKey)}</span>
                </div>

                {/* CTA */}
                <Link href={card.href}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full py-3 px-5 text-sm font-semibold text-white text-center rounded-xl shadow-md transition-colors cursor-pointer ${card.ctaClass}`}
                  >
                    {t(card.ctaKey)}
                  </motion.div>
                </Link>

              </div>
            </motion.div>
          ))}
        </div>

        {/* Info note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
          className="text-center text-xs text-slate-400 dark:text-gray-500"
        >
          {t("convo_select_note")}
        </motion.p>

      </main>
    </div>
  )
}
