"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { SpeakingQuestion } from "./types"

interface Props {
  question: SpeakingQuestion
  onRecordingComplete: (audio_b64: string, duration_seconds: number) => void
  dir: number
}

type Phase = "prep" | "recording" | "review" | "mic_error"

function levelColor(level: string): string {
  const l = level.toUpperCase()
  if (["A1", "A2", "N5", "N4", "HSK1", "HSK2", "TOPIK1", "TOPIK2"].some((v) => l === v))
    return "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30"
  if (["B1", "B2", "N3", "HSK3", "HSK4", "TOPIK3", "TOPIK4"].some((v) => l === v))
    return "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30"
  return "bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30"
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${sec.toString().padStart(2, "0")}`
}

const variants = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit:  (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
}

export default function SpeakingTaskCard({ question, onRecordingComplete, dir }: Props) {
  const { t } = useTranslation()

  const [phase, setPhase] = useState<Phase>("prep")
  const [prepRemaining, setPrepRemaining] = useState(question.prep_time_seconds)
  const [recRemaining, setRecRemaining] = useState(question.response_time_seconds)
  const [audioUrl, setAudioUrl] = useState<string>("")
  const [recordedDuration, setRecordedDuration] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const recStartRef = useRef<number>(0)
  const blobUrlRef = useRef<string>("")

  // Prep countdown
  useEffect(() => {
    if (phase !== "prep") return
    if (prepRemaining <= 0) { startRecording(); return }
    const id = setTimeout(() => setPrepRemaining((n) => n - 1), 1000)
    return () => clearTimeout(id)
  }, [phase, prepRemaining])

  // Recording countdown
  useEffect(() => {
    if (phase !== "recording") return
    if (recRemaining <= 0) { stopRecording(); return }
    const id = setTimeout(() => setRecRemaining((n) => n - 1), 1000)
    return () => clearTimeout(id)
  }, [phase, recRemaining])

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => { if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current) }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
      ].find((t) => MediaRecorder.isTypeSupported(t)) ?? ""
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      chunksRef.current = []
      recStartRef.current = Date.now()

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const duration = Math.round((Date.now() - recStartRef.current) / 1000)
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" })

        // Revoke previous blob URL if any
        if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current)
        const url = URL.createObjectURL(blob)
        blobUrlRef.current = url
        setAudioUrl(url)
        setRecordedDuration(duration)

        // Convert to base64 and notify parent
        const reader = new FileReader()
        reader.onloadend = () => {
          const b64 = (reader.result as string).split(",")[1] ?? ""
          onRecordingComplete(b64, duration)
        }
        reader.readAsDataURL(blob)

        setPhase("review")
      }

      mediaRecorderRef.current = recorder
      recorder.start(100) // collect data every 100ms
      setPhase("recording")
      setRecRemaining(question.response_time_seconds)
    } catch {
      setPhase("mic_error")
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
  }

  const reRecord = () => {
    setAudioUrl("")
    setPrepRemaining(question.prep_time_seconds)
    setRecRemaining(question.response_time_seconds)
    setPhase("prep")
  }

  return (
    <motion.div
      key={question.question_no}
      custom={dir}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="space-y-4"
    >
      {/* Level badge */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500 dark:text-gray-400">{t("assess_level")}:</span>
        <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full border ${levelColor(question.question_level)}`}>
          {question.question_level}
        </span>
      </div>

      {/* Task prompt */}
      <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-slate-200 dark:border-white/8 bg-white dark:bg-slate-800">
          <span className="text-base">🗣️</span>
          <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">
            {t("assess_speak_task_label")}
          </span>
        </div>
        <p className="px-4 py-3.5 text-sm text-slate-800 dark:text-gray-100 leading-relaxed">
          {question.task_prompt}
        </p>
      </div>

      {/* Phase panel */}
      {phase === "mic_error" && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl px-4 py-4 text-sm text-red-700 dark:text-red-300 text-center">
          {t("assess_speak_no_mic")}
        </div>
      )}

      {phase === "prep" && (
        <div className="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-xl overflow-hidden">
          <div className="px-4 py-2.5 border-b border-amber-200 dark:border-amber-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-base">🕐</span>
              <span className="text-xs font-semibold text-amber-700 dark:text-amber-300 uppercase tracking-wider">
                {t("assess_speak_prep_label")}
              </span>
            </div>
            <span className="text-lg font-bold tabular-nums text-amber-700 dark:text-amber-300">
              {formatTime(prepRemaining)}
            </span>
          </div>
          <div className="px-4 py-3 space-y-3">
            <p className="text-xs text-amber-700 dark:text-amber-400">{t("assess_speak_prep_hint")}</p>
            <button
              type="button"
              onClick={startRecording}
              className="w-full py-2.5 text-sm font-semibold rounded-xl bg-amber-600 hover:bg-amber-500 text-white transition-colors"
            >
              {t("assess_speak_skip_prep")}
            </button>
          </div>
        </div>
      )}

      {phase === "recording" && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl overflow-hidden">
          <div className="px-4 py-2.5 border-b border-red-200 dark:border-red-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <motion.span
                animate={{ opacity: [1, 0.2, 1] }}
                transition={{ repeat: Infinity, duration: 1.2 }}
                className="inline-block w-2.5 h-2.5 rounded-full bg-red-500"
              />
              <span className="text-xs font-semibold text-red-700 dark:text-red-300 uppercase tracking-wider">
                {t("assess_speak_recording")}
              </span>
            </div>
            <span className="text-lg font-bold tabular-nums text-red-700 dark:text-red-300">
              {formatTime(recRemaining)}
            </span>
          </div>
          <div className="px-4 py-3">
            <button
              type="button"
              onClick={stopRecording}
              className="w-full py-2.5 text-sm font-semibold rounded-xl bg-red-600 hover:bg-red-500 text-white transition-colors flex items-center justify-center gap-2"
            >
              <span className="w-3 h-3 rounded-sm bg-white inline-block" />
              {t("assess_speak_stop")}
            </button>
          </div>
        </div>
      )}

      {phase === "review" && (
        <div className="bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl overflow-hidden">
          <div className="px-4 py-2.5 border-b border-emerald-200 dark:border-emerald-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-base">✅</span>
              <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">
                {t("assess_speak_review_label")}
              </span>
            </div>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 tabular-nums">
              {formatTime(recordedDuration)}
            </span>
          </div>
          <div className="px-4 py-3 space-y-3">
            {audioUrl && (
              <audio
                src={audioUrl}
                controls
                className="w-full h-10 rounded-lg"
              />
            )}
            <button
              type="button"
              onClick={reRecord}
              className="w-full py-2 text-xs font-medium rounded-xl border border-emerald-300 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-500/10 transition-colors"
            >
              ↺ {t("assess_speak_rerecord")}
            </button>
          </div>
        </div>
      )}
    </motion.div>
  )
}
