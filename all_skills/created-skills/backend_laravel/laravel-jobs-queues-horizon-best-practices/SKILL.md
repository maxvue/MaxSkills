---
name: laravel-jobs-queues-horizon-best-practices
description: "Use when creating, reviewing, or debugging queue Jobs, Horizon supervisors, retries, backoff strategies, timeouts, API rate limiting, idempotency guards, and HasAgentAiRequest trait in Engeapp Laravel backend."
author: Johnattas Conrady Gomes Santana
---
# Laravel Jobs, Queues & Horizon — Boas Práticas

## Objetivo

Fornecer diretrizes padronizadas e resilientes para criar, manter e monitorar Jobs assíncronos no framework Laravel 13 / PHP 8.4, com filas supervisionadas pelo Horizon no ecossistema Engeapp. Garante consistência em retry, backoff, timeout, idempotência e integração com agentes de IA (`HasAgentAiRequest`).

## Instruções

### 1. Esqueleto de Job Obrigatório

Todo Job deve implementar `ShouldQueue`, usar `Queueable`, declarar `$tries`, `$backoff`, `$timeout` e o método `failed()`:

```php
namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class MyExampleJob implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;
    public array $backoff = [30, 60, 120];
    public int $timeout = 120;

    public function __construct(public string $model_id) {}

    public function handle(): void
    {
        // Lógica do Job
    }

    public function failed(?\Throwable $exception): void
    {
        // Tratamento de falha e notificações
    }
}
```

### 2. Retry & Backoff

Defina a estratégia com base na dependência externa:

| Cenário | `$tries` | `$backoff` | Justificativa |
|---|---|---|---|
| **API WhatsApp** | `5` | `[30, 60, 120, 180, 300]` | Padrão `SendMessageWhatsappJob`, alinhado ao `whatsapp-supervisor` |
| **Chamadas IA / LLM** | `5` | `[60, 120, 300, 600]` | Intervalos longos para reset de rate limits da API |
| **Webhooks (Trello, EFI)** | `3` | `[30, 60, 120]` | Janela moderada de reprocessamento |
| **Tarefas Internas / Sync** | `3` | `[10, 30, 60]` | Recuperação rápida sem dependência de terceiros |
| **Email / Notificações** | `3` | `[15, 30, 60]` | Espera breve para falhas transitórias SMTP |

- **Regra:** Sempre use array explícito para `$backoff` (ou método `backoff(): array`). O `$tries` do Job prevalece sobre o padrão do supervisor.

### 3. Timeout e Alinhamento com Horizon

O `$timeout` do Job **DEVE ser menor ou igual** ao timeout do supervisor do Horizon para evitar término abrupto sem acionamento do `failed()`.

| Tipo de Job | `$timeout` | Supervisor / Timeout | Exemplo |
|---|---|---|---|
| Tarefas Gerais / Sync | `60–120s` | `general-supervisor` (120s) | `ProcessDocumentReaderJob` (120s) |
| Webhooks | `120–200s` | `webhooks-supervisor` (300s) | `WebhookWhatsappJobExecuteJob` (200s) |
| WhatsApp Envio | `30–60s` | `whatsapp-supervisor` (60s) | `SendMessageWhatsappJob` |
| Busca / Scout | `60–120s` | `scout-supervisor` (120s) | Atualização de índices Meilisearch |
| IA / LLM (Pesado) | `240–600s` | `gemini-supervisor` (600s) | `CopywriterJob` (240s), `BrowserAiJob` (até 600s) |

```php
// Timeout dinâmico quando aplicável:
public function timeout(): int
{
    return $this->browserAutomation?->timeout ?? 600;
}
```

### 4. Atribuição de Fila

- **IA / LLM:** Sempre `->onQueue('gemini')`.
- **WhatsApp:** Sempre `->onQueue('whatsapp')` (concorrência fixa).
- **Webhooks:** Sempre `->onQueue('webhooks')`.
- **Geral:** Fila `default` (padrão quando não especificado).

```php
// No construtor (preferencial para fila fixa)
public function __construct(public string $messageId) {
    $this->onQueue('whatsapp');
}
```

### 5. Idempotência e Tratamento de Falhas (`failed()`)

Todo Job deve ser reexecutável com segurança:
1. **Early Return:** Verifique se o resultado já existe (`if ($message->message_meta_id) return;`) antes de reprocessar.
2. **Callback `failed()`:** Resete flags de processamento no model, notifique o frontend via WebSocket/Reverb (`SystemOperationEvent`) e logue no canal dedicado.

```php
public function failed(?\Throwable $exception): void
{
    MyModel::where('id', $this->model_id)->update(['processing' => false]);
    Log::channel('gemini')->error('Job falhou', ['id' => $this->model_id, 'err' => $exception?->getMessage()]);
}
```

### 6. Jobs de IA com `HasAgentAiRequest`

Jobs que executam agentes de IA via aiSDK devem usar o trait `HasAgentAiRequest`:

```php
class MyAiJob implements ShouldQueue
{
    use HasAgentAiRequest, Queueable;

    public int $timeout = 400;
    public string $model = 'gemini-3.5-flash';

    public function __construct(public string $model_id)
    {
        $this->max_calls = 3;
        $this->onQueue('gemini');
    }

    public function handle(): void
    {
        $target = MyModel::findOrFail($this->model_id);
        $agent = new AgentMyAgent($target);
        $this->execute($agent, "Executar tarefa para: {$target->id}");
    }

    public function isDone(): bool
    {
        return MyModel::where('id', $this->model_id)->whereNotNull('result_field')->exists();
    }
}
```

- **Fallback automático de modelo:** Em falhas transitórias, o trait faz fallback na cadeia: `gemini-3.1-flash-lite → gemini-2.5-flash → gemini-3.5-flash → gemini-2.5-pro`.

### 7. Soft Cancel e Logging Estruturado

- **Soft Cancel:** Em jobs longos de IA, cheque flags de cancelamento do usuário (`if (! $project->calculating_ai) return;`).
- **Logs dedicados:** Use canais específicos (`Log::channel('whatsapp')`, `Log::channel('gemini')`, `Log::channel('efi')`, `Log::channel('trello')`) com contexto estruturado em array.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR).
- **NUNCA** use `$this->delete()` dentro de `handle()` para suprimir erros — use o mecanismo de retry e `failed()`.
- **NUNCA** faça dispatch de Jobs dentro de transações de banco de dados sem `afterCommit` — use `ShouldHandleEventsAfterCommit` ou despache pós-commit.
- **NUNCA** passe instâncias Eloquent pesadas ou sujeitas a deleção no construtor — passe IDs e resolva com `findOrFail()` no `handle()`.
- **NUNCA** use `sleep()` bloqueante para rate limiting dentro do worker — controle com `$backoff` ou middleware de rate limiting.
