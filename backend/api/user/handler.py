import json
import uuid
from datetime import datetime, timedelta, date as date_obj

from fastapi import APIRouter, HTTPException, Query
from api.lang_map import localize
from api.hobby_map import localize_hobby
from api.motivation_map import localize_motivation
import bcrypt
from pydantic import BaseModel

from database.script import get_connection

router = APIRouter()


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))


# ─── Request models ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class RegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    native_language: str        # ISO 639-1 code e.g. "en"
    target_language: str        # ISO 639-1 code e.g. "fr"
    learning_goal: str
    selected_motivations: list[str] = []   # canonical English chip labels
    top_hobbies: list[str]                 # exactly 3 hobby names
    preferred_learning_style: str
    daily_goal_minutes: int


# ─── Language → framework mapping ────────────────────────────────────────────

_FRAMEWORK: dict[str, str] = {
    "zh": "HSK",
    "ja": "JLPT",
    "ko": "TOPIK",
}
# Everything else (en, fr, de, es, pt, it, nl, ar, ru, …) uses CEFR
_DEFAULT_FRAMEWORK = "CEFR"

_LEVEL_ORDER: dict[str, list[str]] = {
    "CEFR":  ["A1", "A2", "B1", "B2", "C1", "C2"],
    "HSK":   ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"],
    "JLPT":  ["N5", "N4", "N3", "N2", "N1"],
    "TOPIK": ["TOPIK1", "TOPIK2", "TOPIK3", "TOPIK4", "TOPIK5", "TOPIK6"],
}


def _framework_for(language_code: str) -> str:
    return _FRAMEWORK.get(language_code.lower(), _DEFAULT_FRAMEWORK)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _resolve_language_id(conn, code: str) -> int:
    row = conn.execute(
        "SELECT id FROM languages WHERE code = ?", (code.lower(),)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=400, detail=f"Unknown language code: {code}")
    return row["id"]


def _resolve_hobby_ids(conn, names: list[str]) -> list[int]:
    ids = []
    for name in names:
        row = conn.execute(
            "SELECT id FROM hobbies WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=400, detail=f"Unknown hobby: {name}")
        ids.append(row["id"])
    return ids


def _derive_username(conn, first: str, last: str) -> str:
    base = f"{first.lower()}.{last.lower()}".replace(" ", "")
    candidate = base
    n = 1
    while conn.execute(
        "SELECT 1 FROM users WHERE username = ?", (candidate,)
    ).fetchone():
        candidate = f"{base}{n}"
        n += 1
    return candidate


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/user")
def user():
    return {"message": "Hello from User API"}


class SetLevelRequest(BaseModel):
    level: str


@router.patch("/{user_id}/level")
def set_level(user_id: str, req: SetLevelRequest):
    conn = get_connection()
    try:
        row = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")
        conn.execute(
            "UPDATE users SET current_level = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (req.level, user_id),
        )
        conn.commit()
        return {"ok": True, "level": req.level}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/profile/{user_id}")
def get_profile(user_id: str, ui_lang: str = Query(default="en")):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT u.first_name, u.learning_goal, u.selected_motivations,
                   u.preferred_learning_style, u.daily_goal_minutes,
                   nl.code AS native_code, nl.name AS native_name,
                   tl.code AS target_code, tl.name AS target_name
            FROM users u
            JOIN languages nl ON nl.id = u.native_language_id
            JOIN languages tl ON tl.id = u.target_language_id
            WHERE u.id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="User not found.")

        hobbies = [
            localize_hobby(r["name"], ui_lang)
            for r in conn.execute(
                """
                SELECT h.name FROM hobbies h
                JOIN user_hobbies uh ON uh.hobby_id = h.id
                WHERE uh.user_id = ?
                """,
                (user_id,),
            ).fetchall()
        ]

        raw_motivations = json.loads(row["selected_motivations"]) if row["selected_motivations"] else []
        selected_motivations = [localize_motivation(m, ui_lang) for m in raw_motivations]

        return {
            "firstName": row["first_name"],
            "nativeLanguage": {
                "code": row["native_code"],
                "name": row["native_name"],
                "localizedName": localize(row["native_code"], ui_lang, row["native_name"]),
            },
            "targetLanguage": {
                "code": row["target_code"],
                "name": row["target_name"],
                "localizedName": localize(row["target_code"], ui_lang, row["target_name"]),
            },
            "learningGoal": row["learning_goal"],
            "selectedMotivations": selected_motivations,
            "hobbies": hobbies,
            "learningStyle": row["preferred_learning_style"],
            "dailyGoalMinutes": row["daily_goal_minutes"],
        }

    finally:
        conn.close()


