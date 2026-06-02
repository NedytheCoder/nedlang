# Database Schema

**Project:** AI Language Coach  
**Version:** 1.0 (MVP)  
**Date:** 2026-05-30  
**Engine:** SQLite (development) → PostgreSQL (production)

---

## Design Principles

1. **No hard-coded language assumptions.** No column is named `english_translation`, `french_word`, etc.
2. **`Languages` is the authoritative registry.** Adding a supported language is one `INSERT`.
3. **`UserLanguagePairs` is the core join entity.** Every learning record belongs to a pair, not just a user.
4. **`content_json` stores flexible AI-generated content.** Lesson and assessment content structures evolve without schema migrations.
5. **All foreign keys are explicit.** Referential integrity is enforced at the database level.

---

## Entity Relationship Summary

```
Users ──< UserLanguagePairs >── Languages (source)
                │           └── Languages (target)
                │
                ├──< Lessons
                ├──< ConversationSessions ──< Messages
                ├──< ProgressRecords
                ├──< VocabularyItems
                └──< Assessments ──< AssessmentAnswers
```

---

## Tables

### `schema_migrations`

Tracks which numbered migration files have been applied. Used by the migration runner in `backend/database/migrations/__init__.py` to ensure each `.sql` file is applied exactly once.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `version` | TEXT | NOT NULL, UNIQUE | Migration filename, e.g. `"001_assessment_questions.sql"` |
| `applied_at` | TEXT | NOT NULL | ISO 8601 UTC, set at application time |

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    version    TEXT    NOT NULL UNIQUE,
    applied_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

---

### `users`

Stores authenticated platform users.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `email` | TEXT | NOT NULL, UNIQUE | |
| `password_hash` | TEXT | NOT NULL | bcrypt |
| `display_name` | TEXT | NOT NULL | |
| `source_language_id` | INTEGER | FK → languages.id | User's native / known language |
| `created_at` | TEXT | NOT NULL | ISO 8601 UTC |
| `last_seen_at` | TEXT | | |

```sql
CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    email              TEXT    NOT NULL UNIQUE,
    password_hash      TEXT    NOT NULL,
    display_name       TEXT    NOT NULL,
    source_language_id INTEGER NOT NULL REFERENCES languages(id),
    created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    last_seen_at       TEXT
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

---

### `refresh_tokens`

Tracks issued refresh tokens to support server-side invalidation.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `user_id` | INTEGER | FK → users.id | |
| `token_hash` | TEXT | NOT NULL, UNIQUE | SHA-256 hash of token |
| `issued_at` | TEXT | NOT NULL | |
| `expires_at` | TEXT | NOT NULL | |
| `revoked` | INTEGER | NOT NULL DEFAULT 0 | Boolean (0/1) |

```sql
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT    NOT NULL UNIQUE,
    issued_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at  TEXT    NOT NULL,
    revoked     INTEGER NOT NULL DEFAULT 0
);
```

---

### `languages`

Registry of all languages the platform can support.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `code` | TEXT | NOT NULL, UNIQUE | IETF BCP 47: `"en"`, `"fr"`, `"ja"`, `"ar"` |
| `name` | TEXT | NOT NULL | English display name: `"French"` |
| `native_name` | TEXT | NOT NULL | In its own script: `"Français"`, `"日本語"` |
| `is_active` | INTEGER | NOT NULL DEFAULT 1 | 0 = hidden from UI |
| `is_rtl` | INTEGER | NOT NULL DEFAULT 0 | Right-to-left script flag |

```sql
CREATE TABLE IF NOT EXISTS languages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    native_name TEXT    NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    is_rtl      INTEGER NOT NULL DEFAULT 0
);

-- Seed data — extend this list to add language support
INSERT INTO languages (code, name, native_name, is_rtl) VALUES
('en', 'English',    'English',    0),
('fr', 'French',     'Français',   0),
('de', 'German',     'Deutsch',    0),
('es', 'Spanish',    'Español',    0),
('pt', 'Portuguese', 'Português',  0),
('it', 'Italian',    'Italiano',   0),
('nl', 'Dutch',      'Nederlands', 0),
('ja', 'Japanese',   '日本語',      0),
('ko', 'Korean',     '한국어',      0),
('ar', 'Arabic',     'العربية',    1),
('yo', 'Yoruba',     'Yorùbá',     0),
('zh', 'Chinese',    '中文',        0);
```

---

### `user_language_pairs`

The central learning context. Every learning record is scoped to a pair.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `user_id` | INTEGER | FK → users.id | |
| `source_language_id` | INTEGER | FK → languages.id | Language the user knows |
| `target_language_id` | INTEGER | FK → languages.id | Language being learned |
| `current_level` | TEXT | NOT NULL DEFAULT 'A0' | CEFR code |
| `total_xp` | INTEGER | NOT NULL DEFAULT 0 | |
| `streak_days` | INTEGER | NOT NULL DEFAULT 0 | Current streak |
| `longest_streak` | INTEGER | NOT NULL DEFAULT 0 | |
| `last_activity_date` | TEXT | | ISO 8601 date only |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS user_language_pairs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_language_id  INTEGER NOT NULL REFERENCES languages(id),
    target_language_id  INTEGER NOT NULL REFERENCES languages(id),
    current_level       TEXT    NOT NULL DEFAULT 'A0',
    total_xp            INTEGER NOT NULL DEFAULT 0,
    streak_days         INTEGER NOT NULL DEFAULT 0,
    longest_streak      INTEGER NOT NULL DEFAULT 0,
    last_activity_date  TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, target_language_id),
    CHECK(source_language_id != target_language_id)
);
CREATE INDEX IF NOT EXISTS idx_pairs_user ON user_language_pairs(user_id);
```

