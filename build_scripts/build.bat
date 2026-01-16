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
    --hidden-import=google.auth ^
    --hidden-import=google_auth_oauthlib ^
    --hidden-import=google.auth.transport.requests ^
    --hidden-import=googleapiclient ^
    --hidden-import=googleapiclient.discovery ^
    --hidden-import=dotenv ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --exclude-module=torch ^
    --exclude-module=tensorflow ^
    --exclude-module=transformers ^
    --exclude-module=sklearn ^
    --exclude-module=scipy ^
    --exclude-module=matplotlib ^
    --exclude-module=cv2 ^
    --exclude-module=onnxruntime ^
    --exclude-module=bitsandbytes ^
    --exclude-module=gradio ^
    --exclude-module=sympy ^
    --exclude-module=numba ^
    --exclude-module=llvmlite ^
    --exclude-module=imageio ^
    --exclude-module=altair ^
    --exclude-module=timm ^
    --exclude-module=torchvision ^
    --exclude-module=uvicorn ^
    --exclude-module=websockets ^
    --exclude-module=anyio ^
    --exclude-module=fsspec ^
    --exclude-module=pydantic ^
    --exclude-module=orjson ^
    --exclude-module=jsonschema ^
    --exclude-module=jsonschema_specifications ^
    --exclude-module=wcwidth ^
    --exclude-module=regex ^
    --exclude-module=pygments ^
    --exclude-module=jinja2 ^
    --exclude-module=tzdata ^
    --exclude-module=zoneinfo ^
    --exclude-module=importlib_resources ^
    --exclude-module=packaging ^
    --hidden-import=typing_extensions ^
    --exclude-module=zipp ^
    --exclude-module=importlib_metadata ^
    --exclude-module=setuptools ^
    --exclude-module=distutils ^
    --exclude-module=pycparser ^
    --exclude-module=win32com ^
    --exclude-module=pythoncom ^
    --exclude-module=pywintypes ^
    --exclude-module=psutil ^
    --collect-all ttkbootstrap ^
    --collect-all google.auth ^
    --collect-all googleapiclient ^
    --collect-all docx ^
    --collect-submodules docx ^
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

