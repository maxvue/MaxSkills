---
name: adonisjs-meilisearch-best-practices
description: Use when configuring, optimizing, or debugging Meilisearch integration in an AdonisJS application, including client setup, Lucid ORM hooks for real-time document indexing, index settings configuration, search query execution, and pagination.
---

## Objetivo
Estabelecer padrões e melhores práticas para integrar, configurar e executar pesquisas eficientes e resilientes com Meilisearch no AdonisJS v6, utilizando BullMQ para indexação assíncrona em background.

## Instruções

## 1. Configuração do Ambiente e do Cliente

### Variáveis de Ambiente
Defina e valide as credenciais do Meilisearch no arquivo `start/env.ts`:
```typescript
MEILISEARCH_HOST: Env.schema.string({ format: 'url' }),
MEILISEARCH_KEY: Env.schema.string.optional(),
```

### Serviço do Meilisearch
Crie o arquivo `app/services/meilisearch_service.ts` para exportar uma instância única do cliente Meilisearch:
```typescript
import { MeiliSearch } from 'meilisearch'
import env from '#start/env'

const meilisearch = new MeiliSearch({
  host: env.get('MEILISEARCH_HOST'),
  apiKey: env.get('MEILISEARCH_KEY'),
})

export default meilisearch
```

## 2. Serialização do Model e Hooks do Lucid

### Interface Searchable
Qualquer model a ser indexado deve implementar um método para serializar seus campos de forma segura para fins de busca, evitando indexar colunas sensíveis.

```typescript
export default class Post extends BaseModel {
  // ... colunas

  /**
   * Serializa o model para o índice do Meilisearch
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
}
```

### Hooks Assíncronos do Lucid
**NÃO** chame a API do Meilisearch diretamente nos hooks do Lucid para evitar que problemas de latência ou quedas de conexão bloqueiem transações de banco de dados ou requisições HTTP. Em vez disso, dispache um job no BullMQ:

```typescript
import { afterSave, afterDelete } from '@adonisjs/lucid/orm'
import MeilisearchIndexJob from '#jobs/meilisearch_index_job'

export default class Post extends BaseModel {
  // ... campos

  @afterSave()
  static async syncToMeilisearch(post: Post) {
    await MeilisearchIndexJob.dispatch(post.id, 'Post', 'index')
  }

  @afterDelete()
  static async removeFromMeilisearch(post: Post) {
    await MeilisearchIndexJob.dispatch(post.id, 'Post', 'delete')
  }
}
```

## 3. Indexação Assíncrona via BullMQ

Crie o arquivo `app/jobs/meilisearch_index_job.ts` para processar as operações em segundo plano.

```typescript
import type { Job } from 'bullmq'
import { webhooksQueue } from '#services/queue_service' // Ou fila específica de busca
import meilisearch from '#services/meilisearch_service'
import Post from '#models/post' // Mapeie outros models conforme necessário

export interface MeilisearchJobData {
  id: string
  modelName: string
  action: 'index' | 'delete'
}

export default class MeilisearchIndexJob {
  static readonly queueName = 'meilisearch-indexing'

  static async dispatch(id: string, modelName: string, action: 'index' | 'delete') {
    // Usando uma fila dedicada ou a webhooksQueue existente
    await webhooksQueue.add('meilisearch-sync', { id, modelName, action })
  }

  static async handle(job: Job<MeilisearchJobData>) {
    const { id, modelName, action } = job.data
    const indexName = modelName.toLowerCase() + 's' // nomenclatura plural padrão

    if (action === 'delete') {
      await meilisearch.index(indexName).deleteDocument(id)
      return
    }

    // Resolva o Model por importação dinâmica ou mapeamento estático
    let modelInstance: any = null
    if (modelName === 'Post') {
      modelInstance = await Post.find(id)
    }

    if (!modelInstance) {
      return
    }

    const searchableData = typeof modelInstance.toSearchableObject === 'function'
      ? modelInstance.toSearchableObject()
      : modelInstance.toJSON()

    await meilisearch.index(indexName).addDocuments([searchableData])
  }
}
```

## 4. Configurando as Configurações do Índice (Ace Command)

Crie um Ace Command `commands/meilisearch_setup.ts` para configurar programaticamente as definições de pesquisa (stop words, atributos pesquisáveis, filtráveis, ordenáveis e tolerância a erros). Execute este comando durante os deploys.

```typescript
import { BaseCommand } from '@adonisjs/core/ace'
import meilisearch from '#services/meilisearch_service'

export default class MeilisearchSetup extends BaseCommand {
  static commandName = 'meilisearch:setup'
  static description = 'Configura e atualiza as definições dos índices do Meilisearch'

  async run() {
    this.logger.info('Configurando índices do Meilisearch...')

    await meilisearch.index('posts').updateSettings({
      searchableAttributes: ['title', 'content'],
      filterableAttributes: ['status'],
      sortableAttributes: ['createdAt'],
      rankingRules: [
        'words',
        'typo',
        'proximity',
        'attribute',
        'sort',
        'exactness',
      ],
    })

    this.logger.success('Definições do Meilisearch configuradas com sucesso!')
  }
}
```

## 5. Execução de Consultas e Paginação

Ao executar buscas, você pode retornar os documentos do Meilisearch diretamente (recomendado por velocidade) ou mapear os IDs de volta para as entidades do banco de dados se dados relacionais forem necessários.

```typescript
import meilisearch from '#services/meilisearch_service'
import Post from '#models/post'

export default class PostService {
  async search(query: string, page: number = 1, limit: number = 20) {
    const searchResults = await meilisearch.index('posts').search(query, {
      limit,
      offset: (page - 1) * limit,
      filter: 'status = active',
    })

    const ids = searchResults.hits.map((hit) => hit.id)
    
    // Opcionalmente, busque os models completos no Banco de Dados
    const posts = await Post.query()
      .whereIn('id', ids)
      .preload('solarCompany') // Exemplo de relacionamento
      // Garanta que os registros do DB mantenham a ordenação de relevância do Meilisearch
      .orderByRaw(`FIELD(id, ${ids.map(id => `'${id}'`).join(',')})`)

    return {
      data: posts,
      total: searchResults.estimatedTotalHits,
      page,
      limit,
    }
  }
}
```

## Restrições
- **Sem Chamadas Síncronas à API:** NÃO chame as APIs do Meilisearch de forma síncrona nos fluxos de requisição HTTP, controllers ou no ciclo de vida de transações de banco de dados. Sempre despache para o BullMQ.
- **Sem Indexação de Segredos:** NÃO serialize credenciais, senhas ou tokens criptografados para o Meilisearch. Defina um mapeamento explícito em `toSearchableObject()`.
- **Eficiência na Indexação em Lote:** Ao escrever rotinas de reindexação em lote, não consulte os registros do banco de dados um a um dentro de loops. Use paginação/lotes (chunking) ou streams de banco de dados.
- **Tratamento de Falhas Resiliente:** Implemente blocos try-catch e logs de erros caso as APIs do Meilisearch falhem, evitando que falhas de indexação interrompam ou quebrem o worker de filas em background.
