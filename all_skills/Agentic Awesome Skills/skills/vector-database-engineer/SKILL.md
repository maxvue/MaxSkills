---
name: vector-database-engineer
description: "Expert in vector databases, embedding strategies, and semantic search implementation. Masters Pinecone, Weaviate, Qdrant, Milvus, and pgvector for RAG applications, recommendation systems, and similar"
risk: critical
source: community
date_added: "2026-02-27"
---

# Vector Database Engineer

Expert in vector databases, embedding strategies, and semantic search implementation. Masters Pinecone, Weaviate, Qdrant, Milvus, and pgvector for RAG applications, recommendation systems, and similarity search. Use PROACTIVELY for vector search implementation, embedding optimization, or semantic retrieval systems.

## Do not use this skill when

- The task is unrelated to vector database engineer
- You need a different domain or tool outside this scope

## Instructions

- Clarify goals, constraints, and required inputs.
- Apply relevant best practices and validate outcomes.
- Provide actionable steps and verification.
- If detailed examples are required, open `resources/implementation-playbook.md`.

## Capabilities

- Vector database selection and architecture
- Embedding model selection and optimization
- Index configuration (HNSW, IVF, PQ)
- Hybrid search (vector + keyword) implementation
- Chunking strategies for documents
- Metadata filtering and pre/post-filtering
- Performance tuning and scaling

## Use this skill when

- Building RAG (Retrieval Augmented Generation) systems
- Implementing semantic search over documents
- Creating recommendation engines
- Building image/audio similarity search
- Optimizing vector search latency and recall
- Scaling vector operations to millions of vectors

## Workflow

1. Analyze data characteristics and query patterns
2. Select appropriate embedding model
3. Design chunking and preprocessing pipeline
4. Choose vector database and index type
5. Configure metadata schema for filtering
6. Implement hybrid search if needed
7. Optimize for latency/recall tradeoffs
8. Set up monitoring and reindexing strategies

## Best Practices

- Choose embedding dimensions based on use case (384-1536)
- Implement proper chunking with overlap
- Use metadata filtering to reduce search space
- Monitor embedding drift over time
- Plan for index rebuilding
- Cache frequent queries
- Test recall vs latency tradeoffs

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

### Index Fine-Tuning Guidelines (HNSW & Quantization)

Consulte o guia completo em `resources/implementation-playbook.md` para benchmarks e rotinas em Python com hnswlib/faiss.

#### Matriz de Hiperparâmetros HNSW:
- **`M` (conexões bidirecionais por nó):**
  - Textos/busca geral: `16` (padrão)
  - Alta dimensionalidade / precisão crítica: `32` a `64`
- **`efConstruction` (profundidade de exploração na indexação):**
  - Padrão: `64` a `128`
  - Alta revocação (>98% recall): `200` a `400`
- **`efSearch` (profundidade de exploração em runtime na query):**
  - Baixa latência (<5ms): `16` a `32`
  - Balanceado: `64`
  - Máxima revocação: `128` a `256`

#### Estratégias de Quantização:
- **FP16:** 50% economia de memória, perda desprezível de recall (<0.1%).
- **INT8 (Scalar Quantization):** 75% economia de memória, perda <1% de recall.
- **Product Quantization (PQ):** 85-95% economia de memória, ideal para bases > 10M de vetores em RAM limitada.
