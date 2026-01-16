# Instruções de Build e Instalação

## Pré-requisitos

1. **Python 3.10+** instalado (recomendado 3.11 ou 3.12)
2. **Ambiente virtual (venv)** configurado
3. **PyInstaller** (instalado no venv)
4. **Inno Setup** (para criar o instalador)
   - Download: https://jrsoftware.org/isdl.php
   - Versão recomendada: Inno Setup 6

## Configuração Inicial

### 1. Ativar Ambiente Virtual

Se acabou de abrir o projeto no VS Code:

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
.venv\Scripts\activate.bat
```

Você verá `(.venv)` no prompt indicando que o ambiente está ativo.

### 2. Instalar Dependências no venv

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## Build do Executável

### Executar o Build

Navegue até a pasta `build_scripts/` e execute:

**PowerShell:**
```powershell
cd build_scripts
.\build.ps1
```

**CMD:**
```cmd
cd build_scripts
build.bat
```

O script irá:
- Limpar builds anteriores
- Criar executável standalone com PyInstaller
- Empacotar todas as dependências do venv (isolado de outros projetos)

**Saída:** `dist\AMSender.exe` (na raiz do projeto)

### Importante sobre Venv

O PyInstaller **apenas empacota dependências instaladas no venv ativo**. Isso evita:
- Conflitos com bibliotecas de outros projetos
- Executável inchado com libs desnecessárias
- Problemas de versão

## Criar Instalador

### Executar o Script de Instalação

Navegue até `build_scripts/` e execute:

**PowerShell:**
```powershell
cd build_scripts
.\create_installer.ps1
```

**CMD:**
```cmd
cd build_scripts
create_installer.bat
```

O script irá:
- Verificar se o executável existe
- Localizar Inno Setup
- Compilar o instalador

**Saída:** `installer\AMSender_Setup.exe` (na raiz do projeto)

## Distribuição

O arquivo `installer\AMSender_Setup.exe` pode ser distribuído e instalado em qualquer computador Windows 10/11, mesmo sem Python instalado.

### Requisitos do Sistema de Destino

- Windows 10 ou Windows 11
- Permissões de administrador para instalação
- Conexão com internet (para envio de emails)

## Estrutura do Instalador

O instalador criado inclui:
- Executável principal (standalone, sem necessidade de Python)
- Arquivos de configuração exemplo
- Documentação completa (pasta `docs/`)
- Pasta `credentials` (para colocar `credentials.json` do OAuth)
- Pasta `exemplos` (templates e planilhas de exemplo)

## Notas Importantes

1. **Primeira execução**: O executável pode demorar alguns segundos para iniciar (PyInstaller precisa extrair arquivos temporários)

2. **Antivírus**: Alguns antivírus podem marcar executáveis criados com PyInstaller como suspeitos. Isso é um falso positivo comum.

3. **Tamanho do executável**: O executável será grande (~100-200MB) pois inclui todas as dependências Python.

4. **Atualizações**: Para atualizar, basta criar um novo build e redistribuir o instalador.

## Solução de Problemas

### Venv não ativa / erro "cannot be loaded"
**PowerShell:** pode precisar alterar a política de execução:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "PyInstaller não encontrado"
Certifique-se de que o venv está ativo e instale:
```powershell
pip install pyinstaller
```

### Erro: "Inno Setup não encontrado"
- Baixe e instale o Inno Setup do site oficial
- O script procura automaticamente nos locais padrão de instalação

### Erro: "Módulo não encontrado" no executável
- Adicione o módulo faltante em `--hidden-import` no script `build_scripts/build.ps1` ou `build.bat`
- Recrie o executável

### Executável não inicia
- Verifique se todas as dependências estão listadas em `--hidden-import`
- Execute o executável pelo terminal (fora do venv) para ver mensagens de erro:
  ```powershell
  .\dist\AMSender.exe
  ```

### Build inclui bibliotecas de outros projetos
- **Causa:** build rodado fora do venv
- **Solução:** sempre ative o venv antes de rodar `build.ps1` ou `build.bat`
