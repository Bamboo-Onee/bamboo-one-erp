@echo off
TITLE Bamboo One - Backend API
echo ========================================================
echo       BAMBOO ONE - INICIANDO BACKEND FASTAPI
echo ========================================================
cd /d "%~dp0..\backend"
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
pause
