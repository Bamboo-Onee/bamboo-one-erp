@echo off
TITLE Bamboo One - Execucao de Testes Automatizados (TDD)
echo ========================================================
echo       BAMBOO ONE - EXECUTANDO TESTES UNITARIOS PYTEST
echo ========================================================
cd /d "%~dp0..\backend"
python -m pytest -v tests/
echo.
echo ========================================================
pause
