"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { FaBolt, FaGoogle, FaGithub } from "react-icons/fa"
import { useTranslation } from "../../../i18n/LanguageProvider"

export default function SignupPage() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4 py-16">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-violet-600/8 dark:bg-violet-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-indigo-600/8 dark:bg-indigo-600/10 rounded-full blur-3xl" />
      </div>

      <motion.div className="relative w-full max-w-md" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }}>
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <FaBolt className="w-5 h-5 text-white" />
            </div>
            <span className="text-slate-900 dark:text-white font-bold text-xl tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
              NedLang
            </span>
          </Link>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-8 shadow-xl shadow-slate-200/50 dark:shadow-black/40">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{t("auth_signup_title")}</h1>
            <p className="text-slate-600 dark:text-gray-400 text-sm">{t("auth_signup_subtitle")}</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {[
              { key: "google", label: t("auth_google"), icon: <FaGoogle className="w-4 h-4" /> },
              { key: "github", label: t("auth_github"), icon: <FaGithub className="w-4 h-4" /> },
            ].map(({ key, label, icon }) => (
              <motion.button key={key} type="button" className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-white/8 hover:border-slate-300 dark:hover:border-white/15 rounded-xl text-sm text-slate-700 dark:text-gray-300 transition-all" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                {icon}
                <span className="truncate">{label}</span>
              </motion.button>
            ))}
          </div>

          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-slate-200 dark:bg-white/8" />
            <span className="text-xs text-slate-500 dark:text-gray-500">{t("auth_or")}</span>
            <div className="flex-1 h-px bg-slate-200 dark:bg-white/8" />
          </div>

          <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
            {[
              { id: "name",    type: "text",     labelKey: "auth_name",    placeholderKey: "auth_name_placeholder" },
              { id: "email",   type: "email",    labelKey: "auth_email",   placeholderKey: "auth_email_placeholder" },
              { id: "pw",      type: "password", labelKey: "auth_password",placeholderKey: "auth_password_placeholder" },
              { id: "confirm", type: "password", labelKey: "auth_confirm_password", placeholderKey: "auth_confirm_placeholder" },
            ].map(({ id, type, labelKey, placeholderKey }) => (
              <div key={id}>
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">{t(labelKey)}</label>
                <input type={type} placeholder={t(placeholderKey)} className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all" />
              </div>
            ))}

            <motion.button type="submit" className="w-full py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 mt-2" whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
              {t("auth_sign_up")}
            </motion.button>
          </form>

          <p className="text-center text-xs text-slate-500 dark:text-gray-500 mt-4">
            {t("auth_terms_pre")}{" "}
            <a href="#" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors">{t("auth_terms_link")}</a>
            {" "}{t("auth_and")}{" "}
            <a href="#" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors">{t("auth_privacy_link")}</a>
          </p>

          <p className="text-center text-sm text-slate-600 dark:text-gray-400 mt-4">
            {t("auth_have_account")}{" "}
            <Link href="/auth/login" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-medium transition-colors">{t("auth_sign_in_link")}</Link>
          </p>
        </div>

        <p className="text-center mt-6">
          <Link href="/" className="text-xs text-slate-500 dark:text-gray-500 hover:text-slate-700 dark:hover:text-gray-300 transition-colors">
            ← {t("auth_back_home")}
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
