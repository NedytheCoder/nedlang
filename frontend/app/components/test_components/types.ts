export interface Question {
  question_no: number
  question_level: string
  question_type: string
  question_skill: string
  question_passage: string
  options: string[]
  answer: string
}

export interface ListeningQuestion {
  question_no: number
  question_level: string
  question_type: string
  question_skill: string
  transcript: string
  question: string
  options: string[]
  correct_answer: string
  audio_b64: string
  tts_status: "ready" | "failed"
}

export interface AssessmentResponse {
  questionId: string
  selectedAnswer: string
}
