// Structured to match the output of the onboarding wizard.
// Replace with real session/cookie data in production.

export interface ReceptionUser {
  firstName: string
  nativeLanguage: { code: string; name: string; flag: string }
  targetLanguage: { code: string; name: string; flag: string }
  learningGoal: string
  hobbies: string[]
  learningStyle: string
  dailyGoalMinutes: number
}

export const mockReceptionUser: ReceptionUser = {
  firstName: "Alex",
  nativeLanguage: { code: "en", name: "English", flag: "🇬🇧" },
  targetLanguage: { code: "fr", name: "French", flag: "🇫🇷" },
  learningGoal: "Reach B2 French for relocation to Paris",
  hobbies: ["Technology", "Cooking", "Travel"],
  learningStyle: "Mixed",
  dailyGoalMinutes: 30,
}
