"""
convo.py
────────
Real-time conversation endpoint using the OpenAI Realtime API.

GET  /convo/session?user_id=...
  Returns the learner's profile (level, languages) so the frontend
  can display context before the WebSocket is opened.

WebSocket /convo/ws?user_id=...
  Relays audio bidirectionally between the browser and OpenAI's
  Realtime API.  The backend builds a personalised French-tutor
  system prompt from the user's DB profile then steps out of the way.

Wire-up (main.py):
  from api.convo import router as convo_router
  app.include_router(convo_router, prefix="/convo", tags=["Convo"])
"""

import asyncio
import base64
import io
import json
import os

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from openai import OpenAI
from pydantic import BaseModel
from websockets.asyncio.client import connect as ws_connect

from database.script import get_connection

load_dotenv()

router = APIRouter()

_REALTIME_URL   = "wss://api.openai.com/v1/realtime?model=gpt-realtime"
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_oai            = OpenAI(api_key=_OPENAI_API_KEY)


# ── User profile ──────────────────────────────────────────────────────────────

def _get_profile(user_id: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT u.current_level, u.learning_goal, u.framework,
                   u.selected_motivations, u.preferred_learning_style,
                   nl.name AS native_name,
                   tl.name AS target_name, tl.code AS target_code
            FROM users u
            JOIN languages nl ON nl.id = u.native_language_id
            JOIN languages tl ON tl.id = u.target_language_id
            WHERE u.id = ?
            """,
            (user_id,),
        ).fetchone()
        if row is None:
            return None

        profile = dict(row)

        hobby_rows = conn.execute(
            """
            SELECT h.name FROM hobbies h
            JOIN user_hobbies uh ON uh.hobby_id = h.id
            WHERE uh.user_id = ?
            ORDER BY h.name
            """,
            (user_id,),
        ).fetchall()
        profile["hobbies"] = [r["name"] for r in hobby_rows]
        return profile
    finally:
        conn.close()


# ── System prompt ─────────────────────────────────────────────────────────────

def _build_system_prompt(profile: dict) -> str:
    level      = profile.get("current_level") or "A1"
    target     = profile.get("target_name")   or "French"
    native     = profile.get("native_name")   or "English"
    goal       = profile.get("learning_goal") or "general fluency"
    style      = profile.get("preferred_learning_style") or ""
    hobbies    = profile.get("hobbies") or []

    motivations: list[str] = []
    raw = profile.get("selected_motivations")
    if raw:
        try:
            motivations = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            pass

    lines = [
        f"You are a warm, patient, and encouraging {target} language tutor.",
        f"Your learner's native language is {native}. They are currently at {level} level.",
        f"Their stated learning goal is: {goal}.",
    ]

    if motivations:
        lines.append(f"Their motivations for learning {target}: {', '.join(motivations)}.")

    if hobbies:
        lines.append(
            f"Their hobbies and interests are: {', '.join(hobbies)}. "
            f"Weave these naturally into conversation topics when relevant."
        )

    if style:
        lines.append(f"They prefer a {style.lower()} learning style — adapt your explanations accordingly.")

    lines += [
        "",
        "CONVERSATION RULES:",
        f"- Speak primarily in {target}. Only switch to {native} briefly when the learner is clearly lost.",
        f"- Keep sentences short and simple, appropriate for {level} level. Never use vocabulary far above this level.",
        "- After each learner turn, gently correct any grammar or pronunciation errors in a natural, encouraging way, then continue.",
        "- If the learner struggles with a word, offer it to them rather than waiting awkwardly.",
        "- Keep the conversation flowing like a real human exchange — ask follow-up questions, react naturally.",
        "- Never break character or discuss topics unrelated to language learning and conversation practice.",
        f"- Start with a warm greeting in {target} and ask the learner what they'd like to talk about today.",
    ]

    return "\n".join(lines)


# ── WhatsApp-style chat helpers ───────────────────────────────────────────────

def _transcribe(audio_bytes: bytes, filename: str) -> str:
    result = _oai.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, io.BytesIO(audio_bytes)),
    )
    return result.text.strip()


def _chat_respond(messages: list[dict]) -> str:
    response = _oai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content or ""


def _tts(text: str) -> str:
    response = _oai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    return base64.b64encode(response.content).decode()


# ── WhatsApp-style chat endpoint ──────────────────────────────────────────────

@router.post("/chat/turn")
async def chat_turn(
    user_id: str        = Query(...),
    audio:   UploadFile = File(...),
    history: str        = Form(default="[]"),
):
    """
    Single turn of the WhatsApp-style chat.

    Accepts a recorded audio clip + the existing conversation history,
    returns the user's transcription, the tutor's text reply, and the
    tutor's reply as a base64-encoded MP3.
    """
    profile = _get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    audio_bytes = await audio.read()

    try:
        past: list[dict] = json.loads(history)
    except (json.JSONDecodeError, TypeError):
        past = []

    system_prompt = _build_system_prompt(profile)
    user_text     = await asyncio.to_thread(_transcribe, audio_bytes, audio.filename or "audio.webm")

    messages = (
        [{"role": "system", "content": system_prompt}]
        + past
        + [{"role": "user", "content": user_text}]
    )

    assistant_text  = await asyncio.to_thread(_chat_respond, messages)
    assistant_audio = await asyncio.to_thread(_tts, assistant_text)

    return {
        "user_text":       user_text,
        "assistant_text":  assistant_text,
        "assistant_audio": assistant_audio,
    }


# ── Text-turn endpoint ───────────────────────────────────────────────────────

class TextTurnRequest(BaseModel):
    user_id: str
    text: str
    history: list[dict] = []


@router.post("/chat/text-turn")
async def chat_text_turn(body: TextTurnRequest):
    """
    Single text turn of the WhatsApp-style chat.

    Accepts the user's typed message + conversation history,
    returns the tutor's text reply and a base64-encoded MP3.
    """
    profile = _get_profile(body.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    system_prompt = _build_system_prompt(profile)
    messages = (
        [{"role": "system", "content": system_prompt}]
        + body.history
        + [{"role": "user", "content": body.text}]
    )

    assistant_text  = await asyncio.to_thread(_chat_respond, messages)
    assistant_audio = await asyncio.to_thread(_tts, assistant_text)

    return {
        "user_text":       body.text,
        "assistant_text":  assistant_text,
        "assistant_audio": assistant_audio,
    }


# ── Session info endpoint ─────────────────────────────────────────────────────

@router.get("/session")
def get_session(user_id: str = Query(...)):
    profile = _get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "level":           profile["current_level"],
        "target_language": profile["target_name"],
        "native_language": profile["native_name"],
    }


# ── WebSocket relay ───────────────────────────────────────────────────────────

@router.websocket("/ws")
async def convo_websocket(websocket: WebSocket, user_id: str = Query(...)):
    await websocket.accept()

    profile = _get_profile(user_id)
    if not profile:
        await websocket.close(code=4004, reason="User not found")
        return

    system_prompt = _build_system_prompt(profile)
    oai_headers = {
        "Authorization": f"Bearer {_OPENAI_API_KEY}",
    }

    session_config = {
        "type": "session.update",
        "session": {
            "type":         "realtime",
            "instructions": system_prompt,
            "audio": {
                "input": {
                    "format": {"type": "audio/pcm", "rate": 24000},
                    "transcription": {"model": "whisper-1"},
                    "turn_detection": {
                        "type":                "server_vad",
                        "threshold":           0.5,
                        "prefix_padding_ms":   300,
                        "silence_duration_ms": 600,
                    },
                },
                "output": {"voice": "alloy"},
            },
        },
    }

    try:
        async with ws_connect(
            _REALTIME_URL,
            additional_headers=oai_headers,
            max_size=2 ** 24,   # 16 MB — handles large audio deltas
        ) as oai_ws:
            await oai_ws.send(json.dumps(session_config))

            async def browser_to_openai() -> None:
                try:
                    while True:
                        data = await websocket.receive_text()
                        await oai_ws.send(data)
                except (WebSocketDisconnect, Exception):
                    pass

            async def openai_to_browser() -> None:
                try:
                    async for message in oai_ws:
                        try:
                            await websocket.send_text(
                                message if isinstance(message, str) else message.decode()
                            )
                        except Exception:
                            break
                except Exception:
                    pass

            b2o = asyncio.ensure_future(browser_to_openai())
            o2b = asyncio.ensure_future(openai_to_browser())

            # Run until either side closes, then cancel the other
            done, pending = await asyncio.wait(
                [b2o, o2b],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    except Exception as exc:
        try:
            await websocket.send_text(json.dumps({
                "type":    "error",
                "message": str(exc),
            }))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
