@echo off
echo Starting FastAPI Backend...
start cmd /k "venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Vite Frontend...
cd AI_Concierge\frontend
start cmd /k "npm run dev"

echo Both services are starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
