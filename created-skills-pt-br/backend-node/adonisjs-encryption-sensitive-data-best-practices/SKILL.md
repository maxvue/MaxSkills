---
name: adonisjs-encryption-sensitive-data-best-practices
description: Use when encrypting, decrypting, or storing sensitive client credentials, access tokens (Meta Graph, Instagram, WhatsApp), and API keys in the database using AdonisJS v6 Encryption service. Triggers on model hooks, custom setters/getters for credential serialization, and environment key rotation.
---

## Objetivo
Estabelecer um padrão uniforme e seguro para criptografar, descriptografar e armazenar dados confidenciais (por exemplo, credenciais de APIs externas, tokens de acesso OAuth do Meta, segredos de webhooks) no banco de dados usando o serviço nativo de Encryption do AdonisJS v6 e Lucid ORM.

## Instruções

### 1. Criptografia Básica de Colunas (Transparente)
Use as propriedades `prepare` e `consume` do decorator `@column` em models do Lucid para criptografar automaticamente os valores antes da inserção no banco de dados e descriptografá-los após a recuperação.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'

export default class ClientCredential extends BaseModel {
  @column()
  declare id: string

  @column({
    // Criptografa os dados antes de salvar no banco de dados
    prepare: (value: string | null) => {
      return value ? encryption.encrypt(value) : null
    },
    // Descriptografa os dados quando recuperados do banco de dados
    consume: (value: string | null) => {
      if (!value) return null
      try {
        return encryption.decrypt<string>(value)
      } catch (error) {
        // Retorna o valor original ou registra um alerta se a descriptografia falhar (ex: dados antigos legados)
        return value
      }
    },
  })
  declare facebookAccessToken: string | null
}
```

### 2. Criptografia de Objetos JSON ou Dados Estruturados
Se você precisar armazenar estruturas aninhadas (como configurações de conexão, segredos e tokens juntos), serialize e criptografe/descriptografe-os corretamente:

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'

interface ConnectionConfig {
  clientId: string
  clientSecret: string
  scopes: string[]
}

export default class ClientIntegration extends BaseModel {
  @column({
    prepare: (value: ConnectionConfig | null) => {
      return value ? encryption.encrypt(JSON.stringify(value)) : null
    },
    consume: (value: string | null) => {
      if (!value) return null
      try {
        const decrypted = encryption.decrypt<string>(value)
        return JSON.parse(decrypted) as ConnectionConfig
      } catch {
        return null
      }
    },
  })
  declare credentials: ConnectionConfig | null
}
```

### 3. Gerenciamento de Rotação de Chaves de Criptografia
Ao realizar a rotação da chave `APP_KEY` em produção, os valores criptografados anteriormente falharão na descriptografia porque o segredo mudou. O AdonisJS v6 permite configurar chaves de fallback no arquivo `config/encryption.ts`.

Garanta que o `config/encryption.ts` inclua chaves antigas no array `keys`:

```typescript
// config/encryption.ts
const encryptionConfig = defineConfig({
  list: {
    aes: drivers.aes({
      // A primeira chave é usada para criptografar novos dados.
      // Todas as chaves listadas abaixo serão tentadas durante a descriptografia.
      keys: [
        env.get('APP_KEY'),
        env.get('LEGACY_APP_KEY_1'), // Chave antiga de fallback
      ],
    }),
  },
})
```

### 4. Consultas em Campos Criptografados
A criptografia padrão (AES-256-GCM) usa um vetor de inicialização (IV) aleatório para cada operação de criptografia. Isso significa que o mesmo texto simples resulta em textos criptografados diferentes, impossibilitando cláusulas `where` em colunas criptografadas.

Se você precisar consultar/buscar registros com base em um campo sensível (por exemplo, pesquisar por URL de webhook ou Client ID), armazene uma representação em hash (blind index) em uma coluna separada:

```typescript
import crypto from 'node:crypto'
import { BaseModel, column, beforeSave } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'

export default class ClientApiKey extends BaseModel {
  @column({
    prepare: (v) => (v ? encryption.encrypt(v) : null),
    consume: (v) => (v ? encryption.decrypt<string>(v) : null),
  })
  declare rawKey: string

  @column()
  declare keyHash: string // Coluna indexável no banco de dados

  @beforeSave()
  static generateHash(apiKey: ClientApiKey) {
    if (apiKey.isDirty('rawKey') && apiKey.rawKey) {
      // Use HMAC ou SHA256 com um salt de ambiente para buscas determinísticas
      apiKey.keyHash = crypto
        .createHmac('sha256', process.env.HASH_SALT || 'fallback-salt')
        .update(apiKey.rawKey)
        .digest('hex')
    }
  }
}
```

## Restrições
- **NÃO** armazene tokens de API, chaves OAuth ou credenciais de clientes em texto limpo sob nenhuma circunstância.
- **NÃO** use criptografia determinística manual. Prefira o serviço de `encryption` padrão do AdonisJS, que gerencia AES-256-GCM e assinaturas de forma automatizada e segura.
- **NÃO** execute consultas diretas como `.where('encrypted_field', value)` no banco de dados. Caso buscas sejam necessárias, implemente uma coluna de índice hash determinístico (blind index).
- **NÃO** exponha valores descriptografados em respostas da API ou logs do sistema. Certifique-se de excluir colunas confidenciais de serializações (por exemplo, usando `@column({ serializeAs: null })` ou removendo-os nos controllers).
