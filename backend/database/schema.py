"""
schema.py
─────────
Raw SQL schema for lingua_ai.db.

All table definitions, index definitions, and the helper functions:
  create_tables(conn)   — create all tables + indexes, migrate existing columns (idempotent)
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

    # ── xp_levels ─────────────────────────────────────────────────────────────
    # XP threshold bands used to compute xpCurrentLevel / xpNextLevel in the
    # dashboard profile. Seeded once in script.py.
    """
    CREATE TABLE IF NOT EXISTS xp_levels (
        level_no    INTEGER PRIMARY KEY,
        label       TEXT    NOT NULL,
        xp_required INTEGER NOT NULL,
        xp_to_next  INTEGER
    )
    """,

    # ── curriculum_modules ────────────────────────────────────────────────────
    # Ordered list of curriculum modules per language + framework combination.
    # Each module contains N lessons and belongs to a specific framework level.
    """
    CREATE TABLE IF NOT EXISTS curriculum_modules (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        language_id   INTEGER NOT NULL,
        framework     TEXT    NOT NULL,
        level         TEXT    NOT NULL,
        module_order  INTEGER NOT NULL,
        title         TEXT    NOT NULL,
        description   TEXT,
        total_lessons INTEGER DEFAULT 0,
        FOREIGN KEY (language_id) REFERENCES languages (id)
    )
    """,

    # ── users ─────────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS users (
        id                       TEXT PRIMARY KEY,
        email                    TEXT UNIQUE NOT NULL,
        username                 TEXT UNIQUE NOT NULL,
        first_name               TEXT,
        last_name                TEXT,
        password_hash            TEXT NOT NULL,
        native_language_id       INTEGER NOT NULL,
        target_language_id       INTEGER NOT NULL,
        learning_goal            TEXT,
        selected_motivations     TEXT,
        preferred_learning_style TEXT,
        daily_goal_minutes       INTEGER,
        current_level            TEXT,
        target_level             TEXT,
        framework                TEXT,
        current_xp               INTEGER DEFAULT 0,
        current_streak           INTEGER DEFAULT 0,
        longest_streak           INTEGER DEFAULT 0,
        total_study_minutes      INTEGER DEFAULT 0,
        is_active                INTEGER DEFAULT 1,
        created_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

    # ── user_module_progress ──────────────────────────────────────────────────
    # Tracks each user's progress through every curriculum module.
    """
    CREATE TABLE IF NOT EXISTS user_module_progress (
        user_id           TEXT    NOT NULL,
        module_id         INTEGER NOT NULL,
        status            TEXT    DEFAULT 'locked',
        completed_lessons INTEGER DEFAULT 0,
        started_at        TIMESTAMP,
        completed_at      TIMESTAMP,
        PRIMARY KEY (user_id, module_id),
        FOREIGN KEY (user_id)   REFERENCES users             (id),
        FOREIGN KEY (module_id) REFERENCES curriculum_modules (id)
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

    # ── skill_scores ──────────────────────────────────────────────────────────
    # Time-series record of each skill score (reading/listening/writing/speaking).
    # One row per skill per assessment. Used to compute current score and trend.
    """
    CREATE TABLE IF NOT EXISTS skill_scores (
        id            TEXT PRIMARY KEY,
        user_id       TEXT    NOT NULL,
        skill         TEXT    NOT NULL,
        score         REAL    NOT NULL,
        assessment_id TEXT,
        recorded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)       REFERENCES users       (id),
        FOREIGN KEY (assessment_id) REFERENCES assessments (id)
    )
    """,

    # ── lessons ───────────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS lessons (
        id                TEXT PRIMARY KEY,
        user_id           TEXT NOT NULL,
        module_id         INTEGER,
        title             TEXT NOT NULL,
        framework         TEXT,
        lesson_level      TEXT,
        skill_focus       TEXT,
        lesson_order      INTEGER,
        estimated_minutes INTEGER,
        lesson_json       TEXT NOT NULL,
        generated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)   REFERENCES users             (id),
        FOREIGN KEY (module_id) REFERENCES curriculum_modules (id)
    )
    """,

    # ── vocabulary_items ──────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS vocabulary_items (
        id                TEXT PRIMARY KEY,
        user_id           TEXT    NOT NULL,
        language_id       INTEGER NOT NULL,
        word              TEXT    NOT NULL,
        translation       TEXT,
        proficiency_score REAL    DEFAULT 0,
        times_seen        INTEGER DEFAULT 0,
        times_correct     INTEGER DEFAULT 0,
        next_review_at    TIMESTAMP,
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)     REFERENCES users     (id),
        FOREIGN KEY (language_id) REFERENCES languages (id)
    )
    """,

    # ── grammar_topics ────────────────────────────────────────────────────────
    # Catalog of grammar concepts per language, framework, and level.
    # Seeded once per language when the curriculum is generated.
    """
    CREATE TABLE IF NOT EXISTS grammar_topics (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        language_id INTEGER NOT NULL,
        framework   TEXT    NOT NULL,
        level       TEXT    NOT NULL,
        topic       TEXT    NOT NULL,
        description TEXT,
        FOREIGN KEY (language_id) REFERENCES languages (id)
    )
    """,

    # ── user_grammar_progress ─────────────────────────────────────────────────
    # Tracks each user's mastery of each grammar topic.
    # status: 'learning' | 'mastered' | 'review'
    """
    CREATE TABLE IF NOT EXISTS user_grammar_progress (
        id                TEXT    PRIMARY KEY,
        user_id           TEXT    NOT NULL,
        topic_id          INTEGER NOT NULL,
        confidence_score  REAL    DEFAULT 0,
        times_practiced   INTEGER DEFAULT 0,
        times_correct     INTEGER DEFAULT 0,
        status            TEXT    DEFAULT 'learning',
        last_practiced_at TIMESTAMP,
        FOREIGN KEY (user_id)   REFERENCES users          (id),
        FOREIGN KEY (topic_id)  REFERENCES grammar_topics (id)
    )
    """,

    # ── error_log ─────────────────────────────────────────────────────────────
    # Accumulates learner errors across lessons and assessments.
    # error_type: 'vocabulary' | 'grammar' | 'structure'
    # count increments each time the same error is observed.
    """
    CREATE TABLE IF NOT EXISTS error_log (
        id           TEXT PRIMARY KEY,
        user_id      TEXT    NOT NULL,
        error_type   TEXT    NOT NULL,
        reference    TEXT    NOT NULL,
        detail       TEXT,
        lesson_id    TEXT,
        count        INTEGER DEFAULT 1,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)   REFERENCES users   (id),
        FOREIGN KEY (lesson_id) REFERENCES lessons (id)
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
    # Stores earned achievements only. In-progress tracking is in
    # achievement_progress.
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

    # ── achievement_progress ──────────────────────────────────────────────────
    # Tracks progress toward not-yet-earned achievements.
    """
    CREATE TABLE IF NOT EXISTS achievement_progress (
        user_id        TEXT    NOT NULL,
        achievement_id INTEGER NOT NULL,
        current_value  INTEGER DEFAULT 0,
        target_value   INTEGER NOT NULL,
        PRIMARY KEY (user_id, achievement_id),
        FOREIGN KEY (user_id)        REFERENCES users        (id),
        FOREIGN KEY (achievement_id) REFERENCES achievements (id)
    )
    """,

    # ── conversations ─────────────────────────────────────────────────────────
    # AI conversation / speaking practice sessions.
    # messages_json holds the full turn-by-turn exchange as a JSON array.
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id               TEXT PRIMARY KEY,
        user_id          TEXT NOT NULL,
        topic            TEXT,
        skill_focus      TEXT DEFAULT 'speaking',
        messages_json    TEXT,
        duration_seconds INTEGER DEFAULT 0,
        xp_earned        INTEGER DEFAULT 0,
        completed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,

    # ── learning_sessions ─────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id            TEXT PRIMARY KEY,
        user_id       TEXT NOT NULL,
        lesson_id     TEXT,
        started_at    TIMESTAMP,
        ended_at      TIMESTAMP,
        minutes_spent INTEGER,
        xp_earned     INTEGER,
        FOREIGN KEY (user_id)   REFERENCES users   (id),
        FOREIGN KEY (lesson_id) REFERENCES lessons (id)
    )
    """,

    # ── user_lesson_progress ──────────────────────────────────────────────────
    # Tracks each user's progress through individual lessons.
    # Needed to derive the current lesson and compute goal completion %.
    """
    CREATE TABLE IF NOT EXISTS user_lesson_progress (
        user_id      TEXT    NOT NULL,
        lesson_id    TEXT    NOT NULL,
        status       TEXT    DEFAULT 'in_progress',   -- 'in_progress' | 'completed'
        started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        PRIMARY KEY  (user_id, lesson_id),
        FOREIGN KEY  (user_id)   REFERENCES users   (id),
        FOREIGN KEY  (lesson_id) REFERENCES lessons (id)
    )
    """,

    # ── scheduled_assessments ─────────────────────────────────────────────────
    # Upcoming / planned assessments shown in the dashboard.
    """
    CREATE TABLE IF NOT EXISTS scheduled_assessments (
        id               TEXT PRIMARY KEY,
        user_id          TEXT NOT NULL,
        title            TEXT NOT NULL,
        assessment_type  TEXT NOT NULL,
        scheduled_at     TIMESTAMP NOT NULL,
        duration_minutes INTEGER,
        is_completed     INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """,
]

