# AI Token & Cost Tracking

## Goal
Implement scalable, assertive practices for counting token consumption in LLM requests (such as Gemini), converting it into financial costs (Billing), and enforcing quota limits within the Engeapp ecosystem databases.

## Instructions

### 1. Table Architecture (Database)
When logging consumption, add precise columns:
- Consumed tokens: `prompt_tokens` and `completion_tokens` (`unsignedInteger()`).
- Financial cost: The `estimated_cost` column must use high precision, such as `decimal('estimated_cost', 10, 6)` or `decimal(12, 8)`, because a single token costs sub-cents.
- Relational attributes: Adopt tables with a `triggerable` morph (who triggered the request), the `provider`, and the model identifier (`model`, e.g., `gemini-1.5-flash`).

### 2. Decoupled and Optimized Pricing
**NEVER add "hardcoded" prices directly in migrations or table records.** AI market pricing is highly variable.
Use the configuration in `config/ai-pricing.php` or create a provider class such as `AiCostCalculator`. Charges are computed by multiplying each input/output rate by the corresponding tokens.

`Cost = (prompt_tokens × prompt_rate) + (completion_tokens × completion_rate)`

### 3. Asynchronous Logging with Queues
Never persist computed consumption to the database *synchronously* during the main thread processing (in Controllers or Repositories). This adds unacceptable latency for the end user.
Dispatch a queued Job (consumed by Horizon) and send the payload:
```php
dispatch(new LogAiUsageJob(
    provider: 'gemini',
    model: 'gemini-1.5-flash',
    promptTokens: $response->promptTokens,
    completionTokens: $response->completionTokens,
    triggerable: auth()->user()
));
```

### 4. Automation with Listeners and Events
Listening to a global event (e.g., `AiResponseReceived`) is recommended. A `LogAiTokenUsage` listener will interface with the queues automatically and remove this responsibility from the application Controllers.

### 5. Limit Control and Rate Limiters
Keep token sums or limits in an ultra-fast cache environment. Use Laravel's `RateLimiter` or a dedicated middleware to block the request before the network call is billed if the user exceeds their credit limit.
