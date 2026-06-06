"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../i18n/LanguageProvider"
import { getFramework, FRAMEWORK_DATA } from "../components/reception/frameworkUtils"
import { ReceptionUser } from "../components/reception/receptionMockData"
import WelcomeHero from "../components/reception/WelcomeHero"
import FrameworkCard from "../components/reception/FrameworkCard"
import LevelSelection, { StartMode } from "../components/reception/LevelSelection"
import WhatsNext from "../components/reception/WhatsNext"
import PersonalizationProfile from "../components/reception/PersonalizationProfile"
import { GiEarthAfricaEurope } from "react-icons/gi"

const FLAG_MAP: Record<string, string> = {
  ar: "🇸🇦", zh: "🇨🇳", nl: "🇳🇱", en: "🇬🇧",
  fr: "🇫🇷", de: "🇩🇪", hi: "🇮🇳", it: "🇮🇹",
  ja: "🇯🇵", ko: "🇰🇷", pt: "🇵🇹", ru: "🇷🇺",
  es: "🇪🇸", tr: "🇹🇷", vi: "🇻🇳", pl: "🇵🇱",
}

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function ReceptionPage() {
  const { t, lang } = useTranslation()
  const router = useRouter()
  const [mode, setMode] = useState<StartMode>("placement")
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null)
  const [user, setUser] = useState<ReceptionUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    const uiLang = localStorage.getItem("fc_ui_lang") || "en"
    if (!userId) {
      router.replace("/auth/signup")
      return
    }
    fetch(`${BACKEND_URL}/user/profile/${userId}?ui_lang=${uiLang}`)
      .then((r) => {
        if (!r.ok) throw new Error("Profile not found")
        return r.json()
      })
      .then((data) => {
        setUser({
          ...data,
          nativeLanguage: { ...data.nativeLanguage, name: data.nativeLanguage.localizedName ?? data.nativeLanguage.name, flag: FLAG_MAP[data.nativeLanguage.code] ?? "🌐" },
          targetLanguage: { ...data.targetLanguage, name: data.targetLanguage.localizedName ?? data.targetLanguage.name, flag: FLAG_MAP[data.targetLanguage.code] ?? "🌐" },
        })
      })
      .catch(() => router.replace("/auth/signup"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!user) return null

  const frameworkId = getFramework(user.targetLanguage.code)
  const framework = FRAMEWORK_DATA[frameworkId]

  const canStartImmediately = mode === "manual" && selectedLevel !== null

  const handleManualStart = async () => {
    if (!selectedLevel) return
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) return
    setSaving(true)
    try {
      await fetch(`${BACKEND_URL}/user/${userId}/level`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: selectedLevel }),
      })
    } finally {
      setSaving(false)
      router.push("/dashboard")
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Background decoration */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-indigo-500/5 dark:bg-indigo-500/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-violet-500/5 dark:bg-violet-500/8 rounded-full blur-3xl" />
      </div>

      {/* Minimal nav */}
      <header className="relative z-10 border-b border-slate-200 dark:border-white/8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-sm">
              <GiEarthAfricaEurope className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-slate-900 dark:text-white text-base tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
              NedLang
            </span>
          </Link>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-xs text-slate-500 dark:text-gray-400">{t("rec_nav_status")}</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* 1 — Welcome hero */}
        <WelcomeHero user={user} />

        {/* 2 — Framework card */}
        <FrameworkCard framework={framework} />

        {/* 3 — Level selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-7"
        >
          <LevelSelection
            framework={framework}
            mode={mode}
            selectedLevel={selectedLevel}
            onModeChange={(m) => {
              setMode(m)
              if (m === "placement") setSelectedLevel(null)
            }}
            onLevelChange={setSelectedLevel}
          />
        </motion.div>

        {/* 4 — What happens next */}
        <WhatsNext />

        {/* 5 — Personalization profile */}
        <PersonalizationProfile user={user} />

        {/* 6 — CTA section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65 }}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-7"
        >
          <div className="space-y-3">
            {/* Primary — always shown */}
            <motion.button
              whileHover={{ scale: 1.015 }}
              whileTap={{ scale: 0.985 }}
              onClick={() => router.push("/reception/reading")}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/35 transition-all text-base"
            >
              🎯 {t("rec_cta_primary")}
            </motion.button>

            {/* Divider */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-slate-200 dark:bg-white/8" />
              <span className="text-xs text-slate-400 dark:text-gray-500">{t("rec_cta_or")}</span>
              <div className="flex-1 h-px bg-slate-200 dark:bg-white/8" />
            </div>

            {/* Secondary — only active when manual level chosen */}
            <div>
              <motion.button
                whileHover={canStartImmediately ? { scale: 1.015 } : {}}
                whileTap={canStartImmediately ? { scale: 0.985 } : {}}
                disabled={!canStartImmediately || saving}
                onClick={handleManualStart}
                className={`w-full py-3.5 rounded-xl font-semibold border-2 transition-all text-sm ${
                  canStartImmediately
                    ? "border-indigo-500 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-500/10"
                    : "border-slate-200 dark:border-white/8 text-slate-400 dark:text-gray-600 cursor-not-allowed"
                }`}
              >
                {saving ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin" />
                    {t("rec_cta_secondary")}
                  </span>
                ) : canStartImmediately ? (
                  <>▶ {t("rec_cta_secondary")} — {selectedLevel}</>
                ) : (
                  t("rec_cta_secondary")
                )}
              </motion.button>
              <AnimatePresence>
                {!canStartImmediately && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-xs text-slate-400 dark:text-gray-500 text-center mt-1.5"
                  >
                    {t("rec_cta_secondary_note")}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
          </div>
        </motion.div>

        <p className="text-center pb-6">
          <Link href="/dashboard" className="text-xs text-slate-400 dark:text-gray-500 hover:text-slate-600 dark:hover:text-gray-300 transition-colors">
            {t("rec_nav_skip")} →
          </Link>
        </p>
      </main>
    </div>
  )
}
