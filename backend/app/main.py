import os

from dotenv import load_dotenv

load_dotenv()  # reads backend/.env into the process environment - must run
# before chatbot.py is imported, since it reads OPENAI_MODEL at import time.

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from .chatbot import get_reply  # noqa: E402
from .models import ChatRequest, ChatResponse  # noqa: E402

app = FastAPI(title="AI Customer Support Chatbot API", version="0.1.0")

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    try:
        reply_text, used_tools = get_reply(request.messages)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=502, detail=f"Chatbot backend error: {exc}") from exc

    return ChatResponse(reply=reply_text, used_tools=used_tools)
