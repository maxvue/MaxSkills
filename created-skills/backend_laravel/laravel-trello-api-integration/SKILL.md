---
name: laravel-trello-api-integration
description: Use when creating, maintaining, or debugging integrations with the Trello API (TrelloService), handling authentication (key, token), processing webhooks, fetching boards/lists/cards/attachments, or managing cards inside the Engeapp ecosystem.
---

# Boas Práticas de Integração com a API do Trello no Laravel

## Objetivo
Padronizar e gerenciar de forma robusta a integração com a API do Trello (via `TrelloService`), garantindo processamento resiliente de webhooks, cache inteligente de requisições, logging específico e comandos Artisan apropriados dentro do ecossistema de backend do Engeapp.

## Instruções

1. **Localização e Injeção do Serviço**:
   - Crie e mantenha o serviço de integração do Trello dentro de `app/Services/TrelloService.php`.
   - Use o namespace `App\Services`.
   - Injete as dependências necessárias (ex: HTTP Client, Cache) via construtor usando Constructor Property Promotion do PHP 8.

2. **Configuração e Credenciais**:
   - Carregue as credenciais da API do Trello (Key, Token e Board ID padrão) através de `config/services.php` ou `config/trello.php`.
   - Recupere os valores do `.env` usando as variáveis de ambiente: `TRELLO_API_KEY`, `TRELLO_API_TOKEN` e `TRELLO_BOARD_ID`.
   - Evite usar o helper `env()` fora dos arquivos de configuração.

3. **Rate Limiting da API e Estratégia de Cache**:
   - Evite o esgotamento do rate limit da API armazenando em cache operações de leitura (como boards, lists, cards e attachments) que não exigem estado em tempo real.
   - Use `Cache::remember` com um TTL padrão de 45 minutos (2700 segundos).
   - Construa chaves de cache consistentes, por exemplo: `trello:board:{board_id}:lists` ou `trello:card:{card_id}`.
   - Limpe ou invalide chaves de cache específicas ao mutar os recursos (ex: após atualizar ou deletar um card via API).

4. **Tratamento Robusto de Exceções e Logging**:
   - Capture falhas de requisição da API do Trello usando o `throw()` do HTTP Client ou verificando `$response->failed()`.
   - Lance exceções de domínio customizadas (ex: `TrelloApiException`) quando as requisições à API falharem.
   - Registre operações, erros e conteúdos de payload específicos do Trello usando o canal de log `trello` (`storage/logs/trello.log`).

5. **Webhooks e Jobs Assíncronos**:
   - **Verifique a assinatura do webhook ANTES de disparar qualquer job**: o Trello assina cada callback com o header `X-Trello-Webhook`, calculado como `base64(HMAC-SHA1(requestBody + callbackURL, apiSecret))`. Recalcule-o com o secret da aplicação e compare usando `hash_equals` (tempo constante). Rejeite com `401` em caso de divergência ou header ausente — nunca processe um payload não verificado.
   - Processe os payloads de webhook recebidos do Trello de forma assíncrona usando jobs em fila (ex: `App\Jobs\ProcessTrelloWebhookJob`).
   - Enfileire as mutações de saída (ex: criar um card ou enviar um attachment) usando jobs (ex: `App\Jobs\SyncToTrelloJob`) para evitar bloquear a thread da requisição HTTP.
   - Garanta que os jobs implementem a interface `ShouldQueue` e sigam os padrões do Horizon (ex: lógica de retry, timeouts e máximo de tentativas).

6. **Comandos Artisan**:
   - Implemente comandos Artisan para ações administrativas (ex: `RegisterTrelloWebhookCommand` e `SyncCardTrelloCommand`).
   - Siga as convenções padrão do Artisan do Laravel (ex: usar flags `--force`, saída de console estruturada e strings de descrição claras).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill está escrito.
