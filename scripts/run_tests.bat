@echo off
TITLE Bamboo One - Execucao de Testes Automatizados (Docker / Local)
echo ========================================================
echo       BAMBOO ONE - EXECUTANDO TESTES UNITARIOS PYTEST
echo ========================================================
cd /d "%~dp0.."
docker inspect -f "{{.State.Running}}" crm_logistico_backend >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [DOCKER] Executando suíte Pytest dentro do container crm_logistico_backend...
    docker compose exec backend pytest -v tests/
) else (
    echo [LOCAL] Container parado; executando no ambiente virtual local...
    cd /d "%~dp0..\backend"
    if exist ".venv\Scripts\python.exe" (
        ".venv\Scripts\python.exe" -m pytest -v tests/
    ) else (
        python -m pytest -v tests/
    )
)
echo.
echo ========================================================
pause
