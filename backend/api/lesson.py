"""
lesson.py
─────────
Lesson endpoint + prompt builder.

GET /lesson/{node_id}?user_id=...&ui_lang=...
  1. Resolves the curriculum node and user profile from the DB.
  2. Returns a cached lesson if one was already generated for this user+node.
  3. Otherwise builds a personalised prompt, calls OpenAI, caches the result,
     and returns the lesson JSON.
"""

import json
import os
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from openai import OpenAI

from database.script import get_connection

load_dotenv()

router  = APIRouter()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_XP_PER_LESSON = 50


@router.get("/{node_id}")
def get_lesson(
    node_id: int,
    user_id: str = Query(...),
    ui_lang: str = Query(default="en"),
):
    conn = get_connection()
    try:
        # ── 1. Resolve curriculum node ─────────────────────────────────────
        node = conn.execute(
            """
            SELECT cn.id, cn.module_id, cn.framework, cn.level, cn.lesson_order,
                   cn.topic, cn.skill_focus, cn.learning_objectives
            FROM curriculum_nodes cn
            WHERE cn.id = ?
            """,
            (node_id,),
        ).fetchone()
        if node is None:
            raise HTTPException(status_code=404, detail=f"Curriculum node {node_id} not found.")

        # ── 2. Resolve user profile ────────────────────────────────────────
        user = conn.execute(
            """
            SELECT u.id, u.learning_goal, u.framework, u.current_level,
                   nl.name AS native_name,
                   tl.name AS target_name, tl.code AS target_code
            FROM users u
            JOIN languages nl ON nl.id = u.native_language_id
            JOIN languages tl ON tl.id = u.target_language_id
            WHERE u.id = ?
            """,
            (user_id,),
        ).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")

        hobbies = [
            r["name"] for r in conn.execute(
                """
                SELECT h.name FROM hobbies h
                JOIN user_hobbies uh ON uh.hobby_id = h.id
                WHERE uh.user_id = ?
                """,
                (user_id,),
            ).fetchall()
        ]

        # ── 3. Derive weaknesses / strengths from the most recent skill scores
        seen_skills: set[str] = set()
        weaknesses: list[str] = []
        strengths: list[str] = []
        for row in conn.execute(
            "SELECT skill, score FROM skill_scores WHERE user_id = ? ORDER BY recorded_at DESC",
            (user_id,),
        ).fetchall():
            if row["skill"] in seen_skills:
                continue
            seen_skills.add(row["skill"])
            score = row["score"] or 0
            if score < 50:
                weaknesses.append(row["skill"])
            elif score >= 70:
                strengths.append(row["skill"])

        # ── 4. Return cached lesson if it exists for this user + node ──────
        cached = conn.execute(
            """
            SELECT l.id, l.lesson_json FROM lessons l
            WHERE l.user_id = ? AND l.node_id = ?
            ORDER BY l.generated_at DESC LIMIT 1
            """,
            (user_id, node_id),
        ).fetchone()

        # ── Curriculum progress (shared by both cached + fresh paths) ────────
        progress_row = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM curriculum_nodes
                 WHERE language_id = (SELECT target_language_id FROM users WHERE id = ?)
                   AND framework   = (SELECT framework      FROM users WHERE id = ?)
                   AND level       = (SELECT current_level  FROM users WHERE id = ?)) AS total,
                (SELECT COUNT(DISTINCT l.node_id) FROM user_lesson_progress ulp
                 JOIN lessons l      ON l.id  = ulp.lesson_id
                 JOIN curriculum_nodes cn ON cn.id = l.node_id
                 WHERE ulp.user_id = ? AND ulp.status = 'completed'
                   AND l.node_id IS NOT NULL
                   AND cn.level = (SELECT current_level FROM users WHERE id = ?)) AS completed
            """,
            (user_id, user_id, user_id, user_id, user_id),
        ).fetchone()
        progress_total     = progress_row["total"]     if progress_row else 0
        progress_completed = progress_row["completed"] if progress_row else 0

        if cached:
            progress = conn.execute(
                "SELECT status FROM user_lesson_progress WHERE user_id = ? AND lesson_id = ?",
                (user_id, cached["id"]),
            ).fetchone()
            session_type = (
                "revision" if (progress and progress["status"] == "completed") else "retry"
            )
            lesson_data = json.loads(cached["lesson_json"])
            lesson_data.update({
                "level":              node["level"],
                "topic":              node["topic"],
                "framework":          node["framework"],
                "node_id":            node_id,
                "lesson_id":          cached["id"],
                "session_type":       session_type,
                "language_code":      user["target_code"],
                "progress_completed": progress_completed,
                "progress_total":     progress_total,
            })
            return lesson_data

        # ── 5. Build and send prompt to OpenAI ────────────────────────────
        context = {
            "node_id":         node["id"],
            "framework":       node["framework"],
            "level":           node["level"],
            "topic":           node["topic"],
            "skill_focus":     json.loads(node["skill_focus"]),
            "target_language": user["target_name"],
            "native_language": user["native_name"],
            "current_level":   user["current_level"] or node["level"],
            "learning_goal":   user["learning_goal"] or "general proficiency",
            "weaknesses":      weaknesses,
            "strengths":       strengths,
            "interests":       hobbies,
            "session_type":    "new_lesson",
        }

        prompt = build_lesson_prompt(context)

        try:
            response = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert language tutor. "
                            "Return valid JSON only — no markdown, no code fences, no extra text."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc

        raw = response.choices[0].message.content or ""
        try:
            lesson_data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=502, detail="AI returned invalid JSON.") from exc

        # ── 6. Cache the generated lesson ─────────────────────────────────
        lesson_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO lessons
                (id, user_id, module_id, node_id, title, framework, lesson_level,
                 skill_focus, lesson_order, estimated_minutes, lesson_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 15, ?)
            """,
            (
                lesson_id,
                user_id,
                node["module_id"],
                node_id,
                lesson_data.get("lesson_title", node["topic"]),
                node["framework"],
                node["level"],
                node["skill_focus"],
                node["lesson_order"],
                json.dumps(lesson_data),
            ),
        )

        conn.execute(
            "INSERT OR IGNORE INTO user_lesson_progress (user_id, lesson_id, status) VALUES (?, ?, 'in_progress')",
            (user_id, lesson_id),
        )

        conn.commit()

        lesson_data.update({
            "level":              node["level"],
            "topic":              node["topic"],
            "framework":          node["framework"],
            "node_id":            node_id,
            "lesson_id":          lesson_id,
            "session_type":       "new_lesson",
            "language_code":      user["target_code"],
            "progress_completed": progress_completed,
            "progress_total":     progress_total,
        })
        return lesson_data

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


