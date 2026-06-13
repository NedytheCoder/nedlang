import asyncio
import base64
import json
import os
import tempfile
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from database.script import get_connection

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ─── Request models ───────────────────────────────────────────────────────────

class ReadingGradingRequest(BaseModel):
    framework: str
    questions: list[dict]   # [{question_no, question_level, answer, ...}]
    responses: list[dict]   # [{questionId, selectedAnswer}]


class ListeningGradingRequest(BaseModel):
    framework: str
    questions: list[dict]   # [{question_no, question_level, correct_answer, ...}]
    responses: list[dict]   # [{questionId, selectedAnswer}]


class WritingGradingRequest(BaseModel):
    framework: str
    target_language: str
    native_language: str
    questions: list[dict]   # [{question_no, question_level, task_prompt, word_count_guide}]
    responses: list[dict]   # [{questionId, response}]


class SpeakingGradingRequest(BaseModel):
    framework: str
    target_language: str
    native_language: str
    questions: list[dict]   # [{question_no, question_level, task_prompt, ...}]
    responses: list[dict]   # [{questionId, audio_b64, duration_seconds}]


class SaveGradingRequest(BaseModel):
    user_id:    str
    session_id: str
    reading:   dict | None = None
    listening: dict | None = None
    writing:   dict | None = None
    speaking:  dict | None = None


# ─── Level ordering ───────────────────────────────────────────────────────────

_LEVEL_ORDER: dict[str, list[str]] = {
    "CEFR":  ["A1", "A2", "B1", "B2", "C1", "C2"],
    "HSK":   ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"],
    "JLPT":  ["N5", "N4", "N3", "N2", "N1"],
    "TOPIK": ["TOPIK1", "TOPIK2", "TOPIK3", "TOPIK4", "TOPIK5", "TOPIK6"],
}

_LANG_NAMES: dict[str, str] = {
    "en": "English", "fr": "French",    "de": "German",   "es": "Spanish",
    "it": "Italian", "pt": "Portuguese","zh": "Chinese",  "ja": "Japanese",
    "ko": "Korean",  "ar": "Arabic",    "ru": "Russian",  "nl": "Dutch",
    "pl": "Polish",  "sv": "Swedish",   "tr": "Turkish",  "hi": "Hindi",
}


def _lang_name(code: str) -> str:
    return _LANG_NAMES.get(code.lower(), code)


def _validate_framework(framework: str) -> str:
    fw = framework.upper()
    if fw not in _LEVEL_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported framework '{framework}'. Accepted: {', '.join(_LEVEL_ORDER)}"
        )
    return fw


def _estimate_level_mcq(per_level: list[dict], framework: str) -> str:
    """
    Walk ordered levels from easiest to hardest.
    The estimated level is the highest level where the learner scored >= 50%.
    Falls back to the first (easiest) level if nothing passes.
    """
    ordered  = _LEVEL_ORDER.get(framework, [])
    if not ordered:
        return "A1"
    estimated = ordered[0]
    for entry in per_level:
        if entry["total"] > 0 and (entry["correct"] / entry["total"]) >= 0.5:
            estimated = entry["level"]
    return estimated


_LEVEL_WEIGHTS = {"reading": 0.30, "listening": 0.30, "writing": 0.20, "speaking": 0.20}


def _determine_overall_level(results: dict[str, dict | None], framework: str) -> str:
    """
    Weighted average of the 4 estimated skill levels.
    Weights: reading 30%, listening 30%, writing 20%, speaking 20%.
    Skips any skill whose grading failed (result is None or missing estimated_level).
    """
    levels  = _LEVEL_ORDER.get(framework, ["A1"])
    indices = {lvl: i for i, lvl in enumerate(levels)}

    total_weight = 0.0
    weighted_sum = 0.0

    for skill, weight in _LEVEL_WEIGHTS.items():
        result = results.get(skill)
        if not result:
            continue
        idx = indices.get(result.get("estimated_level", ""))
        if idx is None:
            continue
        weighted_sum += idx * weight
        total_weight += weight

    if total_weight == 0:
        return levels[0]

    return levels[min(round(weighted_sum / total_weight), len(levels) - 1)]


