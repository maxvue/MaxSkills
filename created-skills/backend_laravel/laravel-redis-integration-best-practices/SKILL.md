---
name: laravel-redis-integration-best-practices
description: "Use ao configurar, otimizar ou depurar conexões Redis no backend Laravel do engeapp: cliente phpredis, prefixo/nomenclatura de chaves, controle de concorrência com operações atômicas (HSETNX em geckodriver_ports), pipelines, fallback resiliente a RedisException, cache tags (apenas em store Redis) e filas/Horizon. Aciona no uso do facade Redis, config de database.php e cache tags."
---

# Boas Práticas de Integração com Redis no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para configurar, otimizar, proteger e desenvolver rotinas resilientes baseadas em Redis no backend Laravel do Engeapp.

> Esta skill cobre a camada de **driver/conexão** do Redis. Para a camada de **cache da aplicação** (padrão cache-aside, TTLs, invalidação por Observers), veja `laravel-cache-best-practices`. A convenção de nomenclatura de chaves e a orientação sobre Cache Tags são **únicas e compartilhadas** entre as duas skills (canônicas em `laravel-cache-best-practices`).

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
Use a **mesma convenção estruturada, separada por dois-pontos e com escopo** definida (canonicamente) em `laravel-cache-best-practices` — chaves no formato `domain:resource:identifier` (ex.: `payments:charge:123456`, `model:inverters:45:nominal_power`). Não invente um esquema paralelo.
* **Prefixo de app:** o `REDIS_PREFIX` configurado em `config/database.php` (ex.: `engeapp_database_`) **já prepende automaticamente** o slug da aplicação a toda chave. Portanto **não** repita o nome do app dentro da chave definida em código — deixe o prefixo por conta da config.
* **Regra:** Nunca use strings hardcoded para chaves Redis. Defina constantes ou métodos helper na classe de service/model que manipula o recurso.

```php
class PaymentService
{
    // Sem repetir o nome do app: o REDIS_PREFIX da config já o adiciona.
    private const KEY_PREFIX = 'payments:charge:';

    public function getCacheKey(int $chargeId): string
    {
        return self::KEY_PREFIX . $chargeId;
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

**Alternativa Laravel-native (`Cache::lock`) — ainda não usada no projeto.** Para regiões críticas mais genéricas, o Laravel oferece locks atômicos via `Cache::lock()`. No engeapp o store de cache padrão é `database` (ver Seção 6); o lock usa a `lock_connection` do store Redis (`config/cache.php`, store `redis`). Se for adotar, aponte para uma conexão Redis e sempre libere o lock em `finally`/closure:

```php
use Illuminate\Support\Facades\Cache;

// Requer um store com lock via Redis (ex.: Cache::store('redis')->lock(...))
$lock = Cache::store('redis')->lock('payment_lock_user_' . $userId, 10);

try {
    // Bloqueia por até 5 segundos aguardando o lock
    $lock->block(5, function () use ($paymentData) {
        // Lógica crítica de transação/pagamento aqui
    });
} catch (\Illuminate\Contracts\Cache\LockTimeoutException $e) {
    // Trata a falha de aquisição do lock de forma elegante
    throw new PaymentProcessingException('Processo já em execução. Tente novamente em alguns segundos.', 429);
}
```

### 4. Pipelines do Redis para Operações em Lote
Ao ler ou escrever múltiplas chaves, use `Redis::pipeline()` para enviar comandos em um único lote, reduzindo o tempo de ida e volta (RTT).

```php
use Illuminate\Support\Facades\Redis;

$results = Redis::pipeline(function ($pipe) use ($geckodriverPorts) {
    foreach ($geckodriverPorts as $port => $timestamp) {
        $pipe->hset('geckodriver_ports', $port, $timestamp);
    }
});
```

### 5. Failbacks de Conexão Resilientes e Tratamento de Exceções
Quedas de conexão com o Redis não devem derrubar a aplicação inteira (a menos que seja uma dependência rígida, como sessão ou rate-limiting).
* Capture `RedisException` ou exceções gerais dos drivers de cache.
* Implemente uma query de fallback no banco de dados ou valores padrão caso o servidor Redis fique offline.

```php
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Redis;
use RedisException;

public function getActivePorts(): array
{
    try {
        return Redis::hgetall('geckodriver_ports') ?: [];
    } catch (RedisException $e) {
        Log::error('Redis connection failure in CleanupGeckodriverPorts', [
            'exception' => $e->getMessage()
        ]);
        
        // Opção de fallback (ex: ler de uma fonte persistente alternativa ou retornar vazio)
        return [];
    }
}
```

### 6. Cache Tags e Invalidação
A orientação sobre Cache Tags é **única e canônica** em `laravel-cache-best-practices` ("Orientação única sobre Cache Tags") — siga-a e não a duplique/contradiga aqui.

> **Estado real do projeto:** o engeapp roda com `CACHE_STORE=database` por padrão (`config/cache.php` linha 18 e `.env.example` linha 45), driver que **NÃO suporta cache tags**. Não há nenhum uso de `Cache::tags()` no código hoje. O exemplo abaixo só é válido se a chamada apontar explicitamente para um store baseado em Redis/Memcached (`Cache::store('redis')`); usar tags no store `database`/`file` lança exceção.

Resumo aplicável ao Redis: o Redis não suporta tags nativamente; o Laravel as implementa via chaves de rastreamento adicionais, que consomem memória. Use tags apenas para grupos de **cardinalidade moderada** e **evite-as ao cachear milhões de chaves** (prefira invalidação por chave/prefixo). Sempre faça `flush()` **seletivo por tag**, nunca limpe o cache inteiro.

```php
use Illuminate\Support\Facades\Cache;

// Só funciona em um store que suporte tags (Redis/Memcached) — NÃO no store 'database' padrão do projeto.
$redisCache = Cache::store('redis');

// Armazenando com tags
$redisCache->tags(['solar-data', 'nasa-power'])->put($cacheKey, $data, now()->addDays(7));

// Invalidando por tag (flush seletivo)
$redisCache->tags(['solar-data'])->flush();
```

### 7. Ajuste do Horizon e das Filas
* Certifique-se de que a configuração de conexão em `horizon.php` corresponda à conexão persistente padrão.
* Evite despachar payloads enormes em jobs. Em vez disso, armazene o ID do Model no payload do job e busque os dados atualizados no banco de dados/cache dentro do job.
* Configure a conexão de fila do redis com um `retry_after` suficientemente alto (maior que o seu job de execução mais longa).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** execute comandos Redis lentos (como `KEYS *`, `FLUSHALL`, `FLUSHDB`) em produção. Use `SCAN` ou limpe o cache usando os comandos nativos de limpeza de cache do Laravel.
* **NÃO** use cache tags do Redis sem verificar o driver. Os drivers de cache database e file não suportam tags.
* **NÃO** escreva queries Redis brutas sem capturar exceções de conexão. Sempre assuma que o Redis pode ficar offline.
* **NÃO** serialize models Eloquent completos diretamente no Redis; use `json_encode` dos dados necessários ou a serialização padrão de model via jobs.
