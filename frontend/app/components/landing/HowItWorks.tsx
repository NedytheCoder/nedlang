"use client"

import { motion } from "framer-motion"
import { FaGlobe, FaUser, FaMicrochip, FaFileAlt, FaChartBar, FaSyncAlt, FaRoute } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

const STEP_ICONS = [
  <FaGlobe     key="globe"   className="w-6 h-6" />,
  <FaUser      key="user"    className="w-6 h-6" />,
  <FaMicrochip key="cpu"     className="w-6 h-6" />,
  <FaFileAlt   key="doc"     className="w-6 h-6" />,
  <FaChartBar  key="chart"   className="w-6 h-6" />,
  <FaSyncAlt   key="arrows"  className="w-6 h-6" />,
]

const GRADIENTS = [
  ["from-indigo-600","to-indigo-500"],
  ["from-violet-600","to-violet-500"],
  ["from-purple-600","to-purple-500"],
  ["from-blue-600","to-blue-500"],
  ["from-emerald-600","to-emerald-500"],
  ["from-indigo-600","to-violet-600"],
]

const STEP_KEYS = [
  { title: "ned_hiw_step1_title", desc: "ned_hiw_step1_desc", number: "01" },
  { title: "ned_hiw_step2_title", desc: "ned_hiw_step2_desc", number: "02" },
  { title: "ned_hiw_step3_title", desc: "ned_hiw_step3_desc", number: "03" },
  { title: "ned_hiw_step4_title", desc: "ned_hiw_step4_desc", number: "04" },
  { title: "ned_hiw_step5_title", desc: "ned_hiw_step5_desc", number: "05" },
  { title: "ned_hiw_step6_title", desc: "ned_hiw_step6_desc", number: "06" },
]

export default function HowItWorks() {
  const { t } = useTranslation()

  return (
    <section id="how-it-works" className="py-16 lg:py-28 bg-slate-100/50 dark:bg-slate-900/40 border-t border-slate-200 dark:border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div className="text-center mb-16" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <div className="inline-flex items-center gap-2 bg-violet-50 dark:bg-violet-500/10 border border-violet-200 dark:border-violet-500/30 rounded-full px-4 py-2 mb-6">
            <FaRoute className="w-3.5 h-3.5 text-violet-600 dark:text-violet-400" />
            <span className="text-sm text-violet-700 dark:text-violet-300 font-medium">{t("ned_hiw_badge")}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4 tracking-tight">{t("ned_hiw_title")}</h2>
          <p className="text-slate-600 dark:text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">{t("ned_hiw_subtitle")}</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {STEP_KEYS.map((step, i) => {
            const [gradFrom, gradTo] = GRADIENTS[i % GRADIENTS.length]
            return (
              <motion.div
                key={step.number}
                className="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-6 hover:border-slate-300 dark:hover:border-white/15 transition-colors group"
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, duration: 0.5 }}
                whileHover={{ y: -4 }}
              >
                <div className="flex items-start justify-between mb-5">
                  <motion.div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradFrom} ${gradTo} flex items-center justify-center text-white shadow-lg`} whileHover={{ rotate: 8, scale: 1.05 }} transition={{ type: "spring", stiffness: 400 }}>
                    {STEP_ICONS[i]}
                  </motion.div>
                  <span className={`text-3xl font-black bg-gradient-to-r ${gradFrom} ${gradTo} bg-clip-text text-transparent opacity-30`}>{step.number}</span>
                </div>
                <h3 className="text-slate-900 dark:text-white font-semibold text-lg mb-2 leading-snug">{t(step.title)}</h3>
                <p className="text-slate-600 dark:text-gray-400 text-sm leading-relaxed">{t(step.desc)}</p>
                {i < STEP_KEYS.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-6 bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-full z-10" />
                )}
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
