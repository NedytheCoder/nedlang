"""
script.py
─────────
Database utilities for lingua_ai.db.

Public API
──────────
    get_connection()       → sqlite3.Connection
    create_database()      → None   (tables + indexes)
    drop_database()        → None   (wipe everything)
    seed_languages(conn)   → None
    seed_hobbies(conn)     → None
    initialize_database()  → None   (full first-run setup)
"""

import json
import sqlite3
import os
from database.schema import create_tables, drop_tables

# ─── Configuration ────────────────────────────────────────────────────────────

_DB_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(_DB_DIR, "lingua_ai.db")


# ─── Seed data ────────────────────────────────────────────────────────────────

_LANGUAGES: list[tuple[str, str, str]] = [
    # (code, name, native_name)
    ("en", "English",    "English"),
    ("fr", "French",     "Français"),
    ("de", "German",     "Deutsch"),
    ("zh", "Chinese",    "中文"),
    # ("es", "Spanish",    "Español"),
    # ("pt", "Portuguese", "Português"),
    # ("it", "Italian",    "Italiano"),
    # ("nl", "Dutch",      "Nederlands"),
    # ("ja", "Japanese",   "日本語"),
    # ("ko", "Korean",     "한국어"),
    # ("ar", "Arabic",     "العربية"),
    # ("ru", "Russian",    "Русский"),
]

_HOBBIES: list[str] = [
    "Technology",
    "Gaming",
    "Football",
    "Basketball",
    "Anime",
    "Cooking",
    "Travel",
    "Reading",
    "Business",
    "Fitness",
    "Movies",
    "Music",
    "Photography",
]

_MOTIVATIONS: list[str] = [
    "Career growth",
    "Travel",
    "Relocating abroad",
    "University studies",
    "Business communication",
    "Watching movies without subtitles",
    "Speaking with family",
    "Personal interest",
]


# ─── Connection ───────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """
    Open (or create) lingua_ai.db and return a connection.

    - Row factory set to sqlite3.Row for dict-like access.
    - Foreign key enforcement enabled on every connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # better concurrent read performance
    return conn


# ─── Create / Drop ────────────────────────────────────────────────────────────

def create_database() -> None:
    """Create all tables and indexes. Idempotent."""
    conn = get_connection()
    try:
        create_tables(conn)
        print(f"[db] Tables and indexes created → {DB_PATH}")
    finally:
        conn.close()


def drop_database() -> None:
    """
    Drop every table.  All data is permanently deleted.
    Use only in development / test resets.
    """
    conn = get_connection()
    try:
        drop_tables(conn)
        print(f"[db] All tables dropped → {DB_PATH}")
    finally:
        conn.close()


# ─── Seed data (continued) ───────────────────────────────────────────────────

# XP level bands — (level_no, label, xp_required, xp_to_next)
# Designed so that xp=8240 lands in level 5 (7000–10000), matching mock data.
_XP_LEVELS: list[tuple[int, str, int, int | None]] = [
    (1,  "Novice",            0,      1000),
    (2,  "Beginner",          1000,   1500),
    (3,  "Elementary",        2500,   2000),
    (4,  "Pre-Intermediate",  4500,   2500),
    (5,  "Intermediate",      7000,   3000),
    (6,  "Upper-Intermediate",10000,  3500),
    (7,  "Advanced",          13500,  4500),
    (8,  "Proficient",        18000,  6000),
    (9,  "Expert",            24000,  8000),
    (10, "Master",            32000,  None),
]

# Achievements — (name, description, xp_reward)
_ACHIEVEMENTS: list[tuple[str, str, int]] = [
    # ── Firsts ────────────────────────────────────────────────────────────────
    ("first_lesson",          "Complete your first lesson",                           50),
    ("first_convo",           "Complete your first conversation",                     50),
    ("first_assessment",      "Complete your first assessment",                       50),

    # ── Vocabulary ────────────────────────────────────────────────────────────
    ("hundred_words",         "Learn 100 vocabulary words",                           100),
    ("vocab_explorer",        "Learn 500 vocabulary words",                           200),
    ("vocab_master",          "Learn 1000 vocabulary words",                          500),

    # ── Streaks ───────────────────────────────────────────────────────────────
    ("streak_3",              "Study 3 days in a row",                                50),
    ("streak_7",              "Study 7 days in a row",                                100),
    ("streak_30",             "Study 30 days in a row",                               500),
    ("streak_100",            "Study 100 days in a row",                              1000),

    # ── Grammar ───────────────────────────────────────────────────────────────
    ("grammar_master",        "Master 10 grammar topics",                             200),
    ("grammar_expert",        "Master 25 grammar topics",                             500),

    # ── Skills ────────────────────────────────────────────────────────────────
    ("listening_specialist",  "Complete 20 listening exercises",                      200),
    ("reading_specialist",    "Complete 20 reading exercises",                        200),
    ("writing_specialist",    "Complete 20 writing exercises",                        200),
    ("speaking_specialist",   "Complete 20 speaking exercises",                       200),

    # ── Assessments ───────────────────────────────────────────────────────────
    ("assessment_champion",   "Complete 5 assessments",                               200),
    ("perfect_score",         "Score 100% on any assessment",                         500),

    # ── Levels ────────────────────────────────────────────────────────────────
    ("level_up",              "Reach app level 5 (Intermediate)",                     200),
    ("framework_advance",     "Advance one full framework level (e.g. A1 → A2)",      300),

    # ── Study time ────────────────────────────────────────────────────────────
    ("ten_hours",             "Accumulate 10 hours of study time",                    100),
    ("fifty_hours",           "Accumulate 50 hours of study time",                    300),
    ("hundred_hours",         "Accumulate 100 hours of study time",                   500),
]


