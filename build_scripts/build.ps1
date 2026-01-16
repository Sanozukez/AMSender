# build.ps1
# Script PowerShell para fazer build do AMSender usando PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AMSender - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se PyInstaller está instalado
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller não encontrado"
    }
} catch {
    Write-Host "PyInstaller não encontrado. Instalando..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host "Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "..\build") { Remove-Item -Recurse -Force "..\build" }
if (Test-Path "..\dist") { Remove-Item -Recurse -Force "..\dist" }
if (Test-Path "..\__pycache__") { Remove-Item -Recurse -Force "..\__pycache__" }

Write-Host ""
Write-Host "Criando executável..." -ForegroundColor Green
Write-Host ""

# Cria o executável
$pyinstallerArgs = @(
    "--name=AMSender",
    "--onefile",
    "--windowed",
    "--noconsole",
    "--distpath=..\dist",
    "--workpath=..\build",
    "--icon=..\image\icon.ico",
    "--add-data", "..\src;src",
    "--add-data", "..\image;image",
    "--hidden-import=ttkbootstrap",
    "--hidden-import=pandas",
    "--hidden-import=openpyxl",
    "--hidden-import=docx",
    "--hidden-import=docx.document",
    "--hidden-import=docx.oxml",
    "--hidden-import=docx.oxml.ns",
    "--hidden-import=docx.oxml.parser",
    "--hidden-import=docx.opc",
    "--hidden-import=docx.opc.package",
    "--hidden-import=docx.opc.part",
    "--hidden-import=docx.opc.oxml",
    "--hidden-import=docx.shared",
    "--hidden-import=docx.text",
    "--hidden-import=docx.text.paragraph",
    "--hidden-import=lxml",
    "--hidden-import=lxml.etree",
    "--hidden-import=lxml._elementpath",
    "--hidden-import=google.auth",
    "--hidden-import=google_auth_oauthlib",
    "--hidden-import=google.auth.transport.requests",
    "--hidden-import=googleapiclient",
    "--hidden-import=googleapiclient.discovery",
    "--hidden-import=dotenv",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--exclude-module=torch",
    "--exclude-module=tensorflow",
    "--exclude-module=transformers",
    "--exclude-module=sklearn",
    "--exclude-module=scipy",
    "--exclude-module=matplotlib",
    "--exclude-module=cv2",
    "--exclude-module=onnxruntime",
    "--exclude-module=bitsandbytes",
    "--exclude-module=gradio",
    "--exclude-module=sympy",
    "--exclude-module=numba",
    "--exclude-module=llvmlite",
    "--exclude-module=imageio",
    "--exclude-module=altair",
    "--exclude-module=timm",
    "--exclude-module=torchvision",
    "--exclude-module=uvicorn",
    "--exclude-module=websockets",
    "--exclude-module=anyio",
    "--exclude-module=fsspec",
    "--exclude-module=pydantic",
    "--exclude-module=orjson",
    "--exclude-module=jsonschema",
    "--exclude-module=jsonschema_specifications",
    "--exclude-module=wcwidth",
    "--exclude-module=regex",
    "--exclude-module=pygments",
    "--exclude-module=jinja2",
    "--exclude-module=tzdata",
    "--exclude-module=zoneinfo",
    "--exclude-module=importlib_resources",
    "--exclude-module=packaging",
    "--hidden-import=typing_extensions",
    "--exclude-module=zipp",
    "--exclude-module=importlib_metadata",
    "--exclude-module=setuptools",
    "--exclude-module=distutils",
    "--exclude-module=pycparser",
    "--exclude-module=win32com",
    "--exclude-module=pythoncom",
    "--exclude-module=pywintypes",
    "--exclude-module=psutil",
    "--collect-all", "ttkbootstrap",
    "--collect-all", "google.auth",
    "--collect-all", "googleapiclient",
    "--collect-all", "docx",
    "--collect-submodules", "docx",
    "..\\main.py"
)

pyinstaller @pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Falha ao criar executável!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build concluído com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Executável criado em: ..\\dist\\AMSender.exe" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"

