"use client"

import { Suspense, useEffect, useState } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { motion } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const SKILL_ICONS: Record<string, string> = {
  reading:   "📖",
  listening: "🎧",
  writing:   "✍️",
  speaking:  "🎤",
}

const SKILL_ORDER = ["reading", "listening", "writing", "speaking"] as const

interface SkillResult {
  estimated_level: string
  score:           number
  correct?:        number
  total_questions?: number
  overall_feedback?: string
  overall_score?:    number
  per_question?:     PerQuestion[]
}

interface PerQuestion {
  question_no:       number
  level:             string
  score:             number
  correct?:          boolean
  task_completion?:  number
  grammar?:          number
  vocabulary?:       number
  coherence?:        number
  fluency?:          number
  transcription?:    string
  feedback?:         string
}

interface SessionResults {
  session_id:   string
  completed_at: string | null
  skills:       Record<string, SkillResult>
}

function ScorePill({ label, value }: { label: string; value: number }) {
  const color =
    value >= 75 ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300" :
    value >= 50 ? "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300" :
                  "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300"
  return (
    <div className={`flex flex-col items-center px-3 py-2 rounded-xl ${color}`}>
      <span className="text-xs font-medium opacity-70">{label}</span>
      <span className="text-base font-bold">{value}</span>
    </div>
  )
}