# ─── French A1 curriculum ─────────────────────────────────────────────────────

# (module_order, title, description, total_lessons)
_FRENCH_A1_MODULES: list[tuple[int, str, str, int]] = [
    (1,  "Sounds and Letters",              "Master the French alphabet, pronunciation, and accent marks",    4),
    (2,  "Core Grammar Foundations",        "Learn subject pronouns, sentence structure, être and avoir",    4),
    (3,  "Numbers, Time, and Identity",     "Numbers, dates, time, nationalities, and occupations",          5),
    (4,  "Nouns and Articles",              "Gender, definite and indefinite articles, and plurals",          4),
    (5,  "Adjectives",                      "Descriptive adjectives, agreement, and possessives",             3),
    (6,  "Verbs",                           "Regular -er/-ir/-re verbs and key irregular verbs",              6),
    (7,  "Questions and Negation",          "Negation, interrogatives, question forms, and opinions",         4),
    (8,  "Modifiers",                       "Prepositions, adverbs, and object pronouns",                    3),
    (9,  "Past and Future Tenses",          "Introduction to passé composé and futur proche",                2),
    (10, "Communication in the Real World", "Self-introduction, family, routines, and written expression",   7),
]

# (unit, lesson_order, topic, skill_focus, learning_objectives)
_FRENCH_A1_NODES: list[tuple[int, int, str, list, list]] = [
    (1,  1,  "Alphabet",
        ["phonetics"],
        ["Recognize all 26 French letters", "Understand basic French pronunciation rules"]),
    (1,  2,  "Pronunciation",
        ["pronunciation"],
        ["Pronounce basic French sounds correctly", "Identify key differences from English pronunciation"]),
    (1,  3,  "French accents and special characters",
        ["phonetics"],
        ["Recognize and write accents (é, è, ê, à, ù, ç)", "Understand how accents affect pronunciation"]),
    (1,  4,  "Basic greetings and introductions",
        ["speaking", "vocabulary"],
        ["Use common greetings in context", "Introduce yourself in French"]),

    (2,  5,  "Subject pronouns",
        ["grammar"],
        ["Identify and use je, tu, il, elle, nous, vous, ils, elles", "Match pronouns to people and contexts"]),
    (2,  6,  "Basic sentence structure",
        ["grammar"],
        ["Form simple subject-verb sentences", "Understand French word order"]),
    (2,  7,  "Être",
        ["grammar"],
        ["Conjugate être in the present tense", "Use être to describe identity and state"]),
    (2,  8,  "Avoir",
        ["grammar"],
        ["Conjugate avoir in the present tense", "Use avoir in common expressions"]),

    (3,  9,  "Numbers 0–100",
        ["vocabulary"],
        ["Count from 0 to 100 in French", "Use numbers in everyday contexts"]),
    (3,  10, "Days, months, dates",
        ["vocabulary"],
        ["Name the days of the week and months", "Express dates in French"]),
    (3,  11, "Time expressions",
        ["vocabulary", "grammar"],
        ["Tell the time in French", "Use common time phrases"]),
    (3,  12, "Nationalities",
        ["vocabulary"],
        ["Name nationalities in French", "Apply gender agreement to nationality adjectives"]),
    (3,  13, "Occupations",
        ["vocabulary"],
        ["Name common occupations in French", "Talk about what you or others do for work"]),

    (4,  14, "Gender of nouns",
        ["grammar"],
        ["Identify masculine and feminine nouns", "Apply gender rules to new vocabulary"]),
    (4,  15, "Definite articles",
        ["grammar"],
        ["Use le, la, les correctly", "Understand when to use definite articles"]),
    (4,  16, "Indefinite articles",
        ["grammar"],
        ["Use un, une, des correctly", "Distinguish between definite and indefinite articles"]),
    (4,  17, "Plurals",
        ["grammar"],
        ["Form regular noun plurals", "Recognize common irregular plurals"]),

    (5,  18, "Adjectives",
        ["grammar", "vocabulary"],
        ["Use common descriptive adjectives", "Place adjectives correctly in sentences"]),
    (5,  19, "Agreement of adjectives",
        ["grammar"],
        ["Apply gender and number agreement to adjectives", "Recognize adjective endings for masculine and feminine"]),
    (5,  20, "Possessive adjectives",
        ["grammar"],
        ["Use mon, ma, mes, ton, ta, tes, son, sa, ses correctly", "Express possession in French"]),

    (6,  21, "Regular -er verbs",
        ["grammar"],
        ["Conjugate regular -er verbs in the present tense", "Use common -er verbs in sentences"]),
    (6,  22, "Regular -ir verbs",
        ["grammar"],
        ["Conjugate regular -ir verbs in the present tense", "Distinguish -ir from -er verb patterns"]),
    (6,  23, "Regular -re verbs",
        ["grammar"],
        ["Conjugate regular -re verbs in the present tense", "Use common -re verbs correctly"]),
    (6,  24, "Aller",
        ["grammar"],
        ["Conjugate aller in the present tense", "Use aller to express going and movement"]),
    (6,  25, "Faire",
        ["grammar"],
        ["Conjugate faire in the present tense", "Use faire in common idiomatic expressions"]),
    (6,  26, "Common irregular verbs",
        ["grammar"],
        ["Recognize and conjugate key irregular verbs", "Use irregular verbs in everyday sentences"]),

    (7,  27, "Negation (ne...pas)",
        ["grammar"],
        ["Form negative sentences using ne...pas", "Apply negation to different verb types"]),
    (7,  28, "Interrogatives",
        ["grammar"],
        ["Use qui, que, où, quand, pourquoi, comment", "Form questions with interrogative words"]),
    (7,  29, "Question forms",
        ["grammar", "speaking"],
        ["Ask questions using inversion and est-ce que", "Choose the appropriate question structure"]),
    (7,  30, "Preferences and opinions",
        ["speaking", "vocabulary"],
        ["Express likes and dislikes in French", "Give simple opinions using aimer, préférer, détester"]),

    (8,  31, "Prepositions",
        ["grammar"],
        ["Use common prepositions of place and time", "Choose correct prepositions with transport and location"]),
    (8,  32, "Adverbs",
        ["grammar"],
        ["Use common frequency and manner adverbs", "Position adverbs correctly in sentences"]),
    (8,  33, "Object pronouns",
        ["grammar"],
        ["Use direct object pronouns le, la, les", "Position object pronouns correctly in simple sentences"]),

    (9,  34, "Passé composé introduction",
        ["grammar"],
        ["Form the passé composé with avoir", "Use passé composé to talk about past events"]),
    (9,  35, "Futur proche",
        ["grammar"],
        ["Form the futur proche with aller + infinitive", "Use futur proche to talk about near-future plans"]),

    (10, 36, "Self-introduction",
        ["speaking"],
        ["Introduce yourself with name, age, origin, and occupation", "Hold a short introductory conversation"]),
    (10, 37, "Family and friends",
        ["speaking", "vocabulary"],
        ["Name family members in French", "Describe relationships and talk about people you know"]),
    (10, 38, "Routines",
        ["speaking", "vocabulary"],
        ["Describe daily routines using reflexive verbs", "Talk about habitual activities"]),
    (10, 39, "Short messages",
        ["writing"],
        ["Write a simple text message or note in French", "Use appropriate informal register"]),
    (10, 40, "Simple paragraphs",
        ["writing"],
        ["Write 3–5 sentence paragraphs on familiar topics", "Connect sentences using simple connectors"]),
    (10, 41, "Talking about plans",
        ["speaking", "grammar"],
        ["Express future intentions using futur proche", "Discuss plans with a partner or in writing"]),
    (10, 42, "Past experiences",
        ["speaking", "grammar"],
        ["Describe a simple past event using passé composé", "Talk about things you have done"]),
]


