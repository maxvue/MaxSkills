---
name: adonisjs-redis-cache-performance-best-practices
description: Use when configuring, querying, or troubleshooting Redis, implementing caching strategies, throttling requests, or optimizing performance in an AdonisJS application. Triggers on Redis service imports, Cache helper implementations, rate limiter middleware configurations, and performance tuning tasks.
---

# Melhores Práticas de Cache e Performance com Redis no AdonisJS

## Objetivo
Estabelecer diretrizes de código, padrões arquiteturais e padrões de implementação para o uso eficiente e resiliente do Redis como camada de cache e limitador de taxa (rate limiter) no AdonisJS v6.

## Pré-requisitos (instalação obrigatória)

> **Atenção:** Este projeto **não** inclui os pacotes abaixo por padrão. Todos os imports desta skill (`@adonisjs/redis/services/main`, `defineConfig` de `@adonisjs/redis`, `config/redis.ts`, `@adonisjs/limiter/services/main`, etc.) **assumem que estes pacotes já foram instalados e configurados**. Instale-os **antes** de aplicar qualquer exemplo:

* **`@adonisjs/redis`** — necessário para o serviço Redis, `defineConfig` e `config/redis.ts`. Instale e configure primeiro:
  ```bash
  node ace add @adonisjs/redis
  ```
* **`@adonisjs/limiter`** — necessário para o rate limiting da Seção 3 (`@adonisjs/limiter/services/main`, `limiter.use('redis', {...})`, `consume()`). O projeto **não** registra nenhum provider de limiter por padrão. Instale e configure:
  ```bash
  node ace add @adonisjs/limiter
  ```

## Instruções

### 1. Inicialização da Conexão
* **Sempre use o serviço oficial `@adonisjs/redis/services/main`** do provider do AdonisJS v6. Ele já gerencia o pool de conexões, múltiplas conexões nomeadas e o ciclo de vida (lazy connect/disconnect). **Nunca** instancie `new Redis({...})` manualmente a partir de `#config/redis` — isso duplica conexões e ignora o gerenciamento do framework.
* A configuração das conexões vive em `config/redis.ts` (helper `defineConfig` de `@adonisjs/redis`); o acesso é sempre via `redis` (conexão padrão) ou `redis.connection('nome')`.
* Defina `maxRetriesPerRequest: null` na configuração da conexão usada pelo BullMQ, evitando que quedas temporárias de conexão lancem exceções não tratadas.

### 2. Implementação do Padrão Cache-Aside (Cache sob demanda)
* Sempre implemente um bloco de fallback (`try/catch`) ao consultar o Redis. Se o servidor do Redis estiver fora do ar, a aplicação deve consultar diretamente o banco de dados principal ou API externa (padrão disjuntor/circuit breaker).
* Utilize tipos genéricos do TypeScript para garantir a segurança de tipo dos payloads em cache.
* Serialize com segurança os valores em cache usando `JSON.stringify()` e deserialize usando `JSON.parse()`. Envolva a desserialização em try-catch para lidar com dados legados ou corrompidos.
* Sempre defina um TTL (Time-To-Live) em itens cacheados para evitar dados desatualizados.

### 3. Rate Limiting Dinâmico para Integrações de API
* **Prefira o pacote oficial `@adonisjs/limiter`** para limitação de taxa. Ele oferece store Redis, `consume`/`attempt`, bloqueio por chave e middleware HTTP pronto — evitando reinventar contadores manuais.
* Use o limiter para proteger tanto rotas internas quanto chamadas a endpoints de terceiros (ex: Gemini via Vercel AI SDK, integrações de distribuidoras/concessionárias fotovoltaicas).
* Force limites por usuário, organização ou IP de forma dinâmica, criando limiters com `limiter.use('redis')` e chaves dinâmicas.
* Apenas quando precisar de uma janela totalmente customizada fora do `@adonisjs/limiter`, use comandos atômicos do Redis como `MULTI`, `INCR` e `EXPIRE` (ou scripts Lua) para evitar condições de corrida (race conditions).

### 4. Invalidação de Cache e Convenção de Chaves
* Use uma convenção clara para nomenclatura de chaves no Redis utilizando dois pontos: `nome_app:dominio:contexto:identificador` (ex: `engeapp:usina:geracao:12345`).
* Remova ativamente os itens do cache (usando `del()`) quando o recurso subjacente for atualizado (ex: atualização de metadados do usuário, expiração ou refresh de token).

