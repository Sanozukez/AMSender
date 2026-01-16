# Testes

## Como executar

Requisitos: ambiente virtual ativo (/.venv) e dependências instaladas (`pip install -r requirements.txt`).

### Ativar venv

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
.venv\Scripts\activate.bat
```

### Executar testes

Via unittest (já incluído na stdlib):

```powershell
python -m unittest discover tests
```

## Cobertura atual

- **`test_template_processor.py`**: valida placeholders permitidos (letras/números/underscore) e limpeza de inválidos (espaços/acentos).
- **`test_validators.py`**: valida emails válidos e inválidos.
- **`test_excel_reader.py`**: verifica seleção de engine por extensão (.xls/.xlsx) e `last_error` quando arquivo não existe.
- **`test_batch_controller.py`**: teste de integração leve com sender mockado; valida fluxo completo de envio/evidências.
- **`test_comprovacao.py`**: verifica criação de `.eml`, registro no resumo e campos de evidência.

## Arquivos de exemplo

- Planilha e template de exemplo em `exemplos/` (Excel e TXT) caso queira rodar fluxos manuais na UI.

## Adicionando novos testes

1. Crie `tests/test_<modulo>.py`
2. Herde de `unittest.TestCase`
3. Rode com `python -m unittest discover tests`
