---
name: adonisjs-meilisearch-sync-bullmq-best-practices
description: Use when designing, implementing, reviewing, or debugging asynchronous Meilisearch index synchronization patterns in AdonisJS, dispatching indexing jobs via BullMQ from Lucid ORM hooks, or handling search reindexing queue errors.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer padrões robustos para indexação assíncrona entre models do Lucid ORM e o Meilisearch via BullMQ no AdonisJS v6. Isso garante que as transações do banco de dados permaneçam desbloqueadas pela latência de APIs externas, que os jobs façam retry de forma resiliente em falhas de rede temporárias, e que as operações de reindexação em massa sejam altamente performáticas.

## Instruções

### 1. Hooks Não-Bloqueantes do Lucid ORM
Não chame a API do Meilisearch de forma síncrona dentro dos hooks do model. Fazer isso bloqueia as transações do banco de dados e atrasa as respostas HTTP. Em vez disso, despache um job em background do BullMQ dentro dos hooks `@afterSave` e `@afterDelete`.

```typescript
import { afterSave, afterDelete } from '@adonisjs/lucid/orm'
import { BaseModel } from '@adonisjs/lucid/orm'
import MeilisearchSyncJob from '#jobs/meilisearch_sync_job'

export default class Post extends BaseModel {
  // Campos e colunas do model...

  /**
   * Serializa os atributos do model de forma segura para indexação de busca.
   * Evite indexar campos sensíveis como senhas, tokens privados, etc.
   */
  toSearchableObject() {
    return {
      id: this.id,
      title: this.title,
      content: this.content,
      status: this.status,
      createdAt: this.createdAt.toISODate(),
    }
  }

  @afterSave()
  static async syncToMeilisearch(post: Post) {
    await MeilisearchSyncJob.dispatch(post.id, 'Post', 'index')
  }

  @afterDelete()
  static async removeFromMeilisearch(post: Post) {
    await MeilisearchSyncJob.dispatch(post.id, 'Post', 'delete')
  }
}
```

### 2. Estrutura do Job e Processamento Polimórfico
Implemente um único job tipado para processar tarefas de sincronização de múltiplos models. Use o sistema de import dinâmico ou um mapa estático de models para resolver a classe do model com base na string `modelName`.

```typescript
// app/jobs/meilisearch_sync_job.ts
import { Queue, type Job } from 'bullmq'
import redisConfig from '#config/redis'
import meilisearch from '#services/meilisearch_service'
import logger from '@adonisjs/core/services/logger'

// Importe os models de forma estática ou dinâmica
import Post from '#models/post'

const MODEL_MAP: Record<string, any> = {
  Post: Post,
  // Adicione outros models pesquisáveis aqui...
}

export interface MeilisearchSyncData {
  id: string | number
  modelName: string
  action: 'index' | 'delete'
}

const QUEUE_NAME = 'meilisearch-sync-queue'
const { connection } = redisConfig

export const meilisearchSyncQueue = new Queue<MeilisearchSyncData>(QUEUE_NAME, { connection })

export default class MeilisearchSyncJob {
  static readonly queueName = QUEUE_NAME

  static async dispatch(id: string | number, modelName: string, action: 'index' | 'delete') {
    await meilisearchSyncQueue.add(
      'sync',
      { id, modelName, action },
      {
        attempts: 5,
        backoff: { type: 'exponential', delay: 2000 }, // 2s, 4s, 8s, 16s, 32s
        removeOnComplete: { count: 100, age: 24 * 3600 },
        removeOnFail: { count: 500, age: 7 * 24 * 3600 },
      }
    )
  }

  static async handle(job: Job<MeilisearchSyncData>) {
    const { id, modelName, action } = job.data
    const indexName = modelName.toLowerCase() + 's' // Nomenclatura padrão de índice no plural

    const Model = MODEL_MAP[modelName]
    if (!Model) {
      logger.error(`[MeilisearchSync] Unsupported model: ${modelName}. Job discarded.`)
      await job.discard()
      throw new Error(`Unsupported model: ${modelName}`)
    }

    if (action === 'delete') {
      try {
        await meilisearch.index(indexName).deleteDocument(id)
      } catch (err) {
        // Se o documento não existe no Meilisearch, não é um erro fatal passível de retry
        if (err.code === 'document_not_found') {
          return
        }
        throw err
      }
      return
    }

    // Resolve a instância a partir do banco de dados
    const instance = await Model.find(id)
    if (!instance) {
      // Registro deletado antes do job rodar: descarta e remove do índice
      await meilisearch.index(indexName).deleteDocument(id).catch(() => {})
      await job.discard()
      return
    }

    const data = typeof instance.toSearchableObject === 'function'
      ? instance.toSearchableObject()
      : instance.toJSON()

    await meilisearch.index(indexName).addDocuments([data])
  }
}
```

