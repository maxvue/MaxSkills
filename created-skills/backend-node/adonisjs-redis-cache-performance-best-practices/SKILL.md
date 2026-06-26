---
name: adonisjs-redis-cache-performance-best-practices
description: Use when configuring, querying, or troubleshooting Redis, implementing caching strategies, throttling requests, or optimizing performance in an AdonisJS application. Triggers on Redis service imports, Cache helper implementations, rate limiter middleware configurations, and performance tuning tasks.
---

# Melhores Práticas de Cache e Performance com Redis no AdonisJS

## Objetivo
Estabelecer diretrizes de código, padrões arquiteturais e padrões de implementação para o uso eficiente e resiliente do Redis como camada de cache e limitador de taxa (rate limiter) no AdonisJS v6.

## Instruções

### 1. Inicialização da Conexão
* Reutilize a configuração centralizada em `#config/redis`.
* Inicialize a conexão de forma resiliente utilizando o `ioredis`. Se preferir um gerenciador global, exporte uma instância singleton.
* Defina `maxRetriesPerRequest: null` ao configurar o Redis para o BullMQ ou uso geral, evitando que quedas temporárias de conexão lancem exceções não tratadas.

### 2. Implementação do Padrão Cache-Aside (Cache sob demanda)
* Sempre implemente um bloco de fallback (`try/catch`) ao consultar o Redis. Se o servidor do Redis estiver fora do ar, a aplicação deve consultar diretamente o banco de dados principal ou API externa (padrão disjuntor/circuit breaker).
* Utilize tipos genéricos do TypeScript para garantir a segurança de tipo dos payloads em cache.
* Serialize com segurança os valores em cache usando `JSON.stringify()` e deserialize usando `JSON.parse()`. Envolva a desserialização em try-catch para lidar com dados legados ou corrompidos.
* Sempre defina um TTL (Time-To-Live) em itens cacheados para evitar dados desatualizados.

### 3. Rate Limiting Dinâmico para Integrações de API
* Use chaves Redis com tempo de expiração por janela de tempo para implementar limitação de taxa ao contactar endpoints de terceiros (ex: Meta/Instagram Graph API, Gemini).
* Force limites por agência, usuário ou IP de forma dinâmica.
* Use comandos atômicos do Redis como `MULTI`, `INCR` e `EXPIRE` (ou scripts Lua) para evitar condições de corrida (race conditions).

### 4. Invalidação de Cache e Convenção de Chaves
* Use uma convenção clara para nomenclatura de chaves no Redis utilizando dois pontos: `nome_app:dominio:contexto:identificador` (ex: `socialmedia:instagram:token:12345`).
* Remova ativamente os itens do cache (usando `del()`) quando o recurso subjacente for atualizado (ex: atualização de metadados do usuário, expiração ou refresh de token).

## Exemplos

### Serviço de Cache Resiliente com Padrão Cache-Aside Genérico
Crie um serviço de cache unificado (`app/services/cache_service.ts`) que gerencie a serialização, TTLs e falhas de conexão de forma transparente:

```typescript
import Redis from 'ioredis'
import redisConfig from '#config/redis'
import logger from '@adonisjs/core/services/logger'

class CacheService {
  private client: Redis | null = null
  private isConnected = false

  constructor() {
    this.init()
  }

  private init() {
    try {
      const { connection } = redisConfig
      this.client = new Redis({
        host: connection.host,
        port: connection.port,
        password: connection.password,
        maxRetriesPerRequest: connection.maxRetriesPerRequest,
        retryStrategy: (times) => Math.min(times * 100, 3000), // Estratégia de tentativa com atraso gradual
      })

      this.client.on('connect', () => {
        this.isConnected = true
        logger.info('CacheService: Conectado ao Redis')
      })

      this.client.on('error', (err) => {
        this.isConnected = false
        logger.error(`CacheService: Erro no Redis - ${err.message}`)
      })
    } catch (error) {
      logger.error(`CacheService: Falha ao inicializar o Redis - ${error.message}`)
    }
  }

  /**
   * Obtém item do cache ou executa o fallback e salva no cache
   */
  async remember<T>(key: string, ttlSeconds: number, callback: () => Promise<T>): Promise<T> {
    if (!this.isConnected || !this.client) {
      logger.warn(`CacheService: Redis offline. Ignorando cache para a chave [${key}]`)
      return callback()
    }

    try {
      const cachedValue = await this.client.get(key)
      if (cachedValue) {
        logger.debug(`CacheService: Hit para a chave [${key}]`)
        return JSON.parse(cachedValue) as T
      }
    } catch (err) {
      logger.error(`CacheService: Erro ao ler a chave [${key}] - ${err.message}`)
    }

    // Cache Miss - Executando callback
    const freshValue = await callback()

    try {
      if (this.isConnected && this.client) {
        await this.client.set(key, JSON.stringify(freshValue), 'EX', ttlSeconds)
        logger.debug(`CacheService: Chave [${key}] salva com TTL de ${ttlSeconds}s`)
      }
    } catch (err) {
      logger.error(`CacheService: Erro ao salvar a chave [${key}] - ${err.message}`)
    }

    return freshValue
  }

  /**
   * Força a invalidação de uma chave de cache
   */
  async invalidate(key: string): Promise<void> {
    if (!this.isConnected || !this.client) return
    try {
      await this.client.del(key)
      logger.debug(`CacheService: Chave [${key}] invalidada`)
    } catch (err) {
      logger.error(`CacheService: Erro ao invalidar a chave [${key}] - ${err.message}`)
    }
  }
}

export default new CacheService()
```

### Rate Limiting Dinâmico para APIs Externas (Limitação de Taxa)
Implementando limitadores de taxa customizados para requisições de integração externas:

```typescript
import cacheService from '#services/cache_service'
import { Exception } from '@adonisjs/core/exceptions'

export class RateLimiterService {
  /**
   * Verifica se o limite de requisições foi excedido para uma chave e ação específica
   */
  static async checkRateLimit(key: string, limit: number, windowSeconds: number): Promise<void> {
    const redis = cacheService['client']
    const isConnected = cacheService['isConnected']

    if (!isConnected || !redis) {
      // Fallback: ignora o rate limit e prossegue se o serviço de cache estiver fora do ar
      return
    }

    const currentCount = await redis.incr(key)
    if (currentCount === 1) {
      await redis.expire(key, windowSeconds)
    }

    if (currentCount > limit) {
      throw new Exception('Limite de requisições excedido para a integração. Tente novamente mais tarde.', {
        status: 429,
        code: 'E_INTEGRATION_RATE_LIMIT',
      })
    }
  }
}
```

## Restrições
* **Não** permita que erros de conexão no Redis interrompam as requisições HTTP ou jobs em background. Envolva as chamadas em `try/catch` e forneça um fallback limpo para o banco de dados principal.
* **Não** armazene credenciais sensíveis, tokens OAuth descriptografados ou payloads excessivamente grandes no Redis sem criptografia apropriada ou estruturas adequadas.
* **Não** omita o tempo de expiração (TTL) ao salvar dados em cache, prevenindo o crescimento indefinido do uso de memória da máquina e dados obsoletos.
* **Não** defina parâmetros de conexão de forma estática no código (hardcoded). Sempre importe as configurações a partir do arquivo `#config/redis`.
