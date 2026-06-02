"use client"

import { useState } from "react"
import { useTranslation } from "../../../../i18n/LanguageProvider"
import { StepProps } from "./types"

function getPasswordStrength(pw: string): 0 | 1 | 2 | 3 | 4 {
  if (!pw) return 0
  let score = 0
  if (pw.length >= 8) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  return score as 0 | 1 | 2 | 3 | 4
}

export default function StepAccount({ data, onChange, errors }: StepProps) {
  const { t } = useTranslation()
  const [showPw, setShowPw] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const strength = getPasswordStrength(data.password)
  const strengthBars = ["", "bg-red-500", "bg-orange-400", "bg-yellow-400", "bg-green-500"]
  const strengthLabels = ["", "onb_pw_weak", "onb_pw_fair", "onb_pw_good", "onb_pw_strong"]
  const strengthTextColors = ["", "text-red-500", "text-orange-500", "text-yellow-600", "text-green-600"]

  const inputCls = (field: string) =>
    `w-full bg-slate-50 dark:bg-slate-800 border ${
      errors[field]
        ? "border-red-400 dark:border-red-500 focus:ring-red-400/20"
        : "border-slate-200 dark:border-white/10 focus:border-indigo-500 dark:focus:border-indigo-500/60 focus:ring-indigo-500/20"
    } focus:outline-none focus:ring-2 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 transition-all`

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">{t("onb_acct_title")}</h2>
        <p className="text-sm text-slate-500 dark:text-gray-400">{t("onb_acct_subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
            {t("onb_first_name")} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder={t("onb_first_name_ph")}
            value={data.first_name}
            onChange={(e) => onChange({ first_name: e.target.value })}
            className={inputCls("first_name")}
          />
          {errors.first_name && <p className="mt-1 text-xs text-red-500">{errors.first_name}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
            {t("onb_last_name")} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder={t("onb_last_name_ph")}
            value={data.last_name}
            onChange={(e) => onChange({ last_name: e.target.value })}
            className={inputCls("last_name")}
          />
          {errors.last_name && <p className="mt-1 text-xs text-red-500">{errors.last_name}</p>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
          {t("auth_email")} <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          placeholder={t("auth_email_placeholder")}
          value={data.email}
          onChange={(e) => onChange({ email: e.target.value })}
          className={inputCls("email")}
        />
        {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
          {t("auth_password")} <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <input
            type={showPw ? "text" : "password"}
            placeholder={t("auth_password_placeholder")}
            value={data.password}
            onChange={(e) => onChange({ password: e.target.value })}
            className={`${inputCls("password")} pr-16`}
          />
          <button
            type="button"
            onClick={() => setShowPw((s) => !s)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 font-medium transition-colors"
          >
            {showPw ? t("onb_hide") : t("onb_show")}
          </button>
        </div>
        {data.password && (
          <div className="mt-2 space-y-1">
            <div className="flex gap-1">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className={`flex-1 h-1 rounded-full transition-all duration-300 ${
                    i <= strength ? strengthBars[strength] : "bg-slate-200 dark:bg-slate-600"
                  }`}
                />
              ))}
            </div>
            <p className="text-xs text-slate-500 dark:text-gray-400">
              {t("onb_pw_strength")}:{" "}
              <span className={`font-medium ${strengthTextColors[strength]}`}>
                {strength > 0 ? t(strengthLabels[strength]) : ""}
              </span>
            </p>
          </div>
        )}
        {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
          {t("auth_confirm_password")} <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <input
            type={showConfirm ? "text" : "password"}
            placeholder={t("auth_confirm_placeholder")}
            value={data.confirm_password}
            onChange={(e) => onChange({ confirm_password: e.target.value })}
            className={`${inputCls("confirm_password")} pr-16`}
          />
          <button
            type="button"
            onClick={() => setShowConfirm((s) => !s)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 font-medium transition-colors"
          >
            {showConfirm ? t("onb_hide") : t("onb_show")}
          </button>
        </div>
        {errors.confirm_password && <p className="mt-1 text-xs text-red-500">{errors.confirm_password}</p>}
      </div>
    </div>
  )
}
