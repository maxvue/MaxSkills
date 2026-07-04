---
name: adonisjs-instagram-comments-ai-moderation-best-practices
description: Use when implementing, reviewing, or debugging Instagram and Meta comments moderation, AI sentiment analysis, automated comment replies, or handling comments webhooks in AdonisJS v6. Triggers on files modifying CommentsController, Meta webhook processors, AI agent replies, or BullMQ jobs for comment moderation.
---

## Objetivo
Estabelecer padrões e boas práticas para integrar a moderação de comentários do Instagram/Meta, o tratamento de eventos de webhook, a análise de sentimento por IA e as respostas automatizadas baseadas em fila dentro de uma aplicação AdonisJS v6.

## Instruções
Ao implementar ou modificar a moderação por IA de comentários do Instagram ou a lógica de webhook, siga os seguintes princípios:

1. **Tratamento de Webhook da Meta e Idempotência**
   - Receba o payload cru do webhook em um controller, persista-o imediatamente no model `Webhook` e retorne uma resposta `200 OK` para a Meta dentro do limite de 3 segundos, para evitar retries.
   - Despache a lógica de processamento para uma fila usando o `BullMQ` (ex: via `MetaWebhookJob.dispatch(webhookId)`).
   - No `MetaWebhookJob`, normalize a estrutura do webhook tanto para o Instagram (`object=instagram`, `field=comments`) quanto para a Facebook Page (`object=page`, `field=feed`, `item=comment`). Use as definições auxiliares em `resources/meta_webhook_payloads.md` como referência.
   - Realize upserts idempotentes (`updateOrCreate`) dos comentários usando o `externalCommentId` (ID do comentário da Meta) como chave de busca.

2. **Análise de Sentimento por IA e Moderação**
   - Use o Vercel AI SDK (com os provedores Google Gemini ou Anthropic) para analisar o sentimento dos comentários.
   - Projete os prompts de IA para produzir um JSON estruturado contendo:
     - `sentiment`: `"positive" | "neutral" | "negative" | "toxic"`
     - `action`: `"approve" | "hide" | "flag" | "reply"`
     - `suggestedReply`: string (se a action for `reply`, personalizada ao conteúdo do post e ao tom do comentário)
   - Utilize um formato de prompt de system instructions similar ao `resources/ai_moderation_prompt_template.md`.
   - Armazene a saída da IA e os metadados no banco de dados (ex: atualize a coluna `hidden` do `SocialMediaComment` ou uma tabela de log de moderação relacionada).

3. **Respostas Automatizadas Baseadas em Fila**
   - Nunca poste respostas de forma síncrona a partir do router do webhook ou do worker primário de IA. Despache um job BullMQ dedicado (ex: `SendInstagramReplyJob`) para realizar a chamada de API à Meta.
   - Implemente estratégias de retry com exponential backoff (ex: `backoff: { type: 'exponential', delay: 5000 }`) e limite as tentativas (ex: `attempts: 3`) para lidar com rate limits da API da Meta ou erros transitórios.
   - Ao postar uma resposta via Meta Graph API (ex: `POST /v20.0/{comment-id}/replies`), atualize a coluna `replied` do comentário para `true` e registre a resposta gerada.

4. **Modelagem de Dados (AdonisJS Lucid)**
   - Utilize ULIDs como chaves primárias nos models de comentário e de webhook.
   - Mantenha os atributos do model `SocialMediaComment`: `externalCommentId`, `eventId` (link para CalendarEvent), `eventApiId`, `text`, `isReply`, `isFromUs`, `replied`, `hidden` e o payload JSON `raw`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Não processe webhooks de forma síncrona. Toda a lógica de negócio e a análise por IA devem ser adiadas para filas BullMQ.
- Não faça requisições de API externas à Meta Graph API sem tratamento de erros e um wrapper de recuperação de rate-limit.
- Não deixe versões de API hardcoded nas URLs da Graph API; use variáveis de configuração (ex: `env.get('META_API_VERSION', 'v20.0')`).
