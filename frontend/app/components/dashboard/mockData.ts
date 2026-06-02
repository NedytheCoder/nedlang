// ─── Learner Profile ─────────────────────────────────────────────────────────

export interface LearnerProfile {
  firstName: string
  lastName: string
  username: string
  displayName: string
  email: string
  avatarInitials: string
  nativeLanguage: string
  targetLanguage: string
  currentLevel: string
  framework: "CEFR" | "HSK" | "JLPT" | "TOPIK"
  xp: number
  xpCurrentLevel: number
  xpNextLevel: number
  learningStyle: string
  hobbies: string[]
  dailyGoalMinutes: number
}

export const mockProfile: LearnerProfile = {
  firstName: "Alex",
  lastName: "Chen",
  username: "alexchen",
  displayName: "Alex Chen",
  email: "alex@example.com",
  avatarInitials: "AC",
  nativeLanguage: "English",
  targetLanguage: "French",
  currentLevel: "B1",
  framework: "CEFR",
  xp: 8240,
  xpCurrentLevel: 7000,
  xpNextLevel: 10000,
  learningStyle: "Mixed",
  hobbies: ["Technology", "Cooking", "Travel"],
  dailyGoalMinutes: 30,
}

export const FRAMEWORK_LEVELS: Record<string, string[]> = {
  CEFR: ["A1", "A2", "B1", "B2", "C1", "C2"],
  HSK: ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"],
  JLPT: ["N5", "N4", "N3", "N2", "N1"],
  TOPIK: ["TOPIK I-1", "TOPIK I-2", "TOPIK II-3", "TOPIK II-4", "TOPIK II-5", "TOPIK II-6"],
}

// ─── Goal & Lesson ───────────────────────────────────────────────────────────

export const mockGoal = {
  title: "Reach B2 French for relocation to Paris",
  percentComplete: 62,
  estimatedCompletion: "March 2026",
  nextMilestone: "Complete B1.2 Curriculum Assessment",
  targetLevel: "B2",
}

export const mockCurrentLesson = {
  title: "Les verbes pronominaux",
  module: "Module 5: Daily Life Conversations",
  lessonNumber: 3,
  totalLessons: 8,
  estimatedMinutes: 18,
}

// ─── Streaks & Heatmap ───────────────────────────────────────────────────────

export const mockStreak = {
  currentStreak: 23,
  longestStreak: 45,
  totalStudyDays: 187,
  weeklyConsistency: 86,
}

function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 233280
  return x - Math.floor(x)
}

export const heatmapData: number[] = Array.from({ length: 365 }, (_, i) => {
  const r = seededRandom(i)
  if (r > 0.62) return 0
  if (r > 0.45) return 1
  if (r > 0.32) return 2
  if (r > 0.18) return 3
  return 4
})

// ─── Skills ──────────────────────────────────────────────────────────────────

export interface SkillData {
  value: number
  trend: number
}

export const mockSkills: Record<"reading" | "listening" | "speaking" | "writing", SkillData> = {
  reading: { value: 74, trend: 8 },
  listening: { value: 61, trend: 12 },
  speaking: { value: 48, trend: 5 },
  writing: { value: 67, trend: 3 },
}

// ─── Achievements ────────────────────────────────────────────────────────────

export interface Achievement {
  id: string
  icon: string
  earned: boolean
  earnedDate?: string
  progress?: number
  target?: number
  current?: number
}

export const mockAchievements: Achievement[] = [
  { id: "first_convo", icon: "💬", earned: true, earnedDate: "Feb 2024" },
  { id: "hundred_words", icon: "📚", earned: true, earnedDate: "Feb 2024" },
  { id: "streak_7", icon: "🔥", earned: true, earnedDate: "Mar 2024" },
  { id: "vocab_explorer", icon: "🗺️", earned: true, earnedDate: "Mar 2024" },
  { id: "grammar_master", icon: "📝", earned: false, progress: 0.7, target: 10, current: 7 },
  { id: "listening_specialist", icon: "🎧", earned: false, progress: 0.4, target: 20, current: 8 },
  { id: "assessment_champion", icon: "🏆", earned: false, progress: 0.6, target: 5, current: 3 },
  { id: "streak_30", icon: "⚡", earned: false, progress: 0.77, target: 30, current: 23 },
]

