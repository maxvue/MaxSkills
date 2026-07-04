# Laravel AI Agent Testing

## Goal
Patterns and best practices for writing unit and integration tests for AI Agents in Laravel with Pest PHP. The objective is to ensure the logical behavior of agents without incurring unnecessary costs from real API calls to external providers.

## Instructions

### 1. Faking the LLM
To prevent real network requests in the test environment, use the native `Laravel\Ai\Ai` facade. Fake the agent at initialization or the top of the test:

```php
use Laravel\Ai\Ai;
use App\Ai\Agents\MyCustomAgent;

Ai::fakeAgent(MyCustomAgent::class, [
    'This is a simulated response sent by the Agent.',
]);
```

### 2. Testing Loops (HasAgentAiRequest)
If your agent's infrastructure relies on the `HasAgentAiRequest` trait (in the scope of Jobs), it may generate loop requests until `isDone()` is `true`. You must provide several mocked strings to `fakeAgent()`:
```php
Ai::fakeAgent(BilletReaderAgent::class, [
    'Cycle 1: reading document.',
    'Cycle 2: document saved.',
]);
```

### 3. Simulating Structured JSON Returns
If it is a `HasStructuredOutput`, pass the associative array instead of a text string. It will be parsed into the native instance.
```php
Ai::fakeAgent(DataExtractorAgent::class, [
    [
        'document_number' => '12345678900',
        'full_name' => 'João Ninguém',
    ]
]);
```

### 4. Asserting Behaviors and Prompts
You can assert that the prompt reached the model as planned:
```php
Ai::assertAgentWasPrompted(MyCustomAgent::class, 'Analise este documento.');

// Or more advanced:
Ai::assertAgentWasPrompted(MyCustomAgent::class, function ($prompt) {
    return str_contains($prompt->prompt, 'analisar keywords')
        && $prompt->model === 'gemini-3.5-flash';
});

// Ensure the agent stays silent:
Ai::assertAgentNeverPrompted(UnusedAgent::class);
```

### 5. Constraints and Limits
- **Never allow real LLM traffic in tests** (if it leaks, add "fake" credentials in `.env.testing`).
- If `HasAgentAiRequest` is used, always account for the loop volume required by the mock so it does not run out or trigger an infinite loop in the tests.