def _next_unstarted_node(conn, user_id: str) -> int | None:
    row = conn.execute(
        """
        SELECT cn.id FROM curriculum_nodes cn
        WHERE cn.language_id = (SELECT target_language_id FROM users WHERE id = ?)
          AND cn.framework   = (SELECT framework             FROM users WHERE id = ?)
          AND cn.level       = (SELECT current_level         FROM users WHERE id = ?)
          AND cn.id NOT IN (
              SELECT l.node_id FROM lessons l
              WHERE l.user_id = ? AND l.node_id IS NOT NULL
          )
        ORDER BY cn.lesson_order
        LIMIT 1
        """,
        (user_id, user_id, user_id, user_id),
    ).fetchone()
    return row["id"] if row else None


@router.post("/{node_id}/complete")
def complete_lesson(
    node_id: int,
    user_id: str = Query(...),
):
    conn = get_connection()
    try:
        lesson_row = conn.execute(
            "SELECT id, estimated_minutes FROM lessons WHERE user_id = ? AND node_id = ? ORDER BY generated_at DESC LIMIT 1",
            (user_id, node_id),
        ).fetchone()
        if lesson_row is None:
            raise HTTPException(status_code=404, detail="Lesson not found. Load the lesson page first.")

        lesson_id = lesson_row["id"]
        minutes   = lesson_row["estimated_minutes"] or 15

        progress = conn.execute(
            "SELECT status FROM user_lesson_progress WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id),
        ).fetchone()

        if progress and progress["status"] == "completed":
            total_xp = conn.execute(
                "SELECT current_xp FROM users WHERE id = ?", (user_id,)
            ).fetchone()["current_xp"] or 0
            return {
                "xp_earned":        0,
                "total_xp":         total_xp,
                "next_node_id":     _next_unstarted_node(conn, user_id),
                "already_completed": True,
            }

        # Flip progress to completed
        if progress:
            conn.execute(
                "UPDATE user_lesson_progress SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE user_id = ? AND lesson_id = ?",
                (user_id, lesson_id),
            )
        else:
            conn.execute(
                "INSERT INTO user_lesson_progress (user_id, lesson_id, status, completed_at) VALUES (?, ?, 'completed', CURRENT_TIMESTAMP)",
                (user_id, lesson_id),
            )

        # Award XP
        conn.execute(
            "UPDATE users SET current_xp = current_xp + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (_XP_PER_LESSON, user_id),
        )

        # Log learning session for streak + heatmap
        conn.execute(
            """
            INSERT INTO learning_sessions (id, user_id, lesson_id, ended_at, minutes_spent, xp_earned)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            """,
            (str(uuid.uuid4()), user_id, lesson_id, minutes, _XP_PER_LESSON),
        )

        conn.commit()

        total_xp = conn.execute(
            "SELECT current_xp FROM users WHERE id = ?", (user_id,)
        ).fetchone()["current_xp"] or 0

        return {
            "xp_earned":         _XP_PER_LESSON,
            "total_xp":          total_xp,
            "next_node_id":      _next_unstarted_node(conn, user_id),
            "already_completed": False,
        }

    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


