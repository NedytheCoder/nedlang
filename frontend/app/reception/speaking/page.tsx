"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { AnimatePresence, motion } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { getFramework } from "../../components/reception/frameworkUtils"
import AssessmentLoader from "../../components/test_components/AssessmentLoader"
import ProgressTracker from "../../components/test_components/ProgressTracker"
import SpeakingTaskCard from "../../components/test_components/SpeakingTaskCard"
import { SpeakingQuestion, SpeakingResponse } from "../../components/test_components/types"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const LOADING_MESSAGE_KEYS = [
  "assess_speak_loading_1",
  "assess_speak_loading_2",
  "assess_speak_loading_3",
  "assess_speak_loading_4",
]

type PageState = "loading" | "error" | "questions"

export default function SpeakingPage() {
  const { t } = useTranslation()
  const router = useRouter()

  const [pageState, setPageState] = useState<PageState>("loading")
  const [questions, setQuestions] = useState<SpeakingQuestion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentRecording, setCurrentRecording] = useState<{ audio_b64: string; duration_seconds: number } | null>(null)
  const [responses, setResponses] = useState<SpeakingResponse[]>([])
  const [loadProgress, setLoadProgress] = useState(0)
  const [dir] = useState(1)

  const questionsRef = useRef<SpeakingQuestion[]>([])
  const responsesRef = useRef<SpeakingResponse[]>([])

  useEffect(() => {
    if (pageState !== "loading") return
    const id = setInterval(() => {
      setLoadProgress((p) => {
        if (p >= 85) { clearInterval(id); return p }
        return p + Math.random() * 6
      })
    }, 400)
    return () => clearInterval(id)
  }, [pageState])

  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) { setPageState("error"); return }

    fetch(`${BACKEND_URL}/user/profile/${userId}`)
      .then((r) => { if (!r.ok) throw new Error(); return r.json() })
      .then((profile) => {
        const framework = getFramework(profile.targetLanguage.code)
        return fetch(`${BACKEND_URL}/reception/test/speaking_questions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            target_language: profile.targetLanguage.code,
            native_language: profile.nativeLanguage.code,
            framework,
            learning_goal: profile.learningGoal,
            interests: profile.hobbies,
          }),
        })
      })
      .then((r) => { if (!r.ok) throw new Error(); return r.json() })
      .then((data: SpeakingQuestion[]) => {
        if (!Array.isArray(data) || data.length === 0) { setPageState("error"); return }
        questionsRef.current = data
        console.log("Speaking questions:", data)
        setLoadProgress(100)
        setTimeout(() => {
          setQuestions(data)
          setPageState("questions")
        }, 500)
      })
      .catch(() => setPageState("error"))
  }, [])

  const handleRecordingComplete = (audio_b64: string, duration_seconds: number) => {
    setCurrentRecording({ audio_b64, duration_seconds })
  }

  const handleSubmit = () => {
    if (!currentRecording) return
    const question = questions[currentIndex]
    const newResponse: SpeakingResponse = {
      questionId: String(question.question_no),
      audio_b64: currentRecording.audio_b64,
      duration_seconds: currentRecording.duration_seconds,
    }
    const updatedResponses = [...responses, newResponse]
    setResponses(updatedResponses)
    responsesRef.current = updatedResponses

    const isFinal = currentIndex === questions.length - 1
    if (isFinal) {
      console.log("Speaking responses:", updatedResponses)
      sessionStorage.setItem("speaking_questions", JSON.stringify(questionsRef.current))
      try {
        sessionStorage.setItem("speaking_responses", JSON.stringify(updatedResponses))
      } catch {
        // Quota exceeded — store without audio bytes; speaking grading will skip transcription
        sessionStorage.setItem(
          "speaking_responses",
          JSON.stringify(updatedResponses.map((r) => ({ questionId: r.questionId, audio_b64: "", duration_seconds: r.duration_seconds })))
        )
      }
      router.push("/reception/grading")
      return
    }

    setCurrentRecording(null)
    setCurrentIndex((i) => i + 1)
  }

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (pageState === "loading") {
    return (
      <AssessmentLoader
        progress={Math.min(loadProgress, 100)}
        messageKeys={LOADING_MESSAGE_KEYS}
        headingKey="assess_speak_loading_heading"
        icon="🎤"
      />
    )
  }

  // ── Error ─────────────────────────────────────────────────────────────────────
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
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{t("assess_error_title")}</h2>
            <p className="text-sm text-slate-500 dark:text-gray-400">{t("assess_error_desc")}</p>
          </div>
          <button
            onClick={() => { setPageState("loading"); setLoadProgress(0) }}
            className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20"
          >
            {t("assess_retry")}
          </button>
        </motion.div>
      </div>
    )
  }

  // ── Questions ─────────────────────────────────────────────────────────────────
  const question = questions[currentIndex]
  const isFinal = currentIndex === questions.length - 1
  const isDone = isFinal && responses.length === questions.length
  const canSubmit = currentRecording !== null

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Ambient blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/4 dark:bg-indigo-500/7 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-violet-500/4 dark:bg-violet-500/7 rounded-full blur-3xl" />
      </div>

      {/* Nav */}
      <header className="relative z-10 border-b border-slate-200 dark:border-white/8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-sm">
              <GiEarthAfricaEurope className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-slate-900 dark:text-white text-base tracking-tight">NedLang</span>
          </div>
          <span className="text-xs font-medium text-slate-500 dark:text-gray-400 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
            🎤 {t("assess_speak_task_label")}
          </span>
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 max-w-xl mx-auto px-4 sm:px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl shadow-xl shadow-slate-200/50 dark:shadow-black/30 overflow-hidden"
        >
          {/* Progress header */}
          <div className="px-5 sm:px-8 pt-6 pb-5 border-b border-slate-100 dark:border-white/6">
            <ProgressTracker current={currentIndex + 1} total={questions.length} />
          </div>

          {/* Card body */}
          <div className="px-5 sm:px-8 py-6 min-h-[480px]">
            <AnimatePresence mode="wait" custom={dir}>
              {isDone ? (
                <motion.div
                  key="done"
                  initial={{ opacity: 0, scale: 0.97 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center justify-center gap-4 py-10 text-center"
                >
                  <div className="w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center text-3xl">
                    ✅
                  </div>
                  <div>
                    <p className="text-base font-bold text-slate-900 dark:text-white">{t("assess_speak_complete")}</p>
                    <p className="text-sm text-slate-500 dark:text-gray-400 mt-1">{t("assess_responses_saved")}</p>
                  </div>
                </motion.div>
              ) : (
                <SpeakingTaskCard
                  key={currentIndex}
                  question={question}
                  onRecordingComplete={handleRecordingComplete}
                  dir={dir}
                />
              )}
            </AnimatePresence>
          </div>

          {/* Footer */}
          {!isDone && (
            <div className="px-5 sm:px-8 pb-6 pt-2 border-t border-slate-100 dark:border-white/6">
              <motion.button
                type="button"
                onClick={handleSubmit}
                disabled={!canSubmit}
                whileHover={canSubmit ? { scale: 1.015 } : {}}
                whileTap={canSubmit ? { scale: 0.985 } : {}}
                className={`w-full py-3.5 rounded-xl text-sm font-semibold transition-all ${
                  canSubmit
                    ? "bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-500/20"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-gray-600 cursor-not-allowed"
                }`}
              >
                {isFinal ? t("assess_speak_finish") : t("assess_speak_submit")}
              </motion.button>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
