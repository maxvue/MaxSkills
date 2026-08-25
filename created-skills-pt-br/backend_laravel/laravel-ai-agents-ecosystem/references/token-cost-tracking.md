# Token & Cost Tracking (agents_ai_cost)

## Objetivo
Registrar o consumo de tokens das requisições ao LLM e convertê-lo em custo
financeiro (USD/BRL) no ecossistema Engeapp. Comentários de código em pt-BR.

> IMPORTANTE: Descreva SEMPRE o fluxo real do projeto. NÃO existe arquitetura assíncrona
> (Job/Listener/Evento) para custo, NÃO existe `config/ai-pricing.php` nem `AiCostCalculator`.
> Não invente essas peças.
>
> O projeto é MULTI-PROVIDER (`gemini`, `deepseek`, `xAi`) — não assuma que tudo é Gemini.

## 1. Onde o cálculo acontece (síncrono, dentro do trait)
O cálculo e a montagem do custo são feitos SÍNCRONAMENTE em `app/Traits/HasAgentAiRequest.php`,
no mesmo fluxo do loop `do-while` do método `execute()`:

- `calculatePrice(array $usageTokens)`: soma os tokens de todos os passos e aplica a fórmula.
- `getTablePrice()`: retorna a tabela de preços do modelo atual (ver §2).
- `execute()` devolve um array com `total_tokens`, `tokens_input`, `tokens_cached`,
  `tokens_input_total`, `tokens_output`, `tools_uses`, `tools_amount`,
  `total_price_usd_raw` (float USD) e `total_duration_s`.

Fórmula real (por milhão de tokens):
```
input_não_cached = (promptTokens - cacheReadInputTokens) × preço_not_cached / 1_000_000
input_cached     =  cacheReadInputTokens                 × preço_cached     / 1_000_000
output           = (completionTokens + reasoningTokens)  × preço_output     / 1_000_000
total_usd = round(input_não_cached + input_cached + output, 6)
```
A conversão para BRL usa o helper `dolarReal()` apenas para exibição/log (não é persistida).

## 2. Preços vivem no BANCO (tabela `ai_models`) — NÃO são hardcoded

> Histórico: até 08/2026 os preços eram uma tabela fixa dentro de
> `getTablePrice()`. Isso MUDOU. A tabela hardcoded não existe mais no trait.

`getTablePrice()` hoje apenas delega ao `AiPricingService`:

```php
private function getTablePrice() : array
{
    // Preços agora vivem em ai_models (cacheados sem TTL pelo AiPricingService).
    return app(\App\Services\Ai\AiPricingService::class)
        ->getPricesFor($this->provider->value, (string) $this->model);
}
```

### Onde ajustar um preço
1. **Tela Settings → IA** (caminho normal para o usuário), ou
2. `UPDATE` direto em `ai_models`, ou
3. `database/seeders/AiProviderSeeder.php` — apenas **carga inicial** (`updateOrCreate`);
   editar o seeder NÃO altera preço de um modelo já cadastrado.

**Nunca** reintroduza uma tabela de preços no código PHP.

### Colunas relevantes de `ai_models`
`ai_provider_id` (FK → `ai_providers`), `model`, `not_cached`, `cached`,
`output_reasoning` (USD por 1M de tokens), `active` (bool), `status`
(`approved` / `pending` / `failed` — ver constantes `AiModel::STATUS_*`),
`fallback_models` (JSON de ULIDs), `replace_by_fallback` (bool).

Modelo não cadastrado → preços 0 → custo gravado como zero, **sem erro visível**.
Ao adotar um modelo novo, confirme que ele existe em `ai_models`, com preço e `active = 1`.

### Cache
`AiPricingService` cacheia o registry inteiro com `rememberForever`
(chave `AiPricingService::CACHE_KEY` = `ai_prices`). A invalidação é automática, via
hooks `booted()` de `AiProvider` e `AiModel`. Após `UPDATE` manual no banco (fora do
Eloquent), limpe o cache — senão o preço antigo continua valendo.

### Descoberta e sugestão de preços (automático)
- `AiModelDiscoveryService` — consulta a API de cada provider e cadastra modelos novos
  como `pending` com preço 0.
- `AiPriceScraperFactory` (+ scrapers `Gemini`/`Anthropic`/`OpenAi`/`XAi`/`DeepSeek`) —
  raspa a página pública de preços e grava em `ai_model_price_suggestions` para aprovação.

