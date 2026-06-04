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
  audio_url: string | null
  tts_status: string
}

export interface AssessmentResponse {
  questionId: string
  selectedAnswer: string
}
