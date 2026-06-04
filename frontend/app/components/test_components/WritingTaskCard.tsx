"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { WritingQuestion } from "./types"

interface Props {
  question: WritingQuestion
  response: string
  onResponseChange: (val: string) => void
  dir: number
}

const CJK = /[一-鿿぀-ゟ゠-ヿ가-힯]/

function levelColor(level: string): string {
  const l = level.toUpperCase()
  if (["A1", "A2", "N5", "N4", "HSK1", "HSK2", "TOPIK1", "TOPIK2"].some((v) => l === v))
    return "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30"
  if (["B1", "B2", "N3", "HSK3", "HSK4", "TOPIK3", "TOPIK4"].some((v) => l === v))
    return "bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30"
  return "bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30"
}

function parseMinCount(guide: string): number {
  const match = guide.match(/(\d+)/)
  return match ? parseInt(match[1], 10) : 0
}

const variants = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit:  (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
}

export default function WritingTaskCard({ question, response, onResponseChange, dir }: Props) {
  const { t } = useTranslation()

  const isCJK = CJK.test(question.task_prompt)
  const count = isCJK
    ? response.replace(/\s/g, "").length
    : response.trim().split(/\s+/).filter(Boolean).length
  const unit = isCJK ? t("assess_write_chars") : t("assess_write_words")
  const minCount = parseMinCount(question.word_count_guide)
  const reachedMin = count >= minCount

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
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-200 dark:border-white/8 bg-white dark:bg-slate-800">
          <div className="flex items-center gap-2">
            <span className="text-base">✍️</span>
            <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">
              {t("assess_write_task_label")}
            </span>
          </div>
          <span className="text-[10px] font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 px-2 py-0.5 rounded-full">
            {t("assess_write_word_guide")} {question.word_count_guide}
          </span>
        </div>
        <p className="px-4 py-3.5 text-sm text-slate-800 dark:text-gray-100 leading-relaxed">
          {question.task_prompt}
        </p>
      </div>

      {/* Response textarea */}
      <div>
        <label className="block text-xs font-medium text-slate-500 dark:text-gray-400 uppercase tracking-wide mb-2">
          {t("assess_write_response_label")}
        </label>
        <textarea
          rows={6}
          value={response}
          onChange={(e) => onResponseChange(e.target.value)}
          placeholder={t("assess_write_placeholder")}
          className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all resize-none leading-relaxed"
        />
        <div className="flex items-center justify-end mt-1.5 px-0.5">
          <span className={`text-xs tabular-nums transition-colors ${
            reachedMin
              ? "text-emerald-600 dark:text-emerald-400"
              : "text-slate-400 dark:text-gray-500"
          }`}>
            {count} {unit}
            {minCount > 0 && !reachedMin && (
              <span className="ml-1 text-slate-300 dark:text-gray-600">/ {minCount}+ {unit}</span>
            )}
          </span>
        </div>
      </div>
    </motion.div>
  )
}
