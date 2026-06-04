"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { ListeningQuestion } from "./types"

interface Props {
  question: ListeningQuestion
  selected: string | null
  onSelect: (option: string) => void
  dir: number
}

const OPTION_LETTERS = ["A", "B", "C", "D"]

function levelColor(level: string): string {
  const l = level.toUpperCase()
  if (["A1", "A2", "N5", "N4", "HSK1", "HSK2", "TOPIK1", "TOPIK2"].some((v) => l === v))
    return "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30"
  if (["B1", "B2", "N3", "HSK3", "HSK4", "TOPIK3", "TOPIK4"].some((v) => l === v))
    return "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30"
  return "bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30"
}

const variants = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit:  (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, "0")}`
}

export default function ListeningQuestionCard({ question, selected, onSelect, dir }: Props) {
  const { t } = useTranslation()
  const audioRef = useRef<HTMLAudioElement>(null)
  const blobUrlRef = useRef<string>("")

  const [audioReady, setAudioReady] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [showTranscript, setShowTranscript] = useState(question.tts_status === "failed")

  useEffect(() => {
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    setAudioReady(false)
    setShowTranscript(question.tts_status === "failed")

    if (!question.audio_b64) return

    const bytes = Uint8Array.from(atob(question.audio_b64), (c) => c.charCodeAt(0))
    const blob = new Blob([bytes], { type: "audio/mpeg" })
    const url = URL.createObjectURL(blob)
    blobUrlRef.current = url

    const audio = audioRef.current
    if (audio) {
      audio.src = url
      audio.load()
    }
    setAudioReady(true)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [question.question_no, question.audio_b64])

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
    } else {
      audio.currentTime === audio.duration ? (audio.currentTime = 0) : null
      audio.play()
    }
  }

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    if (!audio || !duration) return
    const rect = e.currentTarget.getBoundingClientRect()
    audio.currentTime = ((e.clientX - rect.left) / rect.width) * duration
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0
  const isEnded = duration > 0 && currentTime >= duration

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
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => { setIsPlaying(false); setCurrentTime(duration) }}
        onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime ?? 0)}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration ?? 0)}
      />

      {/* Level badge */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500 dark:text-gray-400">{t("assess_level")}:</span>
        <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full border ${levelColor(question.question_level)}`}>
          {question.question_level}
        </span>
      </div>

      {/* Audio player panel */}
      <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">

        {/* Panel header */}
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-slate-200 dark:border-white/8 bg-white dark:bg-slate-800">
          <span className="text-base">🎧</span>
          <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">
            {t("assess_transcript_label")}
          </span>
        </div>

        {/* Controls */}
        {audioReady ? (
          <div className="px-4 py-3.5 space-y-2.5">
            <div className="flex items-center gap-3">
              {/* Play / Pause / Replay button */}
              <button
                type="button"
                onClick={togglePlay}
                className="w-10 h-10 flex-shrink-0 rounded-full bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center shadow-md shadow-indigo-500/25 transition-colors"
              >
                {isEnded ? (
                  // Replay icon
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                  </svg>
                ) : isPlaying ? (
                  // Pause icon
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="4" width="4" height="16" rx="1" />
                    <rect x="14" y="4" width="4" height="16" rx="1" />
                  </svg>
                ) : (
                  // Play icon
                  <svg className="w-4 h-4 text-white translate-x-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>

              {/* Time */}
              <span className="text-xs tabular-nums text-slate-500 dark:text-gray-400 w-20 flex-shrink-0">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>

              {/* Progress bar */}
              <div
                className="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-full cursor-pointer relative overflow-hidden"
                onClick={handleSeek}
              >
                <div
                  className="h-full bg-indigo-500 rounded-full transition-none"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="px-4 py-3 text-xs text-red-500 dark:text-red-400">
            {t("assess_audio_failed")}
          </div>
        )}

        {/* Transcript toggle */}
        <button
          type="button"
          onClick={() => setShowTranscript((v) => !v)}
          className="w-full flex items-center justify-between px-4 py-2 border-t border-slate-200 dark:border-white/8 text-xs text-slate-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800/80 transition-colors"
        >
          <span>{showTranscript ? t("assess_hide_transcript") : t("assess_show_transcript")}</span>
          <svg
            className={`w-3.5 h-3.5 transition-transform ${showTranscript ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
          </svg>
        </button>

        {showTranscript && (
          <p className="px-4 py-3.5 text-sm text-slate-700 dark:text-gray-200 leading-relaxed border-t border-slate-200 dark:border-white/8">
            {question.transcript}
          </p>
        )}
      </div>

      {/* Comprehension question */}
      <p className="text-sm font-semibold text-slate-800 dark:text-white leading-snug px-0.5">
        {question.question}
      </p>

      {/* Options */}
      <div className="space-y-2.5">
        {question.options.map((opt, i) => {
          const letter = OPTION_LETTERS[i]
          const isSelected = selected === letter
          return (
            <motion.button
              key={letter}
              type="button"
              onClick={() => onSelect(letter)}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              className={`w-full flex items-start gap-3.5 px-4 py-3.5 rounded-xl border text-left transition-all duration-150 ${
                isSelected
                  ? "bg-indigo-600 border-indigo-600 shadow-md shadow-indigo-500/20"
                  : "bg-white dark:bg-slate-800 border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500/40"
              }`}
            >
              <span className={`flex-shrink-0 w-6 h-6 rounded-full border flex items-center justify-center text-xs font-bold mt-0.5 ${
                isSelected
                  ? "border-white/50 text-white bg-white/20"
                  : "border-slate-300 dark:border-slate-600 text-slate-500 dark:text-gray-400"
              }`}>
                {letter}
              </span>
              <span className={`text-sm leading-relaxed ${
                isSelected ? "text-white font-medium" : "text-slate-700 dark:text-gray-300"
              }`}>
                {opt}
              </span>
            </motion.button>
          )
        })}
      </div>
    </motion.div>
  )
}
