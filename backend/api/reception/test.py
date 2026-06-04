import asyncio
import base64
import json
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ─── Shared request model ─────────────────────────────────────────────────────
# Both reading and listening assessments accept the same input payload.

class ReadingTestRequest(BaseModel):
    target_language: str          # e.g. "fr", "ja", "zh", "ko"
    native_language: str          # e.g. "en", "de"
    framework: str                # "CEFR" | "HSK" | "JLPT" | "TOPIK"
    learning_goal: str = ""
    interests: list[str] = []


class ListeningTestRequest(BaseModel):
    target_language: str
    native_language: str
    framework: str
    learning_goal: str = ""
    interests: list[str] = []


class WritingTestRequest(BaseModel):
    target_language: str
    native_language: str
    framework: str
    learning_goal: str = ""
    interests: list[str] = []


class SpeakingTestRequest(BaseModel):
    target_language: str
    native_language: str
    framework: str
    learning_goal: str = ""
    interests: list[str] = []


# ─── Listening question schema ────────────────────────────────────────────────

class ListeningQuestion(BaseModel):
    question_no: int
    question_level: str
    question_type: str            # always "listening_mcq"
    question_skill: str           # always "listening"
    transcript: str               # authentic spoken-style passage
    question: str                 # comprehension question
    options: list[str]            # 4 options, no letter prefix
    correct_answer: str           # "A" | "B" | "C" | "D"
    audio_url: Optional[str]      # null until TTS is generated
    tts_status: str               # "pending" | "ready" | "failed"


# ─── Framework distributions ──────────────────────────────────────────────────

_DISTRIBUTIONS: dict[str, list[dict]] = {
    "CEFR": [
        {"level": "A1", "count": 2},
        {"level": "A2", "count": 2},
        {"level": "B1", "count": 2},
        {"level": "B2", "count": 1},
        {"level": "C1", "count": 1},
        {"level": "C2", "count": 1},
    ],
    "HSK": [
        {"level": "HSK1", "count": 2},
        {"level": "HSK2", "count": 2},
        {"level": "HSK3", "count": 2},
        {"level": "HSK4", "count": 1},
        {"level": "HSK5", "count": 1},
        {"level": "HSK6", "count": 1},
    ],
    "JLPT": [
        {"level": "N5", "count": 2},
        {"level": "N4", "count": 2},
        {"level": "N3", "count": 2},
        {"level": "N2", "count": 1},
        {"level": "N1", "count": 1},
    ],
    "TOPIK": [
        {"level": "TOPIK1", "count": 2},
        {"level": "TOPIK2", "count": 2},
        {"level": "TOPIK3", "count": 2},
        {"level": "TOPIK4", "count": 1},
        {"level": "TOPIK5", "count": 1},
        {"level": "TOPIK6", "count": 1},
    ],
}

_VOICE_MAP: dict[str, str] = {
    "fr": "alloy",  "de": "echo",  "es": "nova",  "it": "nova",
    "pt": "nova",   "zh": "echo",  "ja": "shimmer","ko": "shimmer",
    "ar": "echo",   "ru": "fable", "nl": "alloy",  "pl": "fable",
    "sv": "alloy",  "tr": "echo",  "hi": "nova",
}
_DEFAULT_VOICE = "alloy"

_LANG_NAMES: dict[str, str] = {
    "en": "English", "fr": "French",   "de": "German",   "es": "Spanish",
    "it": "Italian", "pt": "Portuguese","zh": "Chinese",  "ja": "Japanese",
    "ko": "Korean",  "ar": "Arabic",    "ru": "Russian",  "nl": "Dutch",
    "pl": "Polish",  "sv": "Swedish",   "tr": "Turkish",  "hi": "Hindi",
}


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _voice_for(language: str) -> str:
    return _VOICE_MAP.get(language.lower(), _DEFAULT_VOICE)

