@echo off
TITLE Bamboo One - Frontend React
echo ========================================================
echo       BAMBOO ONE - INICIANDO FRONTEND VITE REACT
echo ========================================================
cd /d "%~dp0..\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
pause
