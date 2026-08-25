---
name: laravel-api-integration-patterns
description: "Use when creating, debugging, or extending external HTTP APIs over BaseApi in Engeapp. Covers BaseApi connectors, Attributes.json, EndPoints.json, and request caching."
author: Johnattas Conrady Gomes Santana
---
# Padrões de Integração de API do Laravel

## Objetivo
Padronizar a criação, modificação e depuração de integrações de API HTTP externas construídas sobre a classe `BaseApi` (`app/Http/Integrations/BaseApi.php`) do Engeapp, incluindo definição de atributos/endpoints via JSON, chamadas mágicas encadeadas, cache de requisições e cache de token OAuth2.

## Instruções

### 1. Entenda a Arquitetura
O padrão preferencial para novas integrações de API externas no Engeapp é herdar de `BaseApi`, pois isso dá cache de requisição/token, validação de atributos e roteamento de endpoints por JSON de graça. Cada integração baseada em `BaseApi` reside em sua própria pasta (ex.: `app/Http/Integrations/WhapiCloud/`) contendo:
- O connector PHP que estende `BaseApi` (ex.: `Whapi.php`).
- `Attributes.json` (definição/validação dos atributos).
- `EndPoints.json` (estrutura aninhada de endpoints e configuração de execução).

Exceção documentada: nem toda integração de pagamento segue esse padrão. `app/Http/Integrations/Efi/Efi.php` NÃO estende `BaseApi` — usa um `EndPointsTrait` próprio e chama `Http` diretamente por causa das exigências de certificado/mTLS e do fluxo específico da Efí. Ao trabalhar em uma integração existente, verifique primeiro se ela usa `BaseApi` ou um trait dedicado antes de aplicar estes padrões.

### 2. Criando os Atributos (Attributes.json)
- Defina todas as propriedades de query, path e body que serão enviadas para a API.
- Para cada atributo, especifique seu `type`, uma `description` explicando seu propósito e se ele é `required` (booleano). `BaseApi::checkAttributes()` só bloqueia a requisição quando um atributo `required` está ausente do payload.

### 3. Definindo os Endpoints (EndPoints.json)
- Mapeie seus endpoints de API em um objeto JSON hierárquico.
- Todo endpoint executável deve definir: `end_point`, `method` e `attributes` (um objeto agrupando parâmetros em `query`, `path` ou `body`). Placeholders `{...}` em `end_point` DEVEM ser listados em `path`, pois `checkAttributes()` substitui `{chave}` pelo valor de `data_array[chave]` — mas **somente quando esse valor é uma string** (`BaseApi.php:159`, checagem `is_string()`). Se um valor numérico/int for passado para um placeholder de path, a substituição é silenciosamente pulada e a URL final mantém `{chave}` literal, sem nenhum log de erro. Ao popular parâmetros de path (ex.: IDs), converta explicitamente para string.
- Um nó pode definir `base_url` próprio para sobrepor o `base_url` do connector naquele endpoint.

### 4. Implementando o Connector
- Crie uma classe que estende `BaseApi` sob o namespace `App\Http\Integrations\SuaIntegracao`.
- Defina a propriedade `$base_url` diretamente, ou preencha `$bases_url` com as chaves `production` e `development` — `BaseApi::defineComputedBaseUrl()` escolhe a URL conforme `App()->isProduction()`.
- Sobrescreva `getAccessToken()` para retornar o token (string), `null`, ou a estrutura OAuth2. Ex.: `Whapi::getAccessToken()` retorna `config('app.whapi_token')`.
- Chame endpoints via cadeias mágicas: `$connector->grupo()->endpoint($payload)`. O `__call` acumula os nomes em `$calls`, faz merge do payload em `$data_array`, resolve o endpoint em `searchEndPoint()` e dispara a requisição quando exatamente um endpoint casa.
- Métodos utilitários da resposta: `->json()`, `->array()`, `->object()`, `->collect()`, `->response()`, `->successful()`, `->failed()`, `->ok()`, `->serverError()`. Use `->clearApi()` para resetar o estado acumulado entre chamadas.

### 5. Autenticação e Cache de Token (OAuth2)
- Para fluxos OAuth2, defina a propriedade `$OAuth2` (array com `[0]`=usuário, `[1]`=senha do basic auth, além de `end_point`, `body` e `token_response_key`). Se `$OAuth2` for `null` e não houver `$token`, `getAccessToken()` retorna `null` (requisição sem bearer).
- `getAccessToken()` cacheia o token pela facade `Cache` sob a chave `('production:'|'sandbox:') . $this->url`, com TTL de 600 segundos (`Cache::remember`). Em falha de autenticação, retorna um array com `body`, `headers`, `status`, `code`, `json` e `response`.

### 6. Cache de Requisições
`BaseApi` cacheia respostas por requisição. Métodos fluentes para controlar, em DOIS grupos com comportamento diferente:
- `withCache(int $seconds = 0)` / `enableCache(int $seconds = 0)` / `cache(bool $value = true, int $seconds = 0)` — habilitam o cache (`with_cache = true`) e usam TTL padrão de 120s quando `seconds` não é informado ou é `<= 0` (padrão base da classe é `cache_seconds = 60000`).
- `cacheTtl(int $seconds = 0)` / `cacheMinutes(int $minutes = 0)` / `cacheHours(int $hours = 0)` / `cacheTime(int $seconds = 0)` — fazem `with_cache = seconds > 0`: chamados **sem argumento (ou com 0) DESABILITAM o cache** em vez de usar um TTL padrão. Armadilha: `->cacheMinutes()` sozinho não ativa cache nenhum; sempre passe um valor `> 0` a esses métodos.
- `withoutCache()` / `disableCache()` — desabilitam o cache da requisição.
- `clearCache()` — marca para dar `Cache::forget` na chave antes de refazer a requisição.

A chave de cache é construída em `setCacheKey()` a partir de `url + ':data:' + json(data_array ordenado) + ':token:' + token`, isolando cada combinação de endpoint, payload e token.

### 7. Serialização da Resposta em Cache
Ao cachear (`request()`, quando `with_cache` é verdadeiro), `BaseApi` NÃO guarda o objeto `Response` cru. Guarda um array com exatamente três chaves:
- `body`  — `$response->body()`
- `status` — `$response->status()`
- `headers` — `$response->headers()`

Na leitura, `getToCache()` reconstrói um `Illuminate\Http\Client\Response` a partir de um `GuzzleHttp\Psr7\Response($status, $headers, $body)`. Não há filtragem de cookies nem qualquer outro campo além desses três. Ao estender o mecanismo, preserve exatamente esse contrato (`body`/`status`/`headers`), senão `getToCache()` quebra.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito. Comentários de código em pt-BR.
- **NÃO** defina métodos de requisição manualmente com `Http::get`/`Http::post` dentro de um connector que estende `BaseApi` — deixe o roteamento por `EndPoints.json` e `request()` cuidar disso. (Chamada direta a `Http` só é aceitável em integrações que deliberadamente não usam `BaseApi`, como `Efi`.)
- **NÃO** omita os atributos `path` em `EndPoints.json` quando a URL contiver chaves `{...}`; sem isso o placeholder não é substituído.
- **NÃO** escreva SQL inline nem instancie models dentro de connectors.
- **Nunca** cacheie o objeto `Response` cru; guarde apenas o array `body`/`status`/`headers` conforme a Seção 7, para evitar problemas de serialização.
