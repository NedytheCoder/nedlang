// Structured to match the output of the onboarding wizard.
// Replace with real session/cookie data in production.

export interface ReceptionUser {
  firstName: string
  nativeLanguage: { code: string; name: string; flag: string }
  targetLanguage: { code: string; name: string; flag: string }
  learningGoal: string
  selectedMotivations: string[]
  hobbies: string[]
  learningStyle: string
  dailyGoalMinutes: number
}
