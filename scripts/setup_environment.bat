@echo off
TITLE Bamboo One - Instalador de Dependencias
echo ========================================================
echo       BAMBOO ONE - INSTALACAO DE DEPENDENCIAS
echo ========================================================
echo.
echo [1/2] Instalando dependencias do Backend Python...
cd /d "%~dp0..\backend"
pip install -r requirements.txt

echo.
echo [2/2] Instalando dependencias do Frontend Node/React...
cd /d "%~dp0..\frontend"
call npm install

echo.
echo ========================================================
echo  Instalacao concluida com sucesso!
echo  Voce ja pode executar o script 'start_all.bat' para rodar o sistema.
echo ========================================================
pause
