"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import LessonContainer from "../../components/lesson/LessonContainer"
import type { Lesson } from "../../components/lesson/types"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchLesson(slug: string, userId: string, uiLang: string): Promise<Lesson> {
  const res = await fetch(
    `${BACKEND_URL}/lesson/${encodeURIComponent(slug)}?user_id=${encodeURIComponent(userId)}&ui_lang=${encodeURIComponent(uiLang)}`
  )
  if (!res.ok) throw new Error(`Failed to load lesson: ${res.status}`)
  return res.json()
}

function SkeletonBlock({ lines = 3, tall = false }: { lines?: number; tall?: boolean }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      {/* Header row */}
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-800 animate-pulse" />
        <div className="h-3 w-32 bg-slate-100 dark:bg-slate-800 rounded-full animate-pulse" />
      </div>
      {/* Content lines */}
      <div className="space-y-2.5">
        {Array.from({ length: lines }, (_, i) => (
          <div
            key={i}
            className={`bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse ${tall ? "h-14" : "h-3.5"}`}
            style={{ width: i === lines - 1 ? "65%" : "100%", animationDelay: `${i * 80}ms` }}
          />
        ))}
      </div>
    </div>
  )
}

function LessonSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
      {/* Header skeleton */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-3 w-24 bg-slate-100 dark:bg-slate-800 rounded-full animate-pulse" />
          <div className="h-5 w-14 bg-slate-100 dark:bg-slate-800 rounded-full animate-pulse" />
          <div className="h-5 w-20 bg-slate-100 dark:bg-slate-800 rounded-full animate-pulse" />
        </div>
        <div className="h-7 w-3/4 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse mb-5" />
        <div className="flex gap-1.5">
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className="h-1.5 flex-1 rounded-full bg-slate-100 dark:bg-slate-800 animate-pulse" style={{ animationDelay: `${i * 60}ms` }} />
          ))}
        </div>
      </div>
      {/* Intro skeleton */}
      <div className="bg-indigo-50/60 dark:bg-indigo-500/5 border border-indigo-100 dark:border-indigo-500/20 rounded-2xl p-5 sm:p-6">
        <div className="flex gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-indigo-100 dark:bg-indigo-500/20 animate-pulse flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-2.5 w-20 bg-indigo-100 dark:bg-indigo-500/20 rounded-full animate-pulse" />
            <div className="h-3.5 w-full bg-indigo-100 dark:bg-indigo-500/20 rounded-full animate-pulse" />
            <div className="h-3.5 w-4/5 bg-indigo-100 dark:bg-indigo-500/20 rounded-full animate-pulse" />
          </div>
        </div>
      </div>
      {/* Content skeletons */}
      <SkeletonBlock lines={4} />
      <SkeletonBlock lines={3} tall />
      <SkeletonBlock lines={3} />
      <SkeletonBlock lines={2} tall />
    </div>
  )
}

export default function LessonPage() {
  const params = useParams()
  const router = useRouter()
  const { t } = useTranslation()
  const slug = params?.slug as string

  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return

    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) {
      router.replace("/auth/signup")
      return
    }

    const uiLang = localStorage.getItem("fc_ui_lang") || "en"

    fetchLesson(slug, userId, uiLang)
      .then(setLesson)
      .catch(() => setError("not_found"))
      .finally(() => setLoading(false))
  }, [slug])

  /* ── Spinner while redirecting (no userId) ── */
  if (!slug) return null

  /* ── Loading skeleton ── */
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        {/* Minimal nav */}
        <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-white/8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/30">
                <GiEarthAfricaEurope className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight">NedLang</span>
            </div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.4, ease: "linear" }}
              className="w-6 h-6 rounded-full border-2 border-indigo-200 dark:border-indigo-900 border-t-indigo-600"
            />
          </div>
        </header>
        <LessonSkeleton />
      </div>
    )
  }

  /* ── Error state ── */
  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-8 sm:p-10 max-w-md w-full text-center shadow-xl"
        >
          <div className="w-14 h-14 rounded-2xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">📚</span>
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
            {t("lesson_error_title")}
          </h2>
          <p className="text-sm text-slate-500 dark:text-gray-400 mb-6">
            {t("lesson_error_body")}
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t("lesson_error_back")}
          </Link>
        </motion.div>
      </div>
    )
  }

  /* ── Lesson page ── */
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Minimal nav */}
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-white/8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
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
            className="flex items-center gap-1.5 text-sm font-medium text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t("dash_nav_dashboard")}
          </Link>
        </div>
      </header>

      <main>
        <LessonContainer lesson={lesson} />
      </main>
    </div>
  )
}
