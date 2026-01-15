# Como Atualizar Python para Resolver Warnings

## Problema

O sistema está mostrando um warning sobre Python 3.10.6:
```
FutureWarning: You are using a Python version (3.10.6) which Google will stop supporting...
```

## Solução: Atualizar Python

### Opção 1: Atualizar Python (Recomendado)

1. **Baixe Python 3.11 ou superior:**
   - Acesse: https://www.python.org/downloads/
   - Baixe a versão mais recente (3.12 ou 3.11)
   - **IMPORTANTE**: Durante a instalação, marque "Add Python to PATH"

2. **Reinstale as dependências:**
   ```powershell
   cd "L:\Softwares Amatools\mail-sender"
   python -m pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

3. **Teste o sistema:**
   ```powershell
   python main.py
   ```

### Opção 2: Usar Python Virtual Environment (Recomendado para Isolamento)

1. **Crie um ambiente virtual com Python mais recente:**
   ```powershell
   # Se tiver Python 3.11+ instalado
   python3.11 -m venv venv
   
   # Ou se o Python mais recente estiver no PATH
   python -m venv venv
   ```

2. **Ative o ambiente virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Instale as dependências:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Execute o sistema:**
   ```powershell
   python main.py
   ```

### Opção 3: Ignorar o Warning (Temporário)

O sistema já está configurado para suprimir esses warnings automaticamente. Eles não afetam o funcionamento, apenas avisam sobre suporte futuro.

## Verificar Versão do Python

```powershell
python --version
```

## Notas

- Python 3.10 será suportado até outubro de 2026
- Python 3.11+ é recomendado para melhor performance e suporte
- O sistema funciona com Python 3.10, mas atualizar é recomendado para longo prazo

