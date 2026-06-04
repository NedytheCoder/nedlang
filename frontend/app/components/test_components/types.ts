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

export interface WritingQuestion {
  question_no: number
  question_level: string
  question_type: string   // "writing_task"
  task_prompt: string
  word_count_guide: string
}

export interface WritingResponse {
  questionId: string
  response: string
}

export interface SpeakingQuestion {
  question_no: number
  question_level: string
  question_type: string   // "speaking_task"
  task_prompt: string
  prep_time_seconds: number
  response_time_seconds: number
}

export interface SpeakingResponse {
  questionId: string
  audio_b64: string
  duration_seconds: number
}

export interface AssessmentResponse {
  questionId: string
  selectedAnswer: string
}
