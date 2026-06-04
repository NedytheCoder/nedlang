"use client"

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
  exit: (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
}

export default function ListeningQuestionCard({ question, selected, onSelect, dir }: Props) {
  const { t } = useTranslation()

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

      {/* Transcript panel */}
      <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-200 dark:border-white/8 bg-white dark:bg-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-base">🎧</span>
            <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">
              {t("assess_transcript_label")}
            </span>
          </div>
          <span className="text-[10px] font-medium text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 px-2 py-0.5 rounded-full">
            {t("assess_audio_pending")}
          </span>
        </div>
        <p className="px-4 py-3.5 text-sm text-slate-800 dark:text-gray-100 leading-relaxed">
          {question.transcript}
        </p>
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
