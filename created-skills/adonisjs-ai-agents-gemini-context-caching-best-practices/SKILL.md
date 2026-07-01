---
name: adonisjs-ai-agents-gemini-context-caching-best-practices
description: Use when implementing, reviewing, or configuring Gemini context caching, managing cache lifespans (TTL), or optimizing token costs and latency for large prompts, brand guidelines, and system instructions in AdonisJS v6. Triggers on geminiContextCache, createCache, cachedContent, and large prompt agent configurations.
---

## Objetivo
Estabelecer as melhores práticas para a implementação e gerenciamento de Caching de Contexto explícito do Gemini em serviços backend do AdonisJS v6. Isso é feito utilizando o SDK oficial do Google Gen AI (`@google/genai`) para operações de ciclo de vida do cache em conjunto com o Vercel AI SDK (`@ai-sdk/google` / `ai`) para execuções de agentes, reduzindo os custos de tokens de prompt e a latência de execução.

## Instruções

## 1. Estratégia de Caching Explícito
- **Quando utilizar:** Use o caching explícito quando as instruções do sistema, diretrizes de marca, personas ou documentos excederem **32.768 tokens** (para modelos Gemini Pro) ou **1.024/4.096 tokens** (para modelos Gemini Flash) e forem reutilizados em múltiplas execuções sequenciais de agentes.
- **Evitar recriação excessiva:** Não crie um novo cache para cada prompt individual. Armazene no cache a base estática (ex: diretrizes de marca + instrução do sistema) e passe a requisição dinâmica (ex: "Revise este texto") como a mensagem final do usuário.

## 2. Criação do Cache com `@google/genai`
Como o Vercel AI SDK não suporta nativamente a criação de caches de contexto do Gemini, você deve utilizar o SDK oficial e unificado do Google Gen AI (`@google/genai`) para registrar o cache primeiro.

### Instalação
Garanta que tanto o Vercel AI SDK quanto o Google Gen AI SDK estejam instalados:
```bash
npm install @google/genai @ai-sdk/google ai zod
```

### Implementação do Serviço Gerenciador de Cache
Crie uma classe de serviço para lidar com o ciclo de vida dos seus caches de contexto do Gemini, utilizando o Redis ou o banco de dados para reutilizar o ID do cache:

```typescript
// app/services/gemini_cache_service.ts
import { GoogleGenAI } from '@google/genai'
import { createHash } from 'node:crypto'
import env from '#start/env'
import redis from '@adonisjs/redis/services/main'

export class GeminiCacheService {
  private static ai = new GoogleGenAI({ apiKey: env.get('GEMINI_API_KEY') })

  /**
   * Gera uma chave única baseada no hash do conteúdo do prompt para armazenar o ID do cache no Redis
   */
  private static getContentHash(contents: string): string {
    // Use SHA-256 para evitar colisões de chave de cache em prompts grandes
    return createHash('sha256').update(contents).digest('hex')
  }

  /**
   * Recupera um cache ativo ou cria um novo se estiver expirado ou inexistente
   */
  public static async getOrCreateCache(
    model: string,
    displayName: string,
    systemInstruction: string,
    ttlSeconds: number = 300
  ): Promise<string> {
    const hash = this.getContentHash(systemInstruction)
    const redisKey = `gemini_cache:${hash}`

    // 1. Verifica se o cache existe no Redis
    const cachedName = await redis.get(redisKey)
    if (cachedName) {
      return cachedName
    }

    // 2. Cria o cache explícito via Google Gen AI SDK
    const cache = await this.ai.caches.create({
      model: model.startsWith('models/') ? model : `models/${model}`,
      config: {
        displayName,
        ttl: `${ttlSeconds}s`,
        contents: [
          {
            role: 'user',
            parts: [{ text: systemInstruction }]
          }
        ]
      }
    })

    // `cache.name` pode vir undefined no tipo retornado por @google/genai; valide antes de usar
    if (!cache.name) {
      throw new Error('Falha ao criar o cache de contexto do Gemini: nome de recurso ausente')
    }

    // 3. Salva o nome de recurso do Cache (ex: 'cachedContents/xyz123') no Redis
    // Define a expiração no Redis um pouco antes do TTL do cache do Gemini (ex: TTL - 10s)
    const redisTtl = Math.max(ttlSeconds - 10, 10)
    await redis.setex(redisKey, redisTtl, cache.name)

    return cache.name
  }
}
```

## 3. Execução de Requisições do Agente Usando Contexto Cacheado
Ao despachar a geração de texto, passe o nome do cache recuperado (`cachedContents/{CACHE_ID}`) para o provedor Google usando `providerOptions`:

```typescript
// app/ai/agent_ai_request.ts
import { generateText } from 'ai'
import { google } from '@ai-sdk/google'
import { GeminiCacheService } from '#services/gemini_cache_service'

interface ExecOptions {
  agentName: string
  model: string
  systemPrompt: string
  prompt: string
  clientId: string
}

export async function executeAgentWithCache(opts: ExecOptions) {
  // 1. Obtém ou cria a referência de conteúdo cacheado
  const cacheName = await GeminiCacheService.getOrCreateCache(
    opts.model,
    `agent_${opts.agentName}_client_${opts.clientId}`,
    opts.systemPrompt,
    3600 // Cache por 1 hora
  )

  // 2. Executa a geração de texto referenciando o cache
  const result = await generateText({
    model: google(opts.model),
    prompt: opts.prompt,
    providerOptions: {
      google: {
        cachedContent: cacheName,
      },
    },
    onStepFinish: ({ usage, providerMetadata }) => {
      // 3. Monitora os tokens cacheados para análise de custos
      const cacheRead = ((providerMetadata as any)?.google?.cachedContentTokenCount as number) ?? 0
      const promptNonCached = Math.max((usage.inputTokens ?? 0) - cacheRead, 0)
      
      // Salvar métricas...
    }
  })

  return result
}
```

## 4. Gerenciamento de Custos e Métricas
Caches explícitos cobram uma taxa diferente para tokens de entrada dependendo se foram servidos a partir do cache ou não. Sempre monitore e registre ambos os tipos de tokens:
- **Custo de entrada cacheada:** Significativamente mais barato (frequentemente 10% do custo normal de tokens de entrada).
- **Custo de entrada não cacheada:** Taxa cheia do modelo.
- **Custo de armazenamento de cache:** Caches explícitos cobram uma pequena taxa por GB por hora (calcule se for manter caches ativos por horas/dias).

## Restrições
- **Restrição de Requisições Subsequentes:** Ao passar um parâmetro `cachedContent` para o Gemini, você **não pode** especificar `systemInstruction`, `tools` ou `toolConfig` na chamada do `generateText` se estes já tiverem sido definidos dentro do cache. Garanta que estes componentes estejam incluídos diretamente na etapa de criação do cache.
- Não instancie novos caches diretamente dentro de Controllers; delegue a verificação e o registro de cache a um Serviço centralizado (ex: `GeminiCacheService`).
- Não configure TTLs extremamente longos sem um contexto específico de usuário; use o padrão de 5 minutos (`300s`) ou 1 hora (`3600s`) para evitar cobranças excessivas de armazenamento.
- Sempre verifique a quantidade mínima de tokens antes de tentar registrar um cache para evitar erros da API (o Gemini rejeita a criação do cache se a quantidade de tokens for muito baixa).
