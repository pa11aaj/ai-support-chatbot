# Windows PowerShell setup helper for the backend.
# Run from the backend/ folder: .\setup.ps1

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env - open it and add your OPENAI_API_KEY before running the server."
}

Write-Host "Setup complete. Start the server with:"
Write-Host "  uvicorn app.main:app --reload --port 8000"
