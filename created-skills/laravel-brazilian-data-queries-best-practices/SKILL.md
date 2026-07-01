---
name: laravel-brazilian-data-queries-best-practices
description: Use when designing, implementing, or debugging services that query Brazilian corporate and postal data (CNPJ and CEP). Triggers on third-party API integration (ViaCep, ReceitaWS, BrasilAPI, CepAberto), handling fallback mechanisms, normalizing responses, and caching address or registry data.
---

# Laravel Brazilian Data Queries Best Practices

## Goal
Provide solid guidelines, resilient fallback strategies, error handling patterns, response normalization, and caching mechanisms for integrating Brazilian postal (CEP) and corporate (CNPJ) API queries in Laravel applications within the Engeapp ecosystem.

## Instructions

### 1. CEP (Postal Code) Query Guidelines

#### A. Resilient Fallback Strategy
Always attempt to query CEP services in the following order:
1. **ViaCEP**: Reliable, free, but can experience latency.
2. **BrasilAPI**: Fast, aggregates multiple sources under the hood.
3. **AwesomeAPI**: Free and responsive secondary backup.

Implement a service or action class (e.g., `GetAddressFromCepAction`) that iterates through these providers when a connection or server error occurs.

#### B. Cache Strategy
To optimize performance and respect API limits:
- Store successful queries in the cache for **90 days (3 months)**.
- Use a structured cache key: `brazilian-queries:cep:{cep}`.
- Example implementation:
  ```php
  use Illuminate\Support\Facades\Cache;
  use Illuminate\Support\Facades\Http;

  $cepClean = preg_replace('/[^0-9]/', '', $cep);

  $address = Cache::remember("brazilian-queries:cep:{$cepClean}", now()->addMonths(3), function () use ($cepClean) {
      return $this->queryCepWithFallbacks($cepClean);
  });
  ```

#### C. Response Normalization
Regardless of the API used, map the response to a standard structure:
```php
[
    'cep'          => '01001-000',
    'street'       => 'Praça da Sé',
    'neighborhood' => 'Sé',
    'city'         => 'São Paulo',
    'state'        => 'SP',
    'ibge_code'    => '3550308',
]
```

---

### 2. CNPJ (Corporate Registry) Query Guidelines

#### A. Fallback Order & Rate Limits
Query CNPJ services in the following sequence:
1. **BrasilAPI (CNPJ)**: Main stable option using public Receita Federal data.
2. **ReceitaWS**: Good fallback, but has a rate limit of 3 queries per minute on the free tier. Ensure you catch and handle 429 status codes.

#### B. Cache and Local DB Persistence
- Cache API responses for **90 days (3 months)** using `brazilian-queries:cnpj:{cnpj}`.
- For business-critical flows, store the registry data permanently in a local `companies` database table. Check this table before performing any external API request.

#### C. Response Normalization
Normalize CNPJ responses to a consistent format:
```php
[
    'cnpj'         => '00.000.000/0001-91',
    'legal_name'   => 'BANCO DO BRASIL SA',
    'trade_name'   => 'BANCO DO BRASIL',
    'status'       => 'ATIVA',
    'opening_date' => '1808-10-12', // Y-m-d format
    'address'      => [
        'street'       => 'SBS Quadra 1 Bloco G Lote 32',
        'number'       => '32',
        'complement'   => 'Lote 32',
        'neighborhood' => 'Asa Sul',
        'city'         => 'Brasília',
        'state'        => 'DF',
        'cep'          => '70070-110',
    ]
]
```

---

### 3. Exception Handling & Logging
- Follow the guidelines in `laravel-exception-handling-logging`.
- Wrap external HTTP requests in `try/catch` blocks targeting `Illuminate\Http\Client\RequestException` and `Illuminate\Http\Client\ConnectionException`.
- Log failures using the `Log` facade:
  ```php
  use Illuminate\Support\Facades\Log;

  Log::warning("CEP API provider failed. Attempting fallback.", [
      'provider' => 'viacep',
      'cep' => $cep,
      'error' => $exception->getMessage()
  ]);
  ```
- Throw a custom `BrazilianDataQueryException` only when all API providers fail.

## Constraints
- **Do NOT** execute raw cURL requests directly; always use Laravel's `Http` client.
- **Do NOT** store API endpoints or credentials directly in code; manage them via `config()` values mapped to `.env`.
- **Do NOT** perform external API requests inside loops. Implement caching or chunking.
- **Do NOT** ignore the rate limits of free tiers (e.g. ReceitaWS 3 requests/minute). Check status codes and apply delays or fallback immediately.
