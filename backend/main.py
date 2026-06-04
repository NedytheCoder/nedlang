from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from api.reception.test import router as test_router
from api.user.handler import router as user_router
from database.script import get_connection
from api.lang_map import localize
from api.hobby_map import localize_hobby
from api.motivation_map import localize_motivation
import os

load_dotenv()

app = FastAPI(
    title="AI Language Coach API",
    description="Backend API for AI-powered language learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router, prefix="/reception/test", tags=["Reception Test API"])
app.include_router(user_router, prefix="/user", tags=["User"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/hobbies")
def get_hobbies(ui_lang: str = Query(default="en")):
    conn = get_connection()
    try:
        rows = conn.execute("SELECT name FROM hobbies ORDER BY name").fetchall()
        return [
            {"name": r["name"], "localizedName": localize_hobby(r["name"], ui_lang)}
            for r in rows
        ]
    finally:
        conn.close()


@app.get("/motivations")
def get_motivations(ui_lang: str = Query(default="en")):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT label FROM motivations WHERE is_active = 1 ORDER BY id"
        ).fetchall()
        return [
            {"label": r["label"], "localizedLabel": localize_motivation(r["label"], ui_lang)}
            for r in rows
        ]
    finally:
        conn.close()


@app.get("/languages")
def get_languages(ui_lang: str = Query(default="en")):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT code, name, native_name FROM languages WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        return [
            {
                "code": r["code"],
                "name": r["name"],
                "nativeName": r["native_name"],
                "localizedName": localize(r["code"], ui_lang, r["name"]),
            }
            for r in rows
        ]
    finally:
        conn.close()


@app.get("/")
def read_root():
    """
    Root endpoint - Health check.
    
    Returns:
        dict: Simple message confirming the backend is running
    """
    return {"message": "Hello from backend!"}

