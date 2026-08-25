---
name: laravel-brazilian-data-queries-best-practices
description: "Use when querying, validating, or caching Brazilian CNPJ and CEP postal data in Engeapp backend services. Triggers when working with ApiCnpjService fallback providers (ReceitaWS, OpenCNPJ, CnpjAberto), ApiCepService resolution chain, or local address cache models."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Consultas a Dados Brasileiros no Laravel (engeapp)

## Objetivo
Padronizar a implementação e a manutenção dos serviços que consultam dados postais (CEP) e corporativos (CNPJ) brasileiros no engeapp, mantendo fidelidade ao código real: `app/Services/ApiCepService.php` e `app/Services/ApiCnpjService.php`. Ambos usam o cliente `Http` do Laravel, cache e cadeias de fallback entre múltiplos provedores.

Leia os dois serviços antes de alterar comportamento — eles são a fonte da verdade. Esta skill descreve as convenções que eles seguem e por quê.

## Instruções

### 1. Consulta de CNPJ — `ApiCnpjService`

### A. Cadeia de fallback (ordem real)
`getData(string $cnpj)` tenta os provedores nesta ordem, parando no primeiro sucesso (usa `??`):
1. **ReceitaWS** (`tryReceitaWS`) — provedor principal. Usa `Http::withToken(env('RECEITA_WS_TOKEN'))` quando há token (endpoint `/days/30`), senão `Http::get` no endpoint público. Trata "Quota Exceeded" disfarçada de 200 retornando `null` para cair no próximo provedor.
2. **OpenCNPJ** (`tryOpenCnpj`) — `https://api.opencnpj.org/{cnpj}`, sem token.
3. **CnpjAberto** (`tryCnpjAberto`) — `https://cnpjaberto.com.br/api/cnpj/{cnpj}` com `Http::withToken(env('CNP_JABERTO_TOKEN'))` e headers `Origin`/`Referer` = `config('app.url')`.

Não use BrasilAPI para CNPJ: o projeto não a utiliza nessa consulta.

### B. Cache
- Chave: `"cnpj-api-:{$cnpj}:profile"`.
- Só grava em caso de sucesso: `Cache::put($cacheKey, $cnpj_data, now()->addMonths(3))` — TTL de **3 meses**.
- No começo, `getData` faz `Cache::has`/`Cache::get` da mesma chave.
- **Não existe tabela `companies`.** O serviço de CNPJ não persiste em banco — apenas cacheia. Dados de empresas do domínio moram em outras tabelas (ex.: `solar_company`), fora do escopo deste serviço.

### C. Contrato de retorno e normalização
`getData` sempre retorna um array com `status`:
- Sucesso: `['status' => 'done', 'content' => $content]`.
- Falha total ou CNPJ inválido: `['status' => 'fail', 'error' => '...', 'content' => null]`.

`OpenCNPJ` e `CnpjAberto` normalizam a resposta para o mesmo formato pt-BR que a ReceitaWS devolve, com as chaves:
```php
[
    'nome'     => '...', // razão social
    'fantasia' => '...', // nome fantasia
    'telefone' => '(DDD) numero',
    'email'    => '...',
    'status'   => 'OK',
]
```
Ao ler o resultado, consuma `['content']` no formato acima — não invente chaves em inglês (`legal_name`, `trade_name`, etc.).

### 2. Consulta de CEP — `ApiCepService`

### A. Cadeia de fallback (ordem real)
O construtor monta `$api_data_get` e `get()` itera na ordem, parando quando um `City` é resolvido:
1. **CepAberto** — `https://www.cepaberto.com/api/v3/cep?cep=...`, header `Authorization: Token token=` `config('api.cepaberto_token')`.
2. **ViaCep** — `https://viacep.com.br/ws/{cep}/json/`.
3. **OpenCep** — `https://opencep.com/v1/{cep}`.
4. **Brasil Api** — `https://brasilapi.com.br/api/cep/v1/{cep}`.
5. **Awesome Api** — `https://cep.awesomeapi.com.br/json/{cep}`.
6. **apicep** — `https://cdn.apicep.com/file/apicep/{cep_formatado}.json` (rotulado internamente também como "Awesome Api").
7. **BrasilAberto** — `https://api.brasilaberto.com/v2/zipcode/{cep}`, `token` = `config('api.brasil_aberto_token')`.

### B. Resolução via banco antes das APIs
`get(bool $force = false)` prioriza o banco local antes de sair para a rede (quando `$force` é falso):
1. `getCity()` (tenta resolver a partir do estado/cidade já conhecidos).
2. Busca na tabela de CEPs: `Cep::where('cep', $this->cep)->whereNotNull('city_id')->first()`.
3. Só então percorre `$api_data_get`.
4. Fallback final: infere a cidade por faixa `City::where('cep_start','<=',$cep)->where('cep_end','>=',$cep)` quando há exatamente uma.

O CEP é limpo/validado no construtor (`getCepOnlyNumber`, `checkCepValid`, `mb_str_pad(...,8,'0')`). Os models envolvidos são `App\Models\Lists\{Cep, City, State}`.

### C. Cache
- `getApi($item)` usa `Cache::remember($cache_key, now()->addMonths(8), ...)` — TTL de **8 meses**.
- Chave: `'cache_cep_apis' . $url . '-' . $item['name'] . '_cep_' . $this->cep`.
- Em erro de rede/HTTP o closure captura `Throwable`/`failed()` e retorna `false` (o `false` também fica cacheado). Respostas com 2 campos úteis ou menos são descartadas (`count($limpo) <= 2`).

### D. Contrato de retorno e normalização
`getValues()` retorna sempre este array (mesmo vazio quando nada resolve):
```php
[
    'cep'          => '...',
    'cep_value'    => '...',
    'street'       => '...',
    'neighborhood' => '...',
    'city'         => City|null,   // model Eloquent, não string
    'city_id'      => int|null,
    'state'        => State|null,  // model Eloquent
    'uf'           => 'SP',
    'latitude'     => '...',
    'longitude'    => '...',
    'state_name'   => '...',
    'city_name'    => '...',
]
```
Não há chave `ibge_code`. `setData()` faz o mapeamento resiliente de campos vindos de cada provedor (`logradouro`/`street`, `bairro`/`neighborhood`, `localidade`/`cidade`/`city`, `uf`/`UF`/`estado`, etc.) via `getFirstContent`, resolvendo por fim `State` e `City` no banco.

### 3. Tratamento de Erros
- Nenhum dos serviços lança exceção customizada — ambos retornam estruturas de falha (ver 1.C e 2.D). Não existe `BrazilianDataQueryException` no projeto — não a invente.
- Siga `laravel-exception-handling-logging` para logging adicional.
- Sempre use o cliente `Http` do Laravel (nunca cURL bruto).

## Restrições
- **Idioma:** comunique-se com o humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código em pt-BR.
- **Tokens/endpoints:** CEP usa `config('api.*')` (ex.: `cepaberto_token`, `brasil_aberto_token`); CNPJ usa `env()` diretamente (`RECEITA_WS_TOKEN`, `CNP_JABERTO_TOKEN`). Ao adicionar provedor, prefira `config()`.
- **Não** faça requisições a APIs de CNPJ/CEP dentro de loops sobre registros; confie no cache e nas resoluções via banco (models `Cep`/`City`).
- **Não** ignore limites de plano gratuito (ReceitaWS) — o tratamento de "Quota" já cai para o próximo provedor; preserve esse comportamento.
