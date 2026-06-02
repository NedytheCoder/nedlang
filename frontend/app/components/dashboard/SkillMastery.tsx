"use client"

import { useTranslation } from "../../../i18n/LanguageProvider"
import { mockSkills, SkillData } from "./mockData"

type SkillKey = "reading" | "listening" | "speaking" | "writing"

// Radar chart with 4 axes (SVG)
function RadarChart({ skills }: { skills: Record<SkillKey, SkillData> }) {
  const cx = 110
  const cy = 110
  const maxR = 80
  const size = 220

  // Angles (degrees): top=reading, right=listening, bottom=writing, left=speaking
  const axes: { key: SkillKey; angle: number }[] = [
    { key: "reading", angle: -90 },
    { key: "listening", angle: 0 },
    { key: "writing", angle: 90 },
    { key: "speaking", angle: 180 },
  ]

  const toXY = (angleDeg: number, r: number) => {
    const rad = (angleDeg * Math.PI) / 180
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
  }

  const gridLevels = [25, 50, 75, 100]

  const dataPoints = axes.map(({ key, angle }) =>
    toXY(angle, (skills[key].value / 100) * maxR)
  )
  const dataPoly = dataPoints.map((p) => `${p.x},${p.y}`).join(" ")

  return (
    <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-[200px] sm:max-w-[220px] mx-auto">
      {/* Grid polygons */}
      {gridLevels.map((lvl) => {
        const pts = axes.map(({ angle }) => toXY(angle, (lvl / 100) * maxR))
        return (
          <polygon
            key={lvl}
            points={pts.map((p) => `${p.x},${p.y}`).join(" ")}
            fill="none"
            stroke="currentColor"
            strokeWidth="0.8"
            className="text-slate-200 dark:text-slate-700"
          />
        )
      })}

      {/* Axes lines */}
      {axes.map(({ key, angle }) => {
        const ep = toXY(angle, maxR)
        return (
          <line
            key={key}
            x1={cx} y1={cy} x2={ep.x} y2={ep.y}
            stroke="currentColor" strokeWidth="0.8"
            className="text-slate-200 dark:text-slate-700"
          />
        )
      })}

      {/* Data polygon */}
      <polygon
        points={dataPoly}
        fill="rgba(99,102,241,0.18)"
        stroke="rgb(99,102,241)"
        strokeWidth="2"
        strokeLinejoin="round"
      />

      {/* Data dots */}
      {dataPoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="4" fill="rgb(99,102,241)" />
      ))}

      {/* Labels */}
      {axes.map(({ key, angle }) => {
        const lp = toXY(angle, maxR + 18)
        return (
          <text
            key={key}
            x={lp.x}
            y={lp.y}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="9"
            fill="currentColor"
            style={{ fill: "rgb(100,116,139)" }}
          >
            {key.charAt(0).toUpperCase() + key.slice(1)}
          </text>
        )
      })}

      {/* % labels at 25/50/75 */}
      {[25, 50, 75].map((lvl) => (
        <text
          key={lvl}
          x={cx + 4}
          y={cy - (lvl / 100) * maxR - 2}
          fontSize="7"
          fill="currentColor"
          style={{ fill: "rgb(148,163,184)" }}
        >
          {lvl}%
        </text>
      ))}
    </svg>
  )
}

export default function SkillMastery() {
  const { t } = useTranslation()

  const skillList: { key: SkillKey; icon: string; labelKey: string; color: string }[] = [
    { key: "reading", icon: "📖", labelKey: "dash_skill_reading", color: "text-blue-500" },
    { key: "listening", icon: "🎧", labelKey: "dash_skill_listening", color: "text-violet-500" },
    { key: "speaking", icon: "🗣️", labelKey: "dash_skill_speaking", color: "text-orange-500" },
    { key: "writing", icon: "✍️", labelKey: "dash_skill_writing", color: "text-emerald-500" },
  ]

  const sorted = [...skillList].sort((a, b) => mockSkills[b.key].value - mockSkills[a.key].value)
  const strongest = sorted[0]
  const weakest = sorted[sorted.length - 1]

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_skill_title")}</p>
        <div className="flex gap-3 text-xs">
          <span className="text-emerald-600 dark:text-emerald-400">↑ {t("dash_skill_strength")}: {t(`dash_skill_${strongest.key}`)}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
        {/* Radar chart */}
        <RadarChart skills={mockSkills} />

        {/* Skill bars */}
        <div className="space-y-3">
          {skillList.map(({ key, icon, labelKey, color }) => {
            const { value, trend } = mockSkills[key]
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{icon}</span>
                    <span className="text-xs font-medium text-slate-700 dark:text-gray-300">{t(labelKey)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-emerald-500 font-medium">+{trend}%</span>
                    <span className={`text-sm font-bold ${color}`}>{value}%</span>
                  </div>
                </div>
                <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full transition-all"
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            )
          })}

          {/* Focus area */}
          <div className="mt-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-100 dark:border-amber-500/20 rounded-xl p-3">
            <p className="text-xs text-amber-700 dark:text-amber-300">
              <span className="font-semibold">{t("dash_skill_focus")}: </span>
              {t(`dash_skill_${weakest.key}`)} — {mockSkills[weakest.key].value}%
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