def _lang_name(code: str) -> str:
    return _LANG_NAMES.get(code.lower(), code)

def _build_distribution_block(framework: str) -> str:
    lines = []
    for entry in _DISTRIBUTIONS[framework]:
        n = entry["count"]
        lines.append(f"* {entry['level']} = {n} question{'s' if n > 1 else ''}")
    return "\n".join(lines)

def _total_questions(framework: str) -> int:
    return sum(e["count"] for e in _DISTRIBUTIONS[framework])

def _unwrap_array(data: object) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
    raise ValueError("OpenAI response did not contain a JSON array.")

def _validate_framework(framework: str) -> str:
    fw = framework.upper()
    if fw not in _DISTRIBUTIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported framework '{framework}'. "
                f"Accepted values: {', '.join(_DISTRIBUTIONS)}"
            ),
        )
    return fw

# ─── Reading prompt builder ───────────────────────────────────────────────────

def _build_reading_prompts(
    framework: str,
    target: str,
    native: str,
    learning_goal: str,
    interests: str,
    total: int,
    dist: str,
) -> tuple[str, str]:
    system = f"""You are an expert language assessment engine.

Your task is to generate a placement assessment.

The assessment must follow the framework distribution exactly.

FRAMEWORK: {framework}

DISTRIBUTION — generate exactly this many questions per level, in this order:{dist}

LEARNER CONTEXT:
* Target language : {target}
* Native language : {native}
* Learning goal   : {learning_goal}
* Interests       : {interests}

QUESTION RULES:
* All question passages must be written in {target}.
* Questions must increase in difficulty strictly according to the framework level order above.
* Assess vocabulary, grammar, reading comprehension, and sentence understanding.
* Multiple choice only — four options per question (A, B, C, D).
* Exactly one correct answer per question.
* Where natural, weave vocabulary and examples from the learner's interests: {interests}.

OUTPUT RULES:
* Return exactly {total} questions numbered sequentially (question_no 1 → {total}).
* Wrap the array in a JSON object: {{"questions": [ ... ]}}
* The array must contain objects with exactly these keys:
  question_no, question_level, question_type, question_passage, options, answer
* question_type is always "mcq".
* options is an array of 4 strings — the full text of each option (no letter prefix).
* answer is the letter of the correct option: "A", "B", "C", or "D".
* Do not return markdown. Do not return explanations. Return only valid JSON."""

    user = (
        f"Generate the {framework} placement reading assessment for a {native} speaker "
        f"learning {target}. "
        f"Follow the exact distribution. "
        f"Return only the JSON object with the questions array."
    )
    return system, user

# ─── Listening prompt builder ─────────────────────────────────────────────────

