# build_clean.ps1
# Script PowerShell para fazer build do AMSender usando ambiente virtual limpo
# Esta abordagem garante que apenas as dependências necessárias sejam incluídas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AMSender - Build Script (Ambiente Limpo)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Nome do ambiente virtual
$venvName = "venv_build"

# Verifica se PyInstaller está instalado globalmente (necessário para criar o venv)
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller não encontrado"
    }
} catch {
    Write-Host "PyInstaller não encontrado. Instalando..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host "Criando ambiente virtual limpo..." -ForegroundColor Yellow
if (Test-Path $venvName) {
    Write-Host "Removendo ambiente virtual existente..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvName
}

python -m venv $venvName

Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& "$venvName\Scripts\Activate.ps1"

Write-Host "Instalando dependências necessárias..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

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
    "--collect-all", "ttkbootstrap",
    "--collect-all", "google.auth",
    "--collect-all", "googleapiclient",
    "--collect-all", "docx",
    "--collect-submodules", "docx",
    "main.py"
)

pyinstaller @pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Falha ao criar executável!" -ForegroundColor Red
    deactivate
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
Write-Host "Deseja remover o ambiente virtual? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "S" -or $response -eq "s") {
    deactivate
    Remove-Item -Recurse -Force $venvName
    Write-Host "Ambiente virtual removido." -ForegroundColor Green
} else {
    Write-Host "Ambiente virtual mantido em: $venvName" -ForegroundColor Cyan
    deactivate
}

Read-Host "Pressione Enter para sair"

