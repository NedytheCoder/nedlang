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


# ─── Initialization ───────────────────────────────────────────────────────────

def initialize_database() -> None:
    """
    Full first-run setup:

    1. Open connection to lingua_ai.db (creates file if absent)
    2. Create all tables
    3. Create all indexes
    4. Seed languages
    5. Seed hobbies
    6. Commit
    7. Close connection
    """
    print(f"[db] Initializing database at {DB_PATH}")
    conn = get_connection()
    try:
        create_tables(conn)          # step 2 + 3
        seed_languages(conn)         # step 4
        seed_hobbies(conn)           # step 5
        seed_motivations(conn)       # step 6
        conn.commit()                # step 7
        print("[db] Initialization complete.")
    except Exception as exc:
        conn.rollback()
        print(f"[db] Initialization failed: {exc}")
        raise
    finally:
        conn.close()                 # step 7


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
