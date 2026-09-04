---
name: mermaid-diagrammer
description: "Author and render declarative Mermaid diagrams for system architecture, sequence flows, entity relationships, and state machines. Use when visualizing code flows, documenting technical specifications, or generating architecture diagrams."
risk: safe
source: curated-youtube
---
# Mermaid Diagramming Guidelines

## When to Use
- Visualizing application architectures, distributed service interactions, or module boundaries.
- Documenting request/response sequences between frontend, backend, queues, and third-party APIs.
- Creating clean flowchart state diagrams directly in markdown artifacts.

## Syntax Patterns

### 1. Flowchart / Arquitetura
```mermaid
flowchart TD
    User([Usuário]) -->|HTTP POST /api/v1/auth| Gateway[API Gateway / Nginx]
    Gateway --> AuthSvc[Serviço de Autenticação]
    AuthSvc --> Redis[(Redis Token Cache)]
    AuthSvc --> DB[(PostgreSQL Master)]
```

### 2. Diagrama de Sequência (Sequence Diagram)
```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente Web (Vue 3)
    participant S as Servidor API (Laravel)
    participant Q as Redis Queue
    participant W as Worker Horizon

    C->>S: POST /api/pedidos/checkout
    S->>S: Valida payload e autenticação
    S->>Q: Dispatch ProcessOrderJob
    S-->>C: 202 Accepted (jobId)
    Q->>W: Consome evento
    W->>W: Processa gateway de pagamento
```

### 3. Diagrama de Entidade-Relacionamento (ERD)
```mermaid
erDiagram
    TENANT ||--o{ USER : contains
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : includes
```

## Boas Práticas
- Use aspas duplas em rótulos com caracteres especiais ou parênteses: `id["Texto (Info)"]`.
- Evite quebras manuais com `<br/>` em nós complexos; prefira nós estruturados e subgraphs.
