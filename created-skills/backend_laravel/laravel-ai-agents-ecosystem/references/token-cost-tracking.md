# Token & Cost Tracking (agents_ai_cost)

## Objetivo
Registrar o consumo de tokens das requisições ao LLM (Gemini) e convertê-lo em custo
financeiro (USD/BRL) no ecossistema Engeapp. Comentários de código em pt-BR.

> IMPORTANTE: Descreva SEMPRE o fluxo real do projeto. NÃO existe arquitetura assíncrona
> (Job/Listener/Evento) para custo, NÃO existe `config/ai-pricing.php` nem `AiCostCalculator`,
> e os preços NÃO são carregados de config — são fixos no código. Não invente essas peças.

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

## 2. Preços HARDCODED por modelo (não use config)
Os preços ficam FIXOS no método `getTablePrice()` do trait, em USD por 1M de tokens,
com as chaves `not_cached`, `cached` e `output_reasoning`. Modelo desconhecido → tudo 0.
Ao ajustar preço, edite ESTA tabela (nunca uma migration ou config inexistente):

| model                     | not_cached | cached | output_reasoning |
|---------------------------|-----------:|-------:|-----------------:|
| gemini-2.5-flash-lite     | 0.10       | 0.01   | 0.40             |
| gemini-3.1-flash-lite     | 0.25       | 0.025  | 1.50             |
| gemini-2.5-flash          | 0.30       | 0.03   | 2.50             |
| gemini-3.5-flash          | 1.50       | 0.15   | 9.00             |
| gemini-2.5-pro            | 1.25       | 0.125  | 10.00            |
| gemini-3.1-pro-preview    | 2.00       | 0.20   | 12.00            |

Modelos realmente usados pelos agentes (atributo `#[Model(...)]` em `app/Ai/Agents`):
`gemini-2.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-2.5-flash`, `gemini-3.5-flash`,
`gemini-2.5-pro`. Não há `gemini-1.5-*` no projeto.

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
Se uma chamada lança exceção, `execute()` faz downgrade/upgrade automático percorrendo
`['gemini-3.1-flash-lite', 'gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-2.5-pro']` e
tenta novamente (até `max_calls`, padrão 5). Todo o consumo é somado antes de calcular o custo.
Um log de BENCHMARK é sempre emitido no canal `ai_benchmarks` para comparar modelos.
