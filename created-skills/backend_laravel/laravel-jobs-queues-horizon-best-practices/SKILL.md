---
name: laravel-jobs-queues-horizon-best-practices
description: "Use when creating, reviewing, debugging, or refactoring Laravel queue Jobs, configuring queue connections or Horizon supervisors, handling failures, retries, backoff, and timeouts, or optimizing background tasks. Triggers on Job dispatch, onQueue(), failed() callbacks, Horizon tuning, rate limiting for external APIs (Gemini, WhatsApp, EFI), idempotency guards, and the HasAgentAiRequest trait."
---

# Laravel Jobs, Queues & Horizon — Boas Práticas

## Objetivo

Fornecer diretrizes padronizadas, seguras e resilientes para criar, manter e monitorar Jobs assíncronos no framework Laravel, com filas supervisionadas pelo Horizon. Esta skill garante que todos os Jobs no ecossistema Engeapp sigam padrões consistentes de políticas de retry, estratégias de backoff, gerenciamento de timeout, tratamento de falhas, atribuição de fila e integração com agentes de IA.

## Instruções

### 1. Esqueleto de Job — Estrutura Obrigatória

Todo Job **DEVE** seguir este esqueleto mínimo:

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
        // Lógica do Job aqui
    }

    public function failed(?\Throwable $exception): void
    {
        // Tratamento de falha aqui
    }
}
```

**Propriedades obrigatórias:**

| Propriedade | Tipo | Descrição | Padrão |
|----------|------|-------------|---------|
| `$tries` | `int` | Número máximo de tentativas de execução | `3` |
| `$backoff` | `array<int, int>` | Tempo de espera (segundos) entre cada retry | `[30, 60, 120]` |
| `$timeout` | `int` | Tempo máximo de execução em segundos | `120` |

### 2. Estratégia de Retry & Backoff

Escolha a estratégia de retry com base na dependência externa do Job:

| Cenário | `$tries` | `$backoff` | Justificativa |
|----------|----------|------------|-----------|
| **API WhatsApp** (com rate limit) | `3` | `[5, 15, 30]` | Intervalos curtos — a API se recupera rapidamente |
| **Chamadas de IA/LLM** (Gemini, OpenAI) | `5` | `[60, 120, 300, 600]` | Intervalos longos — rate limits resetam lentamente |
| **Processamento de webhook** (Trello, EFI) | `3` | `[30, 60, 120]` | Padrão — janela de retry moderada |
| **Tarefas internas** (cálculos, sync) | `3` | `[10, 30, 60]` | Recuperação rápida — sem dependência externa |
| **Email/Notificação** | `3` | `[15, 30, 60]` | Espera breve para falhas transitórias de SMTP |

**Regras:**
1. **NUNCA** defina `$tries = 0` — sempre permita ao menos 1 tentativa.
2. **SEMPRE** defina `$backoff` como um array explícito, não um único inteiro — isso cria **backoff exponencial**.
3. Para Jobs intensivos em IA, use o padrão do `GeminiContentJob`: `$tries = 5` com `$backoff = [60, 120, 300, 600]`.

### 3. Gerenciamento de Timeout

A propriedade `$timeout` define o máximo de segundos que uma única tentativa pode rodar antes de ser encerrada.

**Diretrizes de Timeout:**

| Tipo de Job | `$timeout` recomendado | Referência |
|----------|----------------------|-----------|
| Operações simples de DB | `60–120` | `AnalyzeProtocolJob` (120s) |
| Processamento de documentos | `120` | `ProcessDocumentReaderJob` (120s) |
| Execução de agente de IA (baseado em tools) | `300–600` | `BrowserAiJob` (dinâmico via `timeout()`) |
| Computação de IA (pesada) | `400` | `CalculateAiCircuitsJob`, `SupportMessageAiJob` |
| Integração com API externa | `120–200` | `WebhookWhatsappJobExecuteJob` (200s) |
| Deploy/DevOps | `400` | `DeployJob` |

**Padrão de timeout dinâmico** (use quando o timeout varia por instância):

```php
public function timeout(): int
{
    return $this->browserAutomation?->timeout ?? 600;
}
```

**Regra Crítica:** O `$timeout` do Job **DEVE** ser menor ou igual ao `timeout` do supervisor do Horizon. Se o supervisor encerrar o processo primeiro, o Job desaparece silenciosamente sem disparar o `failed()`.

### 4. Atribuição de Fila

O ecossistema Engeapp usa **5 filas nomeadas** gerenciadas por supervisores do Horizon:

| Fila | Supervisor | Propósito | Jobs |
|-------|-----------|---------|------|
| `default` | `general-supervisor` | Tarefas de propósito geral | Maioria dos Jobs |
| `whatsapp` | `whatsapp-supervisor` | Envio de mensagens do WhatsApp | `SendMessageWhatsappJob` |
| `gemini` | `gemini-supervisor` | Processamento de IA/LLM | `ProcessDocumentReaderJob`, `ExtractFileDataAiJob` |
| `scout` | `scout-supervisor` | Atualizações de índice de busca | Scout/Meilisearch |
| `webhooks` | `webhooks-supervisor` | Processamento de webhooks externos | Jobs de Webhook |

**Como atribuir uma fila:**

```php
// Opção 1: No construtor (preferido para Jobs de fila dedicada)
public function __construct(public string $message_id)
{
    $this->onQueue('whatsapp');
}

