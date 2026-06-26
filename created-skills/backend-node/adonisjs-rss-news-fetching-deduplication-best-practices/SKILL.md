---
name: adonisjs-rss-news-fetching-deduplication-best-practices
description: Use when implementing, configuring, or debugging RSS news fetching services, parsing XML feeds, calculating string similarity for title deduplication, managing URL hash uniqueness, and updating keyword associations on pending news items in AdonisJS v6 backend.
---

# Boas Práticas de Busca e Deduplicação de Notícias RSS no AdonisJS

## Objetivo
Padronizar a ingestão de notícias via RSS, parsing leve de XML sem dependências externas, requisições HTTP resilientes com AbortController, lógica de deduplicação por similaridade de caracteres e transmissão de notificações em tempo real para o frontend no backend AdonisJS v6.

## Instruções

### 1. Estrutura do Model (`social_media_news.ts`)
Defina um model Lucid para armazenar as notícias com as colunas: `solarCompanyId`, `title`, `url`, `urlHash` (SHA1 da URL), `source`, `publishedAt` (DateTime), `description`, `queryKeyword`, `keywords` (array JSON de strings) e `status` ('pending', etc.).
Garanta que as chaves primárias utilizem **ULID** gerados no hook `@beforeCreate()`:

```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, belongsTo, column } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import SolarCompany from '#models/solar_company'

export default class SocialMediaNews extends BaseModel {
  static table = 'social_media_news'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: SocialMediaNews) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare solarCompanyId: string

  @column()
  declare title: string

  @column()
  declare url: string

  @column()
  declare urlHash: string | null

  @column()
  declare source: string | null

  @column.dateTime()
  declare publishedAt: DateTime | null

  @column()
  declare description: string | null

  @column()
  declare queryKeyword: string

  @column({
    prepare: (value) => (value ? JSON.stringify(value) : null),
    consume: (value) => {
      if (value === null || value === undefined) return null
      return typeof value === 'string' ? JSON.parse(value) : value
    },
  })
  declare keywords: string[] | null

  @column()
  declare status: string

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime
}
```

### 2. Parsing Nativo de XML (Baseado em Regex)
Evite bibliotecas pesadas de XML externas. Implemente um parser simples com regex para extrair os itens:

```typescript
function parseRssItems(xml: string) {
  const items: Array<{ title: string; link: string; description: string; pubDate: string; source: string }> = []
  const itemRegex = /<item>([\s\S]*?)<\/item>/g
  let match
  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[1]
    
    const titleMatch = itemXml.match(/<title><!\[CDATA\[([\s\S]*?)\]\]><\/title>/) || itemXml.match(/<title>([\s\S]*?)<\/title>/)
    const linkMatch = itemXml.match(/<link>([\s\S]*?)<\/link>/)
    const descMatch = itemXml.match(/<description><!\[CDATA\[([\s\S]*?)\]\]><\/description>/) || itemXml.match(/<description>([\s\S]*?)<\/description>/)
    const pubDateMatch = itemXml.match(/<pubDate>([\s\S]*?)<\/pubDate>/)
    const sourceMatch = itemXml.match(/<source[^>]*>([\s\S]*?)<\/source>/)

    let title = titleMatch ? titleMatch[1].trim() : ''
    const link = linkMatch ? linkMatch[1].trim() : ''
    let description = descMatch ? descMatch[1].trim() : ''
    const pubDate = pubDateMatch ? pubDateMatch[1].trim() : ''
    const source = sourceMatch ? sourceMatch[1].trim() : ''

    const decodeEntities = (s: string) =>
      s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, ' ')
    title = decodeEntities(title.replace(/<[^>]*>?/gm, ''))
    description = decodeEntities(description.replace(/<[^>]*>?/gm, ''))

    if (title && link) {
      items.push({ title, link, description, pubDate, source })
    }
  }
  return items
}
```

### 3. Fetch Resiliente com Timeout
Configure um limite de tempo máximo (timeout) de 15 segundos usando `AbortController` para evitar que requisições externas travadas bloqueiem o loop de eventos:

```typescript
const controller = new AbortController()
const timeout = setTimeout(() => controller.abort(), 15000)

try {
  const response = await fetch(url, { signal: controller.signal })
  if (!response.ok) {
    logger.warn({ status: response.status }, `Failed to fetch news`)
    return 0
  }
  const xml = await response.text()
} catch (error: any) {
  logger.warn({ err: error?.message }, `Exception fetching news`)
} finally {
  clearTimeout(timeout)
}
```

### 4. Similaridade de Strings e Lógica de Deduplicação
Calcule a similaridade a nível de caracteres entre os títulos para evitar notícias duplicadas com títulos ligeiramente alterados:

```typescript
function similarPercent(a: string, b: string): number {
  if (!a || !b) return 0

  let common = 0
  const aChars = a.toLowerCase().split('')
  const bChars = b.toLowerCase().split('')
  const bMap: Record<string, number> = {}
  for (const c of bChars) {
    bMap[c] = (bMap[c] || 0) + 1
  }
  
  for (const c of aChars) {
    if (bMap[c] > 0) {
      common++
      bMap[c]--
    }
  }

  return (2 * common * 100) / (a.length + b.length)
}
```

Fluxo de validação de deduplicação:
1. Verifique correspondências exatas usando `url_hash` (SHA1) ou `title` via consulta Lucid.
2. Se não encontrar, verifique se há algum registro em cache com similaridade de título >= 92% utilizando a função `similarPercent`.
3. Se encontrar uma duplicata e o status for `pending`, adicione a palavra-chave (`keyword`) pesquisada ao array `keywords` se ela ainda não estiver contida.
4. Se nenhuma duplicata for detectada, crie o registro com o status `pending`.

### 5. Notificações em Tempo Real via SSE (`@adonisjs/transmit`)
Se novas notícias forem importadas, envie a quantidade de novos registros inseridos para o canal em tempo real da empresa:

```typescript
import transmit from '@adonisjs/transmit/services/main'

if (newCount > 0) {
  transmit.broadcast(`companies/${solarCompanyId}/news`, { count: newCount })
}
```

## Restrições
- **SEM Parsers de XML Externos:** Não utilize pacotes de parsing de XML pesados (ex: `fast-xml-parser`, `xml2js`). Sempre realize o parse dos feeds utilizando expressões regulares seguras e decodificação manual de entidades.
- **AbortController OBRIGATÓRIO:** Sempre configure um timeout usando `AbortController` (máximo de 15 segundos) ao realizar chamadas a feeds externos para evitar travamento de recursos.
- **Verificação de Hash da URL:** Sempre calcule e compare o `url_hash` utilizando `crypto.createHash('sha1')` para garantir a unicidade no banco de dados.
- **Keywords sem Duplicidade:** Ao atualizar a lista de palavras-chave (`keywords`) de uma notícia pendente duplicada, certifique-se de validar se o termo já existe no array antes de inseri-lo.
- **Padrão Lucid ORM:** Utilize a query builder do Lucid ORM para as consultas e verificações de registros. Siga a convenção snake_case para comparação de colunas (ex: `solar_company_id`, `url_hash`) dentro das consultas de banco de dados.
