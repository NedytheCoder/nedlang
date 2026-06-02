"use client"

import { motion } from "framer-motion"
import { FaStar } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

const CARDS = [
  { nameKey: "testimonial_sarah_name", initialsKey: "testimonial_sarah_initials", levelKey: "testimonial_sarah_level", xpKey: "testimonial_sarah_xp", quoteKey: "testimonial_sarah_quote", badgeKey: "testimonial_sarah_badge", color: "from-indigo-400 to-indigo-500" },
  { nameKey: "testimonial_james_name", initialsKey: "testimonial_james_initials", levelKey: "testimonial_james_level", xpKey: "testimonial_james_xp", quoteKey: "testimonial_james_quote", badgeKey: "testimonial_james_badge", color: "from-violet-400 to-violet-500" },
  { nameKey: "testimonial_emma_name",  initialsKey: "testimonial_emma_initials",  levelKey: "testimonial_emma_level",  xpKey: "testimonial_emma_xp",  quoteKey: "testimonial_emma_quote",  badgeKey: "testimonial_emma_badge",  color: "from-blue-400 to-blue-500" },
]

export default function Testimonials() {
  const { t } = useTranslation()

  return (
    <section className="py-16 lg:py-28 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div className="text-center mb-16" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4 tracking-tight">{t("testimonials_title")}</h2>
          <p className="text-slate-600 dark:text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">{t("testimonials_subtitle")}</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {CARDS.map((card, index) => (
            <motion.div
              key={card.nameKey}
              className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-6 hover:border-slate-300 dark:hover:border-white/15 transition-colors"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.12, duration: 0.5 }}
              whileHover={{ y: -4 }}
            >
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <motion.div key={i} initial={{ opacity: 0, scale: 0 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: index * 0.12 + 0.3 + i * 0.07, type: "spring", stiffness: 400 }}>
                    <FaStar className="w-4 h-4 text-amber-400" />
                  </motion.div>
                ))}
              </div>

              <p className="text-slate-700 dark:text-gray-300 text-sm leading-relaxed mb-6">
                &ldquo;{t(card.quoteKey)}&rdquo;
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${card.color} flex items-center justify-center shrink-0`}>
                    <span className="text-white font-semibold text-sm">{t(card.initialsKey)}</span>
                  </div>
                  <div>
                    <p className="text-slate-900 dark:text-white font-semibold text-sm">{t(card.nameKey)}</p>
                    <p className="text-slate-500 dark:text-gray-500 text-xs">{t(card.levelKey)}</p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{t(card.xpKey)}</p>
                  <p className="text-xs text-amber-600 dark:text-amber-500">{t(card.badgeKey)}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
