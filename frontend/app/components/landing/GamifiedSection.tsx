"use client"

import { motion } from "framer-motion"
import { FaBolt, FaFire, FaStar, FaSitemap, FaBrain } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

function FeatureCard({ icon, title, description, accentColor, index }: {
  icon: React.ReactNode; title: string; description: string; accentColor: string; index: number
}) {
  return (
    <motion.div
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-6 hover:border-slate-300 dark:hover:border-white/15 transition-colors group"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={{ y: -4 }}
    >
      <motion.div className={`w-12 h-12 rounded-xl ${accentColor} flex items-center justify-center mb-4`} whileHover={{ scale: 1.1, rotate: 5 }} transition={{ type: "spring", stiffness: 400 }}>
        {icon}
      </motion.div>
      <h3 className="text-slate-900 dark:text-white font-semibold text-lg mb-2">{title}</h3>
      <p className="text-slate-600 dark:text-gray-400 text-sm leading-relaxed">{description}</p>
    </motion.div>
  )
}

function AnimatedSkillBar({ name, percentage, colorFrom, colorTo, index }: {
  name: string; percentage: number; colorFrom: string; colorTo: string; index: number
}) {
  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-700 dark:text-gray-300">{name}</span>
        <span className="text-sm text-slate-500 dark:text-gray-500">{percentage}%</span>
      </div>
      <div className="w-full bg-slate-200/60 dark:bg-slate-700/60 rounded-full h-2.5 overflow-hidden">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${colorFrom} ${colorTo} relative overflow-hidden`}
          initial={{ width: 0 }}
          whileInView={{ width: `${percentage}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 + index * 0.1 }}
        >
          <div className="absolute inset-0 nedlang-shimmer-bar" />
        </motion.div>
      </div>
    </div>
  )
}

export default function GamifiedSection() {
  const { t } = useTranslation()

  const features = [
    { accentColor: "bg-gradient-to-br from-indigo-600/20 to-indigo-500/10 border border-indigo-500/20", icon: <FaBolt className="w-6 h-6 text-indigo-500 dark:text-indigo-400" />, titleKey: "ned_gamified_xp_title", descKey: "ned_gamified_xp_desc" },
    { accentColor: "bg-gradient-to-br from-orange-600/20 to-orange-500/10 border border-orange-500/20", icon: <FaFire className="w-6 h-6 text-orange-500 dark:text-orange-400" />, titleKey: "ned_gamified_streak_title", descKey: "ned_gamified_streak_desc" },
    { accentColor: "bg-gradient-to-br from-violet-600/20 to-violet-500/10 border border-violet-500/20", icon: <FaSitemap className="w-6 h-6 text-violet-500 dark:text-violet-400" />, titleKey: "ned_gamified_skilltree_title", descKey: "ned_gamified_skilltree_desc" },
    { accentColor: "bg-gradient-to-br from-emerald-600/20 to-emerald-500/10 border border-emerald-500/20", icon: <FaBrain className="w-6 h-6 text-emerald-500 dark:text-emerald-400" />, titleKey: "ned_gamified_adaptive_title", descKey: "ned_gamified_adaptive_desc" },
  ]

  const skillBars = [
    { key: "ned_gamified_vocab",     percentage: 72, colorFrom: "from-indigo-500", colorTo: "to-indigo-400" },
    { key: "ned_gamified_grammar",   percentage: 45, colorFrom: "from-violet-500", colorTo: "to-violet-400" },
    { key: "ned_gamified_speaking",  percentage: 28, colorFrom: "from-purple-500", colorTo: "to-purple-400" },
    { key: "ned_gamified_listening", percentage: 61, colorFrom: "from-blue-500",   colorTo: "to-blue-400" },
  ]

  return (
    <section id="features" className="py-16 lg:py-28 bg-slate-100/50 dark:bg-slate-900/40 border-y border-slate-200 dark:border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div className="text-center mb-16" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 rounded-full px-4 py-2 mb-6">
            <FaStar className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            <span className="text-sm text-amber-700 dark:text-amber-300 font-medium">{t("ned_gamified_badge")}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4 tracking-tight">{t("ned_gamified_title")}</h2>
          <p className="text-slate-600 dark:text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">{t("ned_gamified_subtitle")}</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-14 lg:mb-20">
          {features.map((f, i) => (
            <FeatureCard key={f.titleKey} accentColor={f.accentColor} icon={f.icon} title={t(f.titleKey)} description={t(f.descKey)} index={i} />
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h3 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-4">{t("ned_gamified_tree_title")}</h3>
            <p className="text-slate-600 dark:text-gray-400 leading-relaxed mb-8">{t("ned_gamified_tree_subtitle")}</p>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 mb-4">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
                    <FaStar className="w-3.5 h-3.5 text-white" />
                  </div>
                  <span className="text-slate-900 dark:text-white font-semibold">{t("ned_gamified_level")} 5</span>
                </div>
                <span className="text-sm text-slate-500 dark:text-gray-400">2,450 / 3,000 XP</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden mt-3">
                <motion.div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full relative overflow-hidden" initial={{ width: 0 }} whileInView={{ width: "83%" }} viewport={{ once: true }} transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}>
                  <div className="absolute inset-0 nedlang-shimmer-bar" />
                </motion.div>
              </div>
              <div className="flex flex-wrap items-center justify-between gap-2 mt-2">
                <span className="text-xs text-slate-500 dark:text-gray-500">83% {t("ned_gamified_complete")}</span>
                <div className="flex items-center gap-1.5">
                  <FaFire className="w-3.5 h-3.5 text-orange-500 dark:text-orange-400" />
                  <span className="text-sm font-bold text-slate-900 dark:text-white">47</span>
                  <span className="text-xs text-slate-500 dark:text-gray-400">{t("ned_hero_preview_streak_label")}</span>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-6" initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            {skillBars.map((bar, i) => (
              <AnimatedSkillBar key={bar.key} name={t(bar.key)} percentage={bar.percentage} colorFrom={bar.colorFrom} colorTo={bar.colorTo} index={i} />
            ))}
            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-white/8">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {skillBars.map((bar, i) => (
                  <motion.div key={bar.key} className="flex flex-col items-center gap-2" initial={{ opacity: 0, scale: 0.8 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: 0.5 + i * 0.1 }}>
                    <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${bar.colorFrom} ${bar.colorTo} flex items-center justify-center text-white text-xs font-bold shadow-lg`}>
                      {bar.percentage}
                    </div>
                    <span className="text-xs text-slate-500 dark:text-gray-500 text-center">{t(bar.key)}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
