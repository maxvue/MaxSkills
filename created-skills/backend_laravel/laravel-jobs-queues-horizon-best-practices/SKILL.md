---
name: laravel-jobs-queues-horizon-best-practices
description: >-
  Use when creating, reviewing, debugging, or refactoring Laravel queue Jobs,
  configuring queue connections or Horizon supervisors, handling job failures and
  retry policies, setting backoff strategies, defining timeouts, or optimizing
  background task performance. Triggers on Job dispatch, queue assignment via
  onQueue(), retry/backoff configuration, failed() callback implementation,
  Horizon supervisor tuning, rate-limit protection for external APIs (Gemini,
  WhatsApp, EFI), idempotency guards against duplicate processing, and
  integration with the HasAgentAiRequest trait for AI agent Jobs.
---

# Laravel Jobs, Queues & Horizon — Best Practices

## Goal

Provide standardized, safe, and resilient guidelines for creating, maintaining, and monitoring asynchronous Jobs in the Laravel framework, with queues supervised by Horizon. This skill ensures that all Jobs in the Engeapp ecosystem follow consistent patterns for retry policies, backoff strategies, timeout management, failure handling, queue assignment, and integration with AI agents.

## Instructions

### 1. Job Skeleton — Required Structure

Every Job **MUST** follow this minimal skeleton:

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class MyExampleJob implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    /** @var array<int, int> */
    public array $backoff = [30, 60, 120];

    public int $timeout = 120;

    public function __construct(
        public string $model_id,
    ) {}

    public function handle(): void
    {
        // Job logic here
    }

    public function failed(?\Throwable $exception): void
    {
        // Failure handling here
    }
}
```

**Mandatory properties:**

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `$tries` | `int` | Maximum number of execution attempts | `3` |
| `$backoff` | `array<int, int>` | Wait time (seconds) between each retry | `[30, 60, 120]` |
| `$timeout` | `int` | Maximum execution time in seconds | `120` |

### 2. Retry & Backoff Strategy

Choose the retry strategy based on the Job's external dependency:

| Scenario | `$tries` | `$backoff` | Rationale |
|----------|----------|------------|-----------|
| **WhatsApp API** (rate-limited) | `3` | `[5, 15, 30]` | Short intervals — API recovers quickly |
| **AI/LLM calls** (Gemini, OpenAI) | `5` | `[60, 120, 300, 600]` | Long intervals — rate limits reset slowly |
| **Webhook processing** (Trello, EFI) | `3` | `[30, 60, 120]` | Standard — moderate retry window |
| **Internal tasks** (calculations, sync) | `3` | `[10, 30, 60]` | Fast recovery — no external dependency |
| **Email/Notification** | `3` | `[15, 30, 60]` | Brief wait for transient SMTP failures |

**Rules:**
1. **NEVER** set `$tries = 0` — always allow at least 1 attempt.
2. **ALWAYS** define `$backoff` as an explicit array, not a single integer — this creates **exponential backoff**.
3. For AI-intensive Jobs, use the pattern from `GeminiContentJob`: `$tries = 5` with `$backoff = [60, 120, 300, 600]`.

### 3. Timeout Management

The `$timeout` property defines the maximum seconds a single attempt can run before being killed.

**Timeout Guidelines:**

| Job Type | Recommended `$timeout` | Reference |
|----------|----------------------|-----------|
| Simple DB operations | `60–120` | `AnalyzeProtocolJob` (120s) |
| Document processing | `120` | `ProcessDocumentReaderJob` (120s) |
| AI agent execution (tool-based) | `300–600` | `BrowserAiJob` (dynamic via `timeout()`) |
| AI computation (heavy) | `400` | `CalculateAiCircuitsJob`, `SupportMessageAiJob` |
| External API integration | `120–200` | `WebhookWhatsappJobExecuteJob` (200s) |
| Deploy/DevOps | `400` | `DeployJob` |

**Dynamic timeout pattern** (use when timeout varies per instance):

```php
public function timeout(): int
{
    return $this->browserAutomation?->timeout ?? 600;
}
```

**Critical Rule:** The Job's `$timeout` **MUST** be less than or equal to the Horizon supervisor's `timeout`. If the supervisor kills the process first, the Job silently disappears without triggering `failed()`.

### 4. Queue Assignment

The Engeapp ecosystem uses **5 named queues** managed by Horizon supervisors:

| Queue | Supervisor | Purpose | Jobs |
|-------|-----------|---------|------|
| `default` | `general-supervisor` | General-purpose tasks | Most Jobs |
| `whatsapp` | `whatsapp-supervisor` | WhatsApp message sending | `SendMessageWhatsappJob` |
| `gemini` | `gemini-supervisor` | AI/LLM processing | `ProcessDocumentReaderJob`, `ExtractFileDataAiJob` |
| `scout` | `scout-supervisor` | Search index updates | Scout/Meilisearch |
| `webhooks` | `webhooks-supervisor` | External webhook processing | Webhook Jobs |

**How to assign a queue:**

```php
// Option 1: In the constructor (preferred for dedicated-queue Jobs)
public function __construct(public string $message_id)
{
    $this->onQueue('whatsapp');
}

