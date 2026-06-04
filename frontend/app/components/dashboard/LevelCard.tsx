"use client"

import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { FRAMEWORK_DATA } from "../reception/frameworkUtils"

const LEVEL_COLORS: Record<string, string> = {
  A1: "from-emerald-400 to-teal-500",
  A2: "from-teal-400 to-cyan-500",
  B1: "from-blue-400 to-indigo-500",
  B2: "from-indigo-400 to-violet-500",
  C1: "from-violet-400 to-purple-500",
  C2: "from-purple-400 to-pink-500",
  HSK1: "from-emerald-400 to-teal-500",
  HSK2: "from-teal-400 to-cyan-500",
  HSK3: "from-blue-400 to-indigo-500",
  HSK4: "from-indigo-400 to-violet-500",
  HSK5: "from-violet-400 to-purple-500",
  HSK6: "from-purple-400 to-pink-500",
  N5: "from-emerald-400 to-teal-500",
  N4: "from-teal-400 to-cyan-500",
  N3: "from-blue-400 to-indigo-500",
  N2: "from-indigo-400 to-violet-500",
  N1: "from-violet-400 to-purple-500",
}

interface Props {
  profile: { framework: string; currentLevel: string; xp: number; xpCurrentLevel: number; xpNextLevel: number }
}

export default function LevelCard({ profile }: Props) {
  const { t } = useTranslation()
  const { framework, currentLevel, xp, xpCurrentLevel, xpNextLevel } = profile

  const levels = FRAMEWORK_DATA[framework as keyof typeof FRAMEWORK_DATA]?.levels ?? []
  const currentIdx = levels.indexOf(currentLevel)
  const nextLevel = levels[currentIdx + 1]
  const xpProgress = ((xp - xpCurrentLevel) / (xpNextLevel - xpCurrentLevel)) * 100
  const gradient = LEVEL_COLORS[currentLevel] ?? "from-indigo-400 to-violet-500"

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_level_title")}</p>
        <span className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-gray-400 px-2 py-1 rounded-lg font-medium">
          {framework}
        </span>
      </div>

      {/* Level badge */}
      <div className="flex items-center gap-4 mb-6">
        <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg flex-shrink-0`}>
          <span className="text-white font-bold text-xl">{currentLevel}</span>
        </div>
        <div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{xp.toLocaleString()} <span className="text-sm font-normal text-slate-400">{t("dash_level_xp")}</span></p>
          {nextLevel && (
            <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
              {(xpNextLevel - xp).toLocaleString()} {t("dash_level_to_next")} <span className="font-semibold text-indigo-600 dark:text-indigo-400">{nextLevel}</span>
            </p>
          )}
        </div>
      </div>

      {/* XP progress */}
      <div>
        <div className="flex justify-between text-xs text-slate-500 dark:text-gray-400 mb-1.5">
          <span>{currentLevel}</span>
          {nextLevel && <span>{nextLevel}</span>}
        </div>
        <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            className={`h-full bg-gradient-to-r ${gradient} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${xpProgress}%` }}
            transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
          />
        </div>

        {/* Framework level track */}
        <div className="flex gap-1 mt-3">
          {levels.map((lvl, i) => (
            <div key={lvl} className={`flex-1 h-1 rounded-full ${i <= currentIdx ? `bg-gradient-to-r ${gradient}` : "bg-slate-200 dark:bg-slate-700"}`} />
          ))}
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-slate-400">{levels[0]}</span>
          <span className="text-xs text-slate-400">{levels[levels.length - 1]}</span>
        </div>
      </div>
    </div>
  )
}