def _estimate_level_open(per_level: list[dict], framework: str) -> str:
    """
    For open-ended skills (writing, speaking).
    The estimated level is the highest level where avg_score >= 60.
    """
    ordered  = _LEVEL_ORDER.get(framework, [])
    if not ordered:
        return "A1"
    estimated = ordered[0]
    for entry in per_level:
        if entry.get("avg_score", 0) >= 60:
            estimated = entry["level"]
    return estimated


# ─── Health endpoints ─────────────────────────────────────────────────────────

@router.get("/reading")
def reading_health():
    return {"message": "Hello from Reading Grading API"}

@router.get("/listening")
def listening_health():
    return {"message": "Hello from Listening Grading API"}

@router.get("/writing")
def writing_health():
    return {"message": "Hello from Writing Grading API"}

@router.get("/speaking")
def speaking_health():
    return {"message": "Hello from Speaking Grading API"}

@router.get("/save")
def save_health():
    return {"message": "Hello from Grading Save API"}


# ─── READING GRADING ──────────────────────────────────────────────────────────
#
# Pure calculation — no OpenAI needed.
# Compares each selectedAnswer against the question's 'answer' field.

def _grade_mcq(
    skill: str,
    framework: str,
    questions: list[dict],
    responses: list[dict],
    correct_key: str,
) -> dict:
    answer_map = {str(q["question_no"]): q.get(correct_key, "") for q in questions}
    level_map  = {str(q["question_no"]): q.get("question_level", "") for q in questions}

    question_results = []
    level_buckets: dict[str, dict] = {}

    for r in responses:
        qid      = str(r["questionId"])
        given    = r.get("selectedAnswer", "")
        expected = answer_map.get(qid, "")
        level    = level_map.get(qid, "?")
        correct  = given.upper() == expected.upper()

        question_results.append({
            "question_no": int(qid),
            "level":       level,
            "correct":     correct,
            "given":       given,
            "expected":    expected,
        })

        if level not in level_buckets:
            level_buckets[level] = {"level": level, "correct": 0, "total": 0}
        level_buckets[level]["total"]   += 1
        level_buckets[level]["correct"] += int(correct)

    ordered_levels = _LEVEL_ORDER.get(framework, [])
    per_level = []
    for lvl in ordered_levels:
        if lvl in level_buckets:
            b = level_buckets[lvl]
            per_level.append({
                "level":   lvl,
                "correct": b["correct"],
                "total":   b["total"],
                "score":   round(b["correct"] / b["total"] * 100, 1) if b["total"] else 0,
            })

    total_q   = len(question_results)
    total_cor = sum(1 for r in question_results if r["correct"])
    score     = round(total_cor / total_q * 100, 1) if total_q else 0

    return {
        "skill":            skill,
        "framework":        framework,
        "total_questions":  total_q,
        "correct":          total_cor,
        "score":            score,
        "estimated_level":  _estimate_level_mcq(per_level, framework),
        "per_level":        per_level,
        "question_results": sorted(question_results, key=lambda x: x["question_no"]),
    }


@router.post("/reading")
def reading_grading(req: ReadingGradingRequest):
    """
    Grade a placement reading assessment.

    Compares each selectedAnswer against the question's correct 'answer' field.
    Returns per-question results, per-level breakdown, overall score, and estimated level.
    No OpenAI call — pure calculation.
    """
    framework = _validate_framework(req.framework)
    return _grade_mcq("reading", framework, req.questions, req.responses, correct_key="answer")


# ─── LISTENING GRADING ────────────────────────────────────────────────────────
#
# Identical calculation logic to reading.
# The only difference is the correct-answer key: 'correct_answer' vs 'answer'.

@router.post("/listening")
def listening_grading(req: ListeningGradingRequest):
    """
    Grade a placement listening assessment.

    Compares each selectedAnswer against the question's 'correct_answer' field.
    Returns per-question results, per-level breakdown, overall score, and estimated level.
    No OpenAI call — pure calculation.
    """
    framework = _validate_framework(req.framework)
    return _grade_mcq("listening", framework, req.questions, req.responses, correct_key="correct_answer")


# ─── WRITING GRADING ──────────────────────────────────────────────────────────
#
# Uses OpenAI GPT to score each written response on 4 criteria:
#   task_completion, grammar, vocabulary, coherence.
# All per-question feedback is in the learner's native language.
# All questions are batched into a single OpenAI call for efficiency.

