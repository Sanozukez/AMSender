@echo off
REM build.bat
REM Script para fazer build do AMSender usando PyInstaller

echo ========================================
echo AMSender - Build Script
echo ========================================
echo.

REM Verifica se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Criando executavel...
echo.

REM Cria o executável
pyinstaller --name="AMSender" ^
    --onefile ^
    --windowed ^
    --noconsole ^
    --icon=image\icon.ico ^
    --add-data "src;src" ^
    --add-data "image;image" ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=docx ^
    --hidden-import=docx.oxml ^
    --hidden-import=docx.oxml.ns ^
    --hidden-import=google.auth ^
    --hidden-import=google.auth.oauthlib ^
    --hidden-import=google.auth.transport.requests ^
    --hidden-import=googleapiclient ^
    --hidden-import=googleapiclient.discovery ^
    --hidden-import=dotenv ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all ttkbootstrap ^
    --collect-all google ^
    --collect-all google.auth ^
    --collect-all googleapiclient ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao criar executavel!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build concluido com sucesso!
echo ========================================
echo.
echo Executavel criado em: dist\AMSender.exe
echo.
pause

