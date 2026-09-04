---
name: laravel-redis-integration-best-practices
description: "Use when configuring, optimizing, or debugging Redis connections in Engeapp (phpredis client, key prefixes, atomic HSETNX operations, pipelines, RedisException fallback, cache tags, and Horizon queues). Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Integração com Redis no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para configurar, otimizar, proteger e desenvolver rotinas resilientes baseadas em Redis no backend Laravel do Engeapp.

> Esta skill cobre a camada de **driver/conexão** do Redis. Para a camada de **cache da aplicação** (padrão cache-aside, TTLs, invalidação por Observers), veja `laravel-cache-best-practices`. A convenção de nomenclatura de chaves é **única e compartilhada** entre as duas skills (canônica em `laravel-cache-best-practices`).

## Instruções

### 1. Cliente Redis e Configuração
* **Cliente Padrão:** Sempre use `phpredis` como cliente padrão (por ser implementado em C e oferecer performance muito superior ao `predis`).
* **Conexões Persistentes:** A config real usa `'persistent' => env('REDIS_PERSISTENT', false)`. Em produção, habilite `REDIS_PERSISTENT=true` no `.env` para evitar o overhead de abrir uma nova conexão a cada requisição — não altere o default do arquivo.
* **Timeout e Read Timeout (sugestão, não presente hoje):** o `config/database.php` atual do engeapp **não** define `timeout`/`read_timeout`. Caso observe web workers bloqueados por uma instância lenta do Redis, considere adicionar essas chaves com valores razoáveis (ex.: 1.5s a 2.0s).

Estrutura real em `config/database.php` (a partir da linha 192) — o exemplo abaixo reflete o arquivo do projeto e marca como comentário o que seria um acréscimo sugerido, não algo já configurado:
```php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster'    => env('REDIS_CLUSTER', 'redis'),
        'prefix'     => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_') . '_database_'),
        'persistent' => env('REDIS_PERSISTENT', false), // habilite via .env em produção
        // 'timeout'      => 1.5, // sugestão de best-practice — NÃO existe hoje no projeto
        // 'read_timeout' => 1.5, // sugestão de best-practice — NÃO existe hoje no projeto
    ],
    // ... configuração das conexões (default, cache, etc.) ...
],
```

### 2. Convenção Semântica de Nomenclatura de Chaves
Use um dos três formatos canônicos definidos em `laravel-cache-best-practices` — `api:{provider}:{endpoint}:{id}`, `model:{table}:{id}:{attr}` ou `app:{context}:{id}` (ex.: `model:inverters:45:nominal_power`). Não invente um esquema paralelo.
* **Prefixo de app:** o `REDIS_PREFIX` configurado em `config/database.php` (ex.: `engeapp_database_`) **já prepende automaticamente** o slug da aplicação a toda chave. Portanto **não** repita o nome do app dentro da chave definida em código — deixe o prefixo por conta da config.
* **Regra:** Nunca use strings hardcoded para chaves Redis. Defina constantes ou métodos helper na classe de service/model que manipula o recurso. **Dívida técnica documentada:** o código real hoje viola essa regra — `geckodriver_ports` (`app/Classes/Browser.php:37,53,109` e `app/Console/Commands/CleanupGeckodriverPorts.php:30,43,59`) e `'trt-payment-schedule:'` (`TrtPaymentSchedulingService.php:109`) são strings literais inline, sem constante/helper. Não replique esse padrão em código novo.

```php
class TrtPaymentSchedulingService
{
    // Sem repetir o nome do app: o REDIS_PREFIX da config já o adiciona.
    private const KEY_PREFIX = 'app:trt_payment_schedule:';

    public function getCacheKey(int $projectId): string
    {
        return self::KEY_PREFIX . $projectId;
    }
}
```

### 3. Controle de Concorrência com Operações Atômicas do Redis
Para lógica de negócio crítica (ex.: alocar um recurso escasso, evitar processamento duplicado) use operações atômicas do Redis para evitar condições de corrida.

**Padrão real do projeto — alocação atômica de porta via `HSETNX`.** Em `app/Classes/Browser.php` (linha ~37) o engeapp reserva uma porta livre para o GeckoDriver percorrendo um intervalo e usando `Redis::hsetnx()`, que só grava o campo se ele ainda não existir (retorna `true` uma única vez por chave, mesmo sob concorrência). Esse é o mecanismo de lock/reserva efetivamente usado no código:

```php
use Illuminate\Support\Facades\Redis;

$port = null;
// Percorre o intervalo de portas até conseguir reservar uma atomicamente
for ($p = 44500; $p <= 44599; $p++) {
    // hsetnx só grava (e retorna true) se o campo ainda não existir — atômico
    if (Redis::hsetnx('geckodriver_ports', $p, now()->timestamp)) {
        $port = $p;

        break;
    }
}

if ( ! $port) {
    throw new Exception('Nenhuma porta disponível para o GeckoDriver.');
}

// ... ao terminar, libere o recurso:
// Redis::hdel('geckodriver_ports', $port);
```