def _build_writing_grading_prompt(
    framework: str,
    target: str,
    native: str,
    items: list[dict],
) -> tuple[str, str]:
    system = f"""You are an expert language evaluator specialising in written production assessment.

You will evaluate written responses from a learner sitting a {framework} placement test.
The learner is a {native} speaker writing in {target}.

Score each response from 0 to 100 on four criteria calibrated to the stated {framework} level.
A learner at A1/HSK1/N5/TOPIK1 is expected to produce very simple sentences — score relative to that level's standard, not against a native benchmark.

CRITERIA:
* task_completion — Did the response address all parts of the task prompt?
* grammar         — Grammatical accuracy appropriate to this level
* vocabulary      — Range and appropriateness of vocabulary for this level
* coherence       — Logical flow and organisation of ideas

For each question write a short 1–2 sentence "feedback" in {native}, identifying one main strength and one main area for improvement.

Return a JSON object with exactly this structure — no markdown, no extra keys:
{{
  "results": [
    {{
      "question_no": <int>,
      "task_completion": <0-100>,
      "grammar": <0-100>,
      "vocabulary": <0-100>,
      "coherence": <0-100>,
      "score": <average of the four criteria, rounded to 1 decimal>,
      "feedback": "<in {native}>"
    }}
  ],
  "overall_feedback": "<2-3 sentences summarising the learner's overall written production, in {native}>"
}}"""

    blocks = []
    for item in items:
        blocks.append(
            f"QUESTION {item['question_no']} [{item['level']}]\n"
            f"Task: {item['task_prompt']}\n"
            f"Response: {item['response']}"
        )

    user = (
        f"Evaluate the following {len(items)} writing responses for a {native} speaker "
        f"learning {target} under the {framework} framework.\n\n"
        + "\n\n".join(blocks)
    )
    return system, user


@router.post("/writing")
async def writing_grading(req: WritingGradingRequest):
    """
    Grade a placement writing assessment using OpenAI GPT.

    Scores each written response on task completion, grammar, vocabulary, and coherence.
    All questions are sent in a single batched OpenAI call.
    Feedback is returned in the learner's native language.
    Returns per-question scores, per-level breakdown, overall score, and estimated level.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)

    response_map = {str(r["questionId"]): r.get("response", "") for r in req.responses}

    items = [
        {
            "question_no": q["question_no"],
            "level":       q.get("question_level", ""),
            "task_prompt": q.get("task_prompt", ""),
            "response":    response_map.get(str(q["question_no"]), ""),
        }
        for q in req.questions
    ]

    system_prompt, user_prompt = _build_writing_grading_prompt(framework, target, native, items)

    try:
        loop = asyncio.get_event_loop()
        raw  = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            )
        )
        data = json.loads(raw.choices[0].message.content or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    results    = data.get("results", [])
    overall_fb = data.get("overall_feedback", "")
    level_map  = {str(q["question_no"]): q.get("question_level", "") for q in req.questions}

    ordered_levels = _LEVEL_ORDER.get(framework, [])
    level_scores: dict[str, list[float]] = {}
    per_question: list[dict] = []

    for r in results:
        qno   = r.get("question_no")
        level = level_map.get(str(qno), "?")
        score = r.get("score", 0)
        per_question.append({**r, "level": level})
        level_scores.setdefault(level, []).append(score)

    per_level = []
    for lvl in ordered_levels:
        if lvl in level_scores:
            avg = round(sum(level_scores[lvl]) / len(level_scores[lvl]), 1)
            per_level.append({"level": lvl, "avg_score": avg, "questions": len(level_scores[lvl])})

    all_scores    = [r.get("score", 0) for r in results]
    overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    return {
        "skill":            "writing",
        "framework":        framework,
        "overall_score":    overall_score,
        "estimated_level":  _estimate_level_open(per_level, framework),
        "per_level":        per_level,
        "per_question":     sorted(per_question, key=lambda x: x.get("question_no", 0)),
        "overall_feedback": overall_fb,
    }


# ─── SPEAKING GRADING ────────────────────────────────────────────────────────
#
# Two-step process:
#   Step 1 — Transcribe every audio clip with OpenAI Whisper (all in parallel).
#   Step 2 — Score all transcriptions with GPT in a single batched call.
#
# Scores on: task_completion, fluency, vocabulary, grammar.
# Feedback is returned in the learner's native language.

async def _transcribe(audio_b64: str, language: str) -> str:
    """Decode base64 audio, write to a temp file, and transcribe with Whisper."""
    if not audio_b64:
        return ""
    loop = asyncio.get_event_loop()

    def _run() -> str:
        audio_bytes = base64.b64decode(audio_b64)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            with open(tmp_path, "rb") as f:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language if len(language) == 2 else None,
                )
            return result.text
        finally:
            import os as _os
            _os.unlink(tmp_path)

    try:
        return await loop.run_in_executor(None, _run)
    except Exception:
        return ""


def _build_speaking_grading_prompt(
    framework: str,
    target: str,
    native: str,
    items: list[dict],
) -> tuple[str, str]:
    system = f"""You are an expert language evaluator specialising in spoken production assessment.