# ─── INDEX DEFINITIONS ────────────────────────────────────────────────────────

_INDEXES: list[str] = [
    # existing
    "CREATE INDEX IF NOT EXISTS idx_users_email               ON users                  (email)",
    "CREATE INDEX IF NOT EXISTS idx_users_username            ON users                  (username)",
    "CREATE INDEX IF NOT EXISTS idx_assessments_user_id       ON assessments            (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_user_id           ON lessons                (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_vocabulary_user_id        ON vocabulary_items       (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_learning_sessions_user    ON learning_sessions      (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_assessment_questions_aid  ON assessment_questions   (assessment_id)",
    "CREATE INDEX IF NOT EXISTS idx_assessment_responses_aid  ON assessment_responses   (assessment_id)",
    "CREATE INDEX IF NOT EXISTS idx_vocab_word                ON vocabulary_items       (user_id, word)",
    # new
    "CREATE INDEX IF NOT EXISTS idx_skill_scores_user         ON skill_scores           (user_id, skill)",
    "CREATE INDEX IF NOT EXISTS idx_skill_scores_recorded     ON skill_scores           (user_id, recorded_at)",
    "CREATE INDEX IF NOT EXISTS idx_grammar_topics_lang       ON grammar_topics         (language_id, framework)",
    "CREATE INDEX IF NOT EXISTS idx_user_grammar_user         ON user_grammar_progress  (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_grammar_status       ON user_grammar_progress  (user_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_error_log_user            ON error_log              (user_id, error_type)",
    "CREATE INDEX IF NOT EXISTS idx_error_log_reference       ON error_log              (user_id, reference)",
    "CREATE INDEX IF NOT EXISTS idx_curriculum_modules_lang   ON curriculum_modules     (language_id, framework)",
    "CREATE INDEX IF NOT EXISTS idx_conversations_user        ON conversations          (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_scheduled_assessments     ON scheduled_assessments  (user_id, scheduled_at)",
    "CREATE INDEX IF NOT EXISTS idx_achievement_progress_user ON achievement_progress   (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_module            ON lessons                (module_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_lesson_user          ON user_lesson_progress   (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_lesson_status        ON user_lesson_progress   (user_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_learning_sessions_date    ON learning_sessions      (user_id, started_at)",
    "CREATE INDEX IF NOT EXISTS idx_vocab_review              ON vocabulary_items       (user_id, next_review_at)",
]

