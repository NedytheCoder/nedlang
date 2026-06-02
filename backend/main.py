from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
from api.reception.test import router as test_router
import os

load_dotenv()

app = FastAPI(
    title="AI Language Coach API",
    description="Backend API for AI-powered language learning",
    version="1.0.0"
)
app.include_router(test_router, prefix="/reception/test", tags=["Reception Test API"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def read_root():
    """
    Root endpoint - Health check.
    
    Returns:
        dict: Simple message confirming the backend is running
    """
    return {"message": "Hello from backend!"}