You will evaluate transcriptions of spoken responses from a learner sitting a {framework} placement test.
The learner is a {native} speaker speaking in {target}.

Score each response from 0 to 100 on four criteria calibrated to the stated {framework} level.
These are automatic transcriptions of speech — ignore punctuation inconsistencies. Evaluate vocabulary and grammar based on the words used, not transcription formatting.

CRITERIA:
* task_completion — Did the response address all parts of the task prompt?
* fluency         — Natural flow and pace relative to the level (use duration_seconds as a signal — a very short response at a higher level suggests hesitation or limited production)
* vocabulary      — Range and appropriateness of vocabulary for this level
* grammar         — Grammatical accuracy expected at this level

For each question write a short 1–2 sentence "feedback" in {native}, identifying one main strength and one main area for improvement.
If the transcription is empty, score all criteria 0 and note that no audio was received.

Return a JSON object with exactly this structure — no markdown, no extra keys:
{{
  "results": [
    {{
      "question_no": <int>,
      "task_completion": <0-100>,
      "fluency": <0-100>,
      "vocabulary": <0-100>,
      "grammar": <0-100>,
      "score": <average of the four criteria, rounded to 1 decimal>,
      "transcription": "<the transcription text or empty string>",
      "feedback": "<in {native}>"
    }}
  ],
  "overall_feedback": "<2-3 sentences summarising the learner's overall spoken production, in {native}>"
}}"""

    blocks = []
    for item in items:
        blocks.append(
            f"QUESTION {item['question_no']} [{item['level']}] "
            f"(duration: {item.get('duration_seconds', 0)}s)\n"
            f"Task: {item['task_prompt']}\n"
            f"Transcription: {item['transcription'] or '[no audio received]'}"
        )

    user = (
        f"Evaluate the following {len(items)} spoken responses for a {native} speaker "
        f"learning {target} under the {framework} framework.\n\n"
        + "\n\n".join(blocks)
    )
    return system, user


@router.post("/speaking")
async def speaking_grading(req: SpeakingGradingRequest):
    """
    Grade a placement speaking assessment.

    Step 1: Transcribes all audio clips with OpenAI Whisper in parallel.
    Step 2: Scores all transcriptions with GPT-4o-mini in a single batched call.

    Scores on task completion, fluency, vocabulary, and grammar.
    Feedback is returned in the learner's native language.
    Returns per-question transcriptions + scores, per-level breakdown,
    overall score, and estimated level.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)

    response_map = {str(r["questionId"]): r for r in req.responses}

    # Step 1: parallel Whisper transcription
    transcription_tasks = [
        _transcribe(
            response_map.get(str(q["question_no"]), {}).get("audio_b64", ""),
            req.target_language,
        )
        for q in req.questions
    ]
    transcriptions = await asyncio.gather(*transcription_tasks)

    # Assemble items with transcriptions for the grading prompt
    items = []
    for q, transcript in zip(req.questions, transcriptions):
        resp = response_map.get(str(q["question_no"]), {})
        items.append({
            "question_no":      q["question_no"],
            "level":            q.get("question_level", ""),
            "task_prompt":      q.get("task_prompt", ""),
            "transcription":    transcript,
            "duration_seconds": resp.get("duration_seconds", 0),
        })

    # Step 2: single batched GPT scoring call
    system_prompt, user_prompt = _build_speaking_grading_prompt(framework, target, native, items)

    try:
        loop = asyncio.get_event_loop()
        raw  = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            )
        )
        data = json.loads(raw.choices[0].message.content or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    results    = data.get("results", [])
    overall_fb = data.get("overall_feedback", "")
    level_map  = {str(q["question_no"]): q.get("question_level", "") for q in req.questions}

    ordered_levels = _LEVEL_ORDER.get(framework, [])
    level_scores: dict[str, list[float]] = {}
    per_question: list[dict] = []

    for r in results:
        qno   = r.get("question_no")
        level = level_map.get(str(qno), "?")
        score = r.get("score", 0)
        per_question.append({**r, "level": level})
        level_scores.setdefault(level, []).append(score)

    per_level = []
    for lvl in ordered_levels:
        if lvl in level_scores:
            avg = round(sum(level_scores[lvl]) / len(level_scores[lvl]), 1)
            per_level.append({"level": lvl, "avg_score": avg, "questions": len(level_scores[lvl])})

    all_scores    = [r.get("score", 0) for r in results]
    overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    return {
        "skill":            "speaking",
        "framework":        framework,
        "overall_score":    overall_score,
        "estimated_level":  _estimate_level_open(per_level, framework),
        "per_level":        per_level,
        "per_question":     sorted(per_question, key=lambda x: x.get("question_no", 0)),
        "overall_feedback": overall_fb,
    }


# ─── SAVE GRADING RESULTS ─────────────────────────────────────────────────────
#
# Persists all 4 skill results to the database:
#   • Determines the overall level via a weighted average of the 4 skill estimates.
#   • Writes current_level back to the users table.
#   • Inserts one row per skill into the assessments table.

@router.post("/save")
def save_grading(req: SaveGradingRequest):
    """
    Persist placement grading results to the database.

    Computes the overall level from a weighted average of the 4 skill estimated levels
    (reading 30%, listening 30%, writing 20%, speaking 20%), writes it to users.current_level,
    and inserts one assessment record per skill into the assessments table.
    Skips any skill whose result is None (grading failed for that skill).
    Returns the determined current_level and the new assessment IDs.
    """
    conn = get_connection()
    try:
        user_row = conn.execute(
            "SELECT framework, target_language_id FROM users WHERE id = %s",
            (req.user_id,)
        ).fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found.")

        framework          = (user_row["framework"] or "CEFR").upper()
        target_language_id = user_row["target_language_id"]

        results = {
            "reading":   req.reading,
            "listening": req.listening,
            "writing":   req.writing,
            "speaking":  req.speaking,
        }

        current_level = _determine_overall_level(results, framework)

        conn.execute(
            "UPDATE users SET current_level = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (current_level, req.user_id)
        )

        assessment_ids: dict[str, str] = {}
        for skill, result in results.items():
            if not result:
                continue

            assessment_id   = str(uuid.uuid4())
            score           = result.get("score") or result.get("overall_score") or 0
            estimated_level = result.get("estimated_level", "")

            conn.execute(
                """
                INSERT INTO assessments (
                    id, user_id, assessment_type, framework,
                    target_language_id, estimated_level, score,
                    session_id, feedback_json, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (
                    assessment_id, req.user_id,
                    f"placement_{skill}", framework,
                    target_language_id, estimated_level, round(float(score), 1),
                    req.session_id, json.dumps(result),
                )
            )

            # Record point-in-time skill score for trend computation
            conn.execute(
                """
                INSERT INTO skill_scores (id, user_id, skill, score, assessment_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), req.user_id, skill, round(float(score), 1), assessment_id)
            )

            assessment_ids[skill] = assessment_id

        conn.commit()

        return {
            "current_level":  current_level,
            "assessment_ids": assessment_ids,
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


# ─── FETCH SESSION RESULTS ────────────────────────────────────────────────────

@router.get("/session/{session_id}")
def get_session_results(session_id: str):
    """
    Return the full grading results for a completed assessment session.
    Groups all 4 skill rows by session_id and returns feedback_json per skill.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT assessment_type, estimated_level, score, feedback_json, completed_at
            FROM assessments
            WHERE session_id = %s
            ORDER BY completed_at
            """,
            (session_id,),
        ).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Session not found.")

        skills: dict[str, dict] = {}
        completed_at = None
        for row in rows:
            skill = row["assessment_type"].replace("placement_", "")
            feedback = json.loads(row["feedback_json"]) if row["feedback_json"] else {}
            skills[skill] = {
                "estimated_level": row["estimated_level"],
                "score":           row["score"],
                **feedback,
            }
            completed_at = row["completed_at"]

        return {
            "session_id":   session_id,
            "completed_at": str(completed_at) if completed_at else None,
            "skills":       skills,
        }
    finally:
        conn.close()
