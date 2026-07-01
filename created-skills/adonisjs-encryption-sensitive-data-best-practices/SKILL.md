---
name: adonisjs-encryption-sensitive-data-best-practices
description: Use when encrypting, decrypting, or storing sensitive client credentials, access tokens (Meta Graph, Instagram, WhatsApp), and API keys in the database using AdonisJS v6 Encryption service. Triggers on model hooks, custom setters/getters for credential serialization, and environment key rotation.
---

## Goal
Establish a uniform, secure pattern for encrypting, decrypting, and storing sensitive data (e.g., external API credentials, Meta OAuth access tokens, webhook secrets) in the database using the AdonisJS v6 native Encryption service and Lucid ORM.

## Instructions

### 1. Basic Column Encryption (Transparent)
Use the `@column` decorator's `prepare` and `consume` options in Lucid models to encrypt values before database insertion and decrypt them upon retrieval automatically.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'

export default class ClientCredential extends BaseModel {
  @column()
  declare id: string

  @column({
    // Encrypt data before saving to DB
    prepare: (value: string | null) => {
      return value ? encryption.encrypt(value) : null
    },
    // Decrypt data when fetched from DB
    consume: (value: string | null) => {
      if (!value) return null
      try {
        return encryption.decrypt<string>(value)
      } catch (error) {
        // Return raw value or log warning if decrypt fails (e.g., unencrypted legacy data)
        return value
      }
    },
  })
  declare facebookAccessToken: string | null
}
```

### 2. Encryption of JSON Objects or Structured Data
If you store nested structures (like connection configurations, client secrets, and access tokens together), serialize and encrypt/decrypt them properly:

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

### 3. Handle Encryption Key Rotation
When rotating `APP_KEY` in production, old encrypted values will fail decryption because the secret has changed. AdonisJS v6 allows configuring fallback keys in `config/encryption.ts`.

Ensure that `config/encryption.ts` includes previous keys in the `keys` array:

```typescript
// config/encryption.ts
const encryptionConfig = defineConfig({
  list: {
    aes: drivers.aes({
      // The first key is used for encryption.
      // All keys listed in this array are tried during decryption.
      keys: [
        env.get('APP_KEY'),
        env.get('LEGACY_APP_KEY_1'), // Fallback key
      ],
    }),
  },
})
```

### 4. Querying Encrypted Fields
Standard encryption (AES-256-CBC, com HMAC para integridade) uses a random initialization vector (IV) for every encryption operation. This means the same plain text yields different ciphertexts, making `where` clauses on encrypted columns impossible.

If you must query/find models based on a sensitive field (e.g., searching for a webhook URL or Client ID), store a hashed representation (blind index) in a separate column:

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
  declare keyHash: string // Database indexable

  @beforeSave()
  static generateHash(apiKey: ClientApiKey) {
    if (apiKey.isDirty('rawKey') && apiKey.rawKey) {
      // Use HMAC or SHA256 with a salt from environment for deterministic searching
      apiKey.keyHash = crypto
        .createHmac('sha256', process.env.HASH_SALT || 'fallback-salt')
        .update(apiKey.rawKey)
        .digest('hex')
    }
  }
}
```

## Constraints
- **Do NOT** store API tokens, OAuth keys, or clients' credentials in plain text under any circumstances.
- **Do NOT** use deterministic encryption manually. Use the standard AdonisJS `encryption` service which handles AES-256-CBC (com HMAC para integridade) and signing automatically.
- **Do NOT** execute direct queries like `.where('encrypted_field', value)` on the database. If searching is required, you must implement a deterministic hashed index column (blind index).
- **Do NOT** expose decrypted values in API responses or logs. Ensure sensitive columns are excluded from serializations (e.g., using `@column({ serializeAs: null })` or removing them in controllers).