## Exemplos

### Serviço de Cache Resiliente com Padrão Cache-Aside Genérico
Crie um serviço de cache unificado (`app/services/cache_service.ts`) que gerencie a serialização, TTLs e falhas de conexão de forma transparente:

```typescript
import redis from '@adonisjs/redis/services/main'
import logger from '@adonisjs/core/services/logger'

class CacheService {
  /**
   * Obtém item do cache ou executa o fallback e salva no cache.
   * O serviço oficial `@adonisjs/redis` gerencia conexão e pool; aqui
   * apenas envolvemos as chamadas em try/catch para resiliência.
   */
  async remember<T>(key: string, ttlSeconds: number, callback: () => Promise<T>): Promise<T> {
    try {
      const cachedValue = await redis.get(key)
      if (cachedValue) {
        logger.debug(`CacheService: Hit para a chave [${key}]`)
        return JSON.parse(cachedValue) as T
      }
    } catch (err) {
      // Redis indisponível ou dado corrompido: segue para o fallback (circuit breaker)
      logger.error(`CacheService: Erro ao ler a chave [${key}] - ${err.message}`)
    }

    // Cache Miss (ou Redis offline) - Executando callback
    const freshValue = await callback()

    try {
      await redis.set(key, JSON.stringify(freshValue), 'EX', ttlSeconds)
      logger.debug(`CacheService: Chave [${key}] salva com TTL de ${ttlSeconds}s`)
    } catch (err) {
      logger.error(`CacheService: Erro ao salvar a chave [${key}] - ${err.message}`)
    }

    return freshValue
  }

  /**
   * Força a invalidação de uma chave de cache
   */
  async invalidate(key: string): Promise<void> {
    try {
      await redis.del(key)
      logger.debug(`CacheService: Chave [${key}] invalidada`)
    } catch (err) {
      logger.error(`CacheService: Erro ao invalidar a chave [${key}] - ${err.message}`)
    }
  }
}

export default new CacheService()
```

### Rate Limiting Dinâmico para APIs Externas (Limitação de Taxa)
Prefira o pacote oficial `@adonisjs/limiter` (store Redis) em vez de contadores manuais. Ele encapsula `INCR`/`EXPIRE` atomicamente e expõe uma API resiliente:

```typescript
import limiter from '@adonisjs/limiter/services/main'

export class RateLimiterService {
  /**
   * Verifica/consome o limite de requisições para uma chave e ação específica.
   * Lança automaticamente E_TOO_MANY_REQUESTS (HTTP 429) quando excedido.
   */
  static async checkRateLimit(key: string, limit: number, windowSeconds: number): Promise<void> {
    const integrationLimiter = limiter.use('redis', {
      requests: limit,
      duration: `${windowSeconds} seconds`,
      // chave dinâmica por usuário/organização/IP, ex: `engeapp:gemini:org:42`
      blockDuration: `${windowSeconds} seconds`,
    })

    // consume() incrementa e lança ThrottleException (429) se o limite for excedido
    await integrationLimiter.consume(key)
  }
}
```

> Acesse a conexão Redis diretamente apenas se realmente precisar de uma janela customizada que o `@adonisjs/limiter` não cobre. Nesse caso, importe `redis` de `@adonisjs/redis/services/main` e use `MULTI`/`INCR`/`EXPIRE` — nunca acesse propriedades privadas de outro serviço via bracket access.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Não** permita que erros de conexão no Redis interrompam as requisições HTTP ou jobs em background. Envolva as chamadas em `try/catch` e forneça um fallback limpo para o banco de dados principal.
* **Não** armazene credenciais sensíveis, tokens OAuth descriptografados ou payloads excessivamente grandes no Redis sem criptografia apropriada ou estruturas adequadas.
* **Não** omita o tempo de expiração (TTL) ao salvar dados em cache, prevenindo o crescimento indefinido do uso de memória da máquina e dados obsoletos.
* **Não** defina parâmetros de conexão de forma estática no código (hardcoded). Configure as conexões em `config/redis.ts` (via `defineConfig` do `@adonisjs/redis`) e acesse-as sempre pelo serviço oficial `@adonisjs/redis/services/main`.
* **Não** instancie `new Redis(...)` (ioredis) manualmente nem acesse propriedades privadas de serviços via bracket access (`cacheService['client']`). Use o serviço gerenciado pelo framework e o `@adonisjs/limiter` para rate limiting.