function SkillCard({ skill, data }: { skill: string; data: SkillResult }) {
  const { t } = useTranslation()
  const score = data.overall_score ?? data.score ?? 0
  const isOpenSkill = skill === "writing" || skill === "speaking"

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl overflow-hidden"
    >
      {/* Skill header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-100 dark:border-white/6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">{SKILL_ICONS[skill] ?? "📋"}</span>
          <span className="font-semibold text-slate-900 dark:text-white capitalize">{skill}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 dark:text-gray-400">
            {t("assess_results_est_level")}: <span className="font-bold text-slate-700 dark:text-gray-200">{data.estimated_level}</span>
          </span>
          <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-50 dark:bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 rounded-full">
            {Math.round(score)}%
          </span>
        </div>
      </div>

      <div className="px-5 sm:px-6 py-4 space-y-4">
        {/* MCQ skills: reading / listening */}
        {!isOpenSkill && typeof data.correct === "number" && (
          <div className="flex gap-3">
            <div className="flex-1 flex items-center gap-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl px-3 py-2.5">
              <span className="text-base">✅</span>
              <div>
                <p className="text-xs text-emerald-600 dark:text-emerald-400">{t("assess_results_correct")}</p>
                <p className="font-bold text-emerald-700 dark:text-emerald-300">{data.correct} / {data.total_questions}</p>
              </div>
            </div>
            <div className="flex-1 flex items-center gap-2 bg-red-50 dark:bg-red-500/10 rounded-xl px-3 py-2.5">
              <span className="text-base">❌</span>
              <div>
                <p className="text-xs text-red-600 dark:text-red-400">{t("assess_results_incorrect")}</p>
                <p className="font-bold text-red-700 dark:text-red-300">{(data.total_questions ?? 0) - (data.correct ?? 0)} / {data.total_questions}</p>
              </div>
            </div>
          </div>
        )}

        {/* Open skills: writing / speaking */}
        {isOpenSkill && data.per_question && data.per_question.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs font-medium text-slate-500 dark:text-gray-400 uppercase tracking-wide">
              {t("assess_results_breakdown")}
            </p>
            {data.per_question.map((q) => (
              <div key={q.question_no} className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 space-y-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-slate-500 dark:text-gray-400">Q{q.question_no} · {q.level}</span>
                  <span className="text-xs font-semibold text-slate-700 dark:text-gray-200">{Math.round(q.score)}%</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {skill === "writing" && (
                    <>
                      {typeof q.task_completion === "number" && <ScorePill label={t("assess_results_task_completion")} value={q.task_completion} />}
                      {typeof q.grammar === "number" && <ScorePill label={t("assess_results_grammar")} value={q.grammar} />}
                      {typeof q.vocabulary === "number" && <ScorePill label={t("assess_results_vocabulary")} value={q.vocabulary} />}
                      {typeof q.coherence === "number" && <ScorePill label={t("assess_results_coherence")} value={q.coherence} />}
                    </>
                  )}
                  {skill === "speaking" && (
                    <>
                      {typeof q.task_completion === "number" && <ScorePill label={t("assess_results_task_completion")} value={q.task_completion} />}
                      {typeof q.fluency === "number" && <ScorePill label={t("assess_results_fluency")} value={q.fluency} />}
                      {typeof q.vocabulary === "number" && <ScorePill label={t("assess_results_vocabulary")} value={q.vocabulary} />}
                      {typeof q.grammar === "number" && <ScorePill label={t("assess_results_grammar")} value={q.grammar} />}
                    </>
                  )}
                </div>
                {q.transcription && (
                  <p className="text-xs text-slate-500 dark:text-gray-400 italic">
                    <span className="not-italic font-medium text-slate-600 dark:text-gray-300">{t("assess_results_transcription")}: </span>
                    {q.transcription}
                  </p>
                )}
                {q.feedback && (
                  <p className="text-xs text-slate-600 dark:text-gray-300 bg-white dark:bg-slate-900 rounded-lg px-3 py-2 border border-slate-100 dark:border-white/6">
                    <span className="font-medium">{t("assess_results_feedback")}: </span>
                    {q.feedback}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Overall feedback for open skills */}
        {isOpenSkill && data.overall_feedback && (
          <div className="bg-indigo-50 dark:bg-indigo-500/10 rounded-xl px-4 py-3">
            <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400 mb-1">{t("assess_results_overall_fb")}</p>
            <p className="text-sm text-slate-700 dark:text-gray-200">{data.overall_feedback}</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

function ResultsContent() {
  const { t } = useTranslation()
  const searchParams = useSearchParams()
  const sessionId  = searchParams.get("session_id")
  const levelParam = searchParams.get("level")

  const [results, setResults] = useState<SessionResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(false)

  useEffect(() => {
    if (!sessionId) { setError(true); setLoading(false); return }
    fetch(`${BACKEND_URL}/reception/grade/session/${sessionId}`)
      .then((r) => { if (!r.ok) throw new Error(); return r.json() })
      .then((data: SessionResults) => { setResults(data); setLoading(false) })
      .catch(() => { setError(true); setLoading(false) })
  }, [sessionId])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4">
        <div className="text-center space-y-4">
          <div className="text-4xl">⚠️</div>
          <p className="text-slate-600 dark:text-gray-300">Results not found.</p>
          <Link href="/dashboard" className="inline-block px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-semibold rounded-xl">
            {t("assess_results_go_dashboard")}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/4 dark:bg-indigo-500/7 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-violet-500/4 dark:bg-violet-500/7 rounded-full blur-3xl" />
      </div>

      <header className="relative z-10 border-b border-slate-200 dark:border-white/8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-sm">
              <GiEarthAfricaEurope className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-slate-900 dark:text-white text-base tracking-tight">NedLang</span>
          </div>
          <span className="text-xs font-medium text-slate-500 dark:text-gray-400 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
            🏆 {t("assess_results_title")}
          </span>
        </div>
      </header>

      <main className="relative z-10 max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-5">
        {/* Overall level banner */}
        {levelParam && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-6 text-center text-white shadow-xl shadow-indigo-500/25"
          >
            <p className="text-sm font-medium opacity-80 mb-1">{t("assess_results_overall_level")}</p>
            <p className="text-5xl font-black tracking-tight">{levelParam}</p>
            <p className="text-sm opacity-70 mt-2">{t("assess_results_subtitle")}</p>
          </motion.div>
        )}

        {/* Per-skill cards */}
        {SKILL_ORDER.filter((s) => results.skills[s]).map((skill, i) => (
          <motion.div key={skill} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}>
            <SkillCard skill={skill} data={results.skills[skill]} />
          </motion.div>
        ))}

        {/* Dashboard CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="pb-6"
        >
          <Link
            href="/dashboard"
            className="block w-full py-4 text-center bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-500/25 transition-all"
          >
            {t("assess_results_go_dashboard")} →
          </Link>
        </motion.div>
      </main>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <ResultsContent />
    </Suspense>
  )
}