def _build_listening_prompts(
    framework: str,
    target: str,
    native: str,
    learning_goal: str,
    interests: str,
    total: int,
    dist: str,
) -> tuple[str, str]:
    system = f"""You are an expert language assessment engine specialising in listening comprehension.

Your task is to generate a placement listening assessment.
Each question consists of an authentic spoken-language transcript paired with a comprehension question.

FRAMEWORK: {framework}

DISTRIBUTION — generate exactly this many questions per level, in this order:{dist}

LEARNER CONTEXT:
* Target language : {target}
* Native language : {native}
* Learning goal   : {learning_goal}
* Interests       : {interests}

TRANSCRIPT RULES:
* Every transcript must be written entirely in {target}.
* Transcripts must sound like authentic natural speech — not textbook sentences.
  Use contractions, hesitations, ellipsis, and colloquial phrasing where appropriate.
* Vary the format: short dialogues, monologues, announcements, voicemails, radio snippets,
  or casual conversations — whichever suits the level.
* Transcript length must match the level:
  - A1/N5/HSK1/TOPIK1: 1–2 sentences (very short, simple)
  - A2/N4/HSK2/TOPIK2: 3–4 sentences
  - B1/N3/HSK3/TOPIK3: 4–6 sentences
  - B2/N2/HSK4/TOPIK4: 6–8 sentences
  - C1/N1/HSK5/TOPIK5: 8–10 sentences (complex, natural pace)
  - C2/HSK6/TOPIK6: 10+ sentences (nuanced, idiomatic)
* Questions must increase in difficulty strictly according to the framework level order.
* Where natural, weave vocabulary and scenarios from the learner's interests: {interests}.

QUESTION RULES:
* The comprehension question must be answerable solely from the transcript.
* Test: main idea, specific detail, inference, speaker attitude, or vocabulary in context.
* Multiple choice only — four options per question (A, B, C, D).
* Exactly one correct answer per question.
* Write the comprehension question and all four options entirely in {target}.

OUTPUT RULES:
* Return exactly {total} questions numbered sequentially (question_no 1 → {total}).
* Wrap the array in a JSON object: {{"questions": [ ... ]}}
* Each object must contain exactly these keys:
  question_no, question_level, question_type, transcript, question, options, correct_answer
* question_type is always "listening_mcq".
* options is an array of 4 strings — full text, no letter prefix.
* correct_answer is the letter of the correct option: "A", "B", "C", or "D".
* Do not return markdown. Do not return explanations. Return only valid JSON."""

    user = (
        f"Generate the {framework} placement listening assessment for a {native} speaker "
        f"learning {target}. "
        f"All transcripts must be authentic natural {target} speech. "
        f"Comprehension questions and all options must be in {target}. "
        f"Follow the exact distribution. "
        f"Return only the JSON object with the questions array."
    )
    return system, user

# ─── Writing prompt builder ──────────────────────────────────────────────────

def _build_writing_prompts(
    framework: str,
    target: str,
    native: str,
    learning_goal: str,
    interests: str,
    total: int,
    dist: str,
) -> tuple[str, str]:
    system = f"""You are an expert language assessment engine specialising in written production.

Your task is to generate a placement writing assessment.
Each question is a self-contained writing task the learner must respond to in {target}.

FRAMEWORK: {framework}

DISTRIBUTION — generate exactly this many tasks per level, in this order:{dist}

LEARNER CONTEXT:
* Target language : {target}
* Native language : {native}
* Learning goal   : {learning_goal}
* Interests       : {interests}

TASK RULES:
* Every task_prompt must be written entirely in {target}.
* Tasks must increase in complexity strictly according to the framework level order above.
* Vary the task type across the assessment — use a mix of:
  - Sentence completion or simple description (lower levels)
  - Short message, text, or social media post (lower-mid levels)
  - Email, letter, or structured response to a situation (mid levels)
  - Opinion, argument, or analytical paragraph (upper-mid levels)
  - Essay, formal report, or critical commentary (upper levels)
* Where natural, situate tasks within the learner's interests: {interests}.
* word_count_guide must be appropriate to the level and writing system:
  - A1/N5/HSK1/TOPIK1 : "20–40 words"  (or "15–30 characters" for logographic scripts)
  - A2/N4/HSK2/TOPIK2 : "40–70 words"  (or "30–55 characters")
  - B1/N3/HSK3/TOPIK3 : "70–110 words" (or "55–90 characters")
  - B2/N2/HSK4/TOPIK4 : "110–160 words"(or "90–130 characters")
  - C1/N1/HSK5/TOPIK5 : "160–220 words"(or "130–180 characters")
  - C2/HSK6/TOPIK6    : "220+ words"   (or "180+ characters")
  Use the character variant for Chinese, Japanese, and Korean; the word variant for all others.

OUTPUT RULES:
* Return exactly {total} tasks numbered sequentially (question_no 1 → {total}).
* Wrap the array in a JSON object: {{"questions": [ ... ]}}
* Each object must contain exactly these keys:
  question_no, question_level, task_prompt, word_count_guide.
* task_prompt is the full task description — include any scenario, stimulus, or instructions
  the learner needs. Do not split them across separate fields.
* word_count_guide is a short string such as "40–70 words" or "30–55 characters".
* Do not return options. Do not return a correct answer. Do not return markdown.
* Return only valid JSON."""

    user = (
        f"Generate the {framework} placement writing assessment for a {native} speaker "
        f"learning {target}. "
        f"All task prompts must be written entirely in {target}. "
        f"Follow the exact distribution. "
        f"Return only the JSON object with the questions array."
    )
    return system, user

