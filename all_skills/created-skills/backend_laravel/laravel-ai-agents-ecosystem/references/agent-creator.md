# Laravel AI Agent Creator

## Goal
Provide standardized, strict guidelines for creating AI agent classes using the Laravel aiSDK.

## Instructions

### 1. Agent Architecture
The structure follows:
- `app/Ai/Agents/` (the "brains", such as `AgentHealthScore.php`)
- `app/Ai/Tools/` (the "hands", such as `GetClientData.php`)

A execução do agente sempre acontece em fila (Job). O trait `HasAgentAiRequest` fica no próprio Job (padrão majoritário, 13 casos) ou em uma classe de Service invocada por um Job — ex.: `app/Services/Ai/ProjectAiService.php` usado por `app/Jobs/Station/CalculateAiCircuitsJob.php`.

### 2. Creating an Agent
There are 3 types:
- **Simple Text**: `Agent` interface only. No tools or structured output.
- **With Tools**: `Agent, HasTools` interfaces. Can perform actions (database, API).
- **Structured Output**: `Agent, HasStructuredOutput` interfaces. Returns data through a restricted JSON schema.

#### PHP Attributes
Obrigatórios em todos os agentes do engeapp: `Provider`, `Model` e `Temperature`.
```php
#[Provider(Lab::Gemini)]
#[Model('gemini-2.5-flash-lite')]
#[Temperature(0)]
```
`MaxTokens` e `Timeout` são recomendados (boa prática defensiva), mas nem todos os agentes os usam — `AgentIconGrouper` e `AgentIconKeywords`, por exemplo, declaram só `Provider`/`Model`/`Temperature`.
```php
#[MaxTokens(8192)]
#[Timeout(120)]
```
For agents with tools, also add `#[MaxSteps(N)]` indicating the number of allowed loops.

Full decorated class example (constructor injection of business context):
```php
namespace App\Ai\Agents;

use App\Models\Calendar\Event;
use Laravel\Ai\Attributes\MaxSteps;
use Laravel\Ai\Attributes\MaxTokens;
use Laravel\Ai\Attributes\Model;
use Laravel\Ai\Attributes\Provider;
use Laravel\Ai\Attributes\Temperature;
use Laravel\Ai\Attributes\Timeout;
use Laravel\Ai\Contracts\Agent;
use Laravel\Ai\Contracts\HasTools;
use Laravel\Ai\Enums\Lab;
use Laravel\Ai\Promptable;

#[Provider(Lab::Gemini)]
#[Model('gemini-2.5-flash')]
#[Temperature(0.8)]
#[MaxTokens(15000)]
#[MaxSteps(20)]
#[Timeout(180)]
class AgentInstagramCopywriter implements Agent, HasTools
{
    use Promptable;

    public function __construct(
        public Event $event,
    ) {}
}
```
Attribute guidance: use `0` temperature for precise data extraction, `0.7`–`0.9` for copywriting; default `#[MaxSteps(20)]` for agents with tools. See §5 for model selection guidance.

#### Implementation and Instructions
Use the `Promptable` trait and HereDoc syntax for instructions:
```php
public function instructions() : Stringable | string
{
    return <<<'INSTRUCTIONS'
        Your instructions here...
        INSTRUCTIONS;
}
```
- **Format**: Never concatenate strings or use double quotes in the HereDoc. Structure it with XML-like tags (`<WORKFLOW>`, `<TERMINOLOGY>`, etc.).
- **Always write end-user-facing prompts/outputs in Brazilian Portuguese (pt-BR).**
- Clearly define tools and rules.

### 3. Creating a Tool
Para tools (Function Calling) em `app/Ai/Tools`, consulte a referência dedicada: [tools-creator.md](tools-creator.md). Ela cobre `description()`, `handle()`, `schema(JsonSchema $schema)` e as saídas JSON padronizadas com `try-catch`.

### 4. Execution Job
Always use the `HasAgentAiRequest` trait in AI dispatch Jobs:
```php
class MyAgentJob implements ShouldQueue {
    use HasAgentAiRequest, Queueable;
    public int $timeout = 300;
    public string $model = 'gemini-3.5-flash';
    // ...
}
```
Implement the `isDone()` method to check in the database whether the agent's final goal has been reached (returning `true`). If `false`, the fallback (retry with model switch) can act.

A cadeia de fallback **não é hardcoded**: vem de `ai_models.fallback_models` (banco, fonte
real) com `config('ai.default_fallback_chains')` como rede de segurança. Ver
[token-cost-tracking.md](token-cost-tracking.md) §5.

### 5. Model Selection Guide

O projeto é **multi-provider**: `gemini`, `deepseek` e `xAi`. Preço e disponibilidade vivem
na tabela `ai_models` — **consulte o banco** (ou a tela Settings → IA) antes de escolher,
em vez de confiar em qualquer lista escrita aqui, que envelhece rápido.

```sql
SELECT p.key, m.model, m.not_cached, m.output_reasoning
FROM ai_models m JOIN ai_providers p ON p.id = m.ai_provider_id
WHERE m.active = 1 ORDER BY p.key, m.not_cached;
```

Critérios de escolha:

- **Texto puro** (triagem, classificação, extração de dados de texto): prefira o modelo
  ativo mais barato. Hoje `deepseek-v4-flash` é ordens de grandeza mais barato que os
  Gemini flash.
- **Multimodal** (PDF, imagem, áudio): exige modelo com suporte à modalidade.
  ⚠️ `deepseek-v4-flash` é **text-only**; no DeepSeek, só o `deepseek-v4-pro` aceita imagem.
  Para PDF/imagem, use um Gemini flash ativo.
- **Raciocínio complexo com múltiplas tools**: modelo de maior capacidade (família `pro`),
  de uso restrito por causa do custo.

Ao adotar um modelo, confirme que ele está em `ai_models` com `active = 1` e preço
preenchido — modelo ausente faz o custo ser gravado como zero, silenciosamente.
