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
    // Decrypt data when fetched from DB.
    // NOTE: decrypt() does NOT throw on invalid/legacy/tampered input — it returns `null`.
    // So handle the null return explicitly instead of relying on try/catch.
    consume: (value: string | null) => {
      if (!value) return null
      const plain = encryption.decrypt<string>(value)
      // If decrypt fails it returns null; fall back to the raw value for unencrypted legacy data.
      return plain ?? value
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
AdonisJS v6 encryption uses a **single** secret — `APP_KEY` (`config('app.appKey')`). The `@adonisjs/encryption` package exports only the `Encryption` class and `errors`; there is **no** `defineConfig`, no `drivers.aes`, and no fallback `keys` array / decrypt-fallback list. Do NOT create a `config/encryption.ts` with a multi-key array — that API does not exist and will not work.

Because there is no built-in decrypt fallback, rotation must **re-encrypt all ciphertext**: during a migration, decrypt each value with the OLD secret and re-encrypt it with the NEW one. Build an `Encryption` instance bound to the old secret (via the exported `Encryption` class, or `encryption.child({ secret })`) to decrypt legacy values, then write them back encrypted under the current `APP_KEY`:

```typescript
import { Encryption } from '@adonisjs/encryption'
import encryption from '@adonisjs/core/services/encryption'
import db from '@adonisjs/lucid/services/db'

// Encryption instance bound to the previous APP_KEY (kept only for the rotation window).
const oldEncryption = new Encryption({ secret: process.env.LEGACY_APP_KEY_1! })

// Read the RAW ciphertext straight from the column (bypass the model's consume/prepare hooks),
// then decrypt-with-old / encrypt-with-new and write it back.
const rows = await db.from('client_credentials').select('id', 'facebook_access_token')
for (const row of rows) {
  const cipher = row.facebook_access_token as string | null
  if (!cipher) continue
  const plain = oldEncryption.decrypt<string>(cipher)
  if (plain === null) continue // already re-encrypted or invalid
  await db
    .from('client_credentials')
    .where('id', row.id)
    .update({ facebook_access_token: encryption.encrypt(plain) })
}
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
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do NOT** store API tokens, OAuth keys, or clients' credentials in plain text under any circumstances.
- **Do NOT** use deterministic encryption manually. Use the standard AdonisJS `encryption` service which handles AES-256-CBC (com HMAC para integridade) and signing automatically.
- **Do NOT** execute direct queries like `.where('encrypted_field', value)` on the database. If searching is required, you must implement a deterministic hashed index column (blind index).
- **Do NOT** expose decrypted values in API responses or logs. Ensure sensitive columns are excluded from serializations (e.g., using `@column({ serializeAs: null })` or removing them in controllers).