# ─── Speaking prompt builder ─────────────────────────────────────────────────

def _build_speaking_prompts(
    framework: str,
    target: str,
    native: str,
    learning_goal: str,
    interests: str,
    total: int,
    dist: str,
) -> tuple[str, str]:
    system = f"""You are an expert language assessment engine specialising in spoken production.

Your task is to generate a placement speaking assessment.
Each question is a self-contained speaking task the learner must respond to aloud in {target}.

FRAMEWORK: {framework}

DISTRIBUTION — generate exactly this many tasks per level, in this order:{dist}

LEARNER CONTEXT:
* Target language : {target}
* Native language : {native}
* Learning goal   : {learning_goal}
* Interests       : {interests}

TASK RULES:
* Every task_prompt must be written entirely in {target}.
* Tasks must increase in complexity strictly according to the framework level order above.
* Vary the task type across the assessment — use a mix of:
  - Simple personal questions (name, preferences, daily life) — lower levels
  - Describe a situation, image, or routine — lower-mid levels
  - Express and justify an opinion on a familiar topic — mid levels
  - Discuss an abstract or hypothetical scenario — upper-mid levels
  - Analyse, debate, or present a nuanced argument — upper levels
* Where natural, situate tasks within the learner's interests: {interests}.
* prep_time_seconds is the thinking time the learner gets before speaking:
  - A1/N5/HSK1/TOPIK1 : 15
  - A2/N4/HSK2/TOPIK2 : 20
  - B1/N3/HSK3/TOPIK3 : 30
  - B2/N2/HSK4/TOPIK4 : 45
  - C1/N1/HSK5/TOPIK5 : 60
  - C2/HSK6/TOPIK6    : 60
* response_time_seconds is the maximum recording time:
  - A1/N5/HSK1/TOPIK1 : 30
  - A2/N4/HSK2/TOPIK2 : 45
  - B1/N3/HSK3/TOPIK3 : 60
  - B2/N2/HSK4/TOPIK4 : 90
  - C1/N1/HSK5/TOPIK5 : 120
  - C2/HSK6/TOPIK6    : 120

OUTPUT RULES:
* Return exactly {total} tasks numbered sequentially (question_no 1 → {total}).
* Wrap the array in a JSON object: {{"questions": [ ... ]}}
* Each object must contain exactly these keys:
  question_no, question_level, task_prompt, prep_time_seconds, response_time_seconds
* task_prompt is the full task description — everything the learner needs to know to respond.
* prep_time_seconds and response_time_seconds are integers.
* Do not return options. Do not return a correct answer. Do not return markdown.
* Return only valid JSON."""

    user = (
        f"Generate the {framework} placement speaking assessment for a {native} speaker "
        f"learning {target}. "
        f"All task prompts must be written entirely in {target}. "
        f"Follow the exact distribution. "
        f"Return only the JSON object with the questions array."
    )
    return system, user

# ─── OpenAI service layer ─────────────────────────────────────────────────────

def _call_openai(system_prompt: str, user_prompt: str) -> list:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    )
    raw = response.choices[0].message.content or ""
    if not raw:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty response.")
    data = json.loads(raw)
    return _unwrap_array(data)

# ─── TTS helpers ──────────────────────────────────────────────────────────────

