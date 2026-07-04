---
name: laravel-redis-integration-best-practices
description: Use when configuring, optimizing, or debugging Redis database connections, queues, sessions, cache stores, pub/sub channels, or distributed locks in Laravel. Triggers on Redis facade usage, phpredis/predis config, cache tags, connection exceptions, and Horizon queue backend configurations.
---

# Boas Práticas de Integração com Redis no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para configurar, otimizar, proteger e desenvolver rotinas resilientes baseadas em Redis no backend Laravel do Engeapp.

> Esta skill cobre a camada de **driver/conexão** do Redis. Para a camada de **cache da aplicação** (padrão cache-aside, TTLs, invalidação por Observers), veja `laravel-cache-best-practices`. A convenção de nomenclatura de chaves e a orientação sobre Cache Tags são **únicas e compartilhadas** entre as duas skills (canônicas em `laravel-cache-best-practices`).

## Instruções

### 1. Cliente Redis e Configuração
* **Cliente Padrão:** Sempre use `phpredis` como cliente padrão (por ser implementado em C e oferecer performance muito superior ao `predis`).
* **Conexões Persistentes:** Garanta que `REDIS_PERSISTENT` esteja habilitado em ambientes de produção para evitar o overhead de estabelecer uma nova conexão a cada requisição.
* **Timeout e Read Timeout:** Defina valores razoáveis para `timeout` e `read_timeout` (ex: 1.5s a 2.0s) para evitar que uma instância lenta do Redis bloqueie os web workers.

Exemplo de configuração em `config/database.php`:
```php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_') . '_database_'),
        'persistent' => env('REDIS_PERSISTENT', true),
        'timeout' => 1.5,
        'read_timeout' => 1.5,
    ],
    // ... configuração das conexões ...
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

### 3. Locks Distribuídos para Controle de Concorrência
Sempre use locks distribuídos para lógica de negócio crítica (ex: processamento de pagamentos, atualizações de estoque, criação concorrente de tickets) para evitar condições de corrida.
* Use `Cache::lock($name, $seconds)`, que utiliza o driver de lock do Redis.
* Utilize `block($seconds, callable)` para aguardar pelo lock se ele estiver atualmente em uso.
* Envolva a lógica em um bloco `try/finally` ou passe uma closure para `block()` para garantir que o lock seja sempre liberado.

```php
use Illuminate\Support\Facades\Cache;

$lock = Cache::lock('payment_lock_user_' . $userId, 10);

try {
    // Bloqueia por até 5 segundos aguardando pelo lock
    $lock->block(5, function () use ($paymentData) {
        // Lógica crítica de transação/pagamento aqui
    });
} catch (\Illuminate\Contracts\Cache\LockTimeoutException $e) {
    // Trata a falha de aquisição do lock de forma elegante
    throw new PaymentProcessingException('Process already in execution. Please try again in a few seconds.', 429);
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
A orientação sobre Cache Tags é **única e canônica** em `laravel-cache-best-practices` ("Orientação única sobre Cache Tags") — siga-a e não a duplique/contradiga aqui. Resumo aplicável ao Redis: o Redis não suporta tags nativamente; o Laravel as implementa via chaves de rastreamento adicionais, que consomem memória. Use tags apenas para grupos de **cardinalidade moderada** e **evite-as ao cachear milhões de chaves** (prefira invalidação por chave/prefixo). Sempre faça `flush()` **seletivo por tag**, nunca limpe o cache inteiro.

```php
use Illuminate\Support\Facades\Cache;

// Armazenando com tags (driver Redis/Memcached)
Cache::tags(['solar-data', 'nasa-power'])->put($cacheKey, $data, now()->addDays(7));

// Invalidando por tag (flush seletivo)
Cache::tags(['solar-data'])->flush();
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