### 3. Classificação Resiliente de Erros e Retries
No handler do job, capture e trate os erros com cuidado. Não silencie falhas de rede (para que o BullMQ possa refazer o retry delas), mas descarte os jobs em falhas irrecuperáveis de validação/formatação.

```typescript
// app/jobs/meilisearch_sync_job.ts (Continuação)
static async handle(job: Job<MeilisearchSyncData>) {
  try {
    // ... lógica de execução ...
  } catch (error) {
    // Timeouts temporários de Rede/HTTP ou sobrecarga do Meilisearch (5xx/429) -> Propaga para retry
    if (error.status === 429 || (error.status >= 500 && error.status < 600) || error.code === 'ENOTFOUND') {
      logger.warn({ err: error, jobId: job.id }, '[MeilisearchSync] Temporary sync failure. Retrying...')
      throw error
    }

    // Erros permanentes (400 Bad Request, index not found, divergência de settings, credenciais inválidas)
    // Descarta o job para evitar retries em loop desperdiçados, registra o alerta
    logger.error({ err: error, jobId: job.id }, '[MeilisearchSync] Fatal index synchronization error.')
    await job.discard()
    throw error
  }
}
```

### 4. Reindexação em Massa de Alta Performance
Ao fazer atualizações em massa ou reindexar todo o banco de dados (ex: via Ace Commands), não busque e envie os documentos um a um dentro de um loop. Em vez disso, recupere os registros do banco usando chunking e despache-os para o Meilisearch em arrays (lotes).

```typescript
// app/commands/meilisearch_reindex.ts
import { BaseCommand } from '@adonisjs/core/ace'
import meilisearch from '#services/meilisearch_service'
import Post from '#models/post'

export default class MeilisearchReindex extends BaseCommand {
  static commandName = 'meilisearch:reindex'
  static description = 'Perform high-performance bulk reindexing of all models to Meilisearch'

  async run() {
    this.logger.info('Starting Meilisearch bulk reindexing for Posts...')

    const index = meilisearch.index('posts')
    const CHUNK_SIZE = 500

    // Busca e indexa em chunks para gerenciar memória e reduzir a sobrecarga da API HTTP
    await Post.query().chunk(CHUNK_SIZE, async (posts) => {
      const payload = posts.map((post) => {
        return typeof post.toSearchableObject === 'function'
          ? post.toSearchableObject()
          : post.toJSON()
      })

      // Envia o chunk inteiro em uma única requisição de rede
      await index.addDocuments(payload)
      this.logger.success(`Indexed chunk of ${posts.length} posts.`)
    })

    this.logger.success('Bulk reindexing completed successfully!')
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem APIs Síncronas nos Hooks:** Nunca chame os clients HTTP do Meilisearch dentro dos hooks do Lucid ORM ou de threads de controller de forma síncrona.
- **Tratamento Gracioso de Erros:** Garanta que erros temporários de rede sejam relançados para retries do BullMQ, enquanto erros de schema/validação são descartados (`job.discard()`) para evitar poluição da fila.
- **Atualizações em Lote:** Não despache jobs individuais do BullMQ durante operações em massa como importações de dados ou reindexação via linha de comando. Use atualizações em massa baseadas em array (`addDocuments`) diretamente.