// Opção 2: No momento do dispatch (preferido para Jobs flexíveis)
MyJob::dispatch($data)->onQueue('gemini');
```

**Regras:**
1. Todos os Jobs de IA/LLM **DEVEM** usar `->onQueue('gemini')` para evitar bloquear a fila geral.
2. Jobs do WhatsApp **DEVEM** usar `->onQueue('whatsapp')` — esta fila tem concorrência fixa (sem auto-scaling).
3. Se nenhuma fila for especificada, os Jobs usam a fila `default` por padrão.

### 5. O Callback `failed()` — Tratamento de Falhas

Todo Job que produz efeitos colaterais visíveis **DEVE** implementar `failed()`:

```php
public function failed(?\Throwable $exception): void
{
    // 1. Resetar quaisquer flags de "em processamento"
    $model = MyModel::find($this->model_id);
    if ($model) {
        $model->processing = false;
        $model->save();
    }

    // 2. Notificar o usuário via Reverb/WebSocket
    SystemOperationEvent::dispatch([
        'type'     => 'operation_failed',
        'model_id' => $this->model_id,
    ], $this->user_id);

    // 3. Atualizar o status da notificação (se aplicável)
    $notification = Notification::find($this->notification_id);
    if ($notification) {
        app(NotificationService::class)->updateNotification($notification, [
            'title'    => 'Operation failed',
            'message'  => 'Error: ' . $exception?->getMessage(),
            'icon'     => 'material-symbols:error-rounded',
            'severity' => 'error',
        ]);
    }

    // 4. Log para debugging
    Log::channel('specific_channel')->error('Job failed', [
        'model_id' => $this->model_id,
        'error'    => $exception?->getMessage(),
    ]);
}
```

**O checklist do `failed()`:**
- [ ] Resetar quaisquer flags de "processing" (`$model->calculating_ai = false`)
- [ ] Disparar evento de falha via Reverb para o frontend
- [ ] Atualizar a notification se alguma foi criada no dispatch
- [ ] Logar o erro com contexto estruturado

### 6. Idempotência — Prevenindo Processamento Duplicado

Jobs podem sofrer retry. Eles **DEVEM** ser projetados para lidar com a reexecução de forma segura:

```php
public function handle(): void
{
    $message = SupportMessage::findOrFail($this->message_id);

    // Guard: se já processado, pule silenciosamente
    if ($message->message_meta_id) {
        Log::channel('whatsapp')->info('Already sent, skipping retry', [
            'message_id' => $this->message_id,
        ]);
        return;
    }

    // Prossiga com o processamento...
}
```

**Padrões de idempotência:**
1. **Check-before-act:** Verifique se o resultado já existe antes de processar (como acima).
2. **Guard baseado em flag:** Use uma coluna booleana (`$model->transcode`, `$model->calculating_ai`) para detectar a conclusão.
3. **Early return:** Se a pré-condição já estiver satisfeita, faça `return` imediatamente sem lançar exception.

### 7. Jobs de Agente de IA — Integração com `HasAgentAiRequest`

Jobs que executam agentes de IA via o aiSDK do Laravel **DEVEM** usar o trait `HasAgentAiRequest`:

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
        // Verifica no banco de dados que o trabalho do agente está concluído
        return MyModel::where('id', $this->model_id)
            ->whereNotNull('result_field')
            ->exists();
    }
}
```

