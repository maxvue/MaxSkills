---
name: adonisjs-user-impersonation-best-practices
description: Use when implementing, configuring, reviewing, or securing user impersonation (login-as) features in AdonisJS v6 backend. Triggers on session simulation, admin impersonator actions, custom Auth guard modifiers, and audit logs for impersonated sessions.
---

# Boas Práticas de Personificação de Usuários (Login-As) no AdonisJS v6

## Objetivo
Estabelecer um padrão arquitetural seguro, auditável e confiável para a implementação de personificação de usuários (login-as / simulação de sessão) em aplicações AdonisJS v6. Isso inclui verificações rigorosas de autorização, gerenciamento da transição de sessões, logs de auditoria detalhados (conformidade com LGPD/GDPR) e indicadores de estado no frontend.

## Instruções

### 1. Políticas de Autorização e Segurança
*   **Restringir Acesso:** Apenas usuários com privilégios administrativos explícitos devem acessar os endpoints de personificação.
*   **Verificação de Bouncer:** Defina uma política ou verificação clara (por exemplo, usando uma verificação personalizada na array de permissões `permissions.can_impersonate` ou uma ação dedicada do Bouncer, se disponível) antes de permitir a personificação.
*   **Proibir Personificações Aninhadas:** Verifique se a sessão ativa já está personificando um usuário. A personificação em cascata/aninhada deve ser estritamente bloqueada.

### 2. Ciclo de Vida da Sessão de Personificação (Troca de Sessão)
*   **Armazenar ID do Admin:** Salve o ID e o contexto do administrador original na sessão antes de alternar identidades:
    ```typescript
    session.put('impersonated_by', auth.user.id)
    ```
*   **Fazer Login no Usuário Alvo:** Autentique a sessão do usuário alvo utilizando a API de autenticação do AdonisJS:
    ```typescript
    await auth.use('web').login(targetUser)
    ```
*   **Tokens Remember-Me:** Nunca gere ou envie tokens `rememberMe` ao fazer login como o usuário alvo. As sessões personificadas devem expirar quando a sessão do navegador for encerrada.
*   **Parar a Personificação:**
    *   Verifique a existência da chave `impersonated_by` na sessão:
        ```typescript
        const adminId = session.get('impersonated_by')
        if (!adminId) {
          throw new Error('Nenhuma sessão de personificação ativa')
        }
        ```
    *   Recupere o usuário administrador no banco de dados.
    *   Remova os metadados de personificação da sessão:
        ```typescript
        session.forget('impersonated_by')
        ```
    *   Realize novamente o login do administrador original:
        ```typescript
        await auth.use('web').login(adminUser)
        ```

### 3. Logs de Auditoria de Segurança e Conformidade (LGPD/GDPR)
*   **Rastreamento de Ações:** Registre todos os eventos de personificação (`start` e `stop`) em um canal de logs de segurança dedicado ou trilha de auditoria no banco de dados.
*   **Conteúdo dos Logs:**
    *   ID do Usuário Personificador (Administrador).
    *   ID do Usuário Alvo.
    *   Tipo de ação (`impersonation_started`, `impersonation_stopped`).
    *   Endereço IP, User Agent e Carimbo de Data/Hora (Timestamp).
*   **Exemplo de Payload de Log:**
    ```json
    {
      "event": "auth.impersonation_started",
      "actor_id": "ulid_admin_user",
      "target_id": "ulid_target_user",
      "ip": "192.168.1.1",
      "user_agent": "Mozilla/5.0 ...",
      "timestamp": "2026-06-25T15:40:00Z"
    }
    ```

### 4. Exposição do Estado de Personificação para o Frontend
*   **Payload da Resposta:** O frontend obtém os dados do usuário via store `@maxvue/max-pinia` (ex: store que faz GET em `/user/data`). Inclua no payload dessa rota uma flag booleana adicional `isImpersonated` e os detalhes do personificador, se ativos — para que sejam carregados na store junto com o restante do estado do usuário.
*   **Integração com Vue:** No componente, leia essa flag a partir da store MaxPinia (não faça `axios.get` manual) para exibir uma barra de aviso persistente e visível (ex: "Você está visualizando esta conta como [Nome do Usuário]. Clique aqui para retornar ao Painel Admin.").

### 5. Testes de Integração com Japa
*   **Validação do Middleware de Autenticação:** Escreva casos de teste validando que contas sem privilégios de administrador recebam `403 Forbidden` ou `401 Unauthorized` ao tentar acessar rotas de personificação.
*   **Teste de Fluxo de Integração:** Implemente um teste Japa que simule o login do admin, chame o endpoint de personificação, verifique os valores na sessão e depois finalize a personificação.

## Restrições
*   **NÃO** permita que usuários comuns ou papéis não autorizados acionem endpoints de personificação sob nenhuma circunstância.
*   **NÃO** registre senhas de usuários alvo, e-mails ou dados pessoais identificáveis em logs de auditoria. Registre apenas IDs, eventos e timestamps.
*   **NÃO** persista sessões personificadas utilizando cookies remember-me.
*   **NÃO** defina regras fixas de papéis (roles) no código (hardcoded); use uma verificação dinâmica de permissão ou política de segurança.
