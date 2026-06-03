import uuid

from fastapi import APIRouter, HTTPException
import bcrypt
from pydantic import BaseModel

from database.script import get_connection

router = APIRouter()


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))


# ─── Request model ────────────────────────────────────────────────────────────

class RegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    native_language: str        # ISO 639-1 code e.g. "en"
    target_language: str        # ISO 639-1 code e.g. "fr"
    learning_goal: str
    top_hobbies: list[str]      # exactly 3 hobby names
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
                learning_goal, preferred_learning_style, daily_goal_minutes,
                framework
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, req.email, username,
                req.first_name, req.last_name, pw_hash,
                native_id, target_id,
                req.learning_goal, req.preferred_learning_style, req.daily_goal_minutes,
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
