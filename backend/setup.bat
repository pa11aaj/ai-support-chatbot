@echo off
REM Windows Command Prompt setup helper for the backend.
REM Run from the backend\ folder: setup.bat

python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist ".env" (
    copy .env.example .env
    echo Created .env - open it and add your OPENAI_API_KEY before running the server.
)

echo Setup complete. Start the server with:
echo   uvicorn app.main:app --reload --port 8000
