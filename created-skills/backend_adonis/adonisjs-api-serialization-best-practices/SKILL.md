---
name: adonisjs-api-serialization-best-practices
description: Use when designing, configuring, customizing, or debugging JSON serialization payloads, formatting Lucid ORM model serialization, mapping snake_case database columns to camelCase API responses, or preventing N+1 queries during response generation in AdonisJS v6. Triggers on custom namingStrategy, serialize() overrides, omit fields serializing, and formatting paginated responses.
---

## Objetivo
Estabelecer práticas seguras, performáticas e padronizadas para a serialização de dados e formatação de respostas de API no AdonisJS v6 utilizando Lucid ORM, garantindo saídas consistentes em camelCase para consumo no frontend Vue 3, enquanto previne consultas N+1 e exposição acidental de dados.

## Instruções

### 1. Estratégia de Nomenclatura para Mapear snake_case do Banco para camelCase na API
Se o esquema do seu banco de dados utiliza a convenção de nomenclatura `snake_case` para colunas, mas o frontend Vue 3 requer chaves em `camelCase`, você deve definir uma `NamingStrategy` personalizada.
Não renomeie campos manualmente em cada controller. Em vez disso, registre uma estratégia de nomenclatura global que traduza as propriedades de forma transparente.

Crie uma estratégia de nomenclatura personalizada em `app/services/api_naming_strategy.ts`:
```typescript
import { SnakeCaseNamingStrategy } from '@adonisjs/lucid/orm'
import string from '@adonisjs/core/helpers/string'

export class ApiCamelCaseNamingStrategy extends SnakeCaseNamingStrategy {
  // Mantém os nomes das colunas no banco de dados como snake_case
  columnName(_model: any, attributeName: string) {
    return string.snakeCase(attributeName)
  }

  // Serializa as chaves do model para camelCase nas respostas da API
  serializedName(_model: any, attributeName: string) {
    return string.camelCase(attributeName)
  }
}
```

Em seguida, registre-a globalmente em um provider (por exemplo, no método `boot` de `providers/app_provider.ts`):
```typescript
import { BaseModel } from '@adonisjs/lucid/orm'
import { ApiCamelCaseNamingStrategy } from '#services/api_naming_strategy'

export default class AppProvider {
  async boot() {
    BaseModel.namingStrategy = new ApiCamelCaseNamingStrategy()
  }
}
```

### 2. Excluindo e Renomeando Campos em Models Lucid
Para evitar que colunas confidenciais do banco de dados (como senhas, tokens de acesso, IDs internos) sejam expostas nos payloads da sua API, configure as opções do decorator `@column`.

- **Excluindo campos:** Defina `serializeAs: null`.
- **Chave de serialização personalizada:** Defina `serializeAs: 'chave_personalizada'`.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class User extends BaseModel {
  @column({ isPrimary: true })
  declare id: string

  @column()
  declare email: string

  // Nunca será serializado ou enviado nas respostas da API
  @column({ serializeAs: null })
  declare password: string

  // Serializado como plantCode em vez de usina_codigo
  @column({ serializeAs: 'plantCode' })
  declare usinaCodigo: string
}
```

### 3. Prevenindo Consultas N+1 Durante a Serialização
O Lucid ORM não serializa relacionamentos a menos que tenham sido explicitamente pré-carregados (preloaded). No entanto, se você escrever uma lógica personalizada em `serialize` ou tentar acessar relacionamentos não pré-carregados durante a formatação da resposta, poderá disparar consultas N+1 acidentais.

- **Regra 1:** Sempre pré-carregue relacionamentos usando `.preload()` antes de serializar.
- **Regra 2:** Proteja a serialização de relacionamentos nas sobreposições do model verificando o estado de `$preloaded`.

```typescript
import { BaseModel, column, hasMany } from '@adonisjs/lucid/orm'
import type { HasMany } from '@adonisjs/lucid/types/relations'
import Comment from '#models/comment'

export default class Post extends BaseModel {
  @column({ isPrimary: true })
  declare id: string

  @hasMany(() => Comment)
  declare comments: HasMany<typeof Comment>

