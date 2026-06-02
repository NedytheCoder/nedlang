"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { FaBolt, FaStar, FaFire, FaArrowRight } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

function StatItem({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center lg:text-left">
      <div className="text-2xl font-bold text-slate-900 dark:text-white">{value}</div>
      <div className="text-sm text-slate-600 dark:text-gray-400 mt-0.5">{label}</div>
    </div>
  )
}

function LevelCard({ levelLabel, levelValue, frameworkLabel }: {
  levelLabel: string; levelValue: string; frameworkLabel: string
}) {
  return (
    <div
      className="absolute top-8 right-0 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-2xl p-4 w-52 shadow-2xl shadow-slate-200/50 dark:shadow-black/40"
      style={{ animation: "nedlang-float 5s ease-in-out infinite" }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/30">
          <FaStar className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="text-xs text-slate-500 dark:text-gray-400">{levelLabel}</div>
          <div className="text-lg font-bold text-slate-900 dark:text-white">{levelValue}</div>
        </div>
      </div>
      <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium bg-indigo-50 dark:bg-indigo-500/10 rounded-lg px-2 py-1 text-center">
        {frameworkLabel}
      </div>
    </div>
  )
}

function XpCard({ xpLabel, xpValue, xpNext }: {
  xpLabel: string; xpValue: string; xpNext: string
}) {
  return (
    <div
      className="absolute top-1/2 -translate-y-1/2 left-8 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-2xl p-4 w-56 shadow-2xl shadow-slate-200/50 dark:shadow-black/40"
      style={{ animation: "nedlang-float 6s ease-in-out infinite 1.5s" }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <FaBolt className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
          <span className="text-xs text-slate-500 dark:text-gray-400">{xpLabel}</span>
        </div>
        <span className="text-sm font-bold text-slate-900 dark:text-white">
          {xpValue} <span className="text-indigo-500 dark:text-indigo-400">XP</span>
        </span>
      </div>
      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mb-2 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full relative overflow-hidden" style={{ width: "83%" }}>
          <div className="absolute inset-0 nedlang-shimmer-bar" />
        </div>
      </div>
      <div className="text-xs text-slate-500 dark:text-gray-500">{xpNext}</div>
    </div>
  )
}

function StreakCard({ streakValue, streakLabel, streakSub }: {
  streakValue: string; streakLabel: string; streakSub: string
}) {
  return (
    <div
      className="absolute bottom-8 right-8 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-2xl p-4 w-44 shadow-2xl shadow-slate-200/50 dark:shadow-black/40"
      style={{ animation: "nedlang-float 4.5s ease-in-out infinite 0.8s" }}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
          <FaFire className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">{streakValue}</div>
          <div className="text-xs text-slate-500 dark:text-gray-400">{streakLabel}</div>
        </div>
      </div>
      <div className="mt-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">{streakSub}</div>
    </div>
  )
}

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.7, ease: [0.25, 0.1, 0.25, 1] as const, delay },
})

export default function Hero() {
  const { t } = useTranslation()

  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-white dark:bg-slate-950 pt-16">
      {/* Background glows */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 dark:bg-indigo-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/3 w-80 h-80 bg-violet-600/10 dark:bg-violet-600/15 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/4 w-64 h-64 bg-indigo-500/8 dark:bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      {/* Grid pattern — dark lines in light mode, white lines in dark mode */}
      <div className="absolute inset-0 opacity-[0.04] dark:hidden" style={{ backgroundImage: "linear-gradient(rgba(15,23,42,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(15,23,42,0.6) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
      <div className="absolute inset-0 opacity-[0.03] hidden dark:block" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: copy */}
          <div className="text-center lg:text-left">
            <motion.div
              className="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/30 rounded-full px-4 py-2 mb-8 mx-auto lg:mx-0"
              {...fadeUp(0.1)}
            >
              <FaBolt className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm text-indigo-700 dark:text-indigo-300 font-medium">AI-Powered Language Learning</span>
            </motion.div>

            <motion.h1
              className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-[1.1] tracking-tight mb-6"
              {...fadeUp(0.2)}
            >
              <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 dark:from-indigo-400 dark:via-violet-400 dark:to-purple-400 bg-clip-text text-transparent">
                {t("ned_hero_title")}
              </span>
            </motion.h1>

            <motion.p
              className="text-lg text-slate-600 dark:text-gray-400 leading-relaxed mb-10 max-w-lg mx-auto lg:mx-0"
              {...fadeUp(0.3)}
            >
              {t("ned_hero_subtitle")}
            </motion.p>

            <motion.div className="flex flex-wrap gap-4 mb-14 justify-center lg:justify-start" {...fadeUp(0.4)}>
              <Link
                href="/auth/signup"
                className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-xl px-7 py-3.5 transition-all shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:-translate-y-0.5"
              >
                {t("ned_hero_cta_start")}
                <FaArrowRight className="w-4 h-4" />
              </Link>
              <button
                onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}
                className="inline-flex items-center gap-2 border border-slate-300 dark:border-white/15 text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-white/5 font-semibold rounded-xl px-7 py-3.5 transition-all hover:-translate-y-0.5"
              >
                {t("ned_hero_cta_explore")}
              </button>
            </motion.div>

            <motion.div
              className="flex flex-wrap gap-x-8 gap-y-4 pt-6 border-t border-slate-200 dark:border-white/8 justify-center lg:justify-start"
              {...fadeUp(0.5)}
            >
              <StatItem value="50+" label={t("ned_hero_stat_languages_label")} />
              <div className="w-px bg-slate-200 dark:bg-white/10 hidden sm:block" />
              <StatItem value="100K+" label={t("ned_hero_stat_learners_label")} />
              <div className="w-px bg-slate-200 dark:bg-white/10 hidden sm:block" />
              <StatItem value="4" label={t("ned_hero_stat_frameworks_label")} />
            </motion.div>
          </div>

          {/* Right: floating preview cards */}
          <motion.div
            className="relative hidden lg:block h-[480px]"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.6, ease: "easeOut" }}
          >
            <LevelCard levelLabel={t("ned_hero_preview_level_label")} levelValue="B1" frameworkLabel={t("ned_hero_preview_framework_label")} />
            <XpCard xpLabel={t("ned_hero_preview_xp_label")} xpValue="2,450" xpNext={t("ned_hero_preview_xp_next")} />
            <StreakCard streakValue="47" streakLabel={t("ned_hero_preview_streak_label")} streakSub={t("ned_hero_preview_streak_sub")} />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-64 h-64 bg-gradient-to-br from-indigo-600/20 to-violet-600/20 rounded-full blur-2xl" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
