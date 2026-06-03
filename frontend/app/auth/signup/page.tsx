"use client"

import { useState } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"
import { OnboardingData, INITIAL_DATA, TOTAL_STEPS } from "./components/types"
import ProgressBar from "./components/ProgressBar"
import StepAccount from "./components/StepAccount"
import StepLanguage from "./components/StepLanguage"
import StepMotivation from "./components/StepMotivation"
import StepInterests from "./components/StepInterests"
import StepPreferences from "./components/StepPreferences"
import StepSummary from "./components/StepSummary"

function validateStep(
  step: number,
  data: OnboardingData,
  t: (k: string) => string
): Record<string, string> {
  const e: Record<string, string> = {}

  if (step === 0) {
    if (!data.first_name || data.first_name.trim().length < 2) e.first_name = t("onb_val_name_min")
    if (!data.last_name || data.last_name.trim().length < 2) e.last_name = t("onb_val_name_min")
    if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) e.email = t("onb_val_email")
    if (!data.password || data.password.length < 8) {
      e.password = t("onb_val_pw_min")
    } else if (new TextEncoder().encode(data.password).length > 72) {
      e.password = t("onb_val_pw_too_long")
    } else {
      let strength = 0
      if (data.password.length >= 8) strength++
      if (/[A-Z]/.test(data.password)) strength++
      if (/[0-9]/.test(data.password)) strength++
      if (/[^A-Za-z0-9]/.test(data.password)) strength++
      if (strength < 3) e.password = t("onb_val_pw_strength")
    }
    if (!data.confirm_password || data.password !== data.confirm_password) e.confirm_password = t("onb_val_pw_match")
  }

  if (step === 1) {
    if (!data.native_language) e.native_language = t("onb_val_required")
    if (!data.target_language) e.target_language = t("onb_val_required")
    if (data.native_language && data.target_language && data.native_language === data.target_language) {
      e.target_language = t("onb_lang_same_err")
    }
  }

  if (step === 2) {
    if (!data.learning_goal || data.learning_goal.trim().length < 20) e.learning_goal = t("onb_motiv_val")
  }

  if (step === 3) {
    if (data.top_hobbies.length !== 3) e.top_hobbies = t("onb_interests_val")
  }

  if (step === 4) {
    if (!data.preferred_learning_style) e.preferred_learning_style = t("onb_prefs_val_style")
    if (!data.daily_goal_minutes) e.daily_goal_minutes = t("onb_prefs_val_goal")
  }

  return e
}

const variants = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
}

export default function SignupPage() {
  const { t } = useTranslation()
  const [step, setStep] = useState(0)
  const [dir, setDir] = useState(1)
  const [data, setData] = useState<OnboardingData>(INITIAL_DATA)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  const handleChange = (updates: Partial<OnboardingData>) => {
    setData((prev) => ({ ...prev, ...updates }))
    setErrors((prev) => {
      const next = { ...prev }
      Object.keys(updates).forEach((k) => delete next[k])
      return next
    })
  }

  const handleNext = () => {
    const newErrors = validateStep(step, data, t)
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    setDir(1)
    setStep((s) => s + 1)
    setErrors({})
  }

  const handleBack = () => {
    setDir(-1)
    setStep((s) => s - 1)
    setErrors({})
  }

  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState("")

  const handleSubmit = async () => {
    setSubmitting(true)
    setSubmitError("")
    try {
      const res = await fetch(`${backendUrl}/user/registration`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          password: data.password,
          native_language: data.native_language,
          target_language: data.target_language,
          learning_goal: data.learning_goal,
          top_hobbies: data.top_hobbies,
          preferred_learning_style: data.preferred_learning_style,
          daily_goal_minutes: data.daily_goal_minutes,
        }),
      })
      const body = await res.json()
      if (!res.ok) {
        setSubmitError(body.detail ?? "Registration failed. Please try again.")
        return
      }
      // TODO: redirect to dashboard or login
      console.log("Registered:", body)
    } catch {
      setSubmitError("Could not reach the server. Please try again.")
    } finally {
      setSubmitting(false)
    }
  }

  const isFinal = step === TOTAL_STEPS - 1
  const sharedProps = { data, onChange: handleChange, errors }

  const renderStep = () => {
    switch (step) {
      case 0: return <StepAccount {...sharedProps} />
      case 1: return <StepLanguage {...sharedProps} />
      case 2: return <StepMotivation {...sharedProps} />
      case 3: return <StepInterests {...sharedProps} />
      case 4: return <StepPreferences {...sharedProps} />
      case 5: return <StepSummary data={data} />
      default: return null
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4 py-10">
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-violet-600/8 dark:bg-violet-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-indigo-600/8 dark:bg-indigo-600/10 rounded-full blur-3xl" />
      </div>

      <motion.div
        className="relative w-full max-w-lg"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="text-center mb-6">
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
          <ProgressBar currentStep={step} />

          <div className="overflow-hidden">
            <AnimatePresence mode="wait" custom={dir}>
              <motion.div
                key={step}
                custom={dir}
                variants={variants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{ duration: 0.22, ease: "easeOut" }}
              >
                {renderStep()}
              </motion.div>
            </AnimatePresence>
          </div>

          {submitError && (
            <p className="mt-4 text-sm text-red-500 text-center">{submitError}</p>
          )}

          <div className={`flex mt-8 gap-3 ${step > 0 ? "justify-between" : "justify-end"}`}>
            {step > 0 && (
              <motion.button
                type="button"
                onClick={handleBack}
                disabled={submitting}
                className="px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-gray-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-all disabled:opacity-50"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ← {t("onb_back")}
              </motion.button>
            )}
            <motion.button
              type="button"
              onClick={isFinal ? handleSubmit : handleNext}
              disabled={submitting}
              className="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all disabled:opacity-60"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isFinal ? (submitting ? "Creating account…" : t("onb_summary_cta")) : `${t("onb_next")} →`}
            </motion.button>
          </div>
        </div>

        <div className="flex items-center justify-between mt-5 px-1">
          <Link href="/" className="text-xs text-slate-500 dark:text-gray-500 hover:text-slate-700 dark:hover:text-gray-300 transition-colors">
            ← {t("auth_back_home")}
          </Link>
          {step === 0 && (
            <p className="text-xs text-slate-600 dark:text-gray-400">
              {t("auth_have_account")}{" "}
              <Link href="/auth/login" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 font-medium transition-colors">
                {t("auth_sign_in_link")}
              </Link>
            </p>
          )}
        </div>
      </motion.div>
    </div>
  )
}
