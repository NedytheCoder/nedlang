export interface Example {
  sentence: string
  translation: string
  note?: string
}

export interface DialogueLine {
  speaker: string
  line: string
  translation: string
}

export interface VocabItem {
  word: string
  translation: string
  example: string
}

export type ExerciseType = "fill_in_blank" | "translation" | "construction" | "matching"

export interface Exercise {
  type: ExerciseType
  instruction: string
  prompt: string
  answer: string
}

export interface QuizItem {
  question: string
  options: { A: string; B: string; C: string; D: string }
  correct: "A" | "B" | "C" | "D"
}

export interface DialogueReinforcementItem {
  role: string
  prompt: string
  suggested_response: string
}

export interface SpeakingItem {
  task: string
  prompt: string
  example_response: string
}

export interface ListeningItem {
  scenario: string
  transcript: string
  question: string
  answer: string
}

export interface ReadingItem {
  passage: string
  question: string
  answer: string
}

export interface WritingItem {
  task: string
  prompt: string
  word_count_guide: string
  model_answer: string
}

export interface ReflectionItem {
  question: string
  hint?: string
}

export type ReinforcementType =
  | "quiz"
  | "dialogue"
  | "speaking"
  | "listening"
  | "reading"
  | "writing"
  | "reflection"
  | "none"

export type Reinforcement =
  | { type: "quiz";       content: QuizItem[] }
  | { type: "dialogue";   content: DialogueReinforcementItem[] }
  | { type: "speaking";   content: SpeakingItem[] }
  | { type: "listening";  content: ListeningItem[] }
  | { type: "reading";    content: ReadingItem[] }
  | { type: "writing";    content: WritingItem[] }
  | { type: "reflection"; content: ReflectionItem[] }
  | { type: "none";       content: [] }

export interface Lesson {
  lesson_title: string
  introduction: string
  core_explanation: string
  examples: Example[]
  dialogues: DialogueLine[]
  vocabulary: VocabItem[]
  exercises: Exercise[]
  reinforcement: Reinforcement
  summary: string
  level?: string
  topic?: string
  framework?: string
}
