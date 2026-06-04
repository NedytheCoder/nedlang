"use client"

import { useTranslation } from "../../../i18n/LanguageProvider"

export interface GrammarTopic {
  topic: string
  confidence_score: number
  progress?: number
}

function ConfidenceBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs font-semibold w-8 text-right text-slate-600 dark:text-gray-400">{value}%</span>
    </div>
  )
}

function TopicSection({
  titleKey,
  topics,
  color,
  badgeColor,
  showProgress,
}: {
  titleKey: string
  topics: GrammarTopic[]
  color: string
  badgeColor: string
  showProgress?: boolean
}) {
  const { t } = useTranslation()
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className={`w-2 h-2 rounded-full ${badgeColor}`} />
        <p className="text-xs font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wide">
          {t(titleKey)} <span className="text-slate-400 dark:text-gray-500 font-normal normal-case">({topics.length})</span>
        </p>
      </div>
      <div className="space-y-3">
        {topics.map((topic) => (
          <div key={topic.topic}>
            <div className="flex justify-between mb-1">
              <span className="text-xs text-slate-700 dark:text-gray-300 leading-tight">{topic.topic}</span>
              {showProgress && topic.progress !== undefined && (
                <span className="text-xs text-slate-400">{Math.round(topic.progress * 100)}%</span>
              )}
            </div>
            <ConfidenceBar value={topic.confidence_score} color={color} />
          </div>
        ))}
      </div>
    </div>
  )
}

interface Props {
  grammar: { mastered: GrammarTopic[]; learning: GrammarTopic[]; review: GrammarTopic[] }
}

export default function GrammarAnalytics({ grammar }: Props) {
  const { t } = useTranslation()

  const total = grammar.mastered.length + grammar.learning.length + grammar.review.length
  const masteredPct = total > 0 ? Math.round((grammar.mastered.length / total) * 100) : 0

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl p-5 sm:p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <span className="text-base">📝</span>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("dash_grammar_title")}</p>
        </div>
        <span className="text-xs bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 px-2 py-1 rounded-lg font-medium border border-emerald-100 dark:border-emerald-500/20">
          {masteredPct}% {t("dash_grammar_mastered_short")}
        </span>
      </div>

      {/* Overview bar */}
      <div className="flex h-2 rounded-full overflow-hidden mb-5 gap-0.5">
        <div className="bg-emerald-400 rounded-l-full transition-all" style={{ width: `${(grammar.mastered.length / total) * 100}%` }} />
        <div className="bg-indigo-400 transition-all" style={{ width: `${(grammar.learning.length / total) * 100}%` }} />
        <div className="bg-amber-400 rounded-r-full transition-all" style={{ width: `${(grammar.review.length / total) * 100}%` }} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <TopicSection
          titleKey="dash_grammar_mastered"
          topics={grammar.mastered}
          color="bg-emerald-400"
          badgeColor="bg-emerald-400"
        />
        <TopicSection
          titleKey="dash_grammar_learning"
          topics={grammar.learning}
          color="bg-indigo-400"
          badgeColor="bg-indigo-400"
          showProgress
        />
        <TopicSection
          titleKey="dash_grammar_review"
          topics={grammar.review}
          color="bg-amber-400"
          badgeColor="bg-amber-400"
        />
      </div>
    </div>
  )
}
