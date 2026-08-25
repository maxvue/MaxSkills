---
name: laravel-meta-graph-api-integration-best-practices
description: "Use when implementing or debugging Meta Graph API (Instagram/Facebook) in Engeapp: publishing photos, reels, carousels via media containers, comments, insights, MetaService, and MetaWebhookJob. Covers objectives, architectural structure, and Meta API endpoints."
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer diretrizes arquiteturais para integrar a Graph API da Meta (Facebook e Instagram) no engeapp usando Laravel 13, fiéis ao módulo real em `App\Services\SocialMedia\Meta`. Cobre a façade de serviço, a camada de transporte HTTP, os fluxos de publicação assíncrona de mídia e a validação de webhooks de entrada.

## Instruções

### 1. Estrutura Arquitetural
- **Padrão Service Façade:** Encapsule a comunicação com a API dentro de `MetaService` (`app/Services/SocialMedia/Meta/MetaService.php`). Cada instância é amarrada a uma credencial persistida (`App\Models\Calendar\SocialMediaCredential`) ou ao token global de config.
- **Handlers por responsabilidade:** O `MetaService` expõe três handlers públicos em `app/Services/SocialMedia/Meta/Handlers/`:
  - `PublishHandler` (`$service->publish`): criação de container, publicação e posts de Página.
  - `CommentHandler` (`$service->comment`): recuperar, responder, ocultar ou deletar comentários.
  - `MediaHandler` (`$service->media`): dados da postagem, insights e remoção quando suportada.
- **Camada de Transporte HTTP:** Use a trait `MetaRequestTrait` (`MetaRequestTrait.php`) que encapsula o cliente `Http` do Laravel. Ela:
  - Monta a URL versionada em `buildUrl()`: `$this->base_url . 'v' . $version . '/' . $endpoint` (ex.: `https://graph.facebook.com/v24.0/...`).
  - Alterna a `base_url` com um único teste de prefixo: se o token começa com `IG` (Instagram Login), usa `https://graph.instagram.com/`; caso contrário (fallback padrão, cobrindo tokens `EAA`/Graph clássico e qualquer outro formato), usa `https://graph.facebook.com/`.
  - Autentica via `Http::withToken($this->token)->acceptJson()`.
  - Normaliza erros: retorna sempre um array; em falha de transporte ou credencial ausente devolve `['error' => ...]` e registra via `Log::error()`/`Log::warning()`, sem lançar exceção para os handlers.

### 2. Origem do Token e da Versão
O módulo **consome um access token já persistido** — não há fluxo OAuth de troca de token curto→longo nem chamadas a `/oauth/access_token` ou `/me/accounts` no projeto. O `laravel/socialite` já existe no engeapp (`composer.json`) e está em uso ativo em `App\Http\Controllers\Auth\SocialiteController`, mas apenas para login social do usuário (Google/Facebook) — não para obter ou renovar tokens da Graph API consumidos pelo `MetaService`. Resolva o token assim:
- **Token global (single-tenant):** `config('api.meta_token')` (env `META_TOKEN`, em `config/api.php`).
- **Versão da Graph API:** `config('api.meta_graph_version', '24.0')` (env `META_GRAPH_VERSION`).
- **Por credencial:** `MetaService::forCredential(SocialMediaCredential $credential)` usa `$credential->access_token` e `$credential->external_account_id`.
- **Por empresa:** `MetaService::forCompany(string $solarCompanyId, string $apiName)` resolve a credencial ativa (`is_active`) da empresa para a API do catálogo `EventApi` (ex.: `"Instagram"`) e recai sobre `config('api.meta_token')` quando não há credencial cadastrada; retorna `null` se nenhuma autenticação estiver disponível.
- **Segurança do Token:** Armazene access tokens no banco (`SocialMediaCredential->access_token`) e nunca exponha tokens crus ao frontend. Não coloque tokens em `.env` versionado nem hardcode no código.

> Se um fluxo OAuth de troca/renovação de token da Graph API (curto→longo, `/oauth/access_token`, `/me/accounts`) vier a ser necessário, ele **ainda não existe** neste projeto — trate-o como novo recurso a ser construído, não como padrão vigente. Isso não se confunde com o Socialite já usado para login social do usuário.

