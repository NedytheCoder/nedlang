# Engineering Rules

**Project:** AI Language Coach  
**Version:** 1.0 (MVP)  
**Date:** 2026-05-30

These rules govern how this codebase is written and evolved. They exist to keep the project maintainable by a solo founder who needs to move fast without creating a maintenance debt that slows future scaling.

---

## Rule 1: No Language Is Hard-Coded

The single most important rule in this codebase.

**Do not:**
- Write `"French"` or `"English"` or any language name as a string literal in source code
- Name database columns `french_word`, `english_translation`, `target_french_text`
- Write conditional logic like `if language == "fr":`
- Create language-specific API routes like `/api/french-lessons`

**Do:**
- Pass `source_language` and `target_language` as parameters everywhere they are needed
- Use `PromptBuilder` for all AI prompts; never write a prompt inline in an API handler
- Use the `languages` database table as the single source of truth for supported languages
- Name things generically: `target_word`, `source_translation`, `target_language_name`

---

## Rule 2: All AI Calls Go Through the AI Layer

No API handler or service may call `client.chat.completions.create()` directly.

All OpenAI calls are routed through:
- `backend/ai/prompt_builder.py` — constructs prompts
- `backend/ai/lesson_generator.py` — generates lesson content
- `backend/ai/chat_handler.py` — manages conversation
- `backend/ai/assessment_scorer.py` — evaluates answers
- `backend/ai/transcriber.py` — audio to text

**Why:** Centralising AI calls makes it trivial to swap models, add caching, add logging, or add fallbacks in one place.

---

## Rule 3: `content_json` Is the Lesson Schema Escape Valve

Lesson content is stored as a JSON blob in `lessons.content_json`. Do not add new columns to the `lessons` table for new content structures.

When a new lesson type requires a new structure, define the structure in the `LessonGenerator` and document it in a comment. The database does not need to know the internal shape of lesson content.

**Why:** Lesson content formats will change frequently during MVP development. Locking them into database columns creates expensive migrations.

---

## Rule 4: One Auth Dependency, Used Everywhere

Every protected endpoint uses exactly one FastAPI dependency:

```python
from fastapi import Depends
from services.auth_service import get_current_user

@router.get("/something")
def my_endpoint(current_user: User = Depends(get_current_user)):
    ...
```

Do not access JWT tokens directly in handlers. Do not roll custom auth checks. Do not bypass `get_current_user` for "internal" endpoints.

**Why:** A single auth entry point means security bugs are fixed in one place.

---

## Rule 6: Every New Language Is a Data Change, Not a Code Change

Adding support for a new language (e.g., Swahili) requires:

1. `INSERT INTO languages ...` — one row
2. Test an AI lesson and chat session with the new language pair
3. (Optional) curate sample assessment questions for that pair

Adding a new language requires zero changes to:
- Python source code
- TypeScript source code
- Database schema
- API routes
- Frontend components

If a code change is needed to add a language, that is a bug in the architecture. Fix the architecture, not the language.

---

## Rule 8: No Over-Engineering

Do not build abstractions the current codebase does not need.

Specifically, do not:
- Build a plugin system for languages before there are more than 3 supported
- Add a message queue before background tasks are needed
- Add a caching layer before response times are measured to be slow
- Abstract the database layer into a generic repository before there are multiple database backends
- Add microservices before the monolith is under measurable load

**The test:** Does this abstraction solve a problem that exists today, or one that might exist someday? If the answer is "might exist someday", do not build it.

---

## Rule 9: Test the AI Layer With Real Prompts

Unit tests for business logic use mocks freely. But the `PromptBuilder` and `LessonGenerator` are tested with real OpenAI calls in a separate test suite tagged `[integration]`.

At minimum, verify each prompt type works correctly for three diverse language pairs:
- A European pair (e.g. English → Spanish)
- A non-Latin script pair (e.g. English → Japanese)
- A non-English source (e.g. Arabic → French)

**Why:** Prompt logic that "looks correct" in a unit test can fail badly for languages with different grammar structures, word order, or scripts.

---

## Rule 10: Migrations Are Numbered, Never Destructive

Every change to the database schema after the initial schema is applied must be a numbered migration file: `backend/database/migrations/001_add_users.sql`.

Migrations are:
- Additive only (new tables, new columns with defaults)
- Idempotent (safe to run twice)
- Never destructive in production (no `DROP TABLE`, no `DROP COLUMN` without a preceding deprecation period)

---

## Rule 11: Environment Variables, Never Source Code Secrets

No API key, JWT secret, database URL, or any credential appears in source code or is committed to the repository.

Required environment variables are documented in `docs/architecture.md`. The `.env` file is in `.gitignore`.

---

## Rule 12: The Frontend Knows the Pair ID, Not the Language Name

The frontend passes `pair_id` to all API calls. The backend resolves `source_language` and `target_language` from the pair. The frontend never reconstructs the language pair from component state and passes language names to the API.

This ensures the frontend is always consistent with the authoritative pair record in the database.

---

## Code Style (Backend)

- Python 3.12+
- Pydantic v2 for all request/response models
- `snake_case` for all identifiers
- FastAPI routers are never more than ~100 lines; extract to services when they grow
- All service functions are synchronous for MVP (async when moving to PostgreSQL)
- `black` + `ruff` formatting enforced

## Code Style (Frontend)

- TypeScript strict mode
- `camelCase` for variables and functions
- `PascalCase` for components and types
- No `any` types — use `unknown` and narrow
- Components do not contain data-fetching logic beyond calling a hook
