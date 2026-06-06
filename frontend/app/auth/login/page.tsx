"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { GiEarthAfricaEurope } from "react-icons/gi"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function LoginPage() {
  const { t } = useTranslation()
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSubmitting(true)
    try {
      const res = await fetch(`${BACKEND_URL}/user/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      const body = await res.json()
      if (!res.ok) {
        setError(body.detail ?? "Login failed. Please try again.")
        return
      }
      localStorage.setItem("nedlang_user_id", body.id)
      router.push("/dashboard")
    } catch {
      setError("Could not reach the server. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4 py-16">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-indigo-600/8 dark:bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/3 w-80 h-80 bg-violet-600/8 dark:bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      <motion.div
        className="relative w-full max-w-md"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <GiEarthAfricaEurope className="w-5 h-5 text-white" />
            </div>
            <span className="text-slate-900 dark:text-white font-bold text-xl tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
              NedLang
            </span>
          </Link>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-8 shadow-xl shadow-slate-200/50 dark:shadow-black/40">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{t("auth_login_title")}</h1>
            <p className="text-slate-600 dark:text-gray-400 text-sm">{t("auth_login_subtitle")}</p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
                {t("auth_email")}
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setError("") }}
                placeholder={t("auth_email_placeholder")}
                required
                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all"
              />
            </div>

            <div>
              <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 mb-1.5">
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300">
                  {t("auth_password")}
                </label>
                <a href="#" className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors shrink-0">
                  {t("auth_forgot")}
                </a>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setError("") }}
                placeholder={t("auth_password_placeholder")}
                required
                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all"
              />
            </div>

            {error && (
              <p className="text-sm text-red-500 text-center">{error}</p>
            )}

            <motion.button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 mt-2 disabled:opacity-60"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              {submitting ? "Signing in…" : t("auth_sign_in")}
            </motion.button>
          </form>

          <p className="text-center text-sm text-slate-600 dark:text-gray-400 mt-6">
            {t("auth_no_account")}{" "}
            <Link href="/auth/signup" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 font-medium transition-colors">
              {t("auth_sign_up_link")}
            </Link>
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
