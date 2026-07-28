import os
import time
from collections import defaultdict, deque
from datetime import date

from dotenv import load_dotenv

load_dotenv()  # reads backend/.env into the process environment - must run
# before chatbot.py is imported, since it reads OPENAI_MODEL at import time.

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
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

# --- Rate limiting / abuse protection --------------------------------------
# This is an in-memory, single-process limiter - good enough for a demo on a
# single Render instance, but wouldn't scale across multiple server processes.
# A production version would use Redis so limits are shared across instances.

PER_IP_MAX_REQUESTS = int(os.environ.get("PER_IP_MAX_REQUESTS", "10"))
PER_IP_WINDOW_SECONDS = int(os.environ.get("PER_IP_WINDOW_SECONDS", "60"))
GLOBAL_DAILY_LIMIT = int(os.environ.get("GLOBAL_DAILY_LIMIT", "300"))

_ip_request_log: dict[str, deque] = defaultdict(deque)
_global_daily_count = {"date": None, "count": 0}


def _get_client_ip(request: Request) -> str:
    # Render (and most hosts) sit behind a proxy, so the real visitor IP is
    # in this header rather than request.client.host.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_per_ip_limit(client_ip: str) -> bool:
    now = time.time()
    window = _ip_request_log[client_ip]
    while window and window[0] < now - PER_IP_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= PER_IP_MAX_REQUESTS:
        return False
    window.append(now)
    return True


def _check_global_daily_limit() -> bool:
    today = date.today().isoformat()
    if _global_daily_count["date"] != today:
        _global_daily_count["date"] = today
        _global_daily_count["count"] = 0
    if _global_daily_count["count"] >= GLOBAL_DAILY_LIMIT:
        return False
    _global_daily_count["count"] += 1
    return True


# -----------------------------------------------------------------------------


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest, http_request: Request):
    client_ip = _get_client_ip(http_request)

    if not _check_per_ip_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many messages - please wait a minute and try again.",
        )

    if not _check_global_daily_limit():
        raise HTTPException(
            status_code=429,
            detail="This demo has hit its daily message limit. Please try again tomorrow.",
        )

    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    try:
        reply_text, used_tools = get_reply(chat_request.messages)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=502, detail=f"Chatbot backend error: {exc}") from exc

    return ChatResponse(reply=reply_text, used_tools=used_tools)