  // Sobrescrita segura do serialize protegendo contra consultas N+1
  serialize(cherryPick?: any) {
    const data = super.serialize(cherryPick)

    // Apenas inclui os comentários se eles foram pré-carregados pela query
    if (this.$preloaded.comments) {
      data.comments = this.comments.map((comment) => comment.serialize())
    } else {
      delete data.comments // Previne chaves vazias ou não inicializadas
    }

    return data
  }
}
```

No Controller, certifique-se de realizar a consulta com preload:
```typescript
// Correto: Pré-carrega os comentários antes de retornar
const posts = await Post.query().preload('comments')
return posts.map(post => post.serialize())
```

### 4. Formatação de Data e Hora (Luxon DateTime)
Por padrão, o Lucid serializa propriedades Luxon `DateTime` em strings no formato ISO 8601. Se a sua API precisar impor um formato específico (por exemplo, apenas data ou formatos de localidade personalizados), configure a propriedade `serialize` no decorator da coluna:

```typescript
import { DateTime } from 'luxon'
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class Event extends BaseModel {
  // Formato de saída: YYYY-MM-DD
  @column.dateTime({
    serialize: (value?: DateTime) => value ? value.toISODate() : null
  })
  declare eventDate: DateTime

  // Formato de saída personalizado
  @column.dateTime({
    serialize: (value?: DateTime) => value ? value.toFormat('dd/MM/yyyy HH:mm') : null
  })
  declare scheduledAt: DateTime
}
```

### 5. Sobrescrita Personalizada de Serialização no Nível do Model
Para transformações complexas, sobrescreva o método `serialize`. Você pode selecionar campos dinamicamente ou injetar propriedades computadas em tempo de execução.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'

export default class PowerPlant extends BaseModel {
  @column({ isPrimary: true })
  declare id: string

  @column()
  declare name: string

  @column({ serializeAs: null })
  declare internalNotes: string

  serialize() {
    return {
      id: this.id,
      name: this.name.toUpperCase(),
      // Adiciona campos computados dinamicamente
      serializedAt: new Date().toISOString(),
    }
  }
}
```

### 6. Padronização de Respostas de API Paginadas
Ao utilizar o método `.paginate(page, limit)` do Lucid, metadados padronizados são gerados. Use o serializador do paginador para formatar coleções e metadados de forma segura.

> **Contrato de envelope (autoridade: `adonisjs-maxpinia-endpoint-patterns-best-practices`).** Se o endpoint **alimenta uma store MaxPinia** (`options.get.route`), ele DEVE envolver a resposta em `{ data: ... }` (e o endpoint de save retorna `{ success: true }` ou os dados atualizados). Nunca retorne um array/coleção crua para uma store cacheada. O exemplo paginado abaixo serve para endpoints REST de listagem **não** consumidos por uma store MaxPinia; ao alimentar uma store, envolva o resultado: `return { data: paginatedPosts.serialize({...}) }`.

No Controller:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import Post from '#models/post'

export default class PostsController {
  async index({ request }: HttpContext) {
    const page = request.input('page', 1)
    const limit = request.input('limit', 10)

    const paginatedPosts = await Post.query().paginate(page, limit)

    // A serialização respeita a custom namingStrategy e serializa a lista de dados automaticamente
    return paginatedPosts.serialize({
      fields: ['id', 'title', 'createdAt'],
    })
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** escreva lógica de mapeamento JSON bruto dentro dos controllers. Sempre delegue a formatação para os models do Lucid ORM usando decorators, estratégias de nomenclatura ou métodos de serialização personalizados.
- **Nunca** exponha credenciais confidenciais (senhas, tokens, chaves secretas) nos models serializados. Utilize `serializeAs: null` em todos os campos sensíveis.
- **Não** dispare consultas ao banco de dados dentro de getters, setters ou métodos de serialização. Isso garante que consultas N+1 não ocorram durante a formatação das respostas.
- **Não** ignore a estratégia de nomenclatura personalizada escrevendo variáveis em snake_case de forma manual no TypeScript. Mantenha a base de código do TypeScript em camelCase e deixe que a fronteira do ORM gerencie a tradução.