// ─── Vocabulary ──────────────────────────────────────────────────────────────

export interface VocabWord {
  word: string
  translation: string
  difficulty?: "easy" | "medium" | "hard"
}

export const mockVocab = {
  total: 1247,
  active: 892,
  retentionRate: 78,
  newPerWeek: 47,
  recent: [
    { word: "se souvenir", translation: "to remember" },
    { word: "néanmoins", translation: "nevertheless" },
    { word: "pourtant", translation: "however" },
    { word: "s'épanouir", translation: "to flourish" },
    { word: "bienveillant", translation: "kind, benevolent" },
  ] as VocabWord[],
  review: [
    { word: "néanmoins", translation: "nevertheless", difficulty: "hard" as const },
    { word: "pourtant", translation: "however", difficulty: "hard" as const },
    { word: "se taire", translation: "to be quiet", difficulty: "medium" as const },
  ] as VocabWord[],
}

// ─── Grammar ─────────────────────────────────────────────────────────────────

export interface GrammarTopic {
  topic: string
  confidence: number
  progress?: number
}

export const mockGrammar = {
  mastered: [
    { topic: "Present Tense", confidence: 92 },
    { topic: "Articles", confidence: 88 },
    { topic: "Basic Adjectives", confidence: 85 },
    { topic: "Negation", confidence: 82 },
  ] as GrammarTopic[],
  learning: [
    { topic: "Passé Composé", confidence: 72, progress: 0.68 },
    { topic: "Pronomial Verbs", confidence: 61, progress: 0.45 },
    { topic: "Object Pronouns", confidence: 58, progress: 0.4 },
  ] as GrammarTopic[],
  review: [
    { topic: "Subjunctive Mood", confidence: 34 },
    { topic: "Conditional Tense", confidence: 48 },
  ] as GrammarTopic[],
}

// ─── Insights ────────────────────────────────────────────────────────────────

export interface Insight {
  type: "strength" | "improvement" | "weakness" | "habit"
  icon: string
  textKey: string
}

export const mockInsights: Insight[] = [
  { type: "strength", icon: "🏆", textKey: "dash_insights_text_reading" },
  { type: "improvement", icon: "📈", textKey: "dash_insights_text_listening" },
  { type: "weakness", icon: "🎯", textKey: "dash_insights_text_adjective" },
  { type: "habit", icon: "💡", textKey: "dash_insights_text_tech" },
]

// ─── Assessments ─────────────────────────────────────────────────────────────

export interface UpcomingAssessment {
  title: string
  typeKey: string
  date: string
  duration: number
}

export interface AssessmentResult {
  date: string
  score: number
  level: string
  typeKey: string
}

export const mockAssessments = {
  upcoming: [
    { title: "B1 Oral Assessment", typeKey: "dash_assess_type_curriculum", date: "Jun 10, 2025", duration: 30 },
    { title: "Monthly Vocabulary Check", typeKey: "dash_assess_type_self", date: "Jun 15, 2025", duration: 15 },
  ] as UpcomingAssessment[],
  history: [
    { date: "May 20, 2025", score: 82, level: "B1", typeKey: "dash_assess_type_curriculum" },
    { date: "May 1, 2025", score: 76, level: "A2+", typeKey: "dash_assess_type_placement" },
    { date: "Apr 15, 2025", score: 91, level: "A2", typeKey: "dash_assess_type_curriculum" },
  ] as AssessmentResult[],
}

// ─── Errors ──────────────────────────────────────────────────────────────────