### 3. Fluxos de Publicação de Mídia (`PublishHandler`)
- **Instagram — imagem única:** `createImageContainer($imageUrl, $caption)` faz `POST {ig-user-id}/media` com `image_url`/`caption`; depois `publishContainer($creationId)` em `{ig-user-id}/media_publish`.
- **Instagram — Reels:** `createReelsContainer($videoUrl, $caption)` faz `POST {ig-user-id}/media` com `media_type => 'REELS'` e `video_url`. Antes de publicar, faça polling via `getContainerStatus($containerId)` (`GET {container-id}` com `fields => 'status_code,status'`) até `status_code` chegar a `FINISHED`; trate `ERROR`.
- **Instagram — carrossel:**
  1. `createCarouselItem($imageUrl)` para cada filho (`is_carousel_item => true`, sem legenda).
  2. Aguarde todos os filhos ficarem `FINISHED`.
  3. `createCarouselContainer($childrenIds, $caption)` monta o container-pai (`media_type => 'CAROUSEL'`, `children` = IDs separados por vírgula).
  4. `publishContainer($creationId)` publica o pai.
- **Página do Facebook (post direto):**
  - `publishFacebookPhoto($imageUrl, $message)`: `POST {page-id}/photos` com `url` (e `message` opcional).
  - `publishFacebookFeed($message, $link)`: `POST {page-id}/feed` com `message` (e `link` opcional).
- Todo payload usa `array_filter(...)` para omitir campos nulos (ex.: legenda ausente).

### 4. Configuração e Validação de Webhook (`MetaWebhookController`)
Controller real: `app/Http/Controllers/Api/SocialMedia/MetaWebhookController.php` (método único `index`).
- **Verificação de Challenge (GET):** Confira o token contra `config('api.meta_webhook_token')` (env `META_WEBHOOK_TOKEN`, definido em `config/api.php`) — **não** existe `config('services.facebook.webhook_verify_token')`. Retorne o `hub_challenge` como inteiro, ou `403` em token inválido:
  ```php
  if ($request->isMethod('get') && $request->has('hub_challenge')) {
      $token = config('api.meta_webhook_token');

      if ($request->input('hub_verify_token') === $token) {
          return response((int) $request->input('hub_challenge'), 200);
      }

      return response('Token inválido', 403);
  }
  ```
- **Tratamento de Eventos (POST):**
  - Persista o payload cru no model `App\Models\Webhook\Webhook` para auditoria (`payload`, `parameters`, `ip`, `route_name`).
  - Despache o processamento para a fila: `MetaWebhookJob::dispatch($webhook->id)->onQueue('webhooks')`.
  - Responda de imediato com `response()->json(false)` para não estourar o timeout da Meta e evitar loops de retentativa.

### 5. Rate Limiting (orientação genérica — sem implementação no projeto)
Os limites da Graph API são por App ou por Página. **Este módulo ainda não implementa proteção de rate limiting** (não há `Redis::throttle` nem exceção dedicada no código). Ao adicionar, siga o padrão da stack real:
- Trate a resposta de erro da Meta (códigos de rate limit) já normalizada pela `MetaRequestTrait` (`['error' => ...]`) e reprograme o job com backoff usando os mecanismos nativos de fila do Laravel (`release()`/`backoff`).
- Se optar por um throttle proativo com Redis, baseie-o no cliente Redis já usado no projeto e defina a exceção/estratégia explicitamente — não presuma classes existentes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR), independentemente do idioma do corpo desta skill.
- **Nunca Faça Hardcode de Segredos:** Nunca faça hardcode de access tokens, app IDs ou tokens de webhook. Obtenha-os sempre de `config()` (`config/api.php`) apoiado por `.env`.
- **Processamento Assíncrono de Webhook:** Nunca execute operações pesadas (parsing, respostas de comentário, chamadas externas) na thread da requisição de webhook. Sempre delegue à fila (`MetaWebhookJob` em `->onQueue('webhooks')`).
- **Transparência de Erros:** Registre exceções do cliente HTTP com contexto (endpoint, método, mensagem), mas não as propague sem tratamento aos controllers — devolva o array previsível `['error' => ...]`, como faz a `MetaRequestTrait`.
- **Comentários de código em pt-BR.**
