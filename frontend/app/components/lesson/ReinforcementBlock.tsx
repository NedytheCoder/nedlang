"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import type {
  Reinforcement,
  QuizItem,
  DialogueReinforcementItem,
  SpeakingItem,
  ListeningItem,
  ReadingItem,
  WritingItem,
  ReflectionItem,
} from "./types"

interface Props {
  reinforcement: Reinforcement
}

const OPTION_LETTERS = ["A", "B", "C", "D"] as const

// ── Quiz ──────────────────────────────────────────────────────────────────────
function QuizReinforcement({ items }: { items: QuizItem[] }) {
  const { t } = useTranslation()
  const [selections, setSelections] = useState<Record<number, string>>({})
  const [revealed, setRevealed] = useState<Record<number, boolean>>({})

  return (
    <div className="space-y-4">
      {items.map((item, i) => {
        const selected = selections[i]
        const isRevealed = revealed[i]
        const isCorrect = selected === item.correct

        return (
          <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
            <div className="px-4 py-3.5 border-b border-slate-200 dark:border-white/8">
              <p className="text-sm font-medium text-slate-800 dark:text-gray-100 leading-relaxed">
                {i + 1}. {item.question}
              </p>
            </div>
            <div className="p-3 space-y-2">
              {OPTION_LETTERS.map((letter) => {
                const isSelected = selected === letter
                const isCorrectOption = letter === item.correct
                let style = "bg-white dark:bg-slate-800 border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500/40"
                if (isSelected && !isRevealed) style = "bg-indigo-600 border-indigo-600 shadow-md shadow-indigo-500/20"
                if (isRevealed && isCorrectOption) style = "bg-emerald-500 border-emerald-500 shadow-sm"
                if (isRevealed && isSelected && !isCorrect) style = "bg-red-500 border-red-500"

                return (
                  <button
                    key={letter}
                    type="button"
                    disabled={isRevealed}
                    onClick={() => setSelections((prev) => ({ ...prev, [i]: letter }))}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl border text-left transition-all duration-150 disabled:cursor-default ${style}`}
                  >
                    <span className={`flex-shrink-0 w-5 h-5 rounded-full border text-[10px] font-bold flex items-center justify-center ${
                      (isSelected && !isRevealed) || (isRevealed && (isCorrectOption || isSelected))
                        ? "border-white/50 text-white bg-white/20"
                        : "border-slate-300 dark:border-slate-600 text-slate-500 dark:text-gray-400"
                    }`}>
                      {letter}
                    </span>
                    <span className={`text-sm leading-relaxed ${
                      (isSelected && !isRevealed) || (isRevealed && (isCorrectOption || isSelected))
                        ? "text-white font-medium"
                        : "text-slate-700 dark:text-gray-300"
                    }`}>
                      {item.options[letter]}
                    </span>
                  </button>
                )
              })}
            </div>
            {selected && !isRevealed && (
              <div className="px-3 pb-3">
                <button
                  type="button"
                  onClick={() => setRevealed((prev) => ({ ...prev, [i]: true }))}
                  className="w-full py-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-500/10 transition-colors"
                >
                  {t("lesson_answer_show")}
                </button>
              </div>
            )}
            {isRevealed && (
              <div className={`px-4 py-2.5 text-xs font-semibold ${isCorrect ? "text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-500/10" : "text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-500/10"}`}>
                {isCorrect ? `✓ ${t("lesson_correct")}` : `✗ ${t("lesson_answer_label")}: ${item.correct}`}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Dialogue ──────────────────────────────────────────────────────────────────
function DialogueReinforcement({ items }: { items: DialogueReinforcementItem[] }) {
  const { t } = useTranslation()
  const [shown, setShown] = useState<Record<number, boolean>>({})

  return (
    <div className="space-y-3">
      {items.map((item, i) => {
        const isLearner = item.role.toLowerCase().includes("learner") || item.role === "B"
        return (
          <div key={i} className={`flex gap-2.5 ${isLearner ? "flex-row-reverse" : "flex-row"}`}>
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold mt-0.5 ${isLearner ? "bg-violet-600" : "bg-indigo-600"}`}>
              {item.role.charAt(0).toUpperCase()}
            </div>
            <div className={`flex-1 max-w-[75%] ${isLearner ? "items-end" : "items-start"} flex flex-col gap-1`}>
              <span className="text-[10px] font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide">
                {item.role}
              </span>
              <div className={`px-4 py-3 rounded-2xl text-sm shadow-sm ${isLearner ? "bg-violet-600 text-white rounded-tr-sm" : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-gray-100 rounded-tl-sm"}`}>
                {item.prompt}
              </div>
              {isLearner && (
                <button
                  type="button"
                  onClick={() => setShown((p) => ({ ...p, [i]: !p[i] }))}
                  className="text-[10px] font-medium text-violet-600 dark:text-violet-400 hover:underline px-1 transition-colors"
                >
                  {shown[i] ? t("lesson_answer_hide") : t("lesson_answer_show")}
                </button>
              )}
              <AnimatePresence>
                {isLearner && shown[i] && (
                  <motion.p
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    className="text-xs text-slate-500 dark:text-gray-400 italic px-1"
                  >
                    {item.suggested_response}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ── Speaking ──────────────────────────────────────────────────────────────────
function SpeakingReinforcement({ items }: { items: SpeakingItem[] }) {
  const { t } = useTranslation()
  const [shown, setShown] = useState<Record<number, boolean>>({})

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-4 space-y-3">
          <div className="flex items-start gap-2">
            <span className="text-lg flex-shrink-0">🎤</span>
            <div>
              <p className="text-xs text-slate-500 dark:text-gray-400 mb-1">{item.task}</p>
              <p className="text-sm font-medium text-slate-800 dark:text-gray-100">{item.prompt}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-10 bg-slate-200 dark:bg-slate-700 rounded-xl flex items-center justify-center text-xs text-slate-400 dark:text-gray-500">
              {t("lesson_speak_aloud")}
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShown((p) => ({ ...p, [i]: !p[i] }))}
            className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline transition-colors"
          >
            {shown[i] ? t("lesson_hide_model_answer") : t("lesson_show_model_answer")}
          </button>
          <AnimatePresence>
            {shown[i] && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="pt-2 px-3.5 pb-3 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 rounded-xl">
                  <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 mb-0.5">{t("lesson_example_response")}</p>
                  <p className="text-sm text-indigo-800 dark:text-indigo-200">{item.example_response}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  )
}

// ── Listening ─────────────────────────────────────────────────────────────────
function ListeningReinforcement({ items }: { items: ListeningItem[] }) {
  const { t } = useTranslation()
  const [shownTranscripts, setShownTranscripts] = useState<Record<number, boolean>>({})
  const [shownAnswers, setShownAnswers] = useState<Record<number, boolean>>({})

  return (
    <div className="space-y-4">
      {items.map((item, i) => (
        <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
          {/* Scenario */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-white/8">
            <span className="text-base">🎧</span>
            <p className="text-xs text-slate-600 dark:text-gray-300">{item.scenario}</p>
          </div>

          <div className="px-4 py-4 space-y-3">
            {/* Transcript toggle */}
            <button
              type="button"
              onClick={() => setShownTranscripts((p) => ({ ...p, [i]: !p[i] }))}
              className="w-full flex items-center justify-between text-xs font-medium text-slate-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              <span>{shownTranscripts[i] ? t("lesson_hide_transcript") : t("lesson_show_transcript")}</span>
              <svg className={`w-3.5 h-3.5 transition-transform ${shownTranscripts[i] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
              </svg>
            </button>

            <AnimatePresence>
              {shownTranscripts[i] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="px-3.5 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-xl">
                    <p className="text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wide">{t("lesson_passage_label")}</p>
                    <p className="text-sm text-slate-700 dark:text-gray-200 leading-relaxed">{item.transcript}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Question */}
            <p className="text-sm font-medium text-slate-800 dark:text-gray-100">{item.question}</p>

            {/* Answer reveal */}
            <button
              type="button"
              onClick={() => setShownAnswers((p) => ({ ...p, [i]: !p[i] }))}
              className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline transition-colors flex items-center gap-1"
            >
              <svg className={`w-3.5 h-3.5 transition-transform ${shownAnswers[i] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
              </svg>
              {shownAnswers[i] ? t("lesson_answer_hide") : t("lesson_answer_show")}
            </button>

            <AnimatePresence>
              {shownAnswers[i] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="px-3.5 py-2.5 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
                    <p className="text-sm text-emerald-800 dark:text-emerald-200">{item.answer}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Reading ───────────────────────────────────────────────────────────────────
function ReadingReinforcement({ items }: { items: ReadingItem[] }) {
  const { t } = useTranslation()
  const [shown, setShown] = useState<Record<number, boolean>>({})

  // Group into passage + questions (assume same passage repeated per question)
  const passage = items[0]?.passage

  return (
    <div className="space-y-4">
      {passage && (
        <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-4">
          <p className="text-xs font-semibold text-slate-400 dark:text-gray-500 uppercase tracking-wide mb-2">{t("lesson_passage_label")}</p>
          <p className="text-sm text-slate-700 dark:text-gray-200 leading-relaxed">{passage}</p>
        </div>
      )}

      <div className="space-y-3">
        {items.map((item, i) => (
          <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-3.5 space-y-2">
            <p className="text-sm font-medium text-slate-800 dark:text-gray-100">{i + 1}. {item.question}</p>
            <button
              type="button"
              onClick={() => setShown((p) => ({ ...p, [i]: !p[i] }))}
              className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline transition-colors flex items-center gap-1"
            >
              <svg className={`w-3.5 h-3.5 transition-transform ${shown[i] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
              </svg>
              {shown[i] ? t("lesson_answer_hide") : t("lesson_answer_show")}
            </button>
            <AnimatePresence>
              {shown[i] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="px-3.5 py-2.5 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
                    <p className="text-sm text-emerald-800 dark:text-emerald-200">{item.answer}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Writing ───────────────────────────────────────────────────────────────────
function WritingReinforcement({ items }: { items: WritingItem[] }) {
  const { t } = useTranslation()
  const [responses, setResponses] = useState<Record<number, string>>({})
  const [shown, setShown] = useState<Record<number, boolean>>({})

  return (
    <div className="space-y-4">
      {items.map((item, i) => (
        <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2.5 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-white/8">
            <div className="flex items-center gap-2">
              <span className="text-base">✍️</span>
              <span className="text-xs font-semibold text-slate-600 dark:text-gray-300 uppercase tracking-wider">{item.task}</span>
            </div>
            <span className="text-[10px] font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 px-2 py-0.5 rounded-full">
              {t("lesson_word_guide")} · {item.word_count_guide}
            </span>
          </div>
          <div className="px-4 py-4 space-y-3">
            <p className="text-sm text-slate-800 dark:text-gray-100 leading-relaxed">{item.prompt}</p>
            <textarea
              rows={5}
              value={responses[i] ?? ""}
              onChange={(e) => setResponses((p) => ({ ...p, [i]: e.target.value }))}
              placeholder={t("lesson_your_response") + "…"}
              className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-3 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all resize-none leading-relaxed"
            />
            <button
              type="button"
              onClick={() => setShown((p) => ({ ...p, [i]: !p[i] }))}
              className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline transition-colors"
            >
              {shown[i] ? t("lesson_hide_model_answer") : t("lesson_show_model_answer")}
            </button>
            <AnimatePresence>
              {shown[i] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="px-3.5 py-3 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 rounded-xl">
                    <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 mb-1">{t("lesson_model_answer")}</p>
                    <p className="text-sm text-indigo-800 dark:text-indigo-200 leading-relaxed">{item.model_answer}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Reflection ────────────────────────────────────────────────────────────────
function ReflectionReinforcement({ items }: { items: ReflectionItem[] }) {
  const { t } = useTranslation()

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-4 space-y-2">
          <div className="flex items-start gap-2.5">
            <span className="text-base flex-shrink-0 mt-0.5">🤔</span>
            <p className="text-sm text-slate-800 dark:text-gray-100 leading-relaxed">{item.question}</p>
          </div>
          {item.hint && (
            <p className="text-xs text-slate-400 dark:text-gray-500 italic pl-7">
              {t("lesson_hint")}: {item.hint}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Section title map ─────────────────────────────────────────────────────────
const SECTION_META: Record<string, { icon: string; color: string; titleKey: string }> = {
  quiz:       { icon: "🧠", color: "bg-blue-100 dark:bg-blue-500/15",    titleKey: "lesson_quiz_title" },
  dialogue:   { icon: "🎭", color: "bg-violet-100 dark:bg-violet-500/15", titleKey: "lesson_dialogue_title" },
  speaking:   { icon: "🎤", color: "bg-pink-100 dark:bg-pink-500/15",    titleKey: "lesson_speaking_title" },
  listening:  { icon: "🎧", color: "bg-sky-100 dark:bg-sky-500/15",      titleKey: "lesson_listening_title" },
  reading:    { icon: "📰", color: "bg-teal-100 dark:bg-teal-500/15",    titleKey: "lesson_reading_title" },
  writing:    { icon: "✍️", color: "bg-amber-100 dark:bg-amber-500/15",  titleKey: "lesson_writing_title" },
  reflection: { icon: "🤔", color: "bg-rose-100 dark:bg-rose-500/15",   titleKey: "lesson_reflection_title" },
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ReinforcementBlock({ reinforcement }: Props) {
  const { t } = useTranslation()

  if (!reinforcement || reinforcement.type === "none" || !reinforcement.content.length) return null

  const meta = SECTION_META[reinforcement.type]

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-4">
        <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${meta.color}`}>
          <span className="text-sm">{meta.icon}</span>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
            {t("lesson_reinforcement_label")}
          </h2>
          <p className="text-xs text-slate-500 dark:text-gray-400">{t(meta.titleKey)}</p>
        </div>
      </div>

      {reinforcement.type === "quiz"       && <QuizReinforcement       items={reinforcement.content as QuizItem[]} />}
      {reinforcement.type === "dialogue"   && <DialogueReinforcement   items={reinforcement.content as DialogueReinforcementItem[]} />}
      {reinforcement.type === "speaking"   && <SpeakingReinforcement   items={reinforcement.content as SpeakingItem[]} />}
      {reinforcement.type === "listening"  && <ListeningReinforcement  items={reinforcement.content as ListeningItem[]} />}
      {reinforcement.type === "reading"    && <ReadingReinforcement    items={reinforcement.content as ReadingItem[]} />}
      {reinforcement.type === "writing"    && <WritingReinforcement    items={reinforcement.content as WritingItem[]} />}
      {reinforcement.type === "reflection" && <ReflectionReinforcement items={reinforcement.content as ReflectionItem[]} />}
    </motion.div>
  )
}
