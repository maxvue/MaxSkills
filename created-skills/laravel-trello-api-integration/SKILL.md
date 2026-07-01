---
name: laravel-trello-api-integration
description: Use when creating, maintaining, or debugging integrations with the Trello API (TrelloService), handling authentication (key, token), processing webhooks, fetching boards/lists/cards/attachments, or managing cards inside the Engeapp ecosystem.
---

# Laravel Trello API Integration Best Practices

## Goal
Standardize and robustly manage the integration with the Trello API (via `TrelloService`), ensuring resilient webhook processing, smart request caching, specific logging, and proper Artisan commands within the Engeapp backend ecosystem.

## Instructions

1. **Service Location & Injection**:
   - Create and maintain the Trello integration service inside `app/Services/TrelloService.php`.
   - Use the `App\Services` namespace.
   - Inject required dependencies (e.g., HTTP Client, Cache) via the constructor using PHP 8 Constructor Property Promotion.

2. **Configuration & Credentials**:
   - Load Trello API credentials (Key, Token, and default Board ID) through `config/services.php` or `config/trello.php`.
   - Retrieve values from `.env` using environment variables: `TRELLO_API_KEY`, `TRELLO_API_TOKEN`, and `TRELLO_BOARD_ID`.
   - Avoid using the `env()` helper outside of configuration files.

3. **API Rate Limiting & Cache Strategy**:
   - Prevent API rate limit exhaustion by caching read operations (such as boards, lists, cards, and attachments) that do not require real-time state.
   - Use `Cache::remember` with a default TTL of 45 minutes (2700 seconds).
   - Construct consistent cache keys, for example: `trello:board:{board_id}:lists` or `trello:card:{card_id}`.
   - Clear or invalidate specific cache keys when mutating the resources (e.g., after updating or deleting a card via the API).

4. **Robust Exception Handling & Logging**:
   - Catch Trello API request failures using the HTTP Client's `throw()` or by checking `$response->failed()`.
   - Throw custom domain exceptions (e.g., `TrelloApiException`) when API requests fail.
   - Log Trello-specific operations, errors, and payload contents using the `trello` log channel (`storage/logs/trello.log`).

5. **Asynchronous Webhooks & Jobs**:
   - Process incoming Trello webhook payloads asynchronously using queued jobs (e.g., `App\Jobs\ProcessTrelloWebhookJob`).
   - Queue outgoing mutations (e.g., creating a card or uploading an attachment) using jobs (e.g., `App\Jobs\SyncToTrelloJob`) to avoid blocking the HTTP request thread.
   - Ensure jobs implement the `ShouldQueue` interface and follow Horizon standards (e.g., retry logic, timeouts, and max attempts).

6. **Artisan Commands**:
   - Implement Artisan commands for administrative actions (e.g., `RegisterTrelloWebhookCommand` and `SyncCardTrelloCommand`).
   - Follow standard Laravel Artisan conventions (e.g., using `--force` flags, structured console output, and clear description strings).

## Constraints
- **No Synchronous Mutations in Controllers**: Do not perform write operations (create/update/delete card) to Trello synchronously inside HTTP Controllers. Offload them to queued Jobs.
- **No Hardcoded API Keys or Secrets**: Secrets must never be stored directly in code repositories; always read from configuration files.
- **No Raw Exception Output**: Never display detailed Trello API raw exceptions or tracebacks to the end-user. Catch them, log to the `trello` channel, and return a clean user-facing error message.
- **No Hardcoded Webhook URLs**: Webhook callback URLs must be generated dynamically using named routes (e.g., `route('trello.webhook')`) and must handle SSL/HTTPS resolution.

## Examples

### Example: TrelloService implementation
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
     * Fetch a card's details by ID with caching.
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
     * Create a card on a list.
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

            // Clear board list cache to keep lists synchronized
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