---

### `lessons`

Structured lesson records. Content is AI-generated and stored as a JSON blob.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `pair_id` | INTEGER | FK → user_language_pairs.id | |
| `level` | TEXT | NOT NULL | CEFR code |
| `lesson_type` | TEXT | NOT NULL | `vocabulary` \| `grammar` \| `reading` \| `listening` \| `writing` \| `speaking` |
| `title` | TEXT | NOT NULL | |
| `topic` | TEXT | | Optional focus topic |
| `content_json` | TEXT | NOT NULL | AI-generated lesson content as JSON |
| `xp_reward` | INTEGER | NOT NULL | |
| `is_completed` | INTEGER | NOT NULL DEFAULT 0 | |
| `score` | INTEGER | | Achieved score |
| `max_score` | INTEGER | | Max possible score |
| `completed_at` | TEXT | | |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS lessons (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id      INTEGER NOT NULL REFERENCES user_language_pairs(id) ON DELETE CASCADE,
    level        TEXT    NOT NULL,
    lesson_type  TEXT    NOT NULL,
    title        TEXT    NOT NULL,
    topic        TEXT,
    content_json TEXT    NOT NULL,
    xp_reward    INTEGER NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    score        INTEGER,
    max_score    INTEGER,
    completed_at TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_lessons_pair ON lessons(pair_id);
CREATE INDEX IF NOT EXISTS idx_lessons_level ON lessons(pair_id, level);
```

---

### `conversation_sessions`

Groups messages into a session with a mode and context.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `pair_id` | INTEGER | FK → user_language_pairs.id | |
| `mode` | TEXT | NOT NULL DEFAULT 'general' | `general` \| `introduction` \| `travelling` \| `daily_life` |
| `message_count` | INTEGER | NOT NULL DEFAULT 0 | |
| `created_at` | TEXT | NOT NULL | |
| `last_message_at` | TEXT | | |

```sql
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id          INTEGER NOT NULL REFERENCES user_language_pairs(id) ON DELETE CASCADE,
    mode             TEXT    NOT NULL DEFAULT 'general',
    message_count    INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    last_message_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_pair ON conversation_sessions(pair_id);
```

---

### `messages`

Individual messages within a conversation session.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `session_id` | INTEGER | FK → conversation_sessions.id | |
| `role` | TEXT | NOT NULL | `user` \| `assistant` |
| `content` | TEXT | NOT NULL | |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    role       TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
    content    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
```

---

### `progress_records`

Daily XP and activity log per language pair. One row per user per pair per day.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `pair_id` | INTEGER | FK → user_language_pairs.id | |
| `date` | TEXT | NOT NULL | ISO 8601 date: `"2026-05-30"` |
| `xp_earned` | INTEGER | NOT NULL DEFAULT 0 | |
| `lessons_completed` | INTEGER | NOT NULL DEFAULT 0 | |
| `messages_sent` | INTEGER | NOT NULL DEFAULT 0 | |

```sql
CREATE TABLE IF NOT EXISTS progress_records (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id            INTEGER NOT NULL REFERENCES user_language_pairs(id) ON DELETE CASCADE,
    date               TEXT    NOT NULL,
    xp_earned          INTEGER NOT NULL DEFAULT 0,
    lessons_completed  INTEGER NOT NULL DEFAULT 0,
    messages_sent      INTEGER NOT NULL DEFAULT 0,
    UNIQUE(pair_id, date)
);
CREATE INDEX IF NOT EXISTS idx_progress_pair_date ON progress_records(pair_id, date);
```

---

### `vocabulary_items`

Words and phrases the learner has encountered, with spaced repetition state.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `pair_id` | INTEGER | FK → user_language_pairs.id | |
| `target_word` | TEXT | NOT NULL | Word in the target language |
| `source_translation` | TEXT | NOT NULL | Translation in the source language |
| `context_sentence` | TEXT | | Example sentence in target language |
| `difficulty_score` | REAL | NOT NULL DEFAULT 0.5 | 0.0 (easy) to 1.0 (hard) |
| `times_seen` | INTEGER | NOT NULL DEFAULT 0 | |
| `times_correct` | INTEGER | NOT NULL DEFAULT 0 | |
| `last_seen_at` | TEXT | | |
| `next_review_at` | TEXT | | Spaced repetition next date |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS vocabulary_items (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id             INTEGER NOT NULL REFERENCES user_language_pairs(id) ON DELETE CASCADE,
    target_word         TEXT    NOT NULL,
    source_translation  TEXT    NOT NULL,
    context_sentence    TEXT,
    difficulty_score    REAL    NOT NULL DEFAULT 0.5,
    times_seen          INTEGER NOT NULL DEFAULT 0,
    times_correct       INTEGER NOT NULL DEFAULT 0,
    last_seen_at        TEXT,
    next_review_at      TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(pair_id, target_word)
);
CREATE INDEX IF NOT EXISTS idx_vocab_pair ON vocabulary_items(pair_id);
CREATE INDEX IF NOT EXISTS idx_vocab_review ON vocabulary_items(pair_id, next_review_at);
```

---

### `assessments`

Assessment sessions tracking placement or progress evaluations.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `pair_id` | INTEGER | FK → user_language_pairs.id | |
| `assessment_type` | TEXT | NOT NULL | `placement` \| `progress` |
| `skills_json` | TEXT | NOT NULL | JSON array of skills tested |
| `status` | TEXT | NOT NULL DEFAULT 'pending' | `pending` \| `completed` |
| `result_level` | TEXT | | CEFR code, set on completion |
| `skill_levels_json` | TEXT | | `{"reading":"A1","writing":"A0"}` |
| `total_xp_awarded` | INTEGER | | |
| `questions_json` | TEXT | NOT NULL DEFAULT '[]' | Full question objects including `correct_index`; never exposed to client. Added by migration `001_assessment_questions.sql`. |
| `feedback` | TEXT | | Human-readable summary generated at submit time; persisted for retrieval. Added by migration `002_assessment_feedback.sql`. |
| `completed_at` | TEXT | | |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS assessments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id           INTEGER NOT NULL REFERENCES user_language_pairs(id) ON DELETE CASCADE,
    assessment_type   TEXT    NOT NULL,
    skills_json       TEXT    NOT NULL,
    status            TEXT    NOT NULL DEFAULT 'pending',
    result_level      TEXT,
    skill_levels_json TEXT,
    total_xp_awarded  INTEGER,
    completed_at      TEXT,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);
-- Migration 001 adds: questions_json TEXT NOT NULL DEFAULT '[]'
-- Migration 002 adds: feedback TEXT
```

---

### `assessment_answers`

Individual answers within an assessment.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `assessment_id` | INTEGER | FK → assessments.id | |
| `question_id` | TEXT | NOT NULL | External question reference |
| `skill` | TEXT | NOT NULL | `reading` \| `listening` \| `writing` \| `speaking` |
| `level` | TEXT | NOT NULL | CEFR level of the question |
| `user_answer` | TEXT | NOT NULL | |
| `is_correct` | INTEGER | | 1/0/NULL (null = pending AI eval) |
| `xp_awarded` | INTEGER | NOT NULL DEFAULT 0 | |
| `feedback` | TEXT | | AI-generated feedback |
| `created_at` | TEXT | NOT NULL | |

```sql
CREATE TABLE IF NOT EXISTS assessment_answers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id  INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id    TEXT    NOT NULL,
    skill          TEXT    NOT NULL,
    level          TEXT    NOT NULL,
    user_answer    TEXT    NOT NULL,
    is_correct     INTEGER,
    xp_awarded     INTEGER NOT NULL DEFAULT 0,
    feedback       TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_answers_assessment ON assessment_answers(assessment_id);
```

---

## XP Thresholds per Level

Stored as application constants (not in the database):

| From | To | XP Required |
|---|---|---|
| A0 | A1 | 500 |
| A1 | A2 | 1,000 |
| A2 | B1 | 2,000 |
| B1 | B2 | 3,500 |
| B2 | C1 | 5,000 |
| C1 | C2 | 7,500 |

---

## Migration Strategy

For MVP, run `init_db.py` once to apply the full schema. As the product evolves:

1. Never modify existing `CREATE TABLE` statements in `schema.py`
2. Add new tables or columns as numbered migration files: `backend/database/migrations/001_add_users.sql`
3. Track applied migrations in a `schema_migrations` table
4. For production (PostgreSQL), use `alembic` for migration management
