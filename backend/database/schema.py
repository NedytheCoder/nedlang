"""
schema.py
─────────
Raw SQL schema for lingua_ai.db.

All table definitions, index definitions, and the two helper functions:
  create_tables(conn)   — create all tables + indexes (idempotent)
  drop_tables(conn)     — drop all tables in dependency-safe order
"""

import sqlite3

# ─── TABLE DEFINITIONS ────────────────────────────────────────────────────────

_TABLES: list[str] = [

    # ── languages ─────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS languages (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        code        TEXT    UNIQUE NOT NULL,
        name        TEXT    NOT NULL,
        native_name TEXT,
        is_active   INTEGER DEFAULT 1,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # ── users ─────────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS users (
        id                      TEXT PRIMARY KEY,
        email                   TEXT UNIQUE NOT NULL,
        username                TEXT UNIQUE NOT NULL,
        first_name              TEXT,
        last_name               TEXT,
        password_hash           TEXT NOT NULL,
        native_language_id      INTEGER NOT NULL,
        target_language_id      INTEGER NOT NULL,
        learning_goal           TEXT,
        selected_motivations    TEXT,
        preferred_learning_style TEXT,
        daily_goal_minutes      INTEGER,
        current_level           TEXT,
        framework               TEXT,
        current_xp              INTEGER DEFAULT 0,
        current_streak          INTEGER DEFAULT 0,
        longest_streak          INTEGER DEFAULT 0,
        total_study_minutes     INTEGER DEFAULT 0,
        is_active               INTEGER DEFAULT 1,
        created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (native_language_id) REFERENCES languages (id),
        FOREIGN KEY (target_language_id) REFERENCES languages (id)
    )
    """,

    # ── hobbies ───────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS hobbies (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """,

    # ── motivations ───────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS motivations (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        label     TEXT UNIQUE NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """,

    # ── user_hobbies ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS user_hobbies (
        user_id  TEXT    NOT NULL,
        hobby_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, hobby_id),
        FOREIGN KEY (user_id)  REFERENCES users   (id),
        FOREIGN KEY (hobby_id) REFERENCES hobbies (id)
    )
    """,

    # ── assessments ───────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS assessments (
        id                 TEXT PRIMARY KEY,
        user_id            TEXT    NOT NULL,
        assessment_type    TEXT    NOT NULL,
        framework          TEXT    NOT NULL,
        target_language_id INTEGER NOT NULL,
        estimated_level    TEXT,
        score              REAL,
        confidence_score   REAL,
        started_at         TIMESTAMP,
        completed_at       TIMESTAMP,
        FOREIGN KEY (user_id)            REFERENCES users     (id),
        FOREIGN KEY (target_language_id) REFERENCES languages (id)
    )
    """,

    # ── assessment_questions ──────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS assessment_questions (
        id               TEXT PRIMARY KEY,
        assessment_id    TEXT    NOT NULL,
        question_no      INTEGER NOT NULL,
        question_level   TEXT    NOT NULL,
        question_type    TEXT    NOT NULL,
        question_passage TEXT    NOT NULL,
        options_json     TEXT    NOT NULL,
        correct_answer   TEXT    NOT NULL,
        FOREIGN KEY (assessment_id) REFERENCES assessments (id)
    )
    """,

    # ── assessment_responses ──────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS assessment_responses (
        id            TEXT PRIMARY KEY,
        assessment_id TEXT    NOT NULL,
        question_id   TEXT    NOT NULL,
        user_answer   TEXT,
        is_correct    INTEGER,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assessment_id) REFERENCES assessments          (id),
        FOREIGN KEY (question_id)   REFERENCES assessment_questions (id)
    )
    """,

    # ── lessons ───────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS lessons (
        id           TEXT PRIMARY KEY,
        user_id      TEXT NOT NULL,
        title        TEXT NOT NULL,
        framework    TEXT,
        lesson_level TEXT,
        skill_focus  TEXT,
        lesson_json  TEXT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,

    # ── vocabulary_items ──────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS vocabulary_items (
        id               TEXT PRIMARY KEY,
        user_id          TEXT    NOT NULL,
        language_id      INTEGER NOT NULL,
        word             TEXT    NOT NULL,
        translation      TEXT,
        proficiency_score REAL   DEFAULT 0,
        times_seen       INTEGER DEFAULT 0,
        times_correct    INTEGER DEFAULT 0,
        next_review_at   TIMESTAMP,
        created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)     REFERENCES users     (id),
        FOREIGN KEY (language_id) REFERENCES languages (id)
    )
    """,

    # ── achievements ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS achievements (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT UNIQUE NOT NULL,
        description TEXT,
        xp_reward   INTEGER DEFAULT 0
    )
    """,

    # ── user_achievements ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS user_achievements (
        user_id        TEXT    NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, achievement_id),
        FOREIGN KEY (user_id)        REFERENCES users        (id),
        FOREIGN KEY (achievement_id) REFERENCES achievements (id)
    )
    """,

    # ── learning_sessions ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id           TEXT PRIMARY KEY,
        user_id      TEXT NOT NULL,
        lesson_id    TEXT,
        started_at   TIMESTAMP,
        ended_at     TIMESTAMP,
        minutes_spent INTEGER,
        xp_earned    INTEGER,
        FOREIGN KEY (user_id)   REFERENCES users   (id),
        FOREIGN KEY (lesson_id) REFERENCES lessons (id)
    )
    """,
]

# ─── INDEX DEFINITIONS ────────────────────────────────────────────────────────

_INDEXES: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_users_email              ON users               (email)",
    "CREATE INDEX IF NOT EXISTS idx_users_username           ON users               (username)",
    "CREATE INDEX IF NOT EXISTS idx_assessments_user_id      ON assessments         (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_user_id          ON lessons             (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_vocabulary_user_id       ON vocabulary_items    (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_learning_sessions_user   ON learning_sessions   (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_assessment_questions_aid ON assessment_questions (assessment_id)",
    "CREATE INDEX IF NOT EXISTS idx_assessment_responses_aid ON assessment_responses (assessment_id)",
    "CREATE INDEX IF NOT EXISTS idx_vocab_word               ON vocabulary_items    (user_id, word)",
]

# ─── DROP ORDER ───────────────────────────────────────────────────────────────
# Must be reverse-dependency order to satisfy foreign key constraints.

_DROP_ORDER: list[str] = [
    "learning_sessions",
    "user_achievements",
    "achievements",
    "vocabulary_items",
    "lessons",
    "assessment_responses",
    "assessment_questions",
    "assessments",
    "user_hobbies",
    "hobbies",
    "motivations",
    "users",
    "languages",
]


# ─── PUBLIC HELPERS ───────────────────────────────────────────────────────────

def create_tables(conn: sqlite3.Connection) -> None:
    """
    Create all tables and indexes if they do not already exist.
    Idempotent — safe to call on an existing database.
    """
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    for ddl in _TABLES:
        cur.execute(ddl)
    for idx in _INDEXES:
        cur.execute(idx)
    conn.commit()


def drop_tables(conn: sqlite3.Connection) -> None:
    """
    Drop all tables in reverse-dependency order.
    Destroys all data — use only in tests or full resets.
    """
    conn.execute("PRAGMA foreign_keys = OFF")
    cur = conn.cursor()
    for table in _DROP_ORDER:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
