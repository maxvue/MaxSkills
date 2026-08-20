---
name: laravel-trello-api-integration
description: "Use when maintaining or debugging Trello API integration in Engeapp (TrelloService), reading config/api.php, handling webhooks via ProcessTrelloWebhookJob, and running trello Artisan commands. Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
---
# Integração com a API do Trello no Laravel (engeapp)

## Objetivo
Padronizar a integração com a API do Trello via `App\Services\TrelloService`, cobrindo credenciais, leitura de boards/lists/cards/anexos, recebimento de webhook e os commands Artisan reais do projeto.

> **Estado atual (Fase 1 desativada):** No engeapp, `getFileForAttachment`, `putData`, `postData`, `ProcessTrelloWebhookJob::handle` e `SyncToTrelloJob::handle` estão com o corpo comentado e retornam cedo com o marcador `// [Trello API] Execução cancelada na Fase 1`. `getData`, `syncMediaForAttachment` e `SyncCardTrello::handle` estão ATIVOS e funcionais. A arquitetura (classes, assinaturas, credenciais) já existe e é a verdade-base desta skill; ao reativar os métodos desativados, **descomente** os corpos existentes em vez de reescrever do zero.

## Instruções

1. **Serviço e credenciais**:
   - O serviço vive em `app/Services/TrelloService.php`, namespace `App\Services`. `baseUrl` = `https://api.trello.com/1/`.
   - As credenciais são lidas no construtor a partir de `config/api.php`:
     - `config('api.trello_key')` → env `TRELLO_KEY`
     - `config('api.trello_token')` → env `TRELLO_TOKEN`
     - `config('api.trello_secret')` → env `TRELLO_SECRET` (usado apenas se/quando verificação de assinatura for adicionada; hoje não é consumido)
   - **Não existe** `config('services.trello.*)` nem `config/trello.php`. Não use os nomes `TRELLO_API_KEY`/`TRELLO_API_TOKEN`/`TRELLO_BOARD_ID` — eles não existem no projeto.
   - Chame `env()` apenas dentro de `config/api.php`; no código, use `config('api.*')`.

2. **Board padrão (sem config)**:
   - Não há chave de config para o board. O board padrão é o **default do parâmetro** dos métodos: `'66e9d8c95de15659b72aac72'` (veja `getListsForBoard`, `getCardsForBoard`, `getCard`).
   - Ao precisar de outro board, passe o id explicitamente; não invente `config('...board_id')`.

3. **Requisições e autenticação**:
   - Leituras passam por `getData(string $route, array $others = [])`, que injeta `key` e `token` como query params (`['key' => $this->key, 'token' => $this->token, ...$others]`) e faz `Http::get($this->baseUrl . $route, $data)`.
   - Mutações passam por `putData`/`postData`, que injetam `key`/`token` no payload.
   - O download de anexo (`getFileForAttachment`/`syncMediaForAttachment`) usa header OAuth: `Authorization: OAuth oauth_consumer_key="{key}", oauth_token="{token}"`.
   - Métodos públicos reais: `getCardsData`, `getListForCard`, `getListsForBoard`, `getList`, `getAttachmentsForCard`, `getAttachmentForCard`, `getFileForAttachment`, `syncMediaForAttachment`, `getMembersForCard`, `getCardsForBoard`, `getCard`, `getActionsOnCard`, `getCheckList`, `updateCardData`, `moveCardList`, `archiveCard`, `addComment`, `updateCheckItemState`, `registerWebhook`.

4. **Tratamento de erros e logging**:
   - O padrão real é `try/catch (\Throwable)` e **retornar vazio/null** (`return []` / `return null`) — não há exceção de domínio como `TrelloApiException` no projeto. Não referencie classes de exceção inexistentes.
   - **Onde há log e onde não há:** hoje o único log que executa no canal `trello` é `Log::channel('trello')->error('Erro ao baixar anexo do Trello', ...)`, no catch de `syncMediaForAttachment` (método ativo). O `getData` (leituras) tem catch **silencioso** — só `return []`, sem log. Os logs de `putData`/`postData` (`Log::channel('trello')->error('Erro no putData/postData do Trello', ...)`) existem apenas dentro dos blocos comentados da Fase 1 e são o contrato previsto ao reativar — não descreva como comportamento atual.
   - O canal `trello` está definido em `config/logging.php` (path `storage_path('logs/trello.log')`). Use-o para toda operação, erro e payload do Trello.

