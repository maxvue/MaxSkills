# Laravel AI Tools Creator

## Goal
Ensure that all custom AI tools (Function Calling) implemented with the aiSDK (`Laravel\Ai\Contracts\Tool`) in Engeapp follow strict coding guidelines, safe schema definitions, and rigorous exception handling.

> **Nota de aderência:** contagem em `app/Ai/Tools` (30 no nível raiz + 11 em `Browser/` = 41 tools). O que É convenção estabelecida: a chave `status` (`'success'`|`'error'`) + `message` (36/41 tools). A chave `data` é OPCIONAL e minoritária (7/41) — tools de leitura frequentemente retornam chaves de domínio no nível raiz do JSON (ver `GetClientData.php`, que retorna `status` + chaves como `empresa`/`projetos`/`pagamentos`, sem `data`). O `try-catch` abaixo é padrão RECOMENDADO, não vigente (15/41 no total; 5/30 no nível raiz — `SaveTrtBilletToProject`, `CheckBankTicket`, `GetReadyThemes`, `GenerateEventArtwork`, `PayBankTicket`); as tools canônicas `GetClientData`/`SetHealth` usam early-return com `{'status':'error'}` em vez de try-catch.

## Instructions

### 1. Structure and Class
- Tools must reside in the `app/Ai/Tools` directory.
- The tool class must implement the `Laravel\Ai\Contracts\Tool` interface.
- Always use explicit typehints for parameters and return values.

### 2. The `description` Method
```php
public function description() : Stringable | string
```
The description tells the LLM when to invoke the tool and what it does. Be concise and specific, avoiding vague descriptions. Use Brazilian Portuguese (pt-BR). Example: "Busca os dados corporativos e projetos em andamento do integrador solar".

### 3. The `schema` Method
```php
public function schema(JsonSchema $schema) : array
{
    return [
        'solar_company_id' => $schema->string()->description('ID (ULID) da empresa solar a ser analisada.')->required(),
    ];
}
```
Inject `JsonSchema`, explicitly describe every argument in pt-BR, and mark fields as `required()` when necessary. Use `snake_case` for variable names.

### 4. The `handle` Method
```php
public function handle(Request $request) : Stringable | string
```
Extract the values as an array from `$request`.
The return **MUST ALWAYS BE A JSON STRING**. Format your output using at least `status`/`message`; `data` is optional — reading tools may return domain keys at the root level instead (ex.: `GetClientData.php`):
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional message"
}
```
Use `json_encode($data, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE)`. NEVER return raw HTML or unstructured text.

### 5. Exception Handling and Security
- `try-catch` é recomendado como boa prática defensiva, mas não é padrão vigente na maioria das tools (ver nota de aderência acima); early-return com `{'status':'error'}` também é aceitável, como fazem `GetClientData`/`SetHealth`.
- Log errors with `Log::error()` and do not expose database traces in the LLM response.
- On failure, return a structured JSON error indicating `{"status": "error", "message": "Your friendly message"}`.
- Do not perform critical destructive actions (such as mass deletion) without confirming permissions and rigorously validating the call's behavior.
