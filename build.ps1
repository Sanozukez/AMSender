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
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }

Write-Host ""
Write-Host "Criando executável..." -ForegroundColor Green
Write-Host ""

# Cria o executável
$pyinstallerArgs = @(
    "--name=AMSender",
    "--onefile",
    "--windowed",
    "--noconsole",
    "--icon=image\icon.ico",
    "--add-data", "src;src",
    "--add-data", "image;image",
    "--hidden-import=ttkbootstrap",
    "--hidden-import=pandas",
    "--hidden-import=openpyxl",
    "--hidden-import=docx",
    "--hidden-import=docx.oxml",
    "--hidden-import=docx.oxml.ns",
    "--hidden-import=google.auth",
    "--hidden-import=google.auth.oauthlib",
    "--hidden-import=google.auth.transport.requests",
    "--hidden-import=googleapiclient",
    "--hidden-import=googleapiclient.discovery",
    "--hidden-import=dotenv",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--collect-all", "ttkbootstrap",
    "--collect-all", "google",
    "--collect-all", "google.auth",
    "--collect-all", "googleapiclient",
    "main.py"
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
Write-Host "Executável criado em: dist\AMSender.exe" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"

