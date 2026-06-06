"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import DashboardNav from "../components/dashboard/DashboardNav"
import HeroProgress from "../components/dashboard/HeroProgress"
import LevelCard from "../components/dashboard/LevelCard"
import StreakCard from "../components/dashboard/StreakCard"
import SkillMastery from "../components/dashboard/SkillMastery"
import Achievements from "../components/dashboard/Achievements"
import VocabularyAnalytics from "../components/dashboard/VocabularyAnalytics"
import GrammarAnalytics from "../components/dashboard/GrammarAnalytics"
import PersonalizedInsights from "../components/dashboard/PersonalizedInsights"
import Assessments from "../components/dashboard/Assessments"
import ErrorAnalysis from "../components/dashboard/ErrorAnalysis"
import CertificationProgress from "../components/dashboard/CertificationProgress"
import LearningStats from "../components/dashboard/LearningStats"
import CurriculumProgress from "../components/dashboard/CurriculumProgress"
import RecommendedActions from "../components/dashboard/RecommendedActions"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function DashboardPage() {
  const router = useRouter()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    const uiLang = localStorage.getItem("fc_ui_lang") || "en"
    if (!userId) { router.replace("/auth/signup"); return }

    fetch(`${BACKEND_URL}/user/dashboard/${userId}?ui_lang=${uiLang}`)
      .then((r) => { if (!r.ok) throw new Error(); return r.json() })
      .then(setData)
      .catch(() => router.replace("/auth/signup"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <GiEarthAfricaEurope className="w-5 h-5 text-white" />
          </div>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1.4, ease: "linear" }}
            className="w-8 h-8 rounded-full border-4 border-indigo-200 dark:border-indigo-900 border-t-indigo-600"
          />
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <DashboardNav profile={data.profile} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        <HeroProgress goal={data.goal} currentLesson={data.currentLesson} nextNodeId={data.nextNodeId} />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <LevelCard profile={data.profile} />
          <div className="lg:col-span-2"><StreakCard streak={data.streak} heatmapData={data.heatmapData} /></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2"><SkillMastery skills={data.skills} /></div>
          <Achievements achievements={data.achievements} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <VocabularyAnalytics vocab={data.vocab} />
          <div className="lg:col-span-2"><GrammarAnalytics grammar={data.grammar} /></div>
        </div>
        <PersonalizedInsights insights={data.insights} />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2"><Assessments assessments={data.assessments} /></div>
          <ErrorAnalysis errors={data.errors} />
        </div>
        <CertificationProgress certification={data.certification} />
        <LearningStats stats={data.stats} />
        <CurriculumProgress curriculum={data.curriculum} />
        <RecommendedActions actions={data.actions} />
      </main>
    </div>
  )
}
