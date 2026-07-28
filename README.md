# AI Customer Support Chatbot (Demo)

A working demo of an AI-powered customer support chatbot for an e-commerce
site: a React chat widget backed by a FastAPI service that uses OpenAI's
tool calling (function calling) to answer general questions, look up product
info, and check order status.

Built as a portfolio sample for a freelance brief asking for exactly this:
a chatbot that handles basic inquiries, product information, and order
tracking, deliverable in a 1-3 month engagement. See
[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for how this demo maps to that
timeline.

> Setup instructions below are written for Windows (PowerShell, the default
> terminal in VS Code on Windows). If you're on macOS/Linux instead, the
> only difference is the venv activation command - see the note in the
> Backend section.

## Why it's built this way

Rather than hand-coding intent detection ("if message contains 'order'..."),
the model itself decides when it needs data and calls one of three tools:
`get_product_info`, `get_order_status`, or `escalate_to_human`. The backend
resolves the tool call against a small mock dataset and hands the result
back to the model to finish its answer. This is the same pattern you'd use
in production - `backend/app/data.py` is the one file that changes to plug
into a real product catalog and order-management system instead of mock data.

## Architecture

```
frontend/ (React + Vite)        backend/ (FastAPI)
┌─────────────────────┐         ┌──────────────────────────┐
│  ChatWidget.jsx      │  POST   │  /api/chat                │
│  - message history   │ ─────▶  │  - calls OpenAI w/ tools  │
│  - input box         │  JSON   │  - resolves tool calls    │
│                       │ ◀───── │    against data.py        │
└─────────────────────┘         │  - loops until final reply │
                                  └──────────────────────────┘
                                              │
                                              ▼
                                     OpenAI API (GPT)
```

## Getting started (Windows / PowerShell)

### Backend

Quickest path: from the `backend/` folder, run `.\setup.ps1` (PowerShell) or `setup.bat` (cmd) - it creates the venv, installs dependencies, and copies `.env.example` to `.env` for you. Then just add your API key to `.env` and start the server (see below).

Or do it manually. Open a terminal in VS Code (PowerShell) at the project root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Then open `.env` and add your real `OPENAI_API_KEY`, and run:

```powershell
uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks the activation script with an execution-policy error,
run this once (in the same terminal) and try activating again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Using Command Prompt (cmd) instead of PowerShell:

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Using macOS/Linux/Git Bash instead:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Get an API key at https://platform.openai.com/api-keys. Without a key, the
server starts fine but `/api/chat` will error when it tries to call OpenAI -
the tests use a mocked client so they don't need one.

### Frontend

Open a second terminal (npm commands are the same on every OS):

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

(macOS/Linux: use `cp .env.example .env` instead of `copy`.)

Open the printed localhost URL, click the "Chat with us" bubble, and try:

- "What's the price of the Aurora headphones?"
- "Where's my order ord-1001?"
- "Do you have the Pulse water bottle in stock?"

Order IDs in the mock data: `ord-1001` (shipped), `ord-1002` (processing),
`ord-1003` (delivered).

### Tests

With the backend venv activated:

```powershell
cd backend
pytest
```

## What's mocked vs. real

| Piece | This demo | Production version |
|---|---|---|
| AI responses | Real OpenAI API call | Same |
| Product catalog | In-memory dict (`data.py`) | Client's product API / DB |
| Order data | In-memory dict (`data.py`) | Client's order-management system |
| Escalation to human | Logs to console | Creates a ticket in Zendesk/Intercom/etc. |
| Auth | None | Session auth so the bot only shows a customer their own orders |

## Project structure

```
ai-support-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI app, /api/chat endpoint
│   │   ├── chatbot.py     # OpenAI tool-calling loop, system prompt, tool schemas
│   │   ├── data.py        # Mock product/order data + lookup helpers
│   │   └── models.py      # Pydantic request/response schemas
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/ChatWidget.jsx
└── docs/
    └── PROJECT_PLAN.md
```

## Extending this for a real client

1. Swap `data.py` for real API calls to their store platform.
2. Add auth so order lookups are scoped to the logged-in customer (or verify
   by order ID + email).
3. Add conversation persistence (e.g. Postgres/Redis) so history survives a
   page refresh.
4. Add analytics/logging on which questions get escalated, to find gaps in
   the bot's knowledge over time.
5. Embed the widget as a script snippet so it can drop into any site, not
   just this Vite app.
