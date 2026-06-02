export type LearningStyle = "reading" | "listening" | "speaking" | "writing" | "mixed" | ""

export interface OnboardingData {
  // Step 1 – Account
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string

  // Step 2 – Language Profile
  native_language: string
  target_language: string

  // Step 3 – Motivation
  learning_goal: string

  // Step 4 – Interests
  top_hobbies: string[]

  // Step 5 – Preferences
  preferred_learning_style: LearningStyle
  daily_goal_minutes: number | null
}

export const INITIAL_DATA: OnboardingData = {
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  confirm_password: "",
  native_language: "",
  target_language: "",
  learning_goal: "",
  top_hobbies: [],
  preferred_learning_style: "",
  daily_goal_minutes: null,
}

export const TOTAL_STEPS = 6

export interface StepProps {
  data: OnboardingData
  onChange: (updates: Partial<OnboardingData>) => void
  errors: Record<string, string>
}