export const mockErrors = {
  vocabulary: [
    { word: "se souvenir", typeKey: "dash_error_type_unknown", count: 4 },
    { word: "néanmoins", typeKey: "dash_error_type_repeated", count: 7 },
    { word: "pourtant", typeKey: "dash_error_type_repeated", count: 5 },
  ],
  grammar: [
    { topic: "Verb conjugation (subjonctif)", count: 12 },
    { topic: "Gender agreement", count: 9 },
    { topic: "Partitive articles", count: 6 },
  ],
  sentenceStructure: [
    { pattern: "Inversion in questions", count: 8 },
    { pattern: "Object pronoun placement", count: 11 },
  ],
  skills: {
    reading: ["Complex sentence parsing", "Literary vocabulary"],
    listening: ["Connected speech", "Regional accents"],
    speaking: ["Liaisons", "Intonation patterns"],
    writing: ["Formal register", "Subjunctive usage"],
  },
}

// ─── Certification ───────────────────────────────────────────────────────────

export const mockCertification = {
  name: "DELF B1",
  targetExam: "DELF B2",
  readiness: 68,
  estimatedReadyDate: "September 2025",
  strongest: ["Reading comprehension", "Written production"],
  weakest: ["Oral production", "Listening comprehension"],
}

// ─── Stats ───────────────────────────────────────────────────────────────────

export const mockStats = {
  totalHours: 127.5,
  thisWeekHours: 4.2,
  thisMonthHours: 18.7,
  avgDailyMinutes: 32,
  lessonsCompleted: 94,
  assessmentsCompleted: 12,
  conversationsCompleted: 31,
  weeklyHoursData: [2.5, 3.1, 4.8, 2.2, 5.1, 3.7, 4.2],
  weekLabels: ["W47", "W48", "W49", "W50", "W51", "W52", "W1"],
}

// ─── Curriculum ──────────────────────────────────────────────────────────────

export interface CurriculumModule {
  id: number
  title: string
  status: "completed" | "current" | "locked"
  lessons: number
  completedLessons: number
}

export const mockCurriculum: CurriculumModule[] = [
  { id: 1, title: "Absolute Beginners", status: "completed", lessons: 8, completedLessons: 8 },
  { id: 2, title: "Greetings & Introductions", status: "completed", lessons: 6, completedLessons: 6 },
  { id: 3, title: "Daily Routines", status: "completed", lessons: 10, completedLessons: 10 },
  { id: 4, title: "Shopping & Services", status: "completed", lessons: 8, completedLessons: 8 },
  { id: 5, title: "Daily Life Conversations", status: "current", lessons: 8, completedLessons: 2 },
  { id: 6, title: "Work & Professions", status: "locked", lessons: 9, completedLessons: 0 },
  { id: 7, title: "Travel & Transport", status: "locked", lessons: 11, completedLessons: 0 },
  { id: 8, title: "Health & Wellbeing", status: "locked", lessons: 8, completedLessons: 0 },
]

// ─── Actions ─────────────────────────────────────────────────────────────────

export interface RecommendedAction {
  id: number
  type: "review" | "lesson" | "assessment" | "practice" | "grammar"
  icon: string
  titleKey: string
  priority: "high" | "medium" | "low"
  estimatedMinutes: number
}

export const mockActions: RecommendedAction[] = [
  { id: 1, type: "review", icon: "📚", titleKey: "dash_action_review_vocab", priority: "high", estimatedMinutes: 10 },
  { id: 2, type: "lesson", icon: "📖", titleKey: "dash_action_lesson", priority: "high", estimatedMinutes: 18 },
  { id: 3, type: "assessment", icon: "🎧", titleKey: "dash_action_listening", priority: "medium", estimatedMinutes: 12 },
  { id: 4, type: "practice", icon: "🗣️", titleKey: "dash_action_speaking", priority: "medium", estimatedMinutes: 10 },
  { id: 5, type: "grammar", icon: "📝", titleKey: "dash_action_grammar", priority: "low", estimatedMinutes: 8 },
]
