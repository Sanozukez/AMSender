# create_installer.ps1
# Script PowerShell para criar o instalador usando Inno Setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AMSender - Criar Instalador" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se o executável foi criado
if (-not (Test-Path "..\dist\AMSender.exe")) {
    Write-Host "ERRO: Executável não encontrado!" -ForegroundColor Red
    Write-Host "Execute build.ps1 primeiro para criar o executável." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verifica se Inno Setup está instalado
$innoSetupPath = $null
$possiblePaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $innoSetupPath = $path
        break
    }
}

if ($null -eq $innoSetupPath) {
    Write-Host "ERRO: Inno Setup não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale o Inno Setup:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Criando diretório de instalador..." -ForegroundColor Yellow
if (-not (Test-Path "..\installer")) {
    New-Item -ItemType Directory -Path "..\installer" | Out-Null
}

Write-Host ""
Write-Host "Compilando instalador com Inno Setup..." -ForegroundColor Green
Write-Host ""

& $innoSetupPath "installer.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Falha ao criar instalador!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalador criado com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Instalador criado em: ..\installer\AMSender_Setup.exe" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"

