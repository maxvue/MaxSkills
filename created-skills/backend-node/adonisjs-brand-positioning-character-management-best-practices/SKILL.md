---
name: adonisjs-brand-positioning-character-management-best-practices
description: Use when creating, modifying, reviewing, or debugging controllers, models, validators, or services related to brand positioning, character profiles, agent persona configurations, reference image uploads, and topic lists in AdonisJS. Triggers on files modifying BrandPositioning, SocialMediaCharacter, character controllers, and related backend logic.
---

# Boas Práticas de Posicionamento de Marca & Gerenciamento de Personagens em AdonisJS

## Objetivo
Estabelecer diretrizes padrão de desenvolvimento para o gerenciamento de posicionamento de marca, perfis de personagens e sua integração com os fluxos de agentes de IA no AdonisJS. Garante isolamento estrito de dados por tenant, uploads de arquivos seguros via AdonisJS Drive e validações de requisições robustas com VineJS.

## Instruções

### 1. Configurações de Models no Lucid ORM
- **Chaves Primárias:** Use ULIDs para todas as chaves primárias. Ative `static selfAssignPrimaryKey = true`.
- **Geração Automática de ULID:** Use o hook `@beforeCreate()` para atribuir um novo ULID.
- **Campos de Auditoria:** Inclua `createdAt` e `updatedAt` usando `@column.dateTime`.
- **Chave do Tenant:** Sempre vincule os models à empresa/tenant com `solarCompanyId` (nome da coluna `solar_company_id`).

#### Estrutura do Model BrandPositioning
- Tabela: `brand_positionings`
- Colunas Chave:
  - `solarCompanyId`: string (FK para `solar_company`)
  - `companyName`: string
  - `activities`, `mission`, `values`, `archetype`, `toneOfVoice`, `languageGuidelines`, `targetAudience`, `additionalInfo`: string/text (nulo por padrão)
  - `contentPillars`: Record<string, any> (coluna JSON com funções prepare/consume para serializar/deserializar)
  - `colorPalette`: Record<string, any> (coluna JSON)
  - `assets`: Record<string, any> (coluna JSON)

#### Estrutura do Model SocialMediaCharacter
- Tabela: `social_media_characters`
- Colunas Chave:
  - `solarCompanyId`: string (FK para `solar_company`)
  - `name`: string
  - `description`: string (traços físicos/detalhes da persona)
  - `images`: Record<string, any> (array JSON que representa as fotos: `{ id, path, name, url }`)
  - `isActive`: boolean
- Relacionamentos:
  - `@manyToMany(() => CalendarEventScriptDetail)` mapeando a tabela pivô `calendar_event_script_detail_character`.

### 2. Validação de Requisições com VineJS
Defina validadores de esquema estritos para os controllers:
- Para BrandPositioning:
  - `company_name`: `vine.string().maxLength(255).nullable().optional()`
  - `content_pillars` & `color_palette`: Arrays ou objetos JSON.
- Para SocialMediaCharacter:
  - `name`: `vine.string().maxLength(255)`
  - `description`: `vine.string().nullable().optional()`
  - `is_active`: `vine.boolean().optional()`

### 3. Ações do Controller & Isolamento Multi-Tenancy
- **Contexto do X-Client-Id:** Identifique o tenant/empresa a partir de `HttpContext.clientId` (mapeado como `solarCompanyId`).
- **Filtragem de Dados:** Consulte `BrandPositioning` ou `SocialMediaCharacter` correspondendo a `solar_company_id = solarCompanyId`.
- **Guard de Autorização:** Para qualquer manipulação de recurso (atualização, exclusão, upload), verifique se o `solarCompanyId` do model corresponde ao ID do cliente da requisição. Lance um erro `403 Forbidden` se forem diferentes:
  ```typescript
  if (character.solarCompanyId !== clientId) {
    throw Object.assign(new Error('Acesso negado.'), { status: 403 })
  }
  ```
- **Upsert do Posicionamento de Marca:** Use `updateOrCreate` chaveado no `solarCompanyId`.

### 4. Upload de Arquivos (AdonisJS Drive)
- **Estrutura de Diretórios:** Salve fotos de referência de personagens em `uploads/characters/`. Salve assets de marca em `uploads/brand/assets/`.
- **Validação de Arquivo:** Restrinja o tamanho do arquivo (ex: 10MB) e as extensões permitidas (`jpg, jpeg, png, gif, webp, svg`).
- **Movendo Arquivos:** Use `file.move(app.publicPath('uploads/...'), { name: fileName })` com um nome ULID único.
- **Mutação de Array:** Mescle novos assets/imagens nos arrays JSON existentes e salve.
- **Exclusão Física:** Na exclusão, limpe o disco removendo os arquivos via `node:fs/promises` (`unlink`).

### 5. Ingestão em Prompts de IA (Vercel AI SDK)
- Formate as diretrizes da marca e as descrições dos personagens em um contexto Markdown estruturado antes de fornecê-lo ao Vercel AI SDK.
- Use a tool `GetBrandPositioning` para obter:
  - Missão, valores, arquétipo, tom de voz, pilares de conteúdo, paleta de cores, estilo gráfico.
  - Perfis de personagens/porta-vozes ativos (id, nome, descrição).
- Formate personagens como:
  ```markdown
  * Character ID: [id] - Name: [name]
    Description (Physical/Tone): [description]
  ```
- Guard rails: Se a lista de personagens estiver vazia, instrua o LLM a não inventar personagens.

## Restrições
- **SEM Tenant Leakage:** Nunca execute consultas ou atualizações sem verificar ou filtrar por `solarCompanyId`.
- **SEM IDs Simples:** Não use IDs inteiros com autoincremento. Todos os identificadores devem usar ULID.
- **SEM Exposição Direta do Caminho do Arquivo:** Salve uploads em uma pasta pública estruturada (ex: `/uploads/...`) e armazene os nomes originais dos arquivos de forma segura.
- **SEM Prompts Hardcoded:** Prompts de IA devem solicitar dinamicamente dados de posicionamento/personagem por meio de ferramentas estruturadas em vez de codificar valores diretamente.