_SESSION_LABELS = {
    "new_lesson": "New Lesson",
    "retry":      "Retry (learner previously struggled — increase reinforcement and repetition)",
    "revision":   "Revision (reviewing previously taught material)",
}

_ADAPTIVE_RULES_MAP = {
    "listening": (
        "- The learner is weak in LISTENING. Include audio-style dialogue scenarios "
        "(natural conversational exchanges, announcements, short monologues). "
        "Write them as if they will be read aloud."
    ),
    "grammar": (
        "- The learner is weak in GRAMMAR. Simplify all grammatical explanations. "
        "Add extra drills in the exercises section that isolate and repeat the core grammar pattern."
    ),
    "pronunciation": (
        "- The learner struggles with PRONUNCIATION. Where relevant, note phonetic cues "
        "or pronunciation tips inside vocabulary entries (e.g. IPA or plain-language hints)."
    ),
    "vocabulary": (
        "- The learner struggles with VOCABULARY. Provide richer vocabulary entries with "
        "example sentences, and repeat key words across examples and dialogues."
    ),
    "reading": (
        "- The learner is weak in READING. Include at least one short reading passage "
        "in the examples or dialogues section and draw comprehension questions from it."
    ),
    "speaking": (
        "- The learner is weak in SPEAKING. Include open-ended dialogue prompts and "
        "role-play scenarios that require the learner to construct their own responses."
    ),
    "writing": (
        "- The learner is weak in WRITING. Add sentence-construction exercises and "
        "a short guided writing task in the exercises section."
    ),
}

# Skill-focus rules — fire based on curriculum node type, not user weakness.
# Applied in addition to (not instead of) weakness-based rules.
_SKILL_FOCUS_RULES_MAP: dict[str, str] = {
    "phonetics": (
        "- This is a PHONETICS lesson. The vocabulary section MUST use letter-sound pairs: "
        "each 'word' field is a letter or character, 'translation' is its IPA symbol plus a "
        "plain-language description, 'example' is a word in the target language containing that "
        "sound. Cover EVERY letter or sound in the topic's inventory — do not sample or abbreviate. "
        "Exercises must be recognition and production drills (e.g. 'Which word contains /y/?', "
        "'Write the letter that makes this sound'), never translation tasks."
    ),
    "pronunciation": (
        "- This is a PRONUNCIATION lesson. Cover every key pronunciation rule, pattern, and "
        "exception for this topic completely. Include IPA notation for every sound discussed. "
        "Exercises must be articulation drills and minimal-pair comparisons that train the learner "
        "to distinguish and produce the sounds correctly."
    ),
}

# Maps skill_focus values → preferred reinforcement type
_SKILL_TO_REINFORCEMENT: dict[str, str] = {
    "grammar":       "quiz",
    "vocabulary":    "quiz",
    "speaking":      "speaking",
    "listening":     "listening",
    "writing":       "writing",
    "reading":       "reading",
    "phonetics":     "reflection",
    "pronunciation": "reflection",
}