**Padrão real do projeto — lock atômico Laravel-native (`Cache::lock`).** Para regiões críticas mais genéricas, o Laravel oferece locks atômicos via `Cache::lock()`, e o engeapp já os usa. Em `app/Services/Finance/TrtPaymentSchedulingService.php`, o método `schedule()` (assinatura na linha 105) adquire `Cache::lock('trt-payment-schedule:' . $project->id . ':' . $index, 120)` na linha 109 com `$lock->get()` para impedir o duplo-envio de pagamento TRT (que pagaria o mesmo boleto duas vezes). O lock funciona no store de cache padrão do projeto — `database` — porque esse store suporta locks atômicos via sua `lock_connection` (`config/cache.php:45`); **não** é preciso forçar `Cache::store('redis')`. Sempre libere o lock em `finally`:

```php
use Illuminate\Support\Facades\Cache;

// Lock no store default (database) — TTL alto para não expirar durante a chamada externa.
$lock = Cache::lock('trt-payment-schedule:' . $project->id . ':' . $index, 120);

if ( ! $lock->get()) {
    // Já existe operação em andamento para este item — aborta sem duplicar o envio.
    return ['state' => 'error', 'message' => 'Já existe uma operação de pagamento em andamento para este item.'];
}

try {
    // Lógica crítica: revalida o estado fresco e executa o pagamento.
} finally {
    $lock->release();
}
```

> Use o store default a menos que tenha um motivo concreto para isolar a conexão de lock.

### 4. Pipelines do Redis para Operações em Lote
Para lotes grandes de comandos, considere `Redis::pipeline()` — envia os comandos em um único lote, reduzindo o tempo de ida e volta (RTT). Hoje não há uso de `pipeline()` no engeapp; o padrão real (seção 3) escreve o hash `geckodriver_ports` campo-a-campo (`hsetnx`/`hset`/`hdel`).

### 5. Failbacks de Conexão Resilientes e Tratamento de Exceções
Quedas de conexão com o Redis não devem derrubar a aplicação inteira (a menos que seja uma dependência rígida, como sessão ou rate-limiting) — mas também não devem passar despercebidas.
* Capture `RedisException` ou exceções gerais dos drivers de cache.
* Implemente uma query de fallback no banco de dados ou valores padrão caso o servidor Redis fique offline.
* **Sempre reporte ao degradar:** `app/Helpers/ExceptionsHelper.php` documenta explicitamente que `RedisException` (assim como `PDOException`) é excluída da lista de exceções transitórias e **deve** ser reportada — queda de Redis é crítica de verdade. Não basta `Log::error`; chame também `report($e)`.

```php
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Redis;
use RedisException;

// Padrão sugerido — não é o código exato de nenhuma classe do engeapp hoje.
public function getActivePorts(): array
{
    try {
        return Redis::hgetall('geckodriver_ports') ?: [];
    } catch (RedisException $e) {
        report($e); // RedisException não é transitória (ExceptionsHelper.php) — sempre reporte

        Log::error('Redis connection failure ao buscar portas ativas', [
            'exception' => $e->getMessage()
        ]);

        // Opção de fallback (ex: ler de uma fonte persistente alternativa ou retornar vazio)
        return [];
    }
}
```

### 6. Cache Tags e Invalidação

> **Estado real do projeto:** o engeapp roda com `CACHE_STORE=database` por padrão (`config/cache.php` linha 18 e `.env.example` linha 45). Não há nenhum uso de `Cache::tags()` no código hoje. O exemplo abaixo só é válido se a chamada apontar explicitamente para um store baseado em Redis/Memcached (ver Restrições). A orientação de fundo sobre Cache Tags é canônica em `laravel-cache-best-practices` — siga-a de lá.

```php
use Illuminate\Support\Facades\Cache;

$redisCache = Cache::store('redis');

// Armazenando com tags (exemplo hipotético/ilustrativo — sem domínio real correspondente hoje)
$redisCache->tags(['example-domain', 'example-resource'])->put($cacheKey, $data, now()->addDays(7));

// Invalidando por tag (flush seletivo)
$redisCache->tags(['example-domain'])->flush();
```

### 7. Ajuste do Horizon e das Filas
* Evite despachar payloads enormes em jobs. Em vez disso, armazene o ID do Model no payload do job e busque os dados atualizados no banco de dados/cache dentro do job.
* Para configuração de conexão/`retry_after` do Horizon, veja `laravel-jobs-queues-horizon-best-practices`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** execute comandos Redis lentos (como `KEYS *`, `FLUSHALL`, `FLUSHDB`) em produção. Use `SCAN` ou limpe o cache usando os comandos nativos de limpeza de cache do Laravel.
* **NÃO** use cache tags do Redis sem verificar o driver. Os drivers de cache database e file não suportam tags.
* **NÃO** escreva queries Redis brutas sem capturar exceções de conexão. Sempre assuma que o Redis pode ficar offline.
* **NÃO** serialize models Eloquent completos diretamente no Redis; use `json_encode` dos dados necessários ou a serialização padrão de model via jobs.
