"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockAchievements, Achievement } from "./mockData"

const TITLE_KEYS: Record<string, string> = {
  first_convo: "dash_achieve_first_convo",
  hundred_words: "dash_achieve_100_words",
  streak_7: "dash_achieve_streak_7",
  vocab_explorer: "dash_achieve_vocab_explorer",
  grammar_master: "dash_achieve_grammar_master",
  listening_specialist: "dash_achieve_listening_specialist",
  assessment_champion: "dash_achieve_assessment_champion",
  streak_30: "dash_achieve_streak_30",
}

function AchievementBadge({ a, index }: { a: Achievement; index: number }) {
  const { t } = useTranslation()
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`relative flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${
        a.earned
          ? "bg-gradient-to-b from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 border-indigo-100 dark:border-indigo-500/20"
          : "bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-white/6 opacity-60"
      }`}
    >
      <div className={`text-2xl ${a.earned ? "" : "grayscale"}`}>{a.icon}</div>
      <p className="text-[10px] font-medium text-center leading-tight text-slate-700 dark:text-gray-300">
        {t(TITLE_KEYS[a.id] ?? a.id)}
      </p>
      {a.earned ? (
        <span className="text-[9px] text-indigo-500 font-medium">{a.earnedDate}</span>
      ) : a.progress !== undefined ? (
        <div className="w-full">
          <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${a.progress * 100}%` }} />
          </div>
          <p className="text-[9px] text-slate-400 text-center mt-0.5">{a.current}/{a.target}</p>
        </div>
      ) : (
        <span className="text-[9px] text-slate-400">🔒 {t("dash_achieve_locked")}</span>
      )}
    </motion.div>
  )
}

export default function Achievements() {
  const { t } = useTranslation()
  const earned = mockAchievements.filter((a) => a.earned).length

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_achieve_title")}</p>
        <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
          {earned}/{mockAchievements.length} {t("dash_achieve_earned")}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {mockAchievements.map((a, i) => (
          <AchievementBadge key={a.id} a={a} index={i} />
        ))}
      </div>
    </div>
  )
}