// Option 2: At dispatch time (preferred for flexible Jobs)
MyJob::dispatch($data)->onQueue('gemini');
```

**Rules:**
1. All AI/LLM Jobs **MUST** use `->onQueue('gemini')` to prevent blocking the general queue.
2. WhatsApp Jobs **MUST** use `->onQueue('whatsapp')` — this queue has fixed concurrency (no auto-scaling).
3. If no queue is specified, Jobs default to the `default` queue.

### 5. The `failed()` Callback — Failure Handling

Every Job that produces visible side-effects **MUST** implement `failed()`:

```php
public function failed(?\Throwable $exception): void
{
    // 1. Reset any in-progress flags
    $model = MyModel::find($this->model_id);
    if ($model) {
        $model->processing = false;
        $model->save();
    }

    // 2. Notify the user via Reverb/WebSocket
    SystemOperationEvent::dispatch([
        'type'     => 'operation_failed',
        'model_id' => $this->model_id,
    ], $this->user_id);

    // 3. Update notification status (if applicable)
    $notification = Notification::find($this->notification_id);
    if ($notification) {
        app(NotificationService::class)->updateNotification($notification, [
            'title'    => 'Operation failed',
            'message'  => 'Error: ' . $exception?->getMessage(),
            'icon'     => 'material-symbols:error-rounded',
            'severity' => 'error',
        ]);
    }

    // 4. Log for debugging
    Log::channel('specific_channel')->error('Job failed', [
        'model_id' => $this->model_id,
        'error'    => $exception?->getMessage(),
    ]);
}
```

**The `failed()` checklist:**
- [ ] Reset any "processing" flags (`$model->calculating_ai = false`)
- [ ] Dispatch failure event via Reverb for the frontend
- [ ] Update notification if one was created at dispatch
- [ ] Log the error with structured context

### 6. Idempotency — Preventing Duplicate Processing

Jobs can be retried. They **MUST** be designed to handle re-execution safely:

```php
public function handle(): void
{
    $message = SupportMessage::findOrFail($this->message_id);

    // Guard: if already processed, skip silently
    if ($message->message_meta_id) {
        Log::channel('whatsapp')->info('Already sent, skipping retry', [
            'message_id' => $this->message_id,
        ]);
        return;
    }

    // Proceed with processing...
}
```

**Idempotency patterns:**
1. **Check-before-act:** Verify if the result already exists before processing (as above).
2. **Flag-based guard:** Use a boolean column (`$model->transcode`, `$model->calculating_ai`) to detect completion.
3. **Early return:** If the precondition is already met, `return` immediately without throwing.

### 7. AI Agent Jobs — Integration with `HasAgentAiRequest`

Jobs that execute AI agents via the Laravel aiSDK **MUST** use the `HasAgentAiRequest` trait:

```php
class MyAiJob implements ShouldQueue
{
    use HasAgentAiRequest, Queueable;

    public int $timeout = 400;
    public string $model = 'gemini-2.5-flash-lite';

    public function __construct(
        public string $model_id,
    ) {
        $this->max_calls = 3;
        $this->onQueue('gemini');
    }

    public function handle(): void
    {
        $target = MyModel::findOrFail($this->model_id);
        $agent = new AgentMyAgent($target);
        $this->execute($agent, "Execute task for: {$target->id}");
    }