# Maps weakness values → preferred reinforcement type
_WEAKNESS_TO_REINFORCEMENT: dict[str, str] = {
    "grammar":   "quiz",
    "speaking":  "dialogue",
    "listening": "listening",
    "writing":   "writing",
    "reading":   "reading",
}

_VALID_REINFORCEMENT_TYPES = frozenset(
    {"quiz", "dialogue", "speaking", "listening", "reading", "writing", "reflection", "none"}
)

_INTRO_TOPIC_KEYWORDS = ("introduction", "intro", "basics", "overview", "what is", "getting started")


def _choose_reinforcement_type(context: dict) -> str:
    """
    Determine the reinforcement type for a lesson based on skill focus,
    user weaknesses, and session type.

    Priority (highest → lowest):
      1. Session type = retry  → must be active (quiz or dialogue); never none/reflection
      2. User weaknesses       → override skill focus when there is a direct match
      3. Skill focus           → primary signal from curriculum node
      4. Session type defaults → new_lesson → reflection; revision → quiz; new_lesson (no focus) → reflection
    """
    skill_focus  = [s.lower().strip() for s in (context.get("skill_focus") or [])]
    weaknesses   = [w.lower().strip() for w in (context.get("weaknesses")  or [])]
    session_type = (context.get("session_type") or "new_lesson").lower()
    topic        = (context.get("topic") or "").lower()

    # Step 1: derive candidate from skill focus (first matching skill wins)
    candidate = "none"
    for skill in skill_focus:
        mapped = _SKILL_TO_REINFORCEMENT.get(skill)
        if mapped:
            candidate = mapped
            break

    # Step 2: weakness can sharpen the candidate (takes precedence over skill focus
    # because addressing a known gap is higher priority than following the node focus)
    for weakness in weaknesses:
        mapped = _WEAKNESS_TO_REINFORCEMENT.get(weakness)
        if mapped:
            candidate = mapped
            break

    # Step 3: session type adjustments
    if session_type == "retry":
        # Retry demands active reinforcement; upgrade passive/absent types
        if candidate in ("none", "reflection"):
            candidate = "quiz"

    elif session_type == "new_lesson":
        if candidate == "none":
            # Introductory topics get a gentle reflection; everything else gets one too
            candidate = "reflection"

    elif session_type == "revision":
        # Revision should always test something
        if candidate == "none":
            candidate = "quiz"

    return candidate if candidate in _VALID_REINFORCEMENT_TYPES else "reflection"


