"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

export interface Achievement {
  id: string
  earned: boolean
  earnedDate?: string
  progress?: number
  target?: number
  current?: number
}

const ICON_MAP: Record<string, string> = {
  first_lesson: "📖", first_convo: "💬", first_assessment: "🎯",
  hundred_words: "📚", vocab_explorer: "🗺️", vocab_master: "👑",
  streak_3: "🔥", streak_7: "🔥", streak_30: "⚡", streak_100: "💎",
  grammar_master: "📝", grammar_expert: "🏛️",
  listening_specialist: "🎧", reading_specialist: "📖",
  writing_specialist: "✍️", speaking_specialist: "🗣️",
  assessment_champion: "🏆", perfect_score: "⭐",
  level_up: "🚀", framework_advance: "📈",
  ten_hours: "⏱️", fifty_hours: "🎓", hundred_hours: "🌟",
}

const TITLE_KEYS: Record<string, string> = {
  first_lesson:          "dash_achieve_first_lesson",
  first_convo:           "dash_achieve_first_convo",
  first_assessment:      "dash_achieve_first_assessment",
  hundred_words:         "dash_achieve_100_words",
  vocab_explorer:        "dash_achieve_vocab_explorer",
  vocab_master:          "dash_achieve_vocab_master",
  streak_3:              "dash_achieve_streak_3",
  streak_7:              "dash_achieve_streak_7",
  streak_30:             "dash_achieve_streak_30",
  streak_100:            "dash_achieve_streak_100",
  grammar_master:        "dash_achieve_grammar_master",
  grammar_expert:        "dash_achieve_grammar_expert",
  listening_specialist:  "dash_achieve_listening_specialist",
  reading_specialist:    "dash_achieve_reading_specialist",
  writing_specialist:    "dash_achieve_writing_specialist",
  speaking_specialist:   "dash_achieve_speaking_specialist",
  assessment_champion:   "dash_achieve_assessment_champion",
  perfect_score:         "dash_achieve_perfect_score",
  level_up:              "dash_achieve_level_up",
  framework_advance:     "dash_achieve_framework_advance",
  ten_hours:             "dash_achieve_ten_hours",
  fifty_hours:           "dash_achieve_fifty_hours",
  hundred_hours:         "dash_achieve_hundred_hours",
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
      <div className={`text-2xl ${a.earned ? "" : "grayscale"}`}>{ICON_MAP[a.id] ?? "🏅"}</div>
      <p className="text-[10px] font-medium text-center leading-tight text-slate-700 dark:text-gray-300">
        {TITLE_KEYS[a.id] ? t(TITLE_KEYS[a.id]) : a.id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
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

interface Props {
  achievements: Achievement[]
}

export default function Achievements({ achievements }: Props) {
  const { t } = useTranslation()
  const earned = achievements.filter((a) => a.earned).length

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_achieve_title")}</p>
        <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
          {earned}/{achievements.length} {t("dash_achieve_earned")}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {achievements.map((a, i) => (
          <AchievementBadge key={a.id} a={a} index={i} />
        ))}
      </div>
    </div>
  )
}
