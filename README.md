# Amatools Mail Sender - Envio em Massa

Sistema com interface gráfica (Tkinter + ttkbootstrap) para envio em massa de emails personalizados via SMTP (senha de app) ou Gmail API (OAuth), com logs, evidências e preview.

## Características
- Interface gráfica simples; preview antes de enviar
- Leitura de destinatários em Excel (pandas/openpyxl)
- Templates TXT/DOCX com placeholders estritos (letras/números/underscore)
- Suporte a múltiplos anexos
- Delay automático entre envios; retry e erros detalhados
- Evidências completas em `Documentos/AmatoolsMailSender`: `.eml`, hashes, headers, raw (OAuth) e `resumo.json`

## Requisitos
- Python 3.10+ (recomendado 3.11 ou 3.12)
- Windows 10/11
- Autenticação: senha de app SMTP **ou** Google OAuth (credentials.json)

## Instalação rápida
```powershell
pip install -r requirements.txt
```

## Autenticação
- **SMTP (senha de app)**: copie `config_example.env` para `.env` e preencha SMTP/porta/usuario/senha de app.
- **OAuth (Gmail API)**: coloque `credentials/credentials.json`; na UI selecione Google OAuth e clique em "Autenticar" (guia em `docs/GUIA_OAUTH.md`). Tokens ficam em `credentials/token_<email>.pickle`.

## Uso
```powershell
python main.py
```
Na interface: escolha Excel, template, anexos e método de envio; veja o preview e clique em "Iniciar Envio".

## Planilha e templates
- Excel: cabeçalho na primeira linha; coluna obrigatória `email`. Outros campos podem ser usados como placeholders.
- Placeholders válidos: `{{nome_da_coluna}}` apenas com letras/números/underscore (sem espaços/acentos). Inválidos são limpos.
- Exemplos em `docs/README_EXEMPLOS.md`.

## Evidências
Cada campanha cria `Documentos/AmatoolsMailSender/<campanha>-<timestamp>/` com:
- `resumo.json` (status, IDs, headers, hashes, historyId/raw quando OAuth)
- `.eml` por destinatário (com SHA-256 registrado)
- Cópias de anexos e template; log txt da campanha

## Documentação
- Arquitetura e princípios: `docs/ARCHITECTURE.md`
- Guia OAuth: `docs/GUIA_OAUTH.md`
- Build/instalador: `docs/BUILD_INSTRUCTIONS.md`
- Exemplos: `docs/README_EXEMPLOS.md`

Licença: uso interno Amatools.

