@echo off
TITLE Bamboo One - Inicializador Completo
echo ========================================================
echo        BAMBOO ONE - SISTEMA INTEGRADO DE GESTAO
echo               GRUPO BAMBOO - INICIALIZADOR
echo ========================================================
echo.
echo [1/2] Iniciando Backend FastAPI (Porta 8000)...
start "Bamboo One - Backend FastAPI" cmd /k "cd /d "%~dp0..\backend" && python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend React Vite (Porta 5173)...
start "Bamboo One - Frontend React" cmd /k "cd /d "%~dp0..\frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ========================================================
echo   Servicos iniciados em janelas dedicadas!
echo   - Backend:  http://127.0.0.1:8000/docs
echo   - Frontend: http://127.0.0.1:5173
echo ========================================================
pause