    public function isDone(): bool
    {
        // Verify in the database that the agent's work is complete
        return MyModel::where('id', $this->model_id)
            ->whereNotNull('result_field')
            ->exists();
    }
}
```

**Key rules for AI Jobs:**
1. **ALWAYS** assign to the `gemini` queue: `$this->onQueue('gemini')`.
2. **ALWAYS** set `$timeout >= 300` — AI calls are inherently slow.
3. **ALWAYS** implement `isDone()` with a database check to verify completion.
4. **ALWAYS** set `$max_calls` to limit the do-while retry loop (default: `5`).
5. The `HasAgentAiRequest` trait handles **automatic model fallback** (`flash-lite → flash → pro`).

### 8. Horizon Configuration — Supervisor Reference

The current Horizon configuration for production:

| Supervisor | Queue | Balance | Min/Max Processes | Timeout | Tries |
|-----------|-------|---------|-------------------|---------|-------|
| `general-supervisor` | `default` | `auto` (size) | 2 / 20 | 120s | 3 |
| `webhooks-supervisor` | `webhooks` | `auto` (size) | 1 / 3 | 300s | default |
| `whatsapp-supervisor` | `whatsapp` | `false` (fixed) | 5 / 10 | 60s | 5 |
| `scout-supervisor` | `scout` | `auto` (size) | — / 28 | 120s | 5 |
| `gemini-supervisor` | `gemini` | `auto` (size) | — / 5 | 600s | 2 |

**Important alignment rules:**
1. Job `$timeout` **MUST** be ≤ supervisor `timeout`.
2. Job `$tries` **SHOULD** match or be ≤ supervisor `tries`.
3. If a Job requires more time than the supervisor allows, configure a dedicated supervisor.

### 9. Logging Strategy

Use dedicated log channels for traceability:

```php
Log::channel('whatsapp')->info('Message sent', ['id' => $this->message_id]);
Log::channel('gemini')->info('Agent completed', ['agent' => $agentName]);
Log::channel('efi')->error('Payment webhook failed', ['code' => $secure_code]);
Log::channel('trello')->info('Webhook received', ['type' => $type]);
Log::channel('agent_browser')->info('Automation started', ['id' => $automationId]);
Log::channel('ai_benchmarks')->info('BENCHMARK', ['model' => $this->model]);
```

**Rules:**
1. **ALWAYS** use a dedicated channel, not the default `Log::info()`.
2. **ALWAYS** pass structured context arrays, not concatenated strings.
3. **ALWAYS** log at `info` level for successful operations and `error` for failures.
4. For AI Jobs, `HasAgentAiRequest` automatically logs to the `gemini` channel — do not duplicate.

### 10. Soft Cancel Pattern

For long-running Jobs, implement a soft cancel check to allow user-initiated cancellation:

```php
public function handle(): void
{
    // Check if the user cancelled the operation
    if (! $this->project->calculating_ai) {
        return;
    }

    // Proceed with long-running operation...
}
```

This pattern is used by `CalculateAiCircuitsJob` to allow the user to cancel AI processing from the frontend.

### 11. Tags for Horizon Monitoring

Use `tags()` to make Jobs searchable in the Horizon dashboard:

```php
public function tags(): array
{
    return [
        'whatsapp',
        'whatsapp_message',
        'message_id:' . $this->message_id,
        $this->message_id,
    ];
}
```

## Constraints

- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
1. **NEVER** create a Job without both `$tries` and `$backoff` properties.
2. **NEVER** use `$this->delete()` inside `handle()` to suppress errors — let the retry mechanism work.
3. **NEVER** dispatch Jobs inside database transactions — the transaction may rollback but the Job is already queued.
4. **NEVER** set `$timeout` higher than the Horizon supervisor's `timeout` for the assigned queue.
5. **NEVER** pass Eloquent models directly to constructors when the model might be deleted before processing — use IDs instead and `findOrFail()` in `handle()`.
6. **NEVER** use `sleep()` inside Jobs to throttle API calls — use `$backoff` instead.
7. **NEVER** forget to implement `failed()` for Jobs that change visible state (UI flags, notifications).
8. **ALWAYS** make Jobs idempotent — safe to re-run without side effects.
9. **ALWAYS** use `Log::channel()` with structured context arrays.
10. **ALWAYS** assign AI Jobs to the `gemini` queue and WhatsApp Jobs to the `whatsapp` queue.
11. **ALWAYS** align Job `$timeout` with the Horizon supervisor timeout for the target queue.
12. **ALWAYS** implement soft cancel for user-facing long-running operations.