# ─── DROP ORDER ───────────────────────────────────────────────────────────────
# Reverse-dependency order — children before parents.

_DROP_ORDER: list[str] = [
    "scheduled_assessments",
    "user_lesson_progress",
    "conversations",
    "achievement_progress",
    "learning_sessions",
    "skill_scores",
    "error_log",
    "user_grammar_progress",
    "user_module_progress",
    "user_achievements",
    "achievements",
    "vocabulary_items",
    "assessment_responses",
    "assessment_questions",
    "assessments",
    "lessons",
    "user_hobbies",
    "hobbies",
    "motivations",
    "users",
    "grammar_topics",
    "curriculum_modules",
    "xp_levels",
    "languages",
]

# ─── MIGRATION HELPERS ────────────────────────────────────────────────────────

def _add_column_if_missing(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    """Add a column to an existing table only if it does not already exist."""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# ─── PUBLIC HELPERS ───────────────────────────────────────────────────────────

def create_tables(conn: sqlite3.Connection) -> None:
    """
    Create all tables and indexes if they do not already exist.
    Also migrates any missing columns onto tables that were created before
    those columns were added to the schema.
    Idempotent — safe to call on an existing database.
    """
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    for ddl in _TABLES:
        cur.execute(ddl)

    # ── Column migrations — run before indexes so new columns exist first ──
    _add_column_if_missing(conn, "users",   "target_level",      "TEXT")
    _add_column_if_missing(conn, "lessons", "module_id",         "INTEGER REFERENCES curriculum_modules(id)")
    _add_column_if_missing(conn, "lessons", "estimated_minutes", "INTEGER")
    _add_column_if_missing(conn, "lessons", "lesson_order",      "INTEGER")

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