@router.get("/check-email")
def check_email(email: str):
    conn = get_connection()
    try:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email.lower(),)
        ).fetchone() is not None
        return {"available": not exists}
    finally:
        conn.close()


@router.post("/login")
def login(req: LoginRequest):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE email = ?",
            (req.email.lower().strip(),),
        ).fetchone()
        if row is None or not _verify_password(req.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return {"id": row["id"], "username": row["username"], "email": row["email"]}
    finally:
        conn.close()


@router.post("/registration", status_code=201)
def register(req: RegistrationRequest):
    conn = get_connection()
    try:
        # Reject duplicate email early with a clear message
        if conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (req.email,)
        ).fetchone():
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        native_id  = _resolve_language_id(conn, req.native_language)
        target_id  = _resolve_language_id(conn, req.target_language)
        hobby_ids  = _resolve_hobby_ids(conn, req.top_hobbies)
        username   = _derive_username(conn, req.first_name, req.last_name)
        user_id    = str(uuid.uuid4())
        pw_hash    = _hash_password(req.password)
        framework  = _framework_for(req.target_language)

        conn.execute(
            """
            INSERT INTO users (
                id, email, username, first_name, last_name, password_hash,
                native_language_id, target_language_id,
                learning_goal, selected_motivations,
                preferred_learning_style, daily_goal_minutes,
                framework
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, req.email, username,
                req.first_name, req.last_name, pw_hash,
                native_id, target_id,
                req.learning_goal, json.dumps(req.selected_motivations),
                req.preferred_learning_style, req.daily_goal_minutes,
                framework,
            ),
        )

        conn.executemany(
            "INSERT INTO user_hobbies (user_id, hobby_id) VALUES (?, ?)",
            [(user_id, hid) for hid in hobby_ids],
        )

        conn.commit()

        return {
            "id": user_id,
            "username": username,
            "email": req.email,
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()


@router.get("/dashboard/{user_id}")
def get_dashboard(user_id: str, ui_lang: str = Query(default="en")):
    conn = get_connection()
    try:
        # ── User + languages ──────────────────────────────────────────────────
        user = conn.execute("""
            SELECT u.*, nl.code AS native_code, nl.name AS native_name,
                   tl.code AS target_code, tl.name AS target_name
            FROM users u
            JOIN languages nl ON nl.id = u.native_language_id
            JOIN languages tl ON tl.id = u.target_language_id
            WHERE u.id = ?
        """, (user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        hobbies = [
            localize_hobby(r["name"], ui_lang)
            for r in conn.execute("""
                SELECT h.name FROM hobbies h
                JOIN user_hobbies uh ON uh.hobby_id = h.id
                WHERE uh.user_id = ?
            """, (user_id,)).fetchall()
        ]

        # ── XP level band ─────────────────────────────────────────────────────
        xp = user["current_xp"] or 0
        xp_row = conn.execute("""
            SELECT xp_required, xp_to_next FROM xp_levels
            WHERE xp_required <= ? ORDER BY xp_required DESC LIMIT 1
        """, (xp,)).fetchone()
        xp_current_level = xp_row["xp_required"] if xp_row else 0
        xp_next_level    = xp_row["xp_to_next"]  if xp_row else 1000

        # ── Study days ────────────────────────────────────────────────────────
        today = date_obj.today()

        total_study_days = conn.execute("""
            SELECT COUNT(DISTINCT DATE(started_at))
            FROM learning_sessions WHERE user_id = ?
        """, (user_id,)).fetchone()[0] or 0

        weekly_active_days = conn.execute("""
            SELECT COUNT(DISTINCT DATE(started_at))
            FROM learning_sessions
            WHERE user_id = ? AND started_at >= DATE('now', '-7 days')
        """, (user_id,)).fetchone()[0] or 0

        # ── Streak (computed dynamically from sessions) ───────────────────────
        all_session_days: set[str] = {
            r["day"] for r in conn.execute(
                "SELECT DISTINCT DATE(started_at) AS day FROM learning_sessions WHERE user_id = ?",
                (user_id,)
            ).fetchall()
        }

        # Count back from today; if no session today allow starting from yesterday
        streak_start = today if today.isoformat() in all_session_days else today - timedelta(days=1)
        current_streak = 0
        d = streak_start
        while d.isoformat() in all_session_days:
            current_streak += 1
            d -= timedelta(days=1)

        longest_streak = 0
        if all_session_days:
            sorted_days = sorted(all_session_days)
            run = 1
            longest_streak = 1
            for i in range(1, len(sorted_days)):
                gap = (date_obj.fromisoformat(sorted_days[i]) - date_obj.fromisoformat(sorted_days[i - 1])).days
                if gap == 1:
                    run += 1
                    if run > longest_streak:
                        longest_streak = run
                else:
                    run = 1

        # ── Heatmap (365 days) ────────────────────────────────────────────────
        session_rows = conn.execute("""
            SELECT DATE(started_at) AS day, SUM(minutes_spent) AS total_min
            FROM learning_sessions
            WHERE user_id = ? AND started_at >= DATE('now', '-365 days')
            GROUP BY DATE(started_at)
        """, (user_id,)).fetchall()
        day_map = {r["day"]: r["total_min"] for r in session_rows}
        heatmap = []
        for i in range(364, -1, -1):
            day_str = (today - timedelta(days=i)).isoformat()
            mins    = day_map.get(day_str) or 0
            if   mins == 0:  heatmap.append(0)
            elif mins < 15:  heatmap.append(1)
            elif mins < 30:  heatmap.append(2)
            elif mins < 60:  heatmap.append(3)
            else:            heatmap.append(4)

        # ── Skill scores + trends ─────────────────────────────────────────────
        skills: dict[str, dict] = {
            "reading":   {"value": 0, "trend": 0},
            "listening": {"value": 0, "trend": 0},
            "writing":   {"value": 0, "trend": 0},
            "speaking":  {"value": 0, "trend": 0},
        }
        # Fetch the two most recent score entries per skill from skill_scores
        for skill in skills:
            rows = conn.execute("""
                SELECT score FROM skill_scores
                WHERE user_id = ? AND skill = ?
                ORDER BY recorded_at DESC LIMIT 2
            """, (user_id, skill)).fetchall()
            if rows:
                skills[skill]["value"] = round(rows[0]["score"])
                if len(rows) == 2:
                    skills[skill]["trend"] = round(rows[0]["score"] - rows[1]["score"])

        # ── Achievements ──────────────────────────────────────────────────────
        all_ach = conn.execute(
            "SELECT id, name, description FROM achievements ORDER BY id"
        ).fetchall()
        earned_map = {
            r["achievement_id"]: r["unlocked_at"]
            for r in conn.execute(
                "SELECT achievement_id, unlocked_at FROM user_achievements WHERE user_id = ?",
                (user_id,)
            ).fetchall()
        }
        progress_map = {
            r["achievement_id"]: {"current": r["current_value"], "target": r["target_value"]}
            for r in conn.execute(
                "SELECT achievement_id, current_value, target_value FROM achievement_progress WHERE user_id = ?",
                (user_id,)
            ).fetchall()
        }
        achievements = []
        for a in all_ach:
            if a["id"] in earned_map:
                ts = earned_map[a["id"]] or ""
                try:
                    earned_date = datetime.fromisoformat(ts.split(".")[0]).strftime("%b %Y")
                except Exception:
                    earned_date = ts[:7]
                achievements.append({"id": a["name"], "earned": True, "earnedDate": earned_date})
            else:
                entry: dict = {"id": a["name"], "earned": False}
                prog = progress_map.get(a["id"])
                if prog:
                    entry["current"]  = prog["current"]
                    entry["target"]   = prog["target"]
                    entry["progress"] = prog["current"] / prog["target"] if prog["target"] > 0 else 0
                achievements.append(entry)

        # ── Vocabulary ────────────────────────────────────────────────────────
        vocab_total    = conn.execute("SELECT COUNT(*) FROM vocabulary_items WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
        vocab_active   = conn.execute("SELECT COUNT(*) FROM vocabulary_items WHERE user_id = ? AND proficiency_score >= 0.3", (user_id,)).fetchone()[0] or 0
        retention_row  = conn.execute("""
            SELECT CAST(SUM(times_correct) AS REAL) / NULLIF(SUM(times_seen), 0) * 100
            FROM vocabulary_items WHERE user_id = ? AND times_seen > 0
        """, (user_id,)).fetchone()[0]
        vocab_retention = round(retention_row or 0)
        vocab_new_week  = conn.execute("""
            SELECT COUNT(*) FROM vocabulary_items
            WHERE user_id = ? AND created_at >= DATE('now', '-7 days')
        """, (user_id,)).fetchone()[0] or 0
        vocab_recent  = [dict(r) for r in conn.execute("""
            SELECT word, translation FROM vocabulary_items WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 5
        """, (user_id,)).fetchall()]
        vocab_review  = [dict(r) for r in conn.execute("""
            SELECT word, translation,
                   CASE WHEN proficiency_score < 0.3 THEN 'hard'
                        WHEN proficiency_score < 0.6 THEN 'medium' ELSE 'easy' END AS difficulty
            FROM vocabulary_items
            WHERE user_id = ? AND next_review_at <= CURRENT_TIMESTAMP
            ORDER BY next_review_at ASC LIMIT 5
        """, (user_id,)).fetchall()]
        vocab_due_count = conn.execute("""
            SELECT COUNT(*) FROM vocabulary_items
            WHERE user_id = ? AND next_review_at <= CURRENT_TIMESTAMP
        """, (user_id,)).fetchone()[0] or 0

        # ── Grammar ───────────────────────────────────────────────────────────
        def _grammar_rows(status: str, limit: int) -> list[dict]:
            return [dict(r) for r in conn.execute("""
                SELECT gt.topic, ugp.confidence_score,
                       CASE WHEN ugp.times_practiced > 0
                            THEN CAST(ugp.times_correct AS REAL) / ugp.times_practiced
                            ELSE 0 END AS progress
                FROM user_grammar_progress ugp
                JOIN grammar_topics gt ON gt.id = ugp.topic_id
                WHERE ugp.user_id = ? AND ugp.status = ?
                ORDER BY ugp.confidence_score DESC LIMIT ?
            """, (user_id, status, limit)).fetchall()]

        grammar_data = {
            "mastered": _grammar_rows("mastered", 10),
            "learning": _grammar_rows("learning", 5),
            "review":   _grammar_rows("review",   5),
        }

        # ── Assessment history ────────────────────────────────────────────────
        def _fmt_date(ts: str | None) -> str:
            if not ts: return ""
            try: return datetime.fromisoformat(ts.split(".")[0]).strftime("%b %d, %Y")
            except Exception: return (ts or "")[:10]

        _TYPE_KEY = {
            "placement_reading":   "dash_assess_type_placement",
            "placement_listening": "dash_assess_type_placement",
            "placement_writing":   "dash_assess_type_placement",
            "placement_speaking":  "dash_assess_type_placement",
        }
        assessment_history = [
            {
                "date":    _fmt_date(r["completed_at"]),
                "score":   round(r["score"] or 0),
                "level":   r["estimated_level"] or "",
                "typeKey": _TYPE_KEY.get(r["assessment_type"], "dash_assess_type_curriculum"),
            }
            for r in conn.execute("""
                SELECT assessment_type, estimated_level, score, completed_at
                FROM assessments WHERE user_id = ? AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 10
            """, (user_id,)).fetchall()
        ]
        upcoming_assessments = [
            {
                "title":    r["title"],
                "typeKey":  "dash_assess_type_curriculum",
                "date":     _fmt_date(r["scheduled_at"]),
                "duration": r["duration_minutes"] or 30,
            }
            for r in conn.execute("""
                SELECT title, assessment_type, scheduled_at, duration_minutes
                FROM scheduled_assessments
                WHERE user_id = ? AND is_completed = 0 AND scheduled_at >= CURRENT_TIMESTAMP
                ORDER BY scheduled_at ASC LIMIT 5
            """, (user_id,)).fetchall()
        ]

        # ── Learning stats ────────────────────────────────────────────────────
        stats_row = conn.execute("""
            SELECT
                COALESCE(SUM(minutes_spent), 0) AS total_min,
                COALESCE(SUM(CASE WHEN started_at >= DATE('now','-7 days')  THEN minutes_spent ELSE 0 END), 0) AS week_min,
                COALESCE(SUM(CASE WHEN started_at >= DATE('now','-30 days') THEN minutes_spent ELSE 0 END), 0) AS month_min,
                COUNT(*) AS session_count
            FROM learning_sessions WHERE user_id = ?
        """, (user_id,)).fetchone()
        assessments_completed   = conn.execute("SELECT COUNT(*) FROM assessments WHERE user_id = ? AND completed_at IS NOT NULL", (user_id,)).fetchone()[0] or 0
        conversations_completed = conn.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,)).fetchone()[0] or 0
        lessons_completed       = conn.execute("SELECT COUNT(*) FROM user_lesson_progress WHERE user_id = ? AND status = 'completed'", (user_id,)).fetchone()[0] or 0
        avg_daily = round((stats_row["total_min"] or 0) / total_study_days) if total_study_days > 0 else 0

        weekly_raw = conn.execute("""
            SELECT strftime('%Y-%W', started_at) AS yw, SUM(minutes_spent) AS total_min
            FROM learning_sessions
            WHERE user_id = ? AND started_at >= DATE('now', '-49 days')
            GROUP BY yw ORDER BY yw
        """, (user_id,)).fetchall()
        yw_map = {r["yw"]: (r["total_min"] or 0) / 60 for r in weekly_raw}
        weekly_hours:  list[float] = []
        weekly_labels: list[str]   = []
        for i in range(6, -1, -1):
            wk = today - timedelta(weeks=i)
            yw = wk.strftime("%Y-%W")
            weekly_hours.append(round(yw_map.get(yw, 0), 1))
            weekly_labels.append(f"W{wk.strftime('%V')}")

        # ── Curriculum modules ────────────────────────────────────────────────
        curriculum = [
            {
                "id":               r["id"],
                "title":            r["title"],
                "status":           r["status"],
                "lessons":          r["total_lessons"],
                "completedLessons": r["completed_lessons"],
            }
            for r in conn.execute("""
                SELECT cm.id, cm.title, cm.total_lessons, cm.module_order,
                       COALESCE(ump.status,'locked') AS status,
                       COALESCE(ump.completed_lessons, 0) AS completed_lessons
                FROM curriculum_modules cm
                LEFT JOIN user_module_progress ump ON ump.module_id = cm.id AND ump.user_id = ?
                WHERE cm.language_id = (SELECT target_language_id FROM users WHERE id = ?)
                  AND cm.framework   = (SELECT framework             FROM users WHERE id = ?)
                ORDER BY cm.module_order
            """, (user_id, user_id, user_id)).fetchall()
        ]

        # ── Goal percent complete ─────────────────────────────────────────────
        # Count completed lessons directly from user_lesson_progress, not from
        # user_module_progress.completed_lessons which is never auto-updated.
        total_curriculum_lessons = sum(m["lessons"] for m in curriculum)
        completed_curriculum_lessons = conn.execute("""
            SELECT COUNT(*) FROM user_lesson_progress ulp
            JOIN lessons l ON l.id = ulp.lesson_id
            JOIN curriculum_modules cm ON cm.id = l.module_id
            WHERE ulp.user_id = ?
              AND ulp.status = 'completed'
              AND cm.language_id = (SELECT target_language_id FROM users WHERE id = ?)
              AND cm.framework   = (SELECT framework             FROM users WHERE id = ?)
        """, (user_id, user_id, user_id)).fetchone()[0] or 0
        goal_pct = (
            min(100, round(completed_curriculum_lessons / total_curriculum_lessons * 100))
            if total_curriculum_lessons > 0 else 0
        )

        # ── Current lesson ────────────────────────────────────────────────────
        current_lesson = None
        cur_mod = conn.execute("""
            SELECT cm.id, cm.title
            FROM user_module_progress ump
            JOIN curriculum_modules cm ON cm.id = ump.module_id
            WHERE ump.user_id = ? AND ump.status = 'current'
            ORDER BY cm.module_order LIMIT 1
        """, (user_id,)).fetchone()

        if cur_mod:
            # Prefer the most recently started in-progress lesson in this module
            lesson_row = conn.execute("""
                SELECT l.id, l.node_id, l.title, l.lesson_order, l.estimated_minutes
                FROM user_lesson_progress ulp
                JOIN lessons l ON l.id = ulp.lesson_id
                WHERE ulp.user_id = ? AND l.module_id = ? AND ulp.status = 'in_progress'
                ORDER BY ulp.started_at DESC LIMIT 1
            """, (user_id, cur_mod["id"])).fetchone()

            if not lesson_row:
                # Fall back to the first lesson that hasn't been completed
                lesson_row = conn.execute("""
                    SELECT l.id, l.node_id, l.title, l.lesson_order, l.estimated_minutes
                    FROM lessons l
                    WHERE l.user_id = ? AND l.module_id = ?
                      AND l.id NOT IN (
                          SELECT lesson_id FROM user_lesson_progress
                          WHERE user_id = ? AND status = 'completed'
                      )
                    ORDER BY l.lesson_order LIMIT 1
                """, (user_id, cur_mod["id"], user_id)).fetchone()

            if lesson_row:
                completed_in_module = conn.execute("""
                    SELECT COUNT(*) FROM user_lesson_progress ulp
                    JOIN lessons l ON l.id = ulp.lesson_id
                    WHERE ulp.user_id = ? AND l.module_id = ? AND ulp.status = 'completed'
                """, (user_id, cur_mod["id"])).fetchone()[0]
                total_in_module = conn.execute(
                    "SELECT COUNT(*) FROM lessons WHERE user_id = ? AND module_id = ?",
                    (user_id, cur_mod["id"])
                ).fetchone()[0]
                current_lesson = {
                    "nodeId":           lesson_row["node_id"],
                    "title":            lesson_row["title"],
                    "module":           cur_mod["title"],
                    "lessonNumber":     completed_in_module + 1,
                    "totalLessons":     max(total_in_module, completed_in_module + 1),
                    "estimatedMinutes": lesson_row["estimated_minutes"] or 15,
                }

        # ── Next unstarted node ───────────────────────────────────────────────
        next_node_row = conn.execute("""
            SELECT cn.id FROM curriculum_nodes cn
            WHERE cn.language_id = (SELECT target_language_id FROM users WHERE id = ?)
              AND cn.framework   = (SELECT framework FROM users WHERE id = ?)
              AND cn.id NOT IN (
                  SELECT l.node_id FROM lessons l
                  WHERE l.user_id = ? AND l.node_id IS NOT NULL
              )
            ORDER BY cn.lesson_order
            LIMIT 1
        """, (user_id, user_id, user_id)).fetchone()
        next_node_id = next_node_row["id"] if next_node_row else None

        # ── Error log ─────────────────────────────────────────────────────────
        errors = {
            "vocabulary": [
                {"word": r["reference"], "typeKey": "dash_error_type_repeated", "count": r["count"]}
                for r in conn.execute(
                    "SELECT reference, count FROM error_log WHERE user_id = ? AND error_type = 'vocabulary' ORDER BY count DESC LIMIT 5",
                    (user_id,)
                ).fetchall()
            ],
            "grammar": [
                {"topic": r["reference"], "count": r["count"]}
                for r in conn.execute(
                    "SELECT reference, count FROM error_log WHERE user_id = ? AND error_type = 'grammar' ORDER BY count DESC LIMIT 5",
                    (user_id,)
                ).fetchall()
            ],
            "sentenceStructure": [
                {"pattern": r["reference"], "count": r["count"]}
                for r in conn.execute(
                    "SELECT reference, count FROM error_log WHERE user_id = ? AND error_type = 'structure' ORDER BY count DESC LIMIT 5",
                    (user_id,)
                ).fetchall()
            ],
            "skills": _compute_skill_weaknesses(conn, user_id, skills),
        }

        # ── Certification ─────────────────────────────────────────────────────
        framework     = (user["framework"] or "CEFR").upper()
        current_level = user["current_level"] or ""
        levels        = _LEVEL_ORDER.get(framework, [])
        curr_idx      = levels.index(current_level) if current_level in levels else -1
        target_exam   = levels[curr_idx + 1] if 0 <= curr_idx < len(levels) - 1 else None
        skill_avg     = round(sum(s["value"] for s in skills.values()) / 4) if skills else 0
        sorted_skills = sorted(skills.items(), key=lambda x: x[1]["value"], reverse=True)
        certification = {
            "name":               f"{framework} {current_level}" if current_level else framework,
            "targetExam":         f"{framework} {target_exam}" if target_exam else None,
            "readiness":          skill_avg,
            "estimatedReadyDate": None,
            "strongest":          [s[0].capitalize() for s in sorted_skills[:2]] if sorted_skills else [],
            "weakest":            [s[0].capitalize() for s in sorted_skills[-2:]] if sorted_skills else [],
        }

        # ── Insights (rule-based) ─────────────────────────────────────────────
        insights = _build_insights(skills, current_streak, total_study_days, vocab_retention)

        # ── Actions (rule-based) ──────────────────────────────────────────────
        actions = _build_actions(
            vocab_due_count   = vocab_due_count,
            current_lesson    = current_lesson,
            upcoming          = upcoming_assessments,
            grammar_review    = grammar_data["review"],
            skills            = skills,
        )

        # ── Build response ────────────────────────────────────────────────────
        first = user["first_name"] or ""
        last  = user["last_name"]  or ""
        return {
            "profile": {
                "firstName":        first,
                "lastName":         last,
                "username":         user["username"],
                "displayName":      f"{first} {last}".strip(),
                "email":            user["email"],
                "avatarInitials":   f"{first[:1]}{last[:1]}".upper(),
                "nativeLanguage":   localize(user["native_code"], ui_lang, user["native_name"]),
                "targetLanguage":   localize(user["target_code"], ui_lang, user["target_name"]),
                "currentLevel":     current_level,
                "targetLevel":      user["target_level"],
                "framework":        framework,
                "xp":               xp,
                "xpCurrentLevel":   xp_current_level,
                "xpNextLevel":      xp_next_level,
                "learningStyle":    user["preferred_learning_style"] or "",
                "hobbies":          hobbies,
                "dailyGoalMinutes": user["daily_goal_minutes"] or 30,
            },
            "goal": {
                "title":           user["learning_goal"] or "",
                "percentComplete": goal_pct,
                "targetLevel":     user["target_level"],
            },
            "currentLesson": current_lesson,
            "nextNodeId":    next_node_id,
            "streak": {
                "currentStreak":     current_streak,
                "longestStreak":     longest_streak,
                "totalStudyDays":    total_study_days,
                "weeklyConsistency": round((weekly_active_days / 7) * 100),
            },
            "heatmapData":  heatmap,
            "skills":       skills,
            "achievements": achievements,
            "vocab": {
                "total":         vocab_total,
                "active":        vocab_active,
                "retentionRate": vocab_retention,
                "newPerWeek":    vocab_new_week,
                "recent":        vocab_recent,
                "review":        vocab_review,
            },
            "grammar":    grammar_data,
            "insights":   insights,
            "assessments": {
                "upcoming": upcoming_assessments,
                "history":  assessment_history,
            },
            "errors":        errors,
            "certification": certification,
            "stats": {
                "totalHours":             round((stats_row["total_min"] or 0) / 60, 1),
                "thisWeekHours":          round((stats_row["week_min"]  or 0) / 60, 1),
                "thisMonthHours":         round((stats_row["month_min"] or 0) / 60, 1),
                "avgDailyMinutes":        avg_daily,
                "lessonsCompleted":       lessons_completed,
                "assessmentsCompleted":   assessments_completed,
                "conversationsCompleted": conversations_completed,
                "weeklyHoursData":        weekly_hours,
                "weekLabels":             weekly_labels,
            },
            "curriculum": curriculum,
            "actions":    actions,
        }

    finally:
        conn.close()


# ── Helper: skill weaknesses from assessment responses ────────────────────────

def _compute_skill_weaknesses(
    conn,
    user_id: str,
    skills: dict[str, dict],
) -> dict[str, list[str]]:
    weaknesses: dict[str, list[str]] = {
        "reading": [], "listening": [], "speaking": [], "writing": []
    }

    # Wrong answers per question type from MCQ assessments
    wrong_by_type: dict[str, int] = {
        r["question_type"]: r["wrong_count"]
        for r in conn.execute("""
            SELECT aq.question_type, COUNT(*) AS wrong_count
            FROM assessment_responses ar
            JOIN assessment_questions aq ON aq.id = ar.question_id
            JOIN assessments a ON a.id = ar.assessment_id
            WHERE a.user_id = ? AND ar.is_correct = 0
            GROUP BY aq.question_type
        """, (user_id,)).fetchall()
    }
    if wrong_by_type.get("mcq", 0) > 2:
        weaknesses["reading"] = ["Reading comprehension", "Vocabulary in context"]
    if wrong_by_type.get("listening_mcq", 0) > 2:
        weaknesses["listening"] = ["Connected speech", "Rapid dialogue"]

    # Derive writing/speaking weaknesses from low placement scores
    for row in conn.execute("""
        SELECT assessment_type, score FROM assessments
        WHERE user_id = ?
          AND assessment_type IN ('placement_writing', 'placement_speaking')
        ORDER BY completed_at DESC LIMIT 2
    """, (user_id,)).fetchall():
        score = row["score"] or 0
        if row["assessment_type"] == "placement_writing" and score < 60:
            weaknesses["writing"] = ["Grammar accuracy", "Sentence structure"]
        elif row["assessment_type"] == "placement_speaking" and score < 60:
            weaknesses["speaking"] = ["Pronunciation", "Fluency"]

    # Fallback: flag skills that have a score but are the weakest area
    skill_values = {k: v["value"] for k, v in skills.items() if v["value"] > 0}
    if skill_values:
        weakest = min(skill_values, key=skill_values.get)
        if not weaknesses[weakest]:
            _fallback: dict[str, list[str]] = {
                "reading":   ["Reading comprehension", "Vocabulary in context"],
                "listening": ["Connected speech", "Rapid dialogue"],
                "speaking":  ["Pronunciation", "Fluency"],
                "writing":   ["Grammar accuracy", "Sentence structure"],
            }
            weaknesses[weakest] = _fallback[weakest]

    return weaknesses


# ── Helper: rule-based insights ───────────────────────────────────────────────

def _build_insights(
    skills: dict[str, dict],
    current_streak: int,
    total_study_days: int,
    vocab_retention: int,
) -> list[dict]:
    insights: list[dict] = []
    skill_values = {k: v["value"] for k, v in skills.items() if v["value"] > 0}

    if skill_values:
        sorted_skills = sorted(skill_values.items(), key=lambda x: x[1], reverse=True)
        strongest_key = sorted_skills[0][0]
        weakest_key   = sorted_skills[-1][0]

        insights.append({
            "type": "strength",
            "icon": "🏆",
            "textKey": f"dash_insights_strength_{strongest_key}",
        })

        # Improvement: pick the skill with the highest positive trend
        improving = [(k, v["trend"]) for k, v in skills.items() if v["trend"] > 0]
        if improving:
            best_key = max(improving, key=lambda x: x[1])[0]
            insights.append({
                "type": "improvement",
                "icon": "📈",
                "textKey": f"dash_insights_improve_{best_key}",
            })

        insights.append({
            "type": "weakness",
            "icon": "🎯",
            "textKey": f"dash_insights_focus_{weakest_key}",
        })

    # Habit insight based on study consistency
    if current_streak >= 7:
        insights.append({"type": "habit", "icon": "🔥", "textKey": "dash_insights_habit_streak"})
    elif total_study_days >= 30:
        insights.append({"type": "habit", "icon": "💡", "textKey": "dash_insights_habit_consistent"})
    else:
        insights.append({"type": "habit", "icon": "💡", "textKey": "dash_insights_habit_routine"})

    return insights


# ── Helper: rule-based recommended actions ────────────────────────────────────

def _build_actions(
    vocab_due_count: int,
    current_lesson: dict | None,
    upcoming: list[dict],
    grammar_review: list[dict],
    skills: dict[str, dict],
) -> list[dict]:
    actions: list[dict] = []
    aid = 1

    if vocab_due_count > 0:
        actions.append({
            "id": aid, "type": "review", "icon": "📚",
            "titleKey": "dash_action_review_vocab",
            "priority": "high" if vocab_due_count >= 10 else "medium",
            "estimatedMinutes": 10,
        })
        aid += 1

    if current_lesson:
        actions.append({
            "id": aid, "type": "lesson", "icon": "📖",
            "titleKey": "dash_action_lesson",
            "priority": "high",
            "estimatedMinutes": current_lesson["estimatedMinutes"],
        })
        aid += 1

    if upcoming:
        actions.append({
            "id": aid, "type": "assessment", "icon": "🎯",
            "titleKey": "dash_action_prepare_assessment",
            "priority": "high",
            "estimatedMinutes": 15,
        })
        aid += 1

    skill_values = {k: v["value"] for k, v in skills.items() if v["value"] > 0}
    if skill_values:
        weakest = min(skill_values, key=skill_values.get)
        if weakest == "listening":
            actions.append({
                "id": aid, "type": "assessment", "icon": "🎧",
                "titleKey": "dash_action_listening",
                "priority": "medium",
                "estimatedMinutes": 12,
            })
            aid += 1
        elif weakest == "speaking":
            actions.append({
                "id": aid, "type": "practice", "icon": "🗣️",
                "titleKey": "dash_action_speaking",
                "priority": "medium",
                "estimatedMinutes": 10,
            })
            aid += 1

    if grammar_review:
        actions.append({
            "id": aid, "type": "grammar", "icon": "📝",
            "titleKey": "dash_action_grammar",
            "priority": "low",
            "estimatedMinutes": 8,
        })

    return actions
