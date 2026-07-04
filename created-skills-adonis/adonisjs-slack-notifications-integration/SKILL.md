---
name: adonisjs-slack-notifications-integration
description: Use when configuring, sending, or debugging Slack notifications and webhooks in AdonisJS v6, formatting Slack blocks for rich messages, or routing system alerts, critical exceptions, and queue failures to Slack channels.
---

# Integração de Notificações do Slack no AdonisJS v6

## Objetivo
Estabelecer padrões de código e práticas de implementação para o envio resiliente e assíncrono de notificações do Slack, alertas do sistema e relatórios estruturados a partir de serviços de backend no AdonisJS v6.

## Instruções

### 1. Configuração e Validação de Ambiente
* Garanta que as URLs de webhook ou tokens de Bot sejam armazenados de forma segura em variáveis de ambiente (ex: `SLACK_WEBHOOK_URL`).
* Valide as variáveis de ambiente no arquivo `start/env.ts` utilizando esquemas de validação do VineJS:
  ```typescript
  SLACK_WEBHOOK_URL: Env.schema.string.optional({ format: 'url' }),
  ```

### 2. Implementação do Serviço (`SlackService`)
* Crie um serviço dedicado em `app/services/slack_service.ts` para gerenciar os payloads enviados.
* Utilize o `fetch` nativo do Node.js para fazer a requisição POST para a URL do webhook do Slack (no backend Adonis o padrão é `fetch` nativo, não Axios).
* Envolva todas as chamadas HTTP em blocos `try/catch` para evitar que falhas de dependências de terceiros quebrem os fluxos principais da aplicação.
* Implemente uma estrutura básica de envio de JSON:
  ```typescript
  import env from '#start/env'

  export default class SlackService {
    public static async sendMessage(payload: Record<string, any>) {
      const url = env.get('SLACK_WEBHOOK_URL')
      if (!url) return

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })

        if (!response.ok) {
          // Registrar log ou tratar erros de rate limit do Slack
        }
      } catch (error) {
        // Silenciar ou enviar para o logger local, não relançar a exceção
      }
    }
  }
  ```

### 3. Formatação de Mensagens Ricas com Block Kit
* Estruture alertas e logs utilizando o formato JSON **Block Kit** do Slack para tornar as notificações legíveis:
  * **Header Block (Cabeçalho):** Texto simples indicando o contexto do alerta (ex: `[CRÍTICO] Alerta de Falha de Job`).
  * **Section Block (Seção):** Campos em formato Markdown com detalhes (ex: *Job:* `publish_event_job`, *Erro:* `Meta API rate limit exceeded`).
  * **Divider Block (Divisor):** Adicione quebras visuais entre seções de contexto.
  * **Actions Block (Ações):** Forneça botões interativos com links para o Sentry, para o dashboard de filas do BullMQ ou para a página de detalhes do erro.
* Exemplo de estrutura de payload:
  ```json
  {
    "blocks": [
      {
        "type": "header",
        "text": { "type": "plain_text", "text": "🚨 Alerta Crítico do Sistema" }
      },
      { "type": "divider" },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Ocorreu uma exceção inesperada:*\n```Error: Graph API Rate Limit Exceeded```"
        }
      }
    ]
  }
  ```

### 4. Envios Resilientes e Assíncronos
* **Execução Assíncrona:** Nunca dispare chamadas de API do Slack de forma síncrona durante o ciclo de requisição-resposta HTTP padrão.
* **Integração com BullMQ:** Enfileire tarefas de notificação (ex: `SlackNotificationJob`) usando BullMQ para todas as mensagens não críticas, relatórios de alertas ou resumos diários.
* **Fallback no Exception Handler:** Dentro do manipulador global de exceções (`app/exceptions/handler.ts`), dispare os alertas de forma assíncrona sem bloquear a resposta do usuário. Trate erros de rede de forma isolada e segura.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* Nunca adicione URLs de webhook do Slack ou tokens de autenticação diretamente no controle de versão.
* Evite o disparo em massa ou repetitivo de notificações. Implemente uma janela de deduplicação simples em memória ou baseada em Redis (ex: limite de um alerta a cada 5 minutos para a mesma assinatura de exceção).
* Evite enviar apenas mensagens em formato de texto puro para erros complexos; sempre utilize a estrutura de `blocks` para garantir clareza visual.
