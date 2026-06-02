"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { ReceptionUser } from "./receptionMockData"

export default function WelcomeHero({ user }: { user: ReceptionUser }) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 p-6 sm:p-10 text-white"
    >
      {/* Decorative blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full bg-white/8" />
        <div className="absolute -bottom-12 -left-12 w-48 h-48 rounded-full bg-white/6" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-white/4 blur-3xl" />
      </div>

      <div className="relative">
        {/* Badge */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="inline-flex items-center gap-2 bg-white/15 border border-white/20 rounded-full px-4 py-1.5 text-sm font-medium mb-5"
        >
          <span className="text-base">🎉</span>
          <span>{t("rec_welcome_badge")}</span>
        </motion.div>

        {/* Title */}
        <h1 className="text-2xl sm:text-4xl font-bold mb-3 leading-tight">
          {t("rec_welcome_greeting")}{" "}
          <span className="text-indigo-200">{user.firstName}</span>!
        </h1>
        <p className="text-indigo-200 text-base sm:text-lg mb-8 max-w-lg">{t("rec_welcome_subtitle")}</p>

        {/* Language journey card */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Native */}
          <div className="bg-white/10 border border-white/15 rounded-xl p-4">
            <p className="text-indigo-200 text-xs font-medium mb-2 uppercase tracking-widest">
              {t("rec_welcome_native_label")}
            </p>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl">{user.nativeLanguage.flag}</span>
              <span className="font-semibold">{user.nativeLanguage.name}</span>
            </div>
          </div>

          {/* Arrow */}
          <div className="hidden sm:flex items-center justify-center">
            <motion.div
              animate={{ x: [0, 6, 0] }}
              transition={{ repeat: Infinity, duration: 1.8, ease: "easeInOut" }}
              className="text-3xl text-white/60"
            >
              →
            </motion.div>
          </div>

          {/* Target */}
          <div className="bg-white/20 border border-white/30 rounded-xl p-4 shadow-lg shadow-black/10">
            <p className="text-indigo-200 text-xs font-medium mb-2 uppercase tracking-widest">
              {t("rec_welcome_target_label")}
            </p>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl">{user.targetLanguage.flag}</span>
              <span className="font-bold text-lg">{user.targetLanguage.name}</span>
            </div>
          </div>
        </div>

        {/* Goal */}
        <div className="mt-4 bg-white/10 border border-white/15 rounded-xl px-5 py-3 flex items-start gap-3">
          <span className="text-lg mt-0.5 flex-shrink-0">🎯</span>
          <div>
            <p className="text-indigo-200 text-xs font-medium uppercase tracking-widest mb-0.5">
              {t("rec_welcome_goal_label")}
            </p>
            <p className="text-sm font-medium leading-snug">{user.learningGoal}</p>
          </div>
        </div>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="mt-6 text-indigo-200 text-sm"
        >
          ✨ {t("rec_welcome_journey")}
        </motion.p>
      </div>
    </motion.div>
  )
}
