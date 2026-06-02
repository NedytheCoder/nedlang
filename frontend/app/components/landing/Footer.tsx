"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { GiEarthAfricaEurope } from "react-icons/gi"

export default function Footer() {
  const { t } = useTranslation()

  const productLinks = [
    { labelKey: "ned_footer_features",  href: "#features" },
    { labelKey: "ned_footer_languages", href: "#" },
    { labelKey: "ned_footer_pricing",   href: "#" },
  ]
  const companyLinks = [
    { labelKey: "ned_footer_about",   href: "#" },
    { labelKey: "ned_footer_blog",    href: "#" },
    { labelKey: "ned_footer_careers", href: "#" },
  ]
  const legalLinks = [
    { labelKey: "ned_footer_privacy", href: "#" },
    { labelKey: "ned_footer_terms",   href: "#" },
  ]

  return (
    <motion.footer
      className="bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-white/8"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4 group w-fit">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                <GiEarthAfricaEurope className="w-4 h-4 text-white" />
              </div>
              <span className="text-slate-900 dark:text-white font-bold text-lg tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                NedLang
              </span>
            </Link>
            <p className="text-slate-600 dark:text-gray-400 text-sm leading-relaxed">{t("ned_footer_tagline")}</p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-slate-900 dark:text-white font-semibold text-sm mb-4">{t("ned_footer_product")}</h4>
            <ul className="space-y-3">
              {productLinks.map(({ labelKey, href }) => (
                <li key={labelKey}>
                  <a href={href} className="text-sm text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                    {t(labelKey)}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-slate-900 dark:text-white font-semibold text-sm mb-4">{t("ned_footer_company")}</h4>
            <ul className="space-y-3">
              {companyLinks.map(({ labelKey, href }) => (
                <li key={labelKey}>
                  <a href={href} className="text-sm text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                    {t(labelKey)}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-slate-900 dark:text-white font-semibold text-sm mb-4">{t("ned_footer_legal")}</h4>
            <ul className="space-y-3">
              {legalLinks.map(({ labelKey, href }) => (
                <li key={labelKey}>
                  <a href={href} className="text-sm text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                    {t(labelKey)}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-200 dark:border-white/8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500 dark:text-gray-500">{t("ned_footer_copyright")}</p>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-gray-500">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>{t("ned_footer_operational")}</span>
          </div>
        </div>
      </div>
    </motion.footer>
  )
}
