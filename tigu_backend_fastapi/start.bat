@echo off
echo 🔄 Starting Tigu Backend FastAPI Server
echo ==========================================

echo 🧹 Cleaning Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo ✅ Cache cleaned!
echo 🚀 Starting server...

poetry run uvicorn tigu_backend_fastapi.app.main:app --reload --host 0.0.0.0 --port 8000

pause 