def _reinforcement_schema(reinforcement_type: str, target_language: str, native_language: str) -> str:
    """Return the JSON schema fragment and generation instructions for the chosen reinforcement type."""

    if reinforcement_type == "quiz":
        return f"""\
"reinforcement": {{
  "type": "quiz",
  "content": [
    {{
      "question": "<comprehension or grammar question in {target_language}>",
      "options": {{"A": "<option>", "B": "<option>", "C": "<option>", "D": "<option>"}},
      "correct": "<A | B | C | D>"
    }}
    // Include at least 4 MCQ items covering the lesson topic; add more if the topic warrants it
  ]
}}"""

    if reinforcement_type == "dialogue":
        return f"""\
"reinforcement": {{
  "type": "dialogue",
  "content": [
    {{
      "role": "<tutor | learner>",
      "prompt": "<conversational turn or role-play cue in {target_language}>",
      "suggested_response": "<expected learner response or model answer in {target_language}>"
    }}
    // Include at least 5 turns forming a coherent role-play exchange; extend if the topic needs more practice
  ]
}}"""

    if reinforcement_type == "speaking":
        return f"""\
"reinforcement": {{
  "type": "speaking",
  "content": [
    {{
      "task": "<brief task description in {target_language}>",
      "prompt": "<the speaking cue or question the learner must respond to aloud, in {target_language}>",
      "example_response": "<a model spoken answer in {target_language}>"
    }}
    // Include at least 3 speaking tasks of increasing complexity
  ]
}}"""

    if reinforcement_type == "listening":
        return f"""\
"reinforcement": {{
  "type": "listening",
  "content": [
    {{
      "scenario": "<brief scene-setting description in {target_language}>",
      "transcript": "<authentic spoken-style passage in {target_language} — write as natural speech>",
      "question": "<comprehension question in {target_language}>",
      "answer": "<correct answer in {target_language}>"
    }}
    // Include at least 3 listening scenarios; transcripts should feel like real speech
  ]
}}"""

    if reinforcement_type == "reading":
        return f"""\
"reinforcement": {{
  "type": "reading",
  "content": [
    {{
      "passage": "<short reading passage in {target_language}, appropriate for the lesson level>",
      "question": "<comprehension or inference question in {target_language}>",
      "answer": "<correct answer in {target_language}>"
    }}
    // Include 1 passage with at least 3 comprehension questions
  ]
}}"""

    if reinforcement_type == "writing":
        return f"""\
"reinforcement": {{
  "type": "writing",
  "content": [
    {{
      "task": "<task type, e.g. short message, description, opinion paragraph>",
      "prompt": "<guided writing prompt in {target_language}>",
      "word_count_guide": "<e.g. 40–70 words>",
      "model_answer": "<a concise model response in {target_language}>"
    }}
    // Include at least 2 writing tasks scaled to the lesson level
  ]
}}"""

    if reinforcement_type == "reflection":
        return f"""\
"reinforcement": {{
  "type": "reflection",
  "content": [
    {{
      "question": "<self-check question inviting the learner to reflect on what they just studied, in {target_language}>",
      "hint": "<optional hint or anchor phrase in {target_language}; may include a {native_language} note if helpful>"
    }}
    // Include at least 3 open reflection prompts — these are not graded
  ]
}}"""

    # type == "none"
    return """\
"reinforcement": {
  "type": "none",
  "content": []
}"""


def _reinforcement_instructions(reinforcement_type: str) -> str:
    """Return the generation instructions for the reinforcement section."""
    instructions = {
        "quiz": (
            "Generate at least 4 multiple-choice questions that test understanding of the lesson topic; "
            "generate more if the topic has a large or enumerable inventory. "
            "Questions must be answerable from the lesson content alone. Each must have exactly 4 options and one correct answer."
        ),
        "dialogue": (
            "Generate at least 5 turns forming a coherent role-play dialogue where the learner practices the lesson topic. "
            "Mark each turn as 'tutor' or 'learner'. Include a suggested_response for every learner turn. "
            "Extend the exchange if the topic requires more practice coverage."
        ),
        "speaking": (
            "Generate at least 3 speaking tasks of increasing difficulty. "
            "Each task must ask the learner to produce spoken output based on the lesson topic. Include a model answer."
        ),
        "listening": (
            "Generate at least 3 short listening scenarios. Each transcript must sound like authentic natural speech — "
            "not textbook sentences. Questions must be answerable solely from the transcript."
        ),
        "reading": (
            "Generate 1 short reading passage appropriate for the lesson level, followed by at least 3 comprehension questions. "
            "Passage length and complexity must match the framework level."
        ),
        "writing": (
            "Generate at least 2 guided writing tasks. Prompts must be written in the target language. "
            "Include a word_count_guide appropriate to the level and a concise model answer."
        ),
        "reflection": (
            "Generate at least 3 open self-check questions that prompt the learner to reflect on what they studied. "
            "These are not graded — they should feel natural, not like a test."
        ),
        "none": (
            "No reinforcement is required for this lesson. Set type to 'none' and content to an empty array."
        ),
    }
    return instructions.get(reinforcement_type, "")


