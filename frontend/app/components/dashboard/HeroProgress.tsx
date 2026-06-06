"use client"

import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface Props {
  goal: { title: string; percentComplete: number; targetLevel: string | null }
  currentLesson: { nodeId: number | null; title: string; module: string; lessonNumber: number; totalLessons: number; estimatedMinutes: number } | null
  nextNodeId: number | null
}

export default function HeroProgress({ goal, currentLesson, nextNodeId }: Props) {
  const { t } = useTranslation()
  const router = useRouter()
  const pct = goal.percentComplete

  return (
    <div className="bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 rounded-2xl p-5 sm:p-8 text-white overflow-hidden relative">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-white/5 rounded-full" />
        <div className="absolute -bottom-8 -left-8 w-48 h-48 bg-white/5 rounded-full" />
      </div>

      <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Goal + Progress */}
        <div className="space-y-5">
          <div>
            <p className="text-indigo-200 text-xs font-medium uppercase tracking-widest mb-2">{t("dash_hero_goal_label")}</p>
            <h2 className="text-xl sm:text-2xl font-bold leading-tight">{goal.title}</h2>
          </div>

          {/* Progress bar */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-indigo-200">{t("dash_hero_progress")}</span>
              <span className="font-bold text-white">{pct}% {t("dash_hero_complete")}</span>
            </div>
            <div className="w-full h-3 bg-white/20 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-white rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white/10 rounded-xl p-3">
              <p className="text-indigo-200 text-xs mb-1">{t("dash_hero_est_completion")}</p>
              <p className="font-semibold text-sm">{goal.targetLevel ?? "—"}</p>
            </div>
            <div className="bg-white/10 rounded-xl p-3">
              <p className="text-indigo-200 text-xs mb-1">{t("dash_hero_next_milestone")}</p>
              <p className="font-semibold text-sm leading-tight">—</p>
            </div>
          </div>
        </div>

        {/* Right: Current lesson + CTAs */}
        <div className="flex flex-col justify-between gap-5">
          {/* Current lesson card */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <p className="text-indigo-200 text-xs mb-1">{t("dash_hero_current_lesson")}</p>
                <p className="font-semibold leading-tight">{currentLesson?.title ?? "—"}</p>
                <p className="text-indigo-200 text-xs mt-1">{currentLesson?.module ?? ""}</p>
              </div>
              <span className="flex-shrink-0 bg-white/20 rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap">
                {currentLesson?.estimatedMinutes ?? 0} {t("dash_hero_min")}
              </span>
            </div>
            {/* Lesson progress dots */}
            {currentLesson && (
              <div className="flex items-center gap-1.5">
                {Array.from({ length: currentLesson.totalLessons }, (_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full transition-colors ${
                      i < currentLesson.lessonNumber - 1
                        ? "bg-white"
                        : i === currentLesson.lessonNumber - 1
                        ? "bg-white/70"
                        : "bg-white/25"
                    }`}
                  />
                ))}
                <span className="text-indigo-200 text-xs ml-1 whitespace-nowrap">
                  {currentLesson.lessonNumber}/{currentLesson.totalLessons}
                </span>
              </div>
            )}
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            {currentLesson ? (
              <>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => currentLesson.nodeId && router.push(`/lesson/${currentLesson.nodeId}`)}
                  disabled={!currentLesson.nodeId}
                  className="flex-1 py-3 px-5 bg-white text-indigo-700 font-semibold rounded-xl text-sm shadow-lg shadow-black/20 transition-all hover:bg-indigo-50 disabled:opacity-50"
                >
                  ▶ {t("dash_hero_continue")}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => nextNodeId && router.push(`/lesson/${nextNodeId}`)}
                  disabled={!nextNodeId}
                  className="flex-1 py-3 px-5 bg-white/15 hover:bg-white/25 border border-white/30 text-white font-semibold rounded-xl text-sm transition-all disabled:opacity-50"
                >
                  + {t("dash_hero_new_lesson")}
                </motion.button>
              </>
            ) : (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => nextNodeId && router.push(`/lesson/${nextNodeId}`)}
                disabled={!nextNodeId}
                className="w-full py-3 px-5 bg-white text-indigo-700 font-semibold rounded-xl text-sm shadow-lg shadow-black/20 transition-all hover:bg-indigo-50 disabled:opacity-50"
              >
                ▶ {t("dash_hero_new_lesson")}
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
