import json
import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ─── Request model ────────────────────────────────────────────────────────────

class ReadingTestRequest(BaseModel):
    target_language: str          # e.g. "fr", "ja", "zh", "ko"
    native_language: str          # e.g. "en", "de"
    framework: str                # "CEFR" | "HSK" | "JLPT" | "TOPIK"
    learning_goal: str = ""
    interests: list[str] = []


# ─── Framework distributions ──────────────────────────────────────────────────
# Each entry specifies how many questions to generate per level.
# Order = ascending difficulty (determines question numbering).

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

# ISO 639-1 → full language name for natural prompting
_LANG_NAMES: dict[str, str] = {
    "en": "English", "fr": "French",   "de": "German",   "es": "Spanish",
    "it": "Italian", "pt": "Portuguese","zh": "Chinese",  "ja": "Japanese",
    "ko": "Korean",  "ar": "Arabic",    "ru": "Russian",  "nl": "Dutch",
    "pl": "Polish",  "sv": "Swedish",   "tr": "Turkish",  "hi": "Hindi",
}


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
    """
    The model may wrap the array in an object (required by json_object mode).
    Walk the top-level values until we find a list and return it.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
    raise ValueError("OpenAI response did not contain a JSON array.")


# ─── Existing health endpoint (unchanged) ────────────────────────────────────

@router.get("/reading")
def reading_test():
    return {"message": "Hello from Reading Test API"}


# ─── Reading questions ────────────────────────────────────────────────────────

@router.post("/reading_questions")
def reading_questions(req: ReadingTestRequest):
    """
    Generate a placement reading assessment.

    Returns a JSON array of multiple-choice questions distributed across
    the correct levels for the given framework (CEFR / HSK / JLPT / TOPIK).
    """
    framework = req.framework.upper()

    if framework not in _DISTRIBUTIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported framework '{req.framework}'. "
                f"Accepted values: {', '.join(_DISTRIBUTIONS)}"
            ),
        )

    target  = _lang_name(req.target_language)
    native  = _lang_name(req.native_language)
    total   = _total_questions(framework)
    dist    = _build_distribution_block(framework)
    interests = ", ".join(req.interests) if req.interests else "general topics"

    system_prompt = f"""You are an expert language assessment engine.

Your task is to generate a placement assessment.

The assessment must follow the framework distribution exactly.

FRAMEWORK: {framework}

DISTRIBUTION — generate exactly this many questions per level, in this order:
{dist}

LEARNER CONTEXT:
* Target language : {target}
* Native language : {native}
* Learning goal   : {req.learning_goal}
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

    user_prompt = (
        f"Generate the {framework} placement reading assessment for a {native} speaker "
        f"learning {target}. "
        f"Follow the exact distribution. "
        f"Return only the JSON object with the questions array."
    )

    try:
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
        questions = _unwrap_array(data)

        return questions

    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from OpenAI: {exc}") from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

# @router.post("/writing_questions")
# def writing_questions(req: WritingTestRequest)