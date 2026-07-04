---
name: laravel-meta-graph-api-integration-best-practices
description: "Use when implementing, reviewing, or debugging Meta Graph API integrations in Laravel 13 — Facebook OAuth, exchanging short-lived for long-lived Page/User tokens, publishing posts/stories/reels to Facebook Pages or Instagram Business, inbound Webhooks, or Redis rate limiting. Triggers on MetaService, FacebookController, InstagramController, MetaWebhookController."
---

## Objetivo
Fornecer diretrizes arquiteturais sólidas, seguras e resilientes para integrar as APIs Meta Graph (Facebook e Instagram) usando Laravel 13. Esta skill ajuda a implementar o ciclo de vida de troca de tokens, publicação assíncrona de mídia, validação segura de webhooks e padrões de rate limiting.

## Instruções

### 1. Estrutura Arquitetural
- **Padrão Service Façade:** Encapsule a comunicação com a API dentro de um serviço central (ex: `MetaService`). Vincule cada instância a um model de credencial de token apoiado por banco de dados (ex: `SocialMediaCredential`).
- **Separação de Responsabilidades:** Delegue tarefas específicas a handlers dentro do namespace do serviço:
  - `PublishHandler`: Upload de mídia, criação de contêiner e publicação.
  - `CommentHandler`: Recuperar, responder, ocultar ou deletar comentários.
  - `MediaHandler`: Buscar detalhes de posts, insights e deletar conteúdo.
- **Camada de Transporte HTTP:** Use uma trait (ex: `MetaRequestTrait`) que encapsula o cliente `Http` do Laravel 13. Esta trait deve:
  - Construir dinamicamente URLs versionadas com base em variáveis de config (ex: `https://graph.facebook.com/v24.0/`).
  - Alternar dinamicamente as base URLs entre o Graph padrão do Facebook/Instagram (`graph.facebook.com`) e a Instagram Login API (`graph.instagram.com`).
  - Anexar o token usando `withToken()`.
  - Registrar falhas com `Log::warning()` ou `Log::error()` e normalizar respostas de erro (ex: retornar `['error' => $message]` em vez de lançar exceções diretamente para os handlers).

### 2. Ciclo de Vida e Troca de Token OAuth
- **Troca de Token de Curta para Longa Duração:** Quando um usuário autoriza via OAuth, troque o User Access Token de curta duração (válido por ~2 horas) por um User Access Token de longa duração (válido por ~60 dias) usando o endpoint `/oauth/access_token`:
  ```php
  Http::get('https://graph.facebook.com/' . $version . '/oauth/access_token', [
      'grant_type' => 'fb_exchange_token',
      'client_id' => config('services.facebook.client_id'),
      'client_secret' => config('services.facebook.client_secret'),
      'fb_exchange_token' => $shortLivedToken,
  ]);
  ```
- **Page Access Tokens:** Recupere Page Access Tokens de longa duração (que não expiram) usando o endpoint `/accounts` com o User Access Token de longa duração:
  ```php
  Http::withToken($longLivedUserToken)->get("https://graph.facebook.com/{$version}/me/accounts");
  ```
- **Segurança do Token:** Armazene os access tokens de forma segura no banco de dados. Criptografe-os usando os serviços de criptografia do Laravel e nunca exponha tokens crus para o frontend cliente em respostas de API.

### 3. Fluxos de Publicação de Mídia
- **Instagram (Processo Assíncrono de 2 Etapas):**
  1. **Criar Contêiner de Mídia:** Submeta a mídia (`image_url` ou `video_url` com `media_type => 'REELS'`) e a legenda para `{ig-user-id}/media`.
  2. **Verificar Status de Processamento:** Para itens de vídeo/carrossel, faça polling do status do contêiner em `{container-id}` (campos `status_code`) até que ele mude para `FINISHED`. Trate erros se ele transicionar para `ERROR`.
  3. **Publicar Contêiner:** Despachado para `{ig-user-id}/media_publish` usando o `creation_id` obtido na etapa 1.
- **Carrosséis do Instagram:**
  1. Crie itens de carrossel individuais (contêineres) com `is_carousel_item => true` (sem legenda).
  2. Espere que todos os contêineres de item transicionem para `FINISHED`.
  3. Crie um contêiner pai em `{ig-user-id}/media` com `media_type => 'CAROUSEL'`, `children` como uma string de IDs de contêineres filhos separados por vírgula, e a legenda.
  4. Publique o ID do contêiner pai via `/media_publish`.
- **Páginas do Facebook (Post Direto):**
  - Publique fotos diretamente via `{page-id}/photos` usando o parâmetro `url`.
  - Publique posts de link/texto via `{page-id}/feed` usando os parâmetros `message` e `link`.

### 4. Configuração e Validação de Webhook
- **Verificação de Challenge (GET):** Responda ao handshake de verificação da Meta checando o `hub.verify_token` e retornando o `hub.challenge` cru como um inteiro:
  ```php
  if ($request->input('hub_verify_token') === config('services.facebook.webhook_verify_token')) {
      return response((int) $request->input('hub_challenge'), 200);
  }
  ```
- **Tratamento de Eventos (POST):**
  - Persista o payload cru em uma tabela de banco de dados (ex: `Webhook`) para fins de auditoria.
  - Despache instantaneamente um Job em background (ex: `MetaWebhookJob::dispatch($webhookId)->onQueue('webhooks')`) para lidar com o processamento.
  - Retorne uma resposta rápida (`200 OK` ou `response()->json(false)`) para a Meta a fim de prevenir penalidades de timeout e loops de retentativa.

### 5. Proteção de Rate Limiting
- Os limites da API Meta são calculados por App ou por Page. Implemente a proteção de rate limiting usando o wrapper de cache Redis do Laravel antes de fazer requisições:
  ```php
  use Illuminate\Support\Facades\Redis;

  // Exemplo: Restringe a 200 chamadas por página por hora
  Redis::throttle("meta-api:{$pageId}")
      ->allow(200)
      ->every(3600)
      ->then(function () use ($endpoint, $payload) {
          return $this->sendRequest($endpoint, $payload);
      }, function () {
          // Devolve o job para a fila com backoff
          throw new RateLimitExceededException();
      });
  ```

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Nunca Faça Hardcode de Segredos:** Nunca faça hardcode de credenciais, access tokens, app IDs ou segredos de webhook. Sempre obtenha-os de arquivos `config()` apoiados por variáveis `.env` seguras.
- **Processamento Assíncrono de Webhook:** Nunca faça operações pesadas de payload (ex: análise, respostas de comentários, requisições a APIs externas) dentro da thread da requisição de webhook. Sempre transfira para uma fila.
- **Requisições Idempotentes:** Use operações transacionais e logs ao despachar jobs de publicação para prevenir posts duplicados em caso de quedas temporárias de rede.
- **Transparência de Erros:** Garanta que todas as exceções do cliente HTTP sejam registradas com contexto (endpoint, payload e mensagens de erro), mas não subam sem tratamento para as camadas de controller. Envolva-as em respostas de array previsíveis.
