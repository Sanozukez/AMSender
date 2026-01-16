@echo off
REM create_installer.bat
REM Script para criar o instalador usando Inno Setup

echo ========================================
echo AMSender - Criar Instalador
echo ========================================
echo.

REM Verifica se o executável foi criado
if not exist "dist\AMSender.exe" (
    echo ERRO: Executavel nao encontrado!
    echo Execute build.bat primeiro para criar o executavel.
    pause
    exit /b 1
)

REM Verifica se Inno Setup está instalado
set INNO_SETUP_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_SETUP_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
) else (
    echo ERRO: Inno Setup nao encontrado!
    echo.
    echo Por favor, instale o Inno Setup:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Criando diretorio de instalador...
if not exist installer mkdir installer

echo.
echo Compilando instalador com Inno Setup...
echo.

"%INNO_SETUP_PATH%" installer.iss

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao criar instalador!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalador criado com sucesso!
echo ========================================
echo.
echo Instalador criado em: installer\AMSender_Setup.exe
echo.
pause