**Regras-chave para Jobs de IA:**
1. **SEMPRE** atribua à fila `gemini`: `$this->onQueue('gemini')`.
2. **SEMPRE** defina `$timeout >= 300` — chamadas de IA são inerentemente lentas.
3. **SEMPRE** implemente `isDone()` com uma verificação no banco de dados para confirmar a conclusão.
4. **SEMPRE** defina `$max_calls` para limitar o loop de retry do do-while (padrão: `5`).
5. O trait `HasAgentAiRequest` trata o **fallback automático de modelo** (`flash-lite → flash → pro`).

### 8. Configuração do Horizon — Referência de Supervisores

A configuração atual do Horizon para produção:

| Supervisor | Fila | Balance | Min/Max Processos | Timeout | Tries |
|-----------|-------|---------|-------------------|---------|-------|
| `general-supervisor` | `default` | `auto` (size) | 2 / 20 | 120s | 3 |
| `webhooks-supervisor` | `webhooks` | `auto` (size) | 1 / 3 | 300s | default |
| `whatsapp-supervisor` | `whatsapp` | `false` (fixed) | 5 / 10 | 60s | 5 |
| `scout-supervisor` | `scout` | `auto` (size) | 8 / 20 | 120s | 5 |
| `gemini-supervisor` | `gemini` | `auto` (size) | — / 5 | 600s | 2 |

**Regras importantes de alinhamento:**
1. O `$timeout` do Job **DEVE** ser ≤ ao `timeout` do supervisor.
2. O `$tries` do Job **DEVE** corresponder ou ser ≤ ao `tries` do supervisor.
3. Se um Job requer mais tempo do que o supervisor permite, configure um supervisor dedicado.

### 9. Estratégia de Logging

Use canais de log dedicados para rastreabilidade:

```php
Log::channel('whatsapp')->info('Message sent', ['id' => $this->message_id]);
Log::channel('gemini')->info('Agent completed', ['agent' => $agentName]);
Log::channel('efi')->error('Payment webhook failed', ['code' => $secure_code]);
Log::channel('trello')->info('Webhook received', ['type' => $type]);
Log::channel('agent_browser')->info('Automation started', ['id' => $automationId]);
Log::channel('ai_benchmarks')->info('BENCHMARK', ['model' => $this->model]);
```

**Regras:**
1. **SEMPRE** use um canal dedicado, não o `Log::info()` padrão.
2. **SEMPRE** passe arrays de contexto estruturados, não strings concatenadas.
3. **SEMPRE** logue no nível `info` para operações bem-sucedidas e `error` para falhas.
4. Para Jobs de IA, o `HasAgentAiRequest` loga automaticamente no canal `gemini` — não duplique.

### 10. Padrão de Soft Cancel

Para Jobs de longa duração, implemente uma verificação de soft cancel para permitir o cancelamento iniciado pelo usuário:

```php
public function handle(): void
{
    // Verifica se o usuário cancelou a operação
    if (! $this->project->calculating_ai) {
        return;
    }

    // Prossiga com a operação de longa duração...
}
```

Este padrão é usado pelo `CalculateAiCircuitsJob` para permitir que o usuário cancele o processamento de IA a partir do frontend.

### 11. Tags para Monitoramento no Horizon

Use `tags()` para tornar os Jobs pesquisáveis no dashboard do Horizon:

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

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
1. **NUNCA** crie um Job sem ambas as propriedades `$tries` e `$backoff`.
2. **NUNCA** use `$this->delete()` dentro de `handle()` para suprimir erros — deixe o mecanismo de retry funcionar.
3. **NUNCA** faça dispatch de Jobs dentro de transações de banco de dados — a transação pode sofrer rollback, mas o Job já foi enfileirado.
4. **NUNCA** defina `$timeout` maior que o `timeout` do supervisor do Horizon para a fila atribuída.
5. **NUNCA** passe models Eloquent diretamente para construtores quando o model possa ser deletado antes do processamento — use IDs no lugar e `findOrFail()` em `handle()`.
6. **NUNCA** use `sleep()` dentro de Jobs para limitar chamadas de API — use `$backoff` no lugar.
7. **NUNCA** esqueça de implementar `failed()` para Jobs que alteram estado visível (flags de UI, notificações).
8. **SEMPRE** torne os Jobs idempotentes — seguros para reexecutar sem efeitos colaterais.
9. **SEMPRE** use `Log::channel()` com arrays de contexto estruturados.
10. **SEMPRE** atribua Jobs de IA à fila `gemini` e Jobs do WhatsApp à fila `whatsapp`.
11. **SEMPRE** alinhe o `$timeout` do Job com o timeout do supervisor do Horizon para a fila de destino.
12. **SEMPRE** implemente soft cancel para operações de longa duração voltadas ao usuário.
