const SESSION_KEY    = "nedlang_test_session"
const EXPIRY_MS      = 2 * 60 * 60 * 1000  // 2 hours

export type Skill = "reading" | "listening" | "writing" | "speaking"

export interface SkillData {
  questions:  unknown[]
  responses:  unknown[]
  complete:   boolean
}

export interface TestSession {
  session_id:  string
  started_at:  string   // ISO
  reading:     SkillData | null
  listening:   SkillData | null
  writing:     SkillData | null
  speaking:    SkillData | null
}

function uuid(): string {
  return typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export function getSession(): TestSession | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    return JSON.parse(raw) as TestSession
  } catch {
    return null
  }
}

export function createSession(): TestSession {
  const session: TestSession = {
    session_id: uuid(),
    started_at: new Date().toISOString(),
    reading:    null,
    listening:  null,
    writing:    null,
    speaking:   null,
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
  return session
}

export function saveSession(session: TestSession): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY)
}

export function isExpired(session: TestSession): boolean {
  return Date.now() - new Date(session.started_at).getTime() > EXPIRY_MS
}

/** Returns the first incomplete skill, or "complete" if all 4 are done. */
export function currentSkill(session: TestSession): Skill | "complete" {
  const order: Skill[] = ["reading", "listening", "writing", "speaking"]
  for (const s of order) {
    if (!session[s]?.complete) return s
  }
  return "complete"
}

export function updateSkillQuestions(skill: Skill, questions: unknown[]): void {
  const session = getSession()
  if (!session) return
  session[skill] = { questions, responses: session[skill]?.responses ?? [], complete: false }
  saveSession(session)
}

export function updateSkillResponses(skill: Skill, responses: unknown[]): void {
  const session = getSession()
  if (!session) return
  session[skill] = {
    questions: session[skill]?.questions ?? [],
    responses,
    complete:  false,
  }
  saveSession(session)
}

export function completeSkill(skill: Skill): void {
  const session = getSession()
  if (!session) return
  session[skill] = {
    questions: session[skill]?.questions ?? [],
    responses: session[skill]?.responses ?? [],
    complete:  true,
  }
  saveSession(session)
}
