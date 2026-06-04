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
