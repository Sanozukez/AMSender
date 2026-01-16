@echo off
REM build_clean.bat
REM Script para fazer build do AMSender usando ambiente virtual limpo
REM Esta abordagem garante que apenas as dependências necessárias sejam incluídas

echo ========================================
echo AMSender - Build Script (Ambiente Limpo)
echo ========================================
echo.

REM Nome do ambiente virtual
set VENV_NAME=venv_build

REM Verifica se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo Criando ambiente virtual limpo...
if exist %VENV_NAME% (
    echo Removendo ambiente virtual existente...
    rmdir /s /q %VENV_NAME%
)

python -m venv %VENV_NAME%

echo Ativando ambiente virtual...
call %VENV_NAME%\Scripts\activate.bat

echo Instalando dependencias necessarias...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

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
    --hidden-import=docx.document ^
    --hidden-import=docx.oxml ^
    --hidden-import=docx.oxml.ns ^
    --hidden-import=docx.oxml.parser ^
    --hidden-import=docx.opc ^
    --hidden-import=docx.opc.package ^
    --hidden-import=docx.opc.part ^
    --hidden-import=docx.opc.oxml ^
    --hidden-import=docx.shared ^
    --hidden-import=docx.text ^
    --hidden-import=docx.text.paragraph ^
    --hidden-import=lxml ^
    --hidden-import=lxml.etree ^
    --hidden-import=lxml._elementpath ^
    --hidden-import=lxml ^
    --hidden-import=lxml.etree ^
    --hidden-import=lxml._elementpath ^
    --hidden-import=google.auth ^
    --hidden-import=google_auth_oauthlib ^
    --hidden-import=google.auth.transport.requests ^
    --hidden-import=googleapiclient ^
    --hidden-import=googleapiclient.discovery ^
    --hidden-import=dotenv ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all ttkbootstrap ^
    --collect-all google.auth ^
    --collect-all googleapiclient ^
    --collect-all docx ^
    --collect-submodules docx ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao criar executavel!
    call %VENV_NAME%\Scripts\deactivate.bat
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
echo Deseja remover o ambiente virtual? (S/N)
set /p response=
if /i "%response%"=="S" (
    call %VENV_NAME%\Scripts\deactivate.bat
    rmdir /s /q %VENV_NAME%
    echo Ambiente virtual removido.
) else (
    echo Ambiente virtual mantido em: %VENV_NAME%
    call %VENV_NAME%\Scripts\deactivate.bat
)

pause

