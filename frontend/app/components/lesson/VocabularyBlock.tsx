"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import type { VocabItem } from "./types"
import SpeakButton from "./SpeakButton"

interface Props {
  vocabulary: VocabItem[]
  lang?: string
}

export default function VocabularyBlock({ vocabulary, lang }: Props) {
  const { t } = useTranslation()

  if (!vocabulary?.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.25, ease: "easeOut" }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-7 h-7 rounded-lg bg-violet-100 dark:bg-violet-500/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">📖</span>
        </div>
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
          {t("lesson_vocab_label")}
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {vocabulary.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.25, delay: 0.04 * i }}
            className="group bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-white/8 rounded-xl px-4 py-3.5 hover:border-violet-300 dark:hover:border-violet-500/40 hover:bg-violet-50/50 dark:hover:bg-violet-500/5 transition-all duration-200 cursor-default"
          >
            {/* Word + translation row */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-1.5 min-w-0">
                <span className="font-bold text-slate-900 dark:text-white text-sm sm:text-base leading-tight">
                  {item.word}
                </span>
                <SpeakButton text={item.word} lang={lang} />
              </div>
              <span className="text-xs font-medium text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-500/10 border border-violet-200 dark:border-violet-500/20 px-2 py-0.5 rounded-full flex-shrink-0">
                {item.translation}
              </span>
            </div>
            {/* Example sentence */}
            <p className="text-xs text-slate-500 dark:text-gray-400 leading-relaxed italic">
              {item.example}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
