# Laravel AI Agent Creator

## Goal
Provide standardized, strict guidelines for creating AI agent classes using the Laravel aiSDK.

## Instructions

### 1. Agent Architecture
The structure follows:
- `app/Ai/Agents/` (the "brains", such as `AgentHealthScore.php`)
- `app/Ai/Tools/` (the "hands", such as `GetClientData.php`)

Agents are always dispatched via **Jobs** using the `HasAgentAiRequest` trait to manage the lifecycle.

### 2. Creating an Agent
There are 3 types:
- **Simple Text**: `Agent` interface only. No tools or structured output.
- **With Tools**: `Agent, HasTools` interfaces. Can perform actions (database, API).
- **Structured Output**: `Agent, HasStructuredOutput` interfaces. Returns data through a restricted JSON schema.

#### Required PHP Attributes
```php
#[Provider(Lab::Gemini)]
#[Model('gemini-3.1-flash-lite')]
#[Temperature(0)]
#[MaxTokens(8192)]
#[Timeout(120)]
```
For agents with tools, also add `#[MaxSteps(N)]` indicating the number of allowed loops.

Full decorated class example (all mandatory attributes + constructor injection of business context):
```php
namespace App\Ai\Agents;

use Laravel\Ai\Attributes\MaxSteps;
use Laravel\Ai\Attributes\MaxTokens;
use Laravel\Ai\Attributes\Model;
use Laravel\Ai\Attributes\Provider;
use Laravel\Ai\Attributes\Temperature;
use Laravel\Ai\Attributes\Timeout;
use Laravel\Ai\Contracts\Agent;
use Laravel\Ai\Enums\Lab;
use Laravel\Ai\Promptable;

#[Provider(Lab::Gemini)]
#[Model('gemini-2.5-flash')]
#[Temperature(0.8)]
#[MaxTokens(15000)]
#[MaxSteps(20)]
#[Timeout(180)]
class AgentInstagramCopywriter implements Agent
{
    use Promptable;

    public function __construct(
        public Event $event,
    ) {}
}
```
Attribute guidance: use `0` temperature for precise data extraction, `0.7`–`0.9` for copywriting; default `#[MaxSteps(20)]`; pick lightweight models (`gemini-3.1-flash-lite`) for OCR/extraction and robust ones (`gemini-2.5-flash`/`gemini-3.5-flash`) for reasoning/copywriting.

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
Must implement the `Tool` interface and have:
- `description()`: A string with clear information.
- `handle(Request $request)`: Performs the action and returns `json_encode(['status' => 'success', 'data' => $result])`.
- `schema(JsonSchema $schema)`: Defines the schema of the required parameters.

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
Default Fallback Chain: `gemini-3.1-flash-lite` -> `gemini-2.5-flash` -> `gemini-3.5-flash` -> `gemini-2.5-pro`.

### 5. Gemini Model Selection Guide
- `gemini-3.1-flash-lite`: Fast and cheap. Excellent for simple structured extraction.
- `gemini-2.5-flash`: Moderate reasoning and multiple steps.
- `gemini-3.5-flash`: Complex reasoning with multiple tools.
- `gemini-2.5-pro`: Extreme quality and decision-making, high cost (restricted use).