5. **Webhook (recebimento)**:
   - Rota (não nomeada): `Route::match(['head', 'post'], '/webhooks/trello', [TrelloWebhookController::class, 'handle'])` em `routes/api.php` → URL pública `/api/webhooks/trello`.
   - `App\Http\Controllers\Api\TrelloWebhookController@handle`: se `$request->isMethod('HEAD')` responde `200` vazio (o Trello confirma o webhook com HEAD ao registrar); caso contrário, despacha `ProcessTrelloWebhookJob::dispatch($request->all())` e retorna `'OK'` 200 imediatamente, para não bloquear a resposta.
   - **Atenção (segurança):** o controller atual **não** verifica assinatura do webhook. Se for endurecer a integração, o Trello assina cada callback no header `X-Trello-Webhook` como `base64(HMAC-SHA1(requestBody + callbackURL, secret))` e o secret disponível é `config('api.trello_secret')`; compare com `hash_equals()`. Isso é orientação genérica de hardening — **não está implementado hoje**, não descreva como se estivesse.

6. **Jobs assíncronos**:
   - `App\Jobs\ProcessTrelloWebhookJob` (recebe o payload do webhook) e `App\Jobs\SyncToTrelloJob` (recebe `string $action, array $data` para mutações de saída como `updateCard`/`moveCardList`).
   - Ambos usam `implements ShouldQueue` + `use Queueable` (estilo Laravel 12/13). Não há propriedades de retry/timeout customizadas no código atual — não invente configuração de Horizon que não existe.

7. **Commands Artisan (nomes reais)**:
   - `App\Console\Commands\RegisterTrelloWebhook` — signature `trello:register-webhook {board?}`, definido via atributos `#[Signature(...)]` / `#[Description(...)]`. Monta o callback como `config('app.url') . '/api/webhooks/trello'` e chama `$trelloService->registerWebhook(...)`.
   - `App\Console\Commands\SyncCardTrello` — signature `sync:cards-trello {--limit=} {--clear} {--no-file}` (carga massiva de cards para o Planner). Usa `$signature`/`$description` como propriedades.
   - **Não** existem classes com sufixo `Command` (`RegisterTrelloWebhookCommand`/`SyncCardTrelloCommand`).

8. **Cache (onde realmente existe)**:
   - O `TrelloService` **não usa Cache** em nenhum método. Não descreva cache dentro do serviço nem chaves como `trello:card:{id}`.
   - O único cache real está no command `SyncCardTrello`, que faz **quatro** `Cache::remember`, todas com TTL de 45 min (`now()->addMinutes(45)`) e chave em notação por ponto:
     - `'trello.all_cards.board'` → `$trelloService->getCardsForBoard()`
     - `'trello.card.actions.' . $card->trello_id` → `$trelloService->getActionsOnCard(...)`
     - `'trello.checklist.' . $check_list_id` → `$trelloService->getCheckList(...)`
     - `'trello.card.attachments.' . $card->trello_id` → `$trelloService->getAttachmentsForCard(...)`
   - Se precisar cachear leituras, siga esse padrão (chave única por ponto + TTL de 45 min) no chamador, nunca dentro do serviço.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código em pt-BR.
- **Sem mutações síncronas em controllers**: não faça escrita (criar/atualizar/mover/arquivar card) direto no controller HTTP; delegue a `SyncToTrelloJob` (ou outro job em fila).
- **Sem secrets hardcoded**: leia sempre de `config('api.*')`; nunca coloque key/token/secret no código.
- **Callback do webhook**: monte a URL a partir de `config('app.url')` + `/api/webhooks/trello` (padrão do `RegisterTrelloWebhook`), pois a rota não é nomeada — não use `route('trello.webhook')`.
- **Não fabrique**: não referencie `config/services.php`/`config/trello.php`, envs `_API_`, `TrelloApiException`, verificação de assinatura ativa ou cache no serviço — nada disso existe no engeapp.

## Exemplos

### Padrão de leitura do serviço (real, `TrelloService`)
```php
class TrelloService
{
    protected string $baseUrl = 'https://api.trello.com/1/';
    protected string $key;
    protected string $token;

    public function __construct()
    {
        $this->key = config('api.trello_key');
        $this->token = config('api.trello_token');
    }

    // Board padrão é o DEFAULT do parâmetro — não vem de config.
    public function getCardsForBoard(string $board_id = '66e9d8c95de15659b72aac72') : array
    {
        return $this->getData('boards/' . $board_id . '/cards');
    }

    private function getData(string $route, array $others = []) : array
    {
        $data = [
            'key'   => $this->key,
            'token' => $this->token,
            ...$others,
        ];

        try {
            $response = Http::withHeaders([])->get($this->baseUrl . $route, $data);
        }
        // Atenção: no getData REAL o catch é SILENCIOSO (só return []). Hoje quem loga no
        // canal `trello` é apenas syncMediaForAttachment; putData/postData só logarão
        // quando seus blocos comentados (Fase 1) forem reativados. Não adicione log aqui achando que existe.
        catch (\Throwable $e) {
            return [];
        }

        return toArray($response?->json());
    }
}
```