def _adaptive_rules(context: dict) -> str:
    weaknesses  = context.get("weaknesses",  []) or []
    interests   = context.get("interests",   []) or []
    skill_focus = [s.lower().strip() for s in (context.get("skill_focus") or [])]
    session     = context.get("session_type", "new_lesson")
    level       = context.get("level") or context.get("current_level", "A1")

    lines: list[str] = []

    # Skill-focus rules fire from the curriculum node, independent of user weaknesses
    for skill in skill_focus:
        rule = _SKILL_FOCUS_RULES_MAP.get(skill)
        if rule:
            lines.append(rule)

    for w in weaknesses:
        rule = _ADAPTIVE_RULES_MAP.get(w.lower().strip())
        if rule:
            lines.append(rule)

    if interests:
        formatted = ", ".join(interests)
        lines.append(
            f"- The learner's interests are: {formatted}. "
            "Embed these naturally into examples, dialogues, and exercises wherever contextually appropriate. "
            "Do not force them — only use when they add clarity or engagement."
        )

    if session == "retry":
        lines.append(
            "- SESSION TYPE IS RETRY. Increase repetition significantly. "
            "Re-explain the core concept from a different angle. "
            "Add more exercises and use stronger reinforcement to consolidate understanding."
        )

    if level in ("A1", "A2", "HSK1", "HSK2", "N5", "N4", "TOPIK1", "TOPIK2"):
        lines.append(
            "- The learner is at a BEGINNER level. Keep sentence structures simple. "
            "Avoid idiomatic expressions unless they are the lesson topic. "
            "Prefer high-frequency vocabulary."
        )

    return "\n".join(lines) if lines else "- No specific adaptive rules apply. Follow standard curriculum delivery."


