# Laravel AI Structured Outputs

## Goal
Establish solid guidelines for modeling, defining, and validating structured JSON outputs produced by Gemini with the aiSDK. This prevents silent parsing failures and frontend breakage.

## Instructions

### 1. Agent Configuration
An agent that returns structured data must implement `Laravel\Ai\Contracts\Agent` and `Laravel\Ai\Contracts\HasStructuredOutput`. The structure is defined by the `schema()` method.

```php
public function schema(JsonSchema $schema): array
{
    return [ ... ];
}
```

### 2. Schema Property Rules
- **Explicit Descriptions**: Use `->description(...)` to detail the field. The LLM will use this description.
- **Required Fields**: Attach `->required()` to maintain data integrity for the database.
- **Clean Numbers (no units)**: Do not allow units of measurement attached to keys (e.g., "W", "V", "A", "%", "years"). Define them strictly as numbers or floats in the description.
- **Consistent Dates**: Request and validate dates always in ISO format (`YYYY-MM-DD`).
- **Clean Identifiers**: CPF, CNPJ, and barcodes must arrive sanitized (digits only), without dots, hyphens, or formatting slashes.

### 3. Complex and Nested Structures
For composite data, use `$schema->object(...)` or an array of items `$schema->array()->items(...)`.
```php
$itemSchema = $schema->object([
    'name'  => $schema->string()->description('Nome do item.')->required(),
    'price' => $schema->number()->description('Preço unitário em float.')->required(),
])->required();
```

### 4. Prompt Synchronization and Fallbacks
- Align the explanation of the structured rules in your HereDoc (inside `instructions()`).
- If a piece of data does not exist in the source document, instruct the LLM in the prompt to return default values (such as `0`, `false`, or `null`).
- Catch JSON parsing exceptions in the code that calls the Agent, to avoid abrupt system breakage.

### 5. Constraints
- Do not insert HTML tags into descriptions in a `JsonSchema`.
- No empty or partial schemas: every contained key must have a description.
- Use exclusively the tools from `Illuminate\Contracts\JsonSchema\JsonSchema`.
