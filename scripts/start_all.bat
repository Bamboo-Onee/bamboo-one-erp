@echo off
TITLE Bamboo One - Inicializador Docker Compose
echo ========================================================
echo        BAMBOO ONE - SISTEMA INTEGRADO DE GESTAO
echo           GRUPO BAMBOO - DOCKER COMPOSE STACK
echo ========================================================
echo.
cd /d "%~dp0.."
REM Desativa BuildKit para evitar erro 'invalid file request Dockerfile' em pastas sincronizadas pelo OneDrive (NTFS Reparse Point)
set DOCKER_BUILDKIT=0
set COMPOSE_DOCKER_CLI_BUILD=0

echo [1/2] Construindo imagens e subindo containers (PostgreSQL 16 + Backend FastAPI 4 Workers + Frontend Vite)...
docker build -t bamboo-one-erp-backend ./backend
docker build -t bamboo-one-erp-frontend ./frontend
docker compose up -d

echo.
echo [2/2] Status dos containers:
docker compose ps

echo.
echo ========================================================
echo   Stack Docker iniciada com sucesso!
echo   - PostgreSQL: localhost:5432 (crm_logistico_postgres)
echo   - Backend:    http://localhost:8000/docs (crm_logistico_backend)
echo   - Frontend:   http://localhost:5173 (crm_logistico_frontend)
echo ========================================================
pause