Por isso existem muitos modelos `pending` com preço 0 em `ai_models`: são descobertas
automáticas ainda não aprovadas, não erros de cadastro.

### Consulta útil
```php
DB::table('ai_models')
    ->join('ai_providers', 'ai_providers.id', '=', 'ai_models.ai_provider_id')
    ->where('ai_models.active', 1)
    ->select('ai_providers.key as provider', 'ai_models.model',
             'ai_models.not_cached', 'ai_models.cached', 'ai_models.output_reasoning')
    ->get();
```

## 3. Persistência (morph `costable`, tabela `agents_ai_cost`)
A gravação é feita pelo método `saveAiCost(EloquentModel $model, array $costData)` do trait,
chamado DENTRO do próprio Job logo após `execute()` (ex.: `app/Jobs/Instagram/ReplanEventJob.php`).
Ele grava via relação polimórfica `aiCosts()` (trait `App\Traits\HasAiCost`):

```php
// dentro do Job, após $response = $this->execute($agent, $prompt);
$this->saveAiCost($this->event, [
    'agent'              => $response['agent'],
    'type_data'          => $response['type_data'],
    'model'              => $response['model'],
    'total_tokens'       => $response['total_tokens'],
    'tokens_input'       => $response['tokens_input'],
    'tokens_cached'      => $response['tokens_cached'],
    'tokens_input_total' => $response['tokens_input_total'],
    'tokens_output'      => $response['tokens_output'],
    'tools_uses'         => $response['tools_uses'],
    'tools_amount'       => $response['tools_amount'],
    'total_price'        => $response['total_price_usd_raw'], // USD (float)
    'total_duration'     => $response['total_duration_s'],
]);
```
`saveAiCost()` envolve o `create()` em try/catch e apenas loga o erro (não deixa o Job falhar).

O model dono precisa do trait `HasAiCost`, que expõe `morphMany(AgentAiCost::class, 'costable')`.

## 4. Schema real da tabela `agents_ai_cost`
Migrations: `2026_06_20_192353_create_agents_ai_cost_table.php`,
`_194530_add_token_breakdown...`, `_201908_add_type_data_and_tool_stats...`.
Model: `App\Models\AgentAiCost` (`HasUlids`, `$table = 'agents_ai_cost'`).

- `id` — `ulid` (primary)
- `costable_type` / `costable_id` — `ulidMorphs('costable')` (o morph é `costable`, NÃO `triggerable`)
- `agent` — `string` (nome da classe do agente, ex. `AgentHealthScore`)
- `type_data` — `string` nullable
- `model` — `string` (id do modelo Gemini; NÃO existe coluna `provider`)
- `total_tokens` — `unsignedBigInteger`
- `tokens_input`, `tokens_cached`, `tokens_input_total`, `tokens_output` — `unsignedBigInteger`
- `tools_uses`, `tools_amount` — `unsignedSmallInteger`
- `total_price` — `decimal(10, 6)` em USD (NÃO existe `estimated_cost`)
- `total_duration` — `decimal(8, 2)` em segundos
- `timestamps`

Não existem colunas `prompt_tokens` nem `completion_tokens`: o breakdown é
`tokens_input` (não-cached), `tokens_cached`, `tokens_input_total` e `tokens_output`.

## 5. Fallback de modelo e resiliência
Se uma chamada lança exceção, `execute()` tenta o próximo modelo da cadeia de fallback
(até `max_calls`, padrão 5). Todo o consumo é somado antes de calcular o custo.
Um log de BENCHMARK é sempre emitido no canal `ai_benchmarks` para comparar modelos.

A cadeia **não é hardcoded**. A resolução tem duas fontes, nesta ordem:

1. **Banco (fonte real)** — coluna `ai_models.fallback_models` (JSON de ULIDs), editável
   na tela Settings → IA e semeada por `AiFallbackChainSeeder`. Resolvida pelo
   `AiFallbackChainResolver`.
2. **`config('ai.default_fallback_chains')`** — rede de segurança em runtime
   (`HasAgentAiRequest::initFallbackChain()`), usada só quando a cadeia do banco está
   vazia. Sem ela, um modelo sem cadeia repetiria o MESMO modelo até esgotar `max_calls`.

As cadeias são declaradas **por provider** e não devem misturar providers diferentes.

Ao editar `config/ai.php`, verifique se os modelos citados existem em `ai_models` e estão
com `active = 1`: uma cadeia que termina em modelo inativo deixa o agente sem plano B.
