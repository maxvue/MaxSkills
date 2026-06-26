---
name: adonisjs-ai-agents-rag-vector-database-best-practices
description: Use when designing, implementing, or debugging Retrieval-Augmented Generation (RAG) workflows, vector database integrations (pgvector), and embedding generation in AdonisJS v6. Triggers on Vercel AI SDK embedding functions, raw SQL vector operations with Lucid ORM, and document chunking strategies.
---

# Melhores Práticas para Agentes de IA, RAG e Banco de Dados Vetorial no AdonisJS

## Objetivo
Estabelecer um padrão estruturado, performático e resiliente para a implementação de Geração Aumentada por Recuperação (RAG), armazenamento vetorial via PostgreSQL (`pgvector`), geração de embeddings usando o Vercel AI SDK (Google Gemini) e indexação assíncrona de blocos (chunks) via BullMQ em aplicações AdonisJS v6.

## Instruções

### 1. Migrações de Banco de Dados para pgvector
Antes de utilizar vetores, certifique-se de que a extensão `vector` do PostgreSQL está habilitada. Defina uma coluna de vetor com dimensão fixa (ex: `768` dimensões para o modelo `text-embedding-004`).

```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'document_chunks'

  async up() {
    // Habilita a extensão pgvector
    await this.db.rawQuery('CREATE EXTENSION IF NOT EXISTS vector')

    this.schema.createTable(this.tableName, (table) => {
      table.string('id').primary()
      table.string('document_id').notNullable()
      table.text('content').notNullable()
      table.integer('chunk_index').notNullable()
      // Define a coluna de vetor com dimensão 768
      table.specificType('embedding', 'vector(768)').nullable()
      table.jsonb('metadata').nullable()
      table.timestamp('created_at')
      table.timestamp('updated_at')
    })

    // Cria um índice HNSW para buscas de similaridade rápidas (usando distância de cosseno)
    this.schema.raw(`
      CREATE INDEX document_chunks_embedding_hnsw_idx 
      ON document_chunks 
      USING hnsw (embedding vector_cosine_ops)
    `)
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

### 2. Mapeamento de Model no Lucid ORM
O Lucid não analisa tipos de vetor nativamente. Mapeie a coluna de vetor usando um serializador personalizado ou trate-a como valores brutos (raw) para inserções e atualizações.

```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { ulid } from 'ulid'

export default class DocumentChunk extends BaseModel {
  static table = 'document_chunks'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: DocumentChunk) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare documentId: string

  @column()
  declare content: string

  @column()
  declare chunkIndex: number

  // A coluna de embedding armazenada como vetor array/string
  @column({
    serialize: (value: number[]) => value ? `[${value.join(',')}]` : null,
  })
  declare embedding: number[] | string | null

  @column()
  declare metadata: Record<string, any> | null

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime
}
```

### 3. Utilitário de Divisão de Texto (Chunking)
Implemente um algoritmo determinístico de divisão de texto por caracteres recursivos ou janela deslizante de tamanho fixo antes de gerar os embeddings para manter as fronteiras semânticas.

```typescript
export function chunkText(text: string, chunkSize: number = 800, chunkOverlap: number = 150): string[] {
  const chunks: string[] = []
  let startIndex = 0

  while (startIndex < text.length) {
    let endIndex = startIndex + chunkSize
    if (endIndex >= text.length) {
      chunks.push(text.slice(startIndex))
      break
    }

    // Tenta encontrar um espaço ou quebra de linha próximo ao limite para não cortar palavras
    const lastSpace = text.lastIndexOf(' ', endIndex)
    if (lastSpace > startIndex + chunkSize - chunkOverlap) {
      endIndex = lastSpace
    }

    chunks.push(text.slice(startIndex, endIndex).trim())
    startIndex = endIndex - chunkOverlap
  }

  return chunks
}
```

### 4. Geração de Embeddings (Vercel AI SDK & Google Gemini)
Utilize o provedor `@ai-sdk/google` com as funções `embed` ou `embedMany` para gerar embeddings.

```typescript
import { google } from '@ai-sdk/google'
import { embed, embedMany } from 'ai'

