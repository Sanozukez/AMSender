# Guia de Configuração do Google OAuth

## Passo a Passo para Configurar OAuth do Google

### 1. Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Ative as APIs necessárias:
   - Vá em "APIs e Serviços" > "Biblioteca"
   - Procure e ative:
     * **Gmail API** (para envio de emails)
     * **Google+ API** ou **People API** (para leitura de perfil do usuário)
   - Clique em "Ativar" em cada uma

### 2. Criar Credenciais OAuth

1. Vá em "APIs e Serviços" > "Credenciais"
2. Clique em "Criar credenciais" > "ID do cliente OAuth"
3. Configure a tela de consentimento OAuth (se ainda não tiver):
   
   **⚠️ IMPORTANTE - Google Workspace:**
   - Se você usa Google Workspace, a tela de consentimento pode estar gerenciada pelo **administrador do Workspace**
   - Se não conseguir acessar "Tela de consentimento OAuth" no Google Cloud Console, você precisa:
     * **Opção 1**: Pedir ao administrador do Workspace para configurar
     * **Opção 2**: Acessar como administrador do Workspace em: admin.google.com
     * **Opção 3**: Usar uma conta pessoal do Google (não recomendado para produção)
   
   **Para configurar (se tiver acesso):**
   - **Tipo de usuário**: 
     * **Interno**: Para Google Workspace (recomendado para empresas)
     * **Externo**: Para contas pessoais do Google
   - Preencha as informações necessárias (nome do app, email de suporte, etc.)
   - **IMPORTANTE**: Se usar "Interno", adicione seu email como usuário de teste em "Usuários de teste"
   - Adicione os escopos necessários:
     * `https://www.googleapis.com/auth/gmail.send`
     * `https://www.googleapis.com/auth/userinfo.email`
4. Configure o ID do cliente OAuth:
   - Tipo de aplicativo: "Aplicativo de desktop"
   - Nome: "Mail Sender" (ou qualquer nome)
5. Clique em "Criar"
6. Baixe o arquivo JSON das credenciais

### 3. Configurar no Sistema

1. Crie a pasta `credentials` na raiz do projeto (se não existir)
2. Renomeie o arquivo JSON baixado para `credentials.json`
3. Coloque o arquivo na pasta `credentials/`
4. Estrutura:
   ```
   mail-sender/
   ├── credentials/
   │   └── credentials.json
   ├── src/
   └── ...
   ```

### 4. Usar no Sistema

1. Abra o sistema Mail Sender
2. Vá na aba "Configurações"
3. Selecione "Google OAuth (Autenticação via Navegador)"
4. **Digite o MESMO email que você usou para criar as credenciais** (ex: `comunicado@amatools.com.br`)
5. Clique em "Autenticar com Google"
6. Uma janela do navegador abrirá
7. **Faça login com o MESMO email usado para criar as credenciais** (não precisa ser administrador)
8. Autorize o acesso
9. A janela fechará automaticamente
10. O status mostrará "Autenticado: comunicado@amatools.com.br"

**⚠️ IMPORTANTE:**
- Use o **mesmo email** que você usou para criar as credenciais OAuth no Google Cloud Console
- **NÃO precisa** fazer login como administrador, a menos que precise configurar a tela de consentimento
- Se o app for "Interno" e você não estiver na lista de usuários de teste, adicione seu email na tela de consentimento OAuth

### 5. Pronto!

Após autenticar uma vez, você não precisará fazer login novamente. O token é salvo automaticamente e renovado quando necessário.

## Notas Importantes

- O arquivo `credentials.json` contém informações sensíveis. Não compartilhe ou version no Git.
- Os tokens são salvos na pasta `credentials/` com o nome `token_[email].pickle`
- Se quiser desconectar, use o botão "Desconectar" na interface
- Para usar outro email, basta digitar o novo email e autenticar novamente

## Solução de Problemas

**Erro: "Arquivo credentials.json não encontrado"**
- Verifique se o arquivo está na pasta `credentials/`
- Verifique se o nome do arquivo está correto: `credentials.json`

**Erro: "Email autenticado não corresponde"**
- Certifique-se de digitar o mesmo email que autorizou no navegador

**Token expirado**
- O sistema renova automaticamente. Se não funcionar, desconecte e autentique novamente

**Não consigo acessar a Tela de Consentimento OAuth no Google Cloud Console**
- **Se você usa Google Workspace**: A tela de consentimento pode estar gerenciada pelo administrador
- **Solução 1**: Peça ao administrador do Workspace para:
  * Acessar Google Cloud Console → APIs e Serviços → Tela de consentimento OAuth
  * Configurar os escopos necessários:
    - `https://www.googleapis.com/auth/gmail.send`
    - `https://www.googleapis.com/auth/userinfo.email`
  * Adicionar seu email (`comunicado@amatools.com.br`) como usuário de teste
- **Solução 2**: Se você tem acesso ao painel de administração do Workspace:
  * Acesse: admin.google.com
  * Vá em: Segurança → Controles de API → Gerenciamento de consentimento
  * Configure conforme necessário
- **Solução 3**: Use uma conta pessoal do Google para testes (não recomendado para produção)

**Qual conta usar para autenticar?**
- **Use a MESMA conta que você usou para criar as credenciais OAuth**
- Exemplo: Se você criou as credenciais com `comunicado@amatools.com.br`, use essa conta para autenticar
- **NÃO precisa** fazer login como administrador (`aureo@amatools.com.br`) para usar o sistema
- A conta de administrador só é necessária se você precisar **configurar** a tela de consentimento OAuth
- Se você criou as credenciais, você pode usar sua própria conta para autenticar

