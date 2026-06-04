"use client"

import { useState } from "react"
import Link from "next/link"
import { useTheme } from "next-themes"
import { motion, AnimatePresence } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"

interface ProfileProps {
  avatarInitials: string
  displayName: string
  username: string
  targetLanguage: string
  currentLevel: string
}

export default function DashboardNav({ profile }: { profile: ProfileProps }) {
  const { t } = useTranslation()
  const { theme, setTheme } = useTheme()
  const [open, setOpen] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-white/8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/30">
                <GiEarthAfricaEurope className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                NedLang
              </span>
            </Link>

            {/* Desktop nav links */}
            <nav className="hidden md:flex items-center gap-1">
              {[
                { href: "/dashboard", labelKey: "dash_nav_dashboard" },
                { href: "#", labelKey: "dash_nav_lessons" },
                { href: "#", labelKey: "dash_nav_practice" },
              ].map(({ href, labelKey }) => (
                <Link
                  key={labelKey}
                  href={href}
                  className="px-4 py-2 text-sm font-medium rounded-lg text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
                >
                  {t(labelKey)}
                </Link>
              ))}
            </nav>

            {/* Right: profile + mobile menu */}
            <div className="flex items-center gap-2">
              {/* Mobile menu toggle */}
              <button
                className="md:hidden p-2 rounded-lg text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                onClick={() => setMobileOpen(true)}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              {/* Profile dropdown */}
              <div className="relative">
                {open && <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />}
                <button
                  onClick={() => setOpen(!open)}
                  className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                    {profile.avatarInitials}
                  </div>
                  <div className="hidden sm:block text-left">
                    <p className="text-xs font-semibold text-slate-900 dark:text-white leading-tight">{profile.displayName}</p>
                    <p className="text-xs text-slate-500 dark:text-gray-400 leading-tight">
                      {profile.targetLanguage} · {profile.currentLevel}
                    </p>
                  </div>
                  <svg className="w-3.5 h-3.5 text-slate-400 hidden sm:block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <AnimatePresence>
                  {open && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95, y: -4 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95, y: -4 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 top-full mt-2 w-72 z-20 bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-2xl shadow-xl overflow-hidden"
                    >
                      {/* User header */}
                      <div className="px-4 py-4 bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 border-b border-slate-100 dark:border-white/8">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold">
                            {profile.avatarInitials}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">{profile.displayName}</p>
                            <p className="text-xs text-slate-500 dark:text-gray-400">@{profile.username}</p>
                            <p className="text-xs text-indigo-600 dark:text-indigo-400 font-medium mt-0.5">
                              {profile.targetLanguage} · {profile.currentLevel}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Menu items */}
                      <div className="p-2">
                        {[
                          { key: "dash_nav_view_profile", icon: "👤" },
                          { key: "dash_nav_edit_profile", icon: "✏️" },
                          { key: "dash_nav_change_username", icon: "🔤" },
                          { key: "dash_nav_display_name", icon: "📛" },
                          { key: "dash_nav_settings", icon: "⚙️" },
                        ].map(({ key, icon }) => (
                          <button
                            key={key}
                            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-xl transition-colors text-left"
                          >
                            <span>{icon}</span>
                            {t(key)}
                          </button>
                        ))}
                      </div>

                      {/* Theme switcher */}
                      <div className="px-3 py-2 border-t border-slate-100 dark:border-white/8">
                        <p className="text-xs font-medium text-slate-400 dark:text-gray-500 mb-2 px-1">{t("dash_nav_theme")}</p>
                        <div className="flex gap-1">
                          {[
                            { value: "light", key: "dash_nav_theme_light", icon: "☀️" },
                            { value: "dark", key: "dash_nav_theme_dark", icon: "🌙" },
                            { value: "system", key: "dash_nav_theme_system", icon: "💻" },
                          ].map(({ value, key, icon }) => (
                            <button
                              key={value}
                              onClick={() => setTheme(value)}
                              className={`flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg transition-all ${
                                theme === value
                                  ? "bg-indigo-600 text-white"
                                  : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-slate-600"
                              }`}
                            >
                              <span>{icon}</span>
                              {t(key)}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Logout */}
                      <div className="p-2 border-t border-slate-100 dark:border-white/8">
                        <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-colors text-left">
                          <span>🚪</span>
                          {t("dash_nav_logout")}
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile menu overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/50"
              onClick={() => setMobileOpen(false)}
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 bottom-0 z-50 w-72 bg-white dark:bg-slate-900 shadow-2xl p-6"
            >
              <div className="flex justify-between items-center mb-6">
                <p className="font-semibold text-slate-900 dark:text-white">{t("dash_nav_menu")}</p>
                <button onClick={() => setMobileOpen(false)} className="p-1 text-slate-400">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <nav className="space-y-1">
                {[
                  { href: "/dashboard", labelKey: "dash_nav_dashboard" },
                  { href: "#", labelKey: "dash_nav_lessons" },
                  { href: "#", labelKey: "dash_nav_practice" },
                ].map(({ href, labelKey }) => (
                  <Link
                    key={labelKey}
                    href={href}
                    onClick={() => setMobileOpen(false)}
                    className="block px-4 py-2.5 text-sm font-medium text-slate-700 dark:text-gray-300 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 rounded-xl transition-colors"
                  >
                    {t(labelKey)}
                  </Link>
                ))}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