async def _generate_audio_b64(transcript: str, language: str) -> str:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.audio.speech.create(
            model="tts-1",
            voice=_voice_for(language),
            input=transcript,
        ),
    )
    return base64.b64encode(response.content).decode("utf-8")


async def _attach_audio(questions: list, language: str) -> list[dict]:
    tasks = [_generate_audio_b64(q["transcript"], language) for q in questions]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    output = []
    for q, result in zip(questions, results):
        if isinstance(result, Exception):
            output.append({**q, "audio_b64": "", "tts_status": "failed"})
        else:
            output.append({**q, "audio_b64": result, "tts_status": "ready"})
    return output

# ─── Health endpoints ─────────────────────────────────────────────────────────

@router.get("/reading")
def reading_health():
    return {"message": "Hello from Reading Test API"}

@router.get("/listening")
def listening_health():
    return {"message": "Hello from Listening Test API"}

@router.get("/writing")
def writing_health():
    return {"message": "Hello from Writing Test API"}

@router.get("/speaking")
def speaking_health():
    return {"message": "Hello from Speaking Test API"}

# ─── Reading questions ────────────────────────────────────────────────────────

@router.post("/reading_questions")
def reading_questions(req: ReadingTestRequest):
    """
    Generate a placement reading assessment.

    Returns a JSON array of MCQ questions distributed across framework levels.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)
    total     = _total_questions(framework)
    dist      = _build_distribution_block(framework)
    interests = ", ".join(req.interests) if req.interests else "general topics"

    system_prompt, user_prompt = _build_reading_prompts(
        framework, target, native, req.learning_goal, interests, total, dist
    )

    try:
        return _call_openai(system_prompt, user_prompt)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# ─── Listening questions ──────────────────────────────────────────────────────

@router.post("/listening_questions")
async def listening_questions(req: ListeningTestRequest):
    """
    Generate a placement listening assessment with embedded audio.

    Returns a JSON array of listening questions, each with an authentic spoken-language
    transcript, a comprehension question, four options, and base64-encoded MP3 audio
    generated in parallel via OpenAI TTS.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)
    total     = _total_questions(framework)
    dist      = _build_distribution_block(framework)
    interests = ", ".join(req.interests) if req.interests else "general topics"

    system_prompt, user_prompt = _build_listening_prompts(
        framework, target, native, req.learning_goal, interests, total, dist
    )

    try:
        raw_questions = _call_openai(system_prompt, user_prompt)
        return await _attach_audio(raw_questions, req.target_language)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# ─── Writing questions ────────────────────────────────────────────────────────

@router.post("/writing_questions")
def writing_questions(req: WritingTestRequest):
    """
    Generate a placement writing assessment.

    Returns a JSON array of writing tasks distributed across framework levels.
    Each task has a prompt and a word/character count guide — no options, no correct answer.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)
    total     = _total_questions(framework)
    dist      = _build_distribution_block(framework)
    interests = ", ".join(req.interests) if req.interests else "general topics"

    system_prompt, user_prompt = _build_writing_prompts(
        framework, target, native, req.learning_goal, interests, total, dist
    )

    try:
        return _call_openai(system_prompt, user_prompt)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# ─── Speaking questions ───────────────────────────────────────────────────────

@router.post("/speaking_questions")
def speaking_questions(req: SpeakingTestRequest):
    """
    Generate a placement speaking assessment.

    Returns a JSON array of speaking tasks distributed across framework levels.
    Each task has a prompt, a prep time, and a max response time — no options, no correct answer.
    """
    framework = _validate_framework(req.framework)
    target    = _lang_name(req.target_language)
    native    = _lang_name(req.native_language)
    total     = _total_questions(framework)
    dist      = _build_distribution_block(framework)
    interests = ", ".join(req.interests) if req.interests else "general topics"

    system_prompt, user_prompt = _build_speaking_prompts(
        framework, target, native, req.learning_goal, interests, total, dist
    )

    try:
        return _call_openai(system_prompt, user_prompt)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