const model = google.embedding('text-embedding-004')

export async function generateSingleEmbedding(text: string): Promise<number[]> {
  const { embedding } = await embed({
    model,
    value: text,
  })
  return embedding
}

export async function generateBatchEmbeddings(texts: string[]): Promise<number[][]> {
  const { embeddings } = await embedMany({
    model,
    values: texts,
  })
  return embeddings
}
```

### 5. Busca por Similaridade Vetorial com Lucid
Para consultar blocos semelhantes no banco de dados, execute uma consulta bruta (raw query) mapeando a distância de cosseno (`<=>`), distância L2 (`<->`) ou o produto interno negativo (`<#>`).

```typescript
import DocumentChunk from '#models/document_chunk'

export async function searchSimilarChunks(
  queryEmbedding: number[],
  limit: number = 5,
  similarityThreshold: number = 0.7
): Promise<DocumentChunk[]> {
  const vectorStr = `[${queryEmbedding.join(',')}]`
  
  // similaridade de cosseno = 1 - distância de cosseno (<=>)
  const result = await DocumentChunk.query()
    .select('*')
    .select(
      DocumentChunk.db.raw('1 - (embedding <=> ?) as similarity', [vectorStr])
    )
    .whereRaw('1 - (embedding <=> ?) >= ?', [vectorStr, similarityThreshold])
    .orderByRaw('embedding <=> ? ASC', [vectorStr])
    .limit(limit)

  return result
}
```

### 6. Indexação Assíncrona de Blocos (Job BullMQ)
Evite realizar chamadas de API de embeddings de forma síncrona dentro de ações do controller. Transfira a carga de processamento para um Job do BullMQ.

```typescript
import type { Job } from 'bullmq'
import { documentIndexingQueue } from '#services/queue_service'
import { chunkText } from '#utils/chunker'
import { generateBatchEmbeddings } from '#services/embedding_service'
import DocumentChunk from '#models/document_chunk'

export interface IndexDocumentJobData {
  documentId: string
  content: string
  metadata?: Record<string, any>
}

export default class IndexDocumentJob {
  static readonly queueName = 'document-indexing'

  static async dispatch(data: IndexDocumentJobData) {
    await documentIndexingQueue.add('index', data)
  }

  static async handle(job: Job<IndexDocumentJobData>) {
    const { documentId, content, metadata } = job.data

    // 1. Divide o documento em blocos (chunks)
    const chunks = chunkText(content)
    if (chunks.length === 0) return

    // 2. Gera os embeddings em lote
    const embeddings = await generateBatchEmbeddings(chunks)

    // 3. Persiste no banco de dados
    const chunksToInsert = chunks.map((chunk, idx) => ({
      documentId,
      content: chunk,
      chunkIndex: idx,
      embedding: embeddings[idx],
      metadata: metadata || null,
    }))

    await DocumentChunk.createMany(chunksToInsert)
  }
}
```

## Restrições
- **Limites Síncronos:** Nunca gere embeddings de forma síncrona durante requisições HTTP. Para grandes volumes de dados, utilize sempre Jobs do BullMQ para evitar timeouts e travamentos da thread.
- **Otimização de Índices:** Sempre defina um índice vetorial (`HNSW` ou `IVFFlat`) nas migrações em ambientes produtivos. Evite consultar colunas vetoriais sem índice em tabelas com mais de 10.000 registros.
- **Tratamento de Falhas (Null Safety):** Certifique-se de que a geração de embeddings tenha tratamento com blocos try-catch para prevenir quedas no sistema caso a API do modelo de linguagem sofra rate limit ou fique temporariamente indisponível.
- **Consumo de Memória:** Limite o tamanho dos lotes ao usar `embedMany` (ex: no máximo 100 blocos de texto por chamada de API) para evitar exceções de Out-Of-Memory ou limitação agressiva da API do Gemini.
