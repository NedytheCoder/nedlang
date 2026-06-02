"use client"

import { useMemo, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { FaGlobe, FaMagic, FaCheckCircle } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

type FrameworkKey = "cefr" | "hsk" | "jlpt" | "topik"

interface FrameworkEntry {
  name: string; description: string; detail: string; languages: string
  levels: string[]; levelLabels: string[]
}

const FRAMEWORK_COLORS: Record<FrameworkKey, { bg: string; border: string; badge: string; text: string }> = {
  cefr:  { bg: "from-indigo-600/10 to-violet-600/5", border: "border-indigo-500/30", badge: "bg-indigo-500/15 border-indigo-500/30 text-indigo-600 dark:text-indigo-300",  text: "text-indigo-600 dark:text-indigo-400" },
  hsk:   { bg: "from-red-600/10 to-orange-600/5",    border: "border-red-500/30",    badge: "bg-red-500/15 border-red-500/30 text-red-700 dark:text-red-300",            text: "text-red-600 dark:text-red-400" },
  jlpt:  { bg: "from-pink-600/10 to-rose-600/5",     border: "border-pink-500/30",   badge: "bg-pink-500/15 border-pink-500/30 text-pink-700 dark:text-pink-300",         text: "text-pink-600 dark:text-pink-400" },
  topik: { bg: "from-sky-600/10 to-cyan-600/5",      border: "border-sky-500/30",    badge: "bg-sky-500/15 border-sky-500/30 text-sky-700 dark:text-sky-300",            text: "text-sky-600 dark:text-sky-400" },
}

function LevelBadge({ level, label, index, total, colorText, colorBg }: {
  level: string; label: string; index: number; total: number; colorText: string; colorBg: string
}) {
  const opacity = 0.3 + (index / (total - 1)) * 0.7
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className={`w-full rounded-xl py-2 px-1 sm:py-3 sm:px-2 flex flex-col items-center border ${colorBg}`} style={{ opacity }}>
        <span className={`text-sm sm:text-lg font-bold ${colorText}`}>{level}</span>
      </div>
      <span className="text-[10px] sm:text-xs text-slate-500 dark:text-gray-500 text-center leading-tight">{label}</span>
    </div>
  )
}

function FrameworkPanel({ framework, colors }: { framework: FrameworkEntry; colors: typeof FRAMEWORK_COLORS.cefr }) {
  return (
    <div className={`bg-gradient-to-br ${colors.bg} border ${colors.border} rounded-2xl p-4 sm:p-6 lg:p-8`}>
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{framework.name}</h3>
          <p className={`text-sm font-medium ${colors.text}`}>{framework.description}</p>
        </div>
        <div className={`text-xs px-3 py-1.5 rounded-full border font-medium ${colors.badge}`}>{framework.languages}</div>
      </div>
      <p className="text-slate-600 dark:text-gray-400 text-sm leading-relaxed mb-8">{framework.detail}</p>
      <div className={`grid gap-2 sm:gap-3 ${framework.levels.length === 5 ? "grid-cols-3 sm:grid-cols-5" : "grid-cols-3 sm:grid-cols-6"}`}>
        {framework.levels.map((level, i) => (
          <LevelBadge key={level} level={level} label={framework.levelLabels[i]} index={i} total={framework.levels.length} colorText={colors.text} colorBg={`border ${colors.border}`} />
        ))}
      </div>
      <div className="mt-6 flex items-center gap-2 text-xs text-slate-500 dark:text-gray-500">
        <FaCheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-500 shrink-0" />
        <span>Progress automatically tracked against {framework.name} standards</span>
      </div>
    </div>
  )
}

export default function FrameworkSection() {
  const { t } = useTranslation()
  const [active, setActive] = useState<FrameworkKey>("cefr")

  const frameworks = useMemo<Record<FrameworkKey, FrameworkEntry>>(() => ({
    cefr:  { name: "CEFR", description: t("ned_cefr_desc"),  detail: t("ned_cefr_detail"),  languages: t("ned_cefr_languages"),  levels: ["A1","A2","B1","B2","C1","C2"], levelLabels: ["Beginner","Elementary","Intermediate","Upper-Int.","Advanced","Mastery"] },
    hsk:   { name: "HSK",  description: t("ned_hsk_desc"),   detail: t("ned_hsk_detail"),   languages: t("ned_hsk_languages"),   levels: ["HSK 1","HSK 2","HSK 3","HSK 4","HSK 5","HSK 6"], levelLabels: ["150 words","300 words","600 words","1,200 words","2,500 words","5,000+"] },
    jlpt:  { name: "JLPT", description: t("ned_jlpt_desc"),  detail: t("ned_jlpt_detail"),  languages: t("ned_jlpt_languages"),  levels: ["N5","N4","N3","N2","N1"], levelLabels: ["Basic","Elementary","Intermediate","Pre-Advanced","Advanced"] },
    topik: { name: "TOPIK",description: t("ned_topik_desc"), detail: t("ned_topik_detail"), languages: t("ned_topik_languages"), levels: ["Level 1","Level 2","Level 3","Level 4","Level 5","Level 6"], levelLabels: ["TOPIK I","TOPIK I","TOPIK II","TOPIK II","TOPIK II","TOPIK II"] },
  }), [t])

  const TAB_KEYS: FrameworkKey[] = ["cefr", "hsk", "jlpt", "topik"]

  return (
    <section className="py-16 lg:py-28 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div className="text-center mb-14" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 rounded-full px-4 py-2 mb-6">
            <FaGlobe className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">{t("ned_framework_badge")}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4 tracking-tight">{t("ned_framework_title")}</h2>
          <p className="text-slate-600 dark:text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">{t("ned_framework_subtitle")}</p>
        </motion.div>

        <motion.div className="flex justify-center mb-8 overflow-x-auto pb-1 -mx-4 px-4 sm:mx-0 sm:px-0" initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5, delay: 0.1 }}>
          <div className="inline-flex bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-1 sm:p-1.5 gap-0.5 sm:gap-1 shrink-0">
            {TAB_KEYS.map((key) => {
              const isActive = key === active
              const colors = FRAMEWORK_COLORS[key]
              return (
                <motion.button key={key} onClick={() => setActive(key)} className={`px-4 py-2 sm:px-5 sm:py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${isActive ? `${colors.badge} shadow-sm` : "text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white hover:bg-white dark:hover:bg-white/5"}`} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                  {key.toUpperCase()}
                </motion.button>
              )
            })}
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div key={active} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
            <FrameworkPanel framework={frameworks[active]} colors={FRAMEWORK_COLORS[active]} />
          </motion.div>
        </AnimatePresence>

        <motion.div className="mt-8 flex justify-center" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.3 }}>
          <div className="inline-flex items-center gap-2 text-sm text-slate-600 dark:text-gray-400 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-full px-5 py-2.5">
            <FaMagic className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            {t("ned_framework_adaptive")}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
