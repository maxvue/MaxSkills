---
name: laravel-api-integration-patterns
description: Use when creating, debugging, extending external HTTP API integrations, or implementing HTTP idempotency mechanisms. Triggers on setting up new API connectors, Attributes.json or EndPoints.json, configuring OAuth2 caching, and designing safe API mutations (especially payments and integrations).
---

# Padrões de Integração de API do Laravel

## Objetivo
Padronizar a criação, modificação e depuração de integrações de API HTTP externas construídas sobre a classe nativa `BaseApi` do Engeapp, além de estabelecer diretrizes limpas e confiáveis para implementar idempotência de requisições de API usando locks distribuídos com Redis/Cache e cache de respostas.

## Instruções

### 1. Entenda a Arquitetura
Todas as integrações de API externas no Engeapp devem herdar de `BaseApi`. Cada integração deve residir em sua própria pasta (ex: `app/Http/Integrations/MyService/`) contendo:
- `Connector.php` (A classe PHP que estende `BaseApi`)
- `Attributes.json` (Definição de validação de atributos)
- `EndPoints.json` (Estrutura aninhada de endpoints e configuração de execução)

### 2. Criando os Atributos (Attributes.json)
- Defina todas as propriedades de query, path e body que serão enviadas para a API.
- Para cada atributo, especifique seu `type`, uma `description` explicando seu propósito, e se ele é `required` (booleano).

### 3. Definindo os Endpoints (EndPoints.json)
- Mapeie seus endpoints de API em um objeto JSON hierárquico.
- Todo endpoint executável deve definir: `end_point`, `method`, `description` e `attributes` (um objeto agrupando parâmetros em `query`, `path` ou `body`). Placeholders em `end_point` DEVEM ser listados em `path`.

### 4. Implementando a Classe Connector (Connector.php)
- Crie uma classe que estende `BaseApi` sob o namespace `App\Http\Integrations\YourIntegrationName`.
- Defina a propriedade `$base_url` ou um array `$bases_url`.
- Implemente `getAccessToken()` para retornar o bearer token ou a estrutura OAuth2.
- Utilize cadeias de chamadas mágicas como `$connector->group()->endpoint($payload)` para chamar endpoints especificados em `EndPoints.json`.

### 5. Autenticação, Cache e Cache de Token
- Para fluxos OAuth2, defina o array da propriedade `$OAuth2` ou implemente lógica de token customizada dentro de `getAccessToken()`. O token será automaticamente cacheado usando a facade Cache do Laravel.
- `BaseApi` fornece métodos fluentes para configurar o cache de requisições: `$api->withCache(seconds)`, `$api->withoutCache()`, `$api->clearCache()`.

### 6. Implementação de Idempotência de API
Implemente um `IdempotentRequestMiddleware` para mutações de API seguras:
1. **Recupere a Chave de Idempotência:** Extraia dos headers `Idempotency-Key` ou `X-Idempotency-Key`.
2. **Lock Distribuído Atômico:** Adquira um lock de cache usando `idempotency:lock:{key}` com um TTL curto. Retorne `409 Conflict` se não conseguir adquirir.
3. **Consulta ao Cache:** Verifique se `idempotency:response:{key}` existe. Se encontrado, libere o lock e retorne a resposta cacheada com o header `Original-Response: true`.
4. **Execução da Requisição:** Permita que a requisição prossiga.
5. **Serialização do Cache de Resposta:** Cacheie o status code, o conteúdo e os headers das respostas bem-sucedidas (HTTP 2xx) por um período duradouro.
6. **Liberação do Lock:** Libere o lock distribuído em um bloco `finally`.

### 7. Diretrizes de Serialização de Resposta
Armazene um payload simplificado no cache em vez do objeto `Response` inteiro: `status`, `content` e `headers` filtrados (excluindo cookies).

### 8. Testando a Idempotência (Pest)
Os testes de feature devem cobrir:
1. **Caminho de Sucesso:** Envie uma requisição com uma chave, verifique o processamento bem-sucedido e envie-a novamente para verificar que a resposta cacheada é retornada.
2. **Conflito de Requisição Concorrente:** Simule (mock) o lock para simular uma requisição concorrente e verifique um `409 Conflict`.
3. **Cache Expirado:** Verifique que as requisições são processadas do zero quando o TTL expira.

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **NÃO** defina métodos de requisição de API manualmente usando `Http::get` ou `Http::post` dentro da classe connector, a menos que esteja implementando agregação de alto nível.
- **NÃO** pule a definição dos atributos `path` em `EndPoints.json` se a URL contiver chaves (curly braces).
- **NÃO** escreva SQL inline nem instancie models em connectors.
- **Nunca** cacheie respostas de erro (HTTP 4xx ou 5xx).
- **Nunca** cacheie o objeto Response cru do PHP diretamente, para evitar problemas de serialização.
- **Não** armazene chaves de idempotência no cache para sempre. Sempre defina um TTL (recomendado 24 horas).
- **Não** contorne o locking; a aquisição do lock deve preceder a consulta ao cache para prevenir condições de corrida.
