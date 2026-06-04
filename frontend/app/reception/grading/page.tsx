"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { getFramework } from "../../components/reception/frameworkUtils"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const MESSAGE_KEYS = [
  "assess_grading_1",
  "assess_grading_2",
  "assess_grading_3",
  "assess_grading_4",
]

type PageState = "grading" | "error"

// Track which of the 4 skills have completed grading
interface GradingStatus {
  reading:   "pending" | "done" | "failed"
  listening: "pending" | "done" | "failed"
  writing:   "pending" | "done" | "failed"
  speaking:  "pending" | "done" | "failed"
}

const SKILL_ICONS: Record<string, string> = {
  reading:   "📖",
  listening: "🎧",
  writing:   "✍️",
  speaking:  "🎤",
}

export default function GradingPage() {
  const { t } = useTranslation()
  const router = useRouter()

  const [pageState, setPageState]     = useState<PageState>("grading")
  const [msgIndex, setMsgIndex]       = useState(0)
  const [progress, setProgress]       = useState(0)
  const [status, setStatus]           = useState<GradingStatus>({
    reading: "pending", listening: "pending", writing: "pending", speaking: "pending",
  })
  const startedRef = useRef(false)

  // Rotate messages
  useEffect(() => {
    const id = setInterval(() => setMsgIndex((i) => (i + 1) % MESSAGE_KEYS.length), 2200)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    runGrading()
  }, [])

  const markDone = (skill: keyof GradingStatus, outcome: "done" | "failed") => {
    setStatus((prev) => ({ ...prev, [skill]: outcome }))
    setProgress((p) => Math.min(p + 25, 100))
  }

  async function runGrading() {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) { setPageState("error"); return }

    // ── Fetch user profile for language codes and framework ──────────────────
    let profile: { targetLanguage: { code: string }; nativeLanguage: { code: string } }
    try {
      const r = await fetch(`${BACKEND_URL}/user/profile/${userId}`)
      if (!r.ok) throw new Error()
      profile = await r.json()
    } catch {
      setPageState("error")
      return
    }

    const targetLang = profile.targetLanguage.code
    const nativeLang = profile.nativeLanguage.code
    const framework  = getFramework(targetLang)

    // ── Read all session data ────────────────────────────────────────────────
    const readingQ  = JSON.parse(sessionStorage.getItem("reading_questions")  ?? "[]")
    const readingR  = JSON.parse(sessionStorage.getItem("reading_responses")  ?? "[]")
    const listeningQ = JSON.parse(sessionStorage.getItem("listening_questions") ?? "[]")
    const listeningR = JSON.parse(sessionStorage.getItem("listening_responses") ?? "[]")
    const writingQ  = JSON.parse(sessionStorage.getItem("writing_questions")  ?? "[]")
    const writingR  = JSON.parse(sessionStorage.getItem("writing_responses")  ?? "[]")
    const speakingQ = JSON.parse(sessionStorage.getItem("speaking_questions") ?? "[]")
    const speakingR = JSON.parse(sessionStorage.getItem("speaking_responses") ?? "[]")

    // ── Fire all 4 grading calls in parallel ─────────────────────────────────
    const grade = async (
      skill: keyof GradingStatus,
      url: string,
      body: object,
    ): Promise<object | null> => {
      try {
        const r = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        })
        if (!r.ok) throw new Error()
        const data = await r.json()
        markDone(skill, "done")
        return data
      } catch {
        markDone(skill, "failed")
        return null
      }
    }

    const [readingResult, listeningResult, writingResult, speakingResult] = await Promise.all([
      grade("reading", `${BACKEND_URL}/reception/grade/reading`, {
        framework,
        questions: readingQ,
        responses: readingR,
      }),
      grade("listening", `${BACKEND_URL}/reception/grade/listening`, {
        framework,
        questions: listeningQ,
        responses: listeningR,
      }),
      grade("writing", `${BACKEND_URL}/reception/grade/writing`, {
        framework,
        target_language: targetLang,
        native_language: nativeLang,
        questions: writingQ,
        responses: writingR,
      }),
      grade("speaking", `${BACKEND_URL}/reception/grade/speaking`, {
        framework,
        target_language: targetLang,
        native_language: nativeLang,
        questions: speakingQ,
        responses: speakingR,
      }),
    ])

    // All 4 failed — show error
    if (!readingResult && !listeningResult && !writingResult && !speakingResult) {
      setPageState("error")
      return
    }

    const assessmentResults: Record<string, object | null> = {
      reading:   readingResult,
      listening: listeningResult,
      writing:   writingResult,
      speaking:  speakingResult,
    }

    // Save results to database
    try {
      const saveRes = await fetch(`${BACKEND_URL}/reception/grade/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id:   userId,
          reading:   readingResult,
          listening: listeningResult,
          writing:   writingResult,
          speaking:  speakingResult,
        }),
      })
      if (saveRes.ok) {
        const saved = await saveRes.json()
        assessmentResults.current_level  = saved.current_level
        assessmentResults.assessment_ids = saved.assessment_ids
      }
    } catch {
      // Save failed — results still available in sessionStorage
    }

    sessionStorage.setItem("assessment_results", JSON.stringify(assessmentResults))
    console.log("Assessment results:", assessmentResults)

    router.push("/dashboard")
  }

  const skillKeys = ["reading", "listening", "writing", "speaking"] as const

  if (pageState === "error") {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-sm text-center space-y-5"
        >
          <div className="w-16 h-16 mx-auto rounded-2xl bg-red-50 dark:bg-red-500/10 flex items-center justify-center text-3xl">
            ⚠️
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">
              {t("assess_grading_error_title")}
            </h2>
            <p className="text-sm text-slate-500 dark:text-gray-400">
              {t("assess_grading_error_desc")}
            </p>
          </div>
          <button
            onClick={() => { startedRef.current = false; setPageState("grading"); setProgress(0); setStatus({ reading: "pending", listening: "pending", writing: "pending", speaking: "pending" }) }}
            className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20"
          >
            {t("assess_grading_retry")}
          </button>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center px-4">
      {/* Ambient blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/6 dark:bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-500/6 dark:bg-violet-500/10 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative flex flex-col items-center gap-8 w-full max-w-sm"
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <GiEarthAfricaEurope className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-slate-900 dark:text-white text-xl tracking-tight">NedLang</span>
        </div>

        {/* Spinner */}
        <div className="relative w-20 h-20">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1.4, ease: "linear" }}
            className="absolute inset-0 rounded-full border-4 border-indigo-200 dark:border-indigo-900 border-t-indigo-600 dark:border-t-indigo-400"
          />
          <div className="absolute inset-3 rounded-full bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center text-lg">
            🏆
          </div>
        </div>

        {/* Heading + rotating message */}
        <div className="text-center space-y-2">
          <p className="text-base font-semibold text-slate-900 dark:text-white">
            {t("assess_grading_heading")}
          </p>
          <div className="h-6 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.p
                key={msgIndex}
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -10, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-sm text-slate-500 dark:text-gray-400 text-center"
              >
                {t(MESSAGE_KEYS[msgIndex])}
              </motion.p>
            </AnimatePresence>
          </div>
        </div>

        {/* Per-skill status indicators */}
        <div className="w-full grid grid-cols-4 gap-2">
          {skillKeys.map((skill) => {
            const s = status[skill]
            return (
              <div key={skill} className="flex flex-col items-center gap-1.5">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-all ${
                  s === "done"    ? "bg-emerald-100 dark:bg-emerald-500/20" :
                  s === "failed"  ? "bg-red-100 dark:bg-red-500/20" :
                  "bg-slate-100 dark:bg-slate-800"
                }`}>
                  {s === "done"   ? "✅" :
                   s === "failed" ? "❌" :
                   <motion.span
                     animate={{ opacity: [0.4, 1, 0.4] }}
                     transition={{ repeat: Infinity, duration: 1.5 }}
                   >
                     {SKILL_ICONS[skill]}
                   </motion.span>}
                </div>
                <span className="text-[10px] text-slate-400 dark:text-gray-500 capitalize">{skill}</span>
              </div>
            )
          })}
        </div>

        {/* Progress bar */}
        <div className="w-full space-y-2">
          <div className="flex justify-between text-xs text-slate-400 dark:text-gray-500 px-0.5">
            <span>{Math.round(progress)}{t("assess_complete")}</span>
            <span className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.2 }}
                  className="inline-block w-1 h-1 rounded-full bg-indigo-500"
                />
              ))}
            </span>
          </div>
          <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-indigo-500 to-violet-600 rounded-full"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>
      </motion.div>
    </div>
  )
}