- **Sem Mutações Síncronas em Controllers**: Não realize operações de escrita (criar/atualizar/deletar card) no Trello de forma síncrona dentro de HTTP Controllers. Delegue-as a Jobs em fila.
- **Sem API Keys ou Secrets Hardcoded**: Secrets nunca devem ser armazenados diretamente em repositórios de código; sempre leia a partir de arquivos de configuração.
- **Sem Saída Bruta de Exceções**: Nunca exiba exceções brutas ou tracebacks detalhados da API do Trello para o usuário final. Capture-os, registre no canal `trello` e retorne uma mensagem de erro limpa voltada ao usuário.
- **Sem URLs de Webhook Hardcoded**: As URLs de callback dos webhooks devem ser geradas dinamicamente usando rotas nomeadas (ex: `route('trello.webhook')`) e devem tratar a resolução de SSL/HTTPS.
- **Validação Estrita da Assinatura do Webhook**: Nunca processe um webhook do Trello sem verificar o header `X-Trello-Webhook` (`base64(HMAC-SHA1(requestBody + callbackURL, apiSecret))`). Sempre compare com `hash_equals()` para comparação em tempo constante e rejeite requisições não verificadas com `401` antes de disparar qualquer job.

## Exemplos

### Exemplo: Verificação da assinatura do webhook (antes de disparar o job)
O Trello assina cada callback com o header `X-Trello-Webhook`, calculado como `base64(HMAC-SHA1(requestBody + callbackURL, apiSecret))`. Verifique-o com `hash_equals` e só então dispare o job em fila.

```php
public function handle(Request $request): Response
{
    $signature = $request->header('X-Trello-Webhook');
    $secret = config('services.trello.secret'); // TRELLO_API_SECRET

    // O Trello envia um HEAD/GET vazio para confirmar o webhook no registro.
    if ($request->isMethod('head') || $request->isMethod('get')) {
        return response('', 200);
    }

    if (empty($signature) || empty($secret)) {
        return response('Unauthorized', 401);
    }

    $callbackUrl = route('trello.webhook'); // deve corresponder ao callbackURL registrado
    $computed = base64_encode(hash_hmac('sha1', $request->getContent() . $callbackUrl, $secret, true));

    if (! hash_equals($computed, $signature)) {
        Log::channel('trello')->warning('Invalid Trello webhook signature.');
        return response('Unauthorized', 401);
    }

    ProcessTrelloWebhookJob::dispatch($request->json()->all());

    return response('Webhook processed successfully', 200);
}
```

### Exemplo: Implementação do TrelloService
```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use App\Exceptions\TrelloApiException;
use Throwable;

class TrelloService
{
    protected string $key;
    protected string $token;
    protected string $baseUrl = 'https://api.trello.com/1';

    public function __construct()
    {
        $this->key = config('services.trello.key');
        $this->token = config('services.trello.token');

        if (empty($this->key) || empty($this->token)) {
            Log::channel('trello')->error('Trello API key or token is not configured.');
        }
    }

    /**
     * Busca os detalhes de um card por ID com cache.
     *
     * @param string $cardId
     * @return array
     * @throws TrelloApiException
     */
    public function getCard(string $cardId): array
    {
        $cacheKey = "trello:card:{$cardId}";

        return Cache::remember($cacheKey, now()->addMinutes(45), function () use ($cardId) {
            try {
                $response = Http::get("{$this->baseUrl}/cards/{$cardId}", [
                    'key' => $this->key,
                    'token' => $this->token,
                ]);

                if ($response->failed()) {
                    throw new TrelloApiException("Failed to fetch Trello card: {$cardId}. HTTP Status: " . $response->status());
                }

                return $response->json();
            } catch (Throwable $e) {
                Log::channel('trello')->error("Error fetching card {$cardId}", [
                    'message' => $e->getMessage(),
                    'trace' => $e->getTraceAsString(),
                ]);

                throw new TrelloApiException("Trello communication failure.", 0, $e);
            }
        });
    }

    /**
     * Cria um card em uma list.
     *
     * @param string $listId
     * @param array $data
     * @return array
     * @throws TrelloApiException
     */
    public function createCard(string $listId, array $data): array
    {
        try {
            $response = Http::post("{$this->baseUrl}/cards", array_merge($data, [
                'idList' => $listId,
                'key' => $this->key,
                'token' => $this->token,
            ]));

            if ($response->failed()) {
                throw new TrelloApiException("Failed to create Trello card. HTTP Status: " . $response->status());
            }

            $card = $response->json();

            // Limpa o cache de cards do board para manter as lists sincronizadas
            Cache::forget("trello:board:" . config('services.trello.board_id') . ":cards");

            return $card;
        } catch (Throwable $e) {
            Log::channel('trello')->error("Error creating card in list {$listId}", [
                'data' => $data,
                'message' => $e->getMessage(),
            ]);

            throw new TrelloApiException("Failed to perform Trello card creation.", 0, $e);
        }
    }
}
```