# ─── Seed helpers ─────────────────────────────────────────────────────────────

def seed_languages(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical language list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = """
        INSERT OR IGNORE INTO languages (code, name, native_name)
        VALUES (?, ?, ?)
    """
    conn.executemany(sql, _LANGUAGES)
    print(f"[db] Languages seeded ({len(_LANGUAGES)} rows)")


def seed_hobbies(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical hobby list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO hobbies (name) VALUES (?)"
    conn.executemany(sql, [(h,) for h in _HOBBIES])
    print(f"[db] Hobbies seeded ({len(_HOBBIES)} rows)")


def seed_motivations(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical motivation list.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO motivations (label) VALUES (?)"
    conn.executemany(sql, [(m,) for m in _MOTIVATIONS])
    print(f"[db] Motivations seeded ({len(_MOTIVATIONS)} rows)")


def seed_xp_levels(conn: sqlite3.Connection) -> None:
    """
    Insert XP level threshold bands.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO xp_levels (level_no, label, xp_required, xp_to_next) VALUES (?, ?, ?, ?)"
    conn.executemany(sql, _XP_LEVELS)
    print(f"[db] XP levels seeded ({len(_XP_LEVELS)} rows)")


def seed_achievements(conn: sqlite3.Connection) -> None:
    """
    Insert the canonical achievement catalog.
    Uses INSERT OR IGNORE so re-running is safe.
    """
    sql = "INSERT OR IGNORE INTO achievements (name, description, xp_reward) VALUES (?, ?, ?)"
    conn.executemany(sql, _ACHIEVEMENTS)
    print(f"[db] Achievements seeded ({len(_ACHIEVEMENTS)} rows)")


def seed_french_curriculum(conn: sqlite3.Connection) -> None:
    """
    Seed curriculum_modules and curriculum_nodes for French A1.
    Uses INSERT OR IGNORE — safe to re-run at any time.
    """
    lang_row = conn.execute(
        "SELECT id FROM languages WHERE code = 'fr'"
    ).fetchone()
    if lang_row is None:
        raise RuntimeError("French language row not found — run seed_languages first.")
    lang_id: int = lang_row["id"]

    # ── Modules ───────────────────────────────────────────────────────────────
    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_modules
            (language_id, framework, level, module_order, title, description, total_lessons)
        VALUES (?, 'CEFR', 'A1', ?, ?, ?, ?)
        """,
        [(lang_id, order, title, desc, total) for order, title, desc, total in _FRENCH_A1_MODULES],
    )

    # Build unit → module_id map (needed for nodes FK)
    module_rows = conn.execute(
        "SELECT id, module_order FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,),
    ).fetchall()
    unit_to_module_id: dict[int, int] = {r["module_order"]: r["id"] for r in module_rows}

    # ── Nodes ─────────────────────────────────────────────────────────────────
    rows = []
    for unit, lesson_order, topic, skill_focus, objectives in _FRENCH_A1_NODES:
        module_id = unit_to_module_id[unit]
        rows.append((
            lang_id,
            module_id,
            lesson_order,
            topic,
            json.dumps(skill_focus),
            json.dumps([]),           # prerequisites — empty for now
            json.dumps(objectives),
        ))

    conn.executemany(
        """
        INSERT OR IGNORE INTO curriculum_nodes
            (language_id, module_id, framework, level, lesson_order, topic,
             skill_focus, prerequisites, learning_objectives)
        VALUES (?, ?, 'CEFR', 'A1', ?, ?, ?, ?, ?)
        """,
        rows,
    )

    modules_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_modules WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    nodes_inserted = conn.execute(
        "SELECT COUNT(*) FROM curriculum_nodes WHERE language_id = ? AND framework = 'CEFR' AND level = 'A1'",
        (lang_id,)
    ).fetchone()[0]
    print(f"[db] French A1 curriculum seeded ({modules_inserted} modules, {nodes_inserted} nodes)")


# ─── Initialization ───────────────────────────────────────────────────────────

def initialize_database() -> None:
    """
    Full first-run setup:

    1. Open connection to lingua_ai.db (creates file if absent)
    2. Create all tables + indexes, migrate any missing columns
    3. Seed reference data (languages, hobbies, motivations, xp_levels, achievements)
    4. Commit and close
    """
    print(f"[db] Initializing database at {DB_PATH}")
    conn = get_connection()
    try:
        create_tables(conn)
        seed_languages(conn)
        seed_hobbies(conn)
        seed_motivations(conn)
        seed_xp_levels(conn)
        seed_achievements(conn)
        seed_french_curriculum(conn)
        conn.commit()
        print("[db] Initialization complete.")
    except Exception as exc:
        conn.rollback()
        print(f"[db] Initialization failed: {exc}")
        raise
    finally:
        conn.close()


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    commands = {
        "init":  initialize_database,
        "drop":  drop_database,
        "reset": lambda: (drop_database(), initialize_database()),
    }

    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    action = commands.get(cmd)

    if action is None:
        print(f"Unknown command '{cmd}'. Use: init | drop | reset")
        sys.exit(1)

    action()
