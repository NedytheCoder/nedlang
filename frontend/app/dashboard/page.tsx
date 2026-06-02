"use client"

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
import { mockProfile } from "../components/dashboard/mockData"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <DashboardNav profile={mockProfile} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">

        {/* ── Hero ───────────────────────────────────────────────────────── */}
        <HeroProgress />

        {/* ── Level + Streak ──────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <LevelCard />
          <div className="lg:col-span-2">
            <StreakCard />
          </div>
        </div>

        {/* ── Skill Mastery + Achievements ────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            <SkillMastery />
          </div>
          <Achievements />
        </div>

        {/* ── Vocab + Grammar ─────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <VocabularyAnalytics />
          <div className="lg:col-span-2">
            <GrammarAnalytics />
          </div>
        </div>

        {/* ── AI Insights ─────────────────────────────────────────────────── */}
        <PersonalizedInsights />

        {/* ── Assessments + Error Analysis ────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            <Assessments />
          </div>
          <ErrorAnalysis />
        </div>

        {/* ── Certification ───────────────────────────────────────────────── */}
        <CertificationProgress />

        {/* ── Learning Stats ──────────────────────────────────────────────── */}
        <LearningStats />

        {/* ── Curriculum Progress ─────────────────────────────────────────── */}
        <CurriculumProgress />

        {/* ── Recommended Actions ─────────────────────────────────────────── */}
        <RecommendedActions />

      </main>
    </div>
  )
}
