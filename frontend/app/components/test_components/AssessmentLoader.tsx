"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"

const DEFAULT_MESSAGE_KEYS = [
  "assess_loading_1",
  "assess_loading_2",
  "assess_loading_3",
  "assess_loading_4",
]

const DEFAULT_HEADING_KEY = "assess_loading_heading"

interface Props {
  progress: number
  messageKeys?: string[]
  headingKey?: string
}

export default function AssessmentLoader({
  progress,
  messageKeys = DEFAULT_MESSAGE_KEYS,
  headingKey = DEFAULT_HEADING_KEY,
}: Props) {
  const { t } = useTranslation()
  const [msgIndex, setMsgIndex] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setMsgIndex((i) => (i + 1) % messageKeys.length)
    }, 1800)
    return () => clearInterval(id)
  }, [messageKeys])

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
          <div className="absolute inset-3 rounded-full bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center">
            <span className="text-lg">📖</span>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center space-y-2">
          <p className="text-base font-semibold text-slate-900 dark:text-white">
            {t(headingKey)}
          </p>

          {/* Rotating message */}
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
                {t(messageKeys[msgIndex])}
              </motion.p>
            </AnimatePresence>
          </div>
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
              initial={{ width: "0%" }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            />
          </div>
        </div>
      </motion.div>
    </div>
  )
}
