# Amatools Mail Sender - Sistema de Envio em Massa de Emails

## Descrição

Sistema com interface gráfica para envio em massa de emails personalizados via Google Workspace (SMTP), com suporte a anexos, templates personalizáveis e sistema de comprovação de envios.

## Características

- ✅ Interface gráfica moderna e minimalista (Tkinter + ttkbootstrap)
- ✅ Leitura de destinatários de planilha Excel
- ✅ Templates personalizáveis (DOCX ou TXT) com placeholders
- ✅ Suporte a múltiplos anexos
- ✅ Delay automático entre envios (conforme recomendações do Google)
- ✅ Sistema de comprovação: logs, arquivos .eml e resumo JSON
- ✅ Tratamento robusto de erros e retry automático
- ✅ Preview do email antes do envio

## Requisitos

- Python 3.8 ou superior
- Conta Google Workspace com senha de app configurada
- Windows 10/11

## Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais:
   - Copie `config_example.env` para `.env`
   - Preencha com suas credenciais SMTP do Google Workspace
   - Use uma senha de app (não a senha normal da conta)

## Como Obter Senha de App do Google

1. Acesse sua conta Google
2. Ative a verificação em duas etapas (se ainda não tiver)
3. Vá em: Conta Google → Segurança → Verificação em duas etapas → Senhas de app
4. Crie uma nova senha de app para "Email"
5. Use essa senha no arquivo `.env`

## Uso

1. Execute o sistema:
```bash
python main.py
```

2. Na interface:
   - Selecione o arquivo Excel com os destinatários
   - Selecione o template (DOCX ou TXT)
   - Selecione os anexos (pode ser múltiplos)
   - Configure o assunto do email
   - Visualize o preview
   - Clique em "Iniciar Envio"

## Formato do Excel

O arquivo Excel deve ter a primeira linha como cabeçalho. Colunas obrigatórias:
- `email`: Email do destinatário
- `nome`: Nome do destinatário (para personalização)

Colunas adicionais podem ser usadas como placeholders no template.

## Templates

Use placeholders no formato `{{nome}}`, `{{email}}`, etc. no template.

Exemplo de template TXT:
```
Olá {{nome}},

Este é um email personalizado para {{email}}.

Atenciosamente,
Equipe
```

## Comprovação de Envios

O sistema gera:
- **Logs detalhados**: `logs/envio_YYYYMMDD_HHMMSS.log`
- **Arquivos .eml**: `comprovacoes/YYYYMMDD_HHMMSS/` (um por email enviado)
- **Resumo JSON**: `comprovacoes/YYYYMMDD_HHMMSS/resumo.json`

Os arquivos .eml podem ser abertos em qualquer cliente de email como comprovação.

## Estrutura de Pastas

```
mail-sender/
├── main.py                 # Aplicação principal
├── src/
│   ├── config.py          # Configurações e carregamento de .env
│   ├── excel_reader.py    # Leitura de planilhas Excel
│   ├── template_processor.py  # Processamento de templates
│   ├── email_sender.py    # Envio via SMTP
│   ├── comprovacao.py     # Sistema de comprovação
│   └── ui/
│       └── main_window.py # Interface gráfica
├── requirements.txt
├── .env                    # Suas credenciais (não versionado)
└── README.md
```

## Licença

Uso interno - Amatools

