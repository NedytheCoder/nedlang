"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import type { DialogueLine } from "./types"
import SpeakButton from "./SpeakButton"

interface Props {
  dialogues: DialogueLine[]
  lang?: string
}

const SPEAKER_COLORS = [
  "bg-indigo-600",
  "bg-violet-600",
  "bg-emerald-600",
  "bg-rose-600",
]

function speakerIndex(speaker: string, allSpeakers: string[]): number {
  const idx = allSpeakers.indexOf(speaker)
  return idx === -1 ? 0 : idx
}

export default function DialogueBlock({ dialogues, lang }: Props) {
  const { t } = useTranslation()

  if (!dialogues?.length) return null

  const uniqueSpeakers = [...new Set(dialogues.map((d) => d.speaker))]

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-5">
        <div className="w-7 h-7 rounded-lg bg-blue-100 dark:bg-blue-500/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">💬</span>
        </div>
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
          {t("lesson_dialogues_label")}
        </h2>
      </div>

      <div className="space-y-3">
        {dialogues.map((line, i) => {
          const idx = speakerIndex(line.speaker, uniqueSpeakers)
          const isRight = idx % 2 !== 0
          const colorClass = SPEAKER_COLORS[idx % SPEAKER_COLORS.length]

          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: isRight ? 20 : -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.05 * i }}
              className={`flex gap-2.5 ${isRight ? "flex-row-reverse" : "flex-row"}`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full ${colorClass} flex items-center justify-center text-white text-xs font-bold shadow-sm mt-0.5`}
              >
                {line.speaker.charAt(0).toUpperCase()}
              </div>

              {/* Bubble */}
              <div className={`flex-1 max-w-[75%] sm:max-w-[70%] ${isRight ? "items-end" : "items-start"} flex flex-col gap-1`}>
                <span className={`text-[10px] font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide ${isRight ? "text-right" : "text-left"}`}>
                  {line.speaker}
                </span>
                <div
                  className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm flex items-start gap-2 ${
                    isRight
                      ? "bg-indigo-600 text-white rounded-tr-sm"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-gray-100 rounded-tl-sm"
                  }`}
                >
                  <span className="flex-1">{line.line}</span>
                  <SpeakButton
                    text={line.line}
                    lang={lang}
                    className={isRight ? "text-white/60 hover:text-white hover:bg-white/10" : ""}
                  />
                </div>
                <p className={`text-xs text-slate-400 dark:text-gray-500 px-1 ${isRight ? "text-right" : "text-left"}`}>
                  {line.translation}
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}
