# Instruções de Build e Instalação

## Pré-requisitos

1. **Python 3.8 ou superior** instalado
2. **PyInstaller** (será instalado automaticamente se não estiver)
3. **Inno Setup** (para criar o instalador)
   - Download: https://jrsoftware.org/isdl.php
   - Versão recomendada: Inno Setup 6

## Passo a Passo

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Criar Executável

**Windows (CMD):**
```cmd
build.bat
```

**Windows (PowerShell):**
```powershell
.\build.ps1
```

O executável será criado em: `dist\AmatoolsMailSender.exe`

### 3. Criar Instalador

**Windows (CMD):**
```cmd
create_installer.bat
```

**Windows (PowerShell):**
```powershell
.\create_installer.ps1
```

O instalador será criado em: `installer\AmatoolsMailSender_Setup.exe`

## Estrutura do Instalador

O instalador criado inclui:
- Executável principal (standalone, não precisa de Python)
- Arquivos de configuração exemplo
- Documentação (README.md, GUIA_OAUTH.md)
- Pasta `credentials` (para arquivo credentials.json do OAuth)
- Pasta `exemplos` (se existir)

## Distribuição

O arquivo `AmatoolsMailSender_Setup.exe` pode ser distribuído e instalado em qualquer computador Windows 10/11, mesmo sem Python instalado.

### Requisitos do Sistema de Destino

- Windows 10 ou Windows 11
- Permissões de administrador para instalação
- Conexão com internet (para envio de emails)

## Notas Importantes

1. **Primeira execução**: O executável pode demorar alguns segundos para iniciar (PyInstaller precisa extrair arquivos temporários)

2. **Antivírus**: Alguns antivírus podem marcar executáveis criados com PyInstaller como suspeitos. Isso é um falso positivo comum.

3. **Tamanho do executável**: O executável será grande (~100-200MB) pois inclui todas as dependências Python.

4. **Atualizações**: Para atualizar, basta criar um novo build e redistribuir o instalador.

## Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install pyinstaller
```

### Erro: "Inno Setup não encontrado"
- Baixe e instale o Inno Setup do site oficial
- O script procura automaticamente nos locais padrão de instalação

### Erro: "Módulo não encontrado" no executável
- Adicione o módulo faltante em `--hidden-import` no script build.bat/build.ps1

### Executável não inicia
- Verifique se todas as dependências estão listadas em `--hidden-import`
- Execute o executável pelo terminal para ver mensagens de erro

