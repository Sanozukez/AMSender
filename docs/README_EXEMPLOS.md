# Exemplos de Uso

## Formato da Planilha Excel

A planilha Excel deve ter a primeira linha como cabeçalho. Colunas obrigatórias:
- `email`: Email do destinatário (obrigatório)
- `nome`: Nome do destinatário (recomendado para personalização)

Colunas adicionais podem ser usadas como placeholders no template.

### Exemplo de estrutura:

| email                | nome        | empresa      | cargo        |
|----------------------|-------------|--------------|--------------|
| joao@exemplo.com     | João Silva  | Empresa A    | Gerente      |
| maria@exemplo.com    | Maria Santos| Empresa B    | Diretora     |

## Formato do Template

Use placeholders no formato `{{nome_da_coluna}}` no template.

### Exemplo de template TXT:

```
Olá {{nome}},

Este é um email personalizado para você.

Seus dados:
- Email: {{email}}
- Empresa: {{empresa}}
- Cargo: {{cargo}}

Atenciosamente,
Equipe
```

### Exemplo de template DOCX:

Crie um documento Word (.docx) e use os mesmos placeholders:
- `{{nome}}`
- `{{email}}`
- `{{empresa}}`
- etc.

## Anexos

Você pode adicionar múltiplos anexos. Formatos suportados:
- PDF
- Imagens (JPG, PNG, etc.)
- Documentos (DOCX, XLSX, etc.)
- Qualquer tipo de arquivo

## Delay entre Envios

O sistema usa um delay de 2.5 segundos entre envios por padrão (configurável no .env).
Isso está de acordo com as recomendações do Google para evitar throttling.
