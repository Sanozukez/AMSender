# Arquitetura do Sistema - Amatools Mail Sender

## Princípios de Design Aplicados

### SRP (Single Responsibility Principle)
Cada módulo/classe tem uma única responsabilidade:

- **`config.py`**: Apenas configurações e carregamento de variáveis de ambiente
- **`config_manager.py`**: Apenas gerenciamento de configurações via interface
- **`excel_reader.py`**: Apenas leitura e processamento de planilhas Excel
- **`template_processor.py`**: Apenas processamento de templates (DOCX/TXT)
- **`email_sender.py`**: Apenas envio via SMTP
- **`gmail_sender.py`**: Apenas envio via Gmail API (OAuth)
- **`google_oauth.py`**: Apenas autenticação OAuth do Google
- **`comprovacao.py`**: Apenas geração de comprovações e logs
- **`validators.py`**: Apenas validações de dados
- **`exceptions.py`**: Apenas definições de exceções customizadas
- **`ui/main_window.py`**: Apenas interface gráfica e orquestração

### SOLID

#### S - Single Responsibility ✅
Cada classe tem uma única responsabilidade bem definida.

#### O - Open/Closed ✅
- Sistema extensível: fácil adicionar novos métodos de envio (ex: Outlook API)
- Fechado para modificação: mudanças internas não afetam outros módulos

#### L - Liskov Substitution ✅
- `EmailSender` e `GmailSender` podem ser substituídos sem quebrar o código
- Ambos implementam interface similar para envio

#### I - Interface Segregation ✅
- Interfaces específicas por responsabilidade
- Não força implementação de métodos não utilizados

#### D - Dependency Inversion ✅
- Módulos dependem de abstrações (interfaces), não de implementações concretas
- Configurações via injeção de dependência

## Estrutura de Pastas

```
mail-sender/
├── main.py                      # Entry point
├── src/
│   ├── __init__.py
│   ├── config.py               # Configurações (SRP)
│   ├── config_manager.py       # Gerenciamento de config (SRP)
│   ├── exceptions.py          # Exceções customizadas (SRP)
│   ├── validators.py           # Validações (SRP)
│   ├── excel_reader.py         # Leitura Excel (SRP)
│   ├── template_processor.py   # Processamento templates (SRP)
│   ├── email_sender.py         # Envio SMTP (SRP)
│   ├── gmail_sender.py         # Envio Gmail API (SRP)
│   ├── google_oauth.py         # OAuth Google (SRP)
│   ├── comprovacao.py          # Comprovações (SRP)
│   └── ui/
│       ├── __init__.py
│       └── main_window.py      # Interface gráfica (SRP)
├── credentials/                # Credenciais OAuth (não versionado)
├── requirements.txt
└── README.md
```

## Robustez para Produção

### 1. Tratamento de Erros
- ✅ Exceções específicas por tipo de erro
- ✅ Tratamento de erros de I/O, permissões, rede
- ✅ Não expõe informações sensíveis em erros
- ✅ Logs detalhados sem expor dados sensíveis

### 2. Validações
- ✅ Validação de emails
- ✅ Validação de arquivos
- ✅ Validação de configurações
- ✅ Validação de dados de entrada

### 3. Segurança
- ✅ Credenciais não expostas em logs
- ✅ Tratamento seguro de senhas
- ✅ Tokens OAuth salvos de forma segura
- ✅ Validação de permissões de arquivo

### 4. Recuperação de Erros
- ✅ Retry automático em envios
- ✅ Reconexão automática SMTP
- ✅ Renovação automática de tokens OAuth
- ✅ Fallback para operações críticas

### 5. Logging e Auditoria
- ✅ Logs detalhados de todas as operações
- ✅ Comprovações completas de envios
- ✅ Rastreabilidade completa

### 6. Performance
- ✅ Operações assíncronas (threading)
- ✅ Delay configurável entre envios
- ✅ Processamento eficiente de dados

## Fluxo de Dados

```
Interface (UI)
    ↓
Orquestração (main_window)
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
ExcelReader    TemplateProcessor  ConfigManager
    ↓                 ↓                 ↓
    └─────────────────┴─────────────────┘
                    ↓
            ┌───────┴───────┐
            │               │
      EmailSender    GmailSender
            │               │
            └───────┬───────┘
                    ↓
            Comprovacao
                    ↓
            Logs/Evidências
```

## Boas Práticas Implementadas

1. **Separação de Responsabilidades**: Cada módulo faz uma coisa bem feita
2. **Baixo Acoplamento**: Módulos independentes, comunicação via interfaces claras
3. **Alta Coesão**: Funcionalidades relacionadas agrupadas
4. **Tratamento Robusto de Erros**: Não quebra em produção
5. **Validações**: Dados validados antes de processamento
6. **Logging**: Rastreabilidade completa
7. **Documentação**: Código documentado com docstrings
8. **Type Hints**: Tipos explícitos para melhor manutenção

## Extensibilidade

O sistema foi projetado para ser facilmente extensível:

- **Novos métodos de envio**: Implementar interface similar a `EmailSender`/`GmailSender`
- **Novos formatos de template**: Adicionar suporte em `TemplateProcessor`
- **Novos formatos de entrada**: Adicionar leitores similares a `ExcelReader`
- **Novos tipos de comprovação**: Estender `Comprovacao`