def build_lesson_prompt(context: dict) -> str:
    """
    Convert a structured context dictionary into a single AI-ready prompt string.

    Args:
        context: Merged dict containing curriculum node, user state, and session type keys.
                 Expected keys (all optional with sensible fallbacks):
                   node_id, framework, level, topic, skill_focus,
                   target_language, native_language, current_level,
                   weaknesses, strengths, interests, learning_goal,
                   session_type

    Returns:
        A fully structured prompt string ready to be sent to OpenAI as a user message.
    """
    # ── Curriculum node ───────────────────────────────────────────────────────
    node_id     = context.get("node_id",     "unknown")
    framework   = context.get("framework",   "CEFR")
    level       = context.get("level",       "A1")
    topic       = context.get("topic",       "general")
    skill_focus = context.get("skill_focus", [])

    skill_focus_str = ", ".join(skill_focus) if skill_focus else "general"

    # ── User state ────────────────────────────────────────────────────────────
    target_language  = context.get("target_language",  "the target language")
    native_language  = context.get("native_language",  "the native language")
    current_level    = context.get("current_level",    level)
    weaknesses       = context.get("weaknesses",       []) or []
    strengths        = context.get("strengths",        []) or []
    interests        = context.get("interests",        []) or []
    learning_goal    = context.get("learning_goal",    "general proficiency")

    weaknesses_str = ", ".join(weaknesses) if weaknesses else "none identified"
    strengths_str  = ", ".join(strengths)  if strengths  else "none identified"
    interests_str  = ", ".join(interests)  if interests  else "general topics"

    # ── Session type ──────────────────────────────────────────────────────────
    session_type  = context.get("session_type", "new_lesson")
    session_label = _SESSION_LABELS.get(session_type, session_type)

    # ── Reinforcement ─────────────────────────────────────────────────────────
    reinforcement_type         = _choose_reinforcement_type(context)
    reinforcement_schema_block = _reinforcement_schema(reinforcement_type, target_language, native_language)
    reinforcement_instructions = _reinforcement_instructions(reinforcement_type)

    # ── Adaptive rules ────────────────────────────────────────────────────────
    adaptive_rules = _adaptive_rules({**context, "level": level})

    # ── Assemble prompt ───────────────────────────────────────────────────────
    prompt = f"""You are a world-class language tutor AI specialising in personalised, curriculum-aligned language instruction.
Your role is to generate a single structured lesson for a real learner. You must adapt your teaching style entirely to the learner's profile below.
You are precise, pedagogically sound, and never deviate from the assigned curriculum node.
You teach like a human tutor — not every lesson is a test. Reinforcement style adapts to teaching intent.

════════════════════════════════════════
CURRICULUM NODE
════════════════════════════════════════
Node ID      : {node_id}
Framework    : {framework}
Level        : {level}
Topic        : {topic}
Skill Focus  : {skill_focus_str}

CURRICULUM LOCK — THIS IS NON-NEGOTIABLE:
The lesson MUST focus ONLY on the topic "{topic}" at {framework} level {level}.
Do NOT introduce grammar structures, vocabulary, or concepts outside of this node.
Do NOT teach content above or below {level} unless it directly supports the node topic.
Every example, dialogue, vocabulary item, and exercise must be anchored to "{topic}".

════════════════════════════════════════
USER PROFILE
════════════════════════════════════════
Target language  : {target_language}
Native language  : {native_language}
Current level    : {current_level}
Learning goal    : {learning_goal}
Weaknesses       : {weaknesses_str}
Strengths        : {strengths_str}
Interests        : {interests_str}

PERSONALISATION RULES:
- Adapt all examples to the learner's interests: {interests_str}
- Adjust difficulty and pacing to account for these weaknesses: {weaknesses_str}
- Leverage these strengths to build confidence: {strengths_str}
- Frame the lesson around the learner's goal: {learning_goal}
- If the learner's level is beginner, keep language simple and explanations accessible
- Reinforce weak areas subtly through exercises and the reinforcement section
- Explanations should be written in {target_language}
- You MAY include brief clarifying notes in {native_language} ONLY when a concept is genuinely ambiguous or likely to cause confusion — keep these minimal

════════════════════════════════════════
SESSION TYPE
════════════════════════════════════════
{session_label}

════════════════════════════════════════
ADAPTIVE RULES
════════════════════════════════════════
{adaptive_rules}

════════════════════════════════════════
REINFORCEMENT MODE: {reinforcement_type.upper()}
════════════════════════════════════════
This lesson uses reinforcement type: "{reinforcement_type}"
{reinforcement_instructions}

════════════════════════════════════════
STRICT GENERATION RULES
════════════════════════════════════════
1. The lesson must be written in {target_language}.
2. Every section must directly relate to the curriculum node: {topic} at {level}.
3. Examples must use vocabulary and structures appropriate for {level} — not higher, not lower.
4. Dialogues must feel natural and contextually relevant to the learner's interests and goal.
5. Vocabulary entries must include the word, its translation into {native_language}, and an example sentence in {target_language}.
6. Exercises must be varied: include at least one fill-in-the-blank, one translation drill, and one open construction task.
7. The reinforcement section must match the assigned type exactly — do not substitute a different type.
8. The summary must be 2–3 sentences reinforcing what was learned and hinting at what comes next.
9. Do NOT include markdown formatting, code fences, explanatory text, or any content outside the JSON object.
10. COMPLETENESS IS REQUIRED — this is the most important rule: if the topic has a finite, enumerable inventory (letters, numbers, days of the week, months, pronouns, article forms, negation patterns, verb endings, etc.) every single item in that set MUST appear in the lesson. Do not sample. Do not use "etc." Do not say "and so on." A learner who completes this lesson must feel fully equipped on the topic. For conceptual topics without a fixed inventory, cover every key rule, pattern, and common exception — not just representative examples. Thin coverage is a failure mode; err strongly on the side of more content, more examples, and more practice items.

════════════════════════════════════════
OUTPUT FORMAT — RETURN ONLY THIS JSON
════════════════════════════════════════
Return a single valid JSON object with exactly these keys and no others:

{{
  "lesson_title": "<concise title for this lesson>",
  "introduction": "<1–2 sentences welcoming the learner to this topic, in {target_language}>",
  "core_explanation": "<clear explanation of the core concept of {topic} at {level}, in {target_language}; brief native-language clarifications allowed if necessary>",
  "examples": [
    {{
      "sentence": "<example sentence in {target_language}>",
      "translation": "<translation in {native_language}>",
      "note": "<optional pedagogical note, may be in {native_language}>"
    }}
  ],
  "dialogues": [
    {{
      "speaker": "<speaker label, e.g. A or B>",
      "line": "<dialogue line in {target_language}>",
      "translation": "<translation in {native_language}>"
    }}
  ],
  "vocabulary": [
    {{
      "word": "<word or phrase in {target_language}>",
      "translation": "<translation in {native_language}>",
      "example": "<example sentence in {target_language}>"
    }}
  ],
  "exercises": [
    {{
      "type": "<fill_in_blank | translation | construction | matching>",
      "instruction": "<exercise instruction in {target_language}>",
      "prompt": "<the exercise item>",
      "answer": "<expected correct answer>"
    }}
  ],
  {reinforcement_schema_block},
  "summary": "<2–3 sentence summary of what was learned, in {target_language}>"
}}

No markdown. No explanations outside the JSON. No extra keys. Return only the JSON object."""
    return prompt