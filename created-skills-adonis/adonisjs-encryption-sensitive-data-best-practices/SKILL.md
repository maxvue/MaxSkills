---
name: adonisjs-encryption-sensitive-data-best-practices
description: Use when encrypting, decrypting, or storing sensitive client credentials, access tokens (Meta Graph, Instagram, WhatsApp), and API keys in the database using AdonisJS v6 Encryption service. Triggers on model hooks, custom setters/getters for credential serialization, and environment key rotation.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer um padrão uniforme e seguro para criptografar, descriptografar e armazenar dados sensíveis (por exemplo, credenciais de APIs externas, tokens de acesso OAuth da Meta, segredos de webhook) no banco de dados usando o serviço nativo de Encryption do AdonisJS v6 e o Lucid ORM.

## Instruções

### 1. Criptografia Básica de Colunas (Transparente)
Use as opções `prepare` e `consume` do decorator `@column` nos models do Lucid para criptografar valores antes da inserção no banco e descriptografá-los automaticamente ao recuperá-los.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'

export default class ClientCredential extends BaseModel {
  @column()
  declare id: string

  @column({
    // Criptografa os dados antes de salvar no banco
    prepare: (value: string | null) => {
      return value ? encryption.encrypt(value) : null
    },
    // Descriptografa os dados ao buscá-los do banco.
    // NOTA: decrypt() NÃO lança exceção com entrada inválida/legada/adulterada — retorna `null`.
    // Portanto, trate o retorno null explicitamente em vez de confiar em try/catch.
    consume: (value: string | null) => {
      if (!value) return null
      const plain = encryption.decrypt<string>(value)
      // Se decrypt falhar, retorna null; use o valor bruto como fallback para dados legados não criptografados.
      return plain ?? value
    },
  })
  declare facebookAccessToken: string | null
}
```

### 2. Criptografia de Objetos JSON ou Dados Estruturados
Se você armazena estruturas aninhadas (como configurações de conexão, client secrets e tokens de acesso juntos), serialize e criptografe/descriptografe-as corretamente:

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

### 3. Rotação de Chaves de Criptografia
A criptografia do AdonisJS v6 usa um **único** segredo — `APP_KEY` (`config('app.appKey')`). O pacote `@adonisjs/encryption` exporta apenas a classe `Encryption` e `errors`; **não** existe `defineConfig`, nem `drivers.aes`, nem um array `keys` de fallback / lista de decrypt-fallback. NÃO crie um `config/encryption.ts` com um array de múltiplas chaves — essa API não existe e não vai funcionar.

Como não há fallback de descriptografia embutido, a rotação deve **recriptografar todos os textos cifrados**: durante uma migration, descriptografe cada valor com o segredo ANTIGO e recriptografe-o com o NOVO. Construa uma instância de `Encryption` vinculada ao segredo antigo (via a classe `Encryption` exportada, ou `encryption.child({ secret })`) para descriptografar valores legados e, em seguida, grave-os de volta criptografados sob o `APP_KEY` atual:

```typescript
import { Encryption } from '@adonisjs/encryption'
import encryption from '@adonisjs/core/services/encryption'
import db from '@adonisjs/lucid/services/db'

// Instância de Encryption vinculada ao APP_KEY anterior (mantida apenas durante a janela de rotação).
const oldEncryption = new Encryption({ secret: process.env.LEGACY_APP_KEY_1! })

// Lê o texto cifrado BRUTO diretamente da coluna (ignorando os hooks consume/prepare do model),
// então descriptografa-com-antigo / criptografa-com-novo e grava de volta.
const rows = await db.from('client_credentials').select('id', 'facebook_access_token')
for (const row of rows) {
  const cipher = row.facebook_access_token as string | null
  if (!cipher) continue
  const plain = oldEncryption.decrypt<string>(cipher)
  if (plain === null) continue // já recriptografado ou inválido
  await db
    .from('client_credentials')
    .where('id', row.id)
    .update({ facebook_access_token: encryption.encrypt(plain) })
}
```

### 4. Consultando Campos Criptografados
A criptografia padrão (AES-256-CBC, com HMAC para integridade) usa um vetor de inicialização (IV) aleatório em cada operação de criptografia. Isso significa que o mesmo texto plano gera textos cifrados diferentes, tornando impossíveis cláusulas `where` em colunas criptografadas.

Se você precisar consultar/localizar models com base em um campo sensível (por exemplo, buscar por uma URL de webhook ou Client ID), armazene uma representação hasheada (blind index) em uma coluna separada:

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
  declare keyHash: string // Indexável no banco de dados

  @beforeSave()
  static generateHash(apiKey: ClientApiKey) {
    if (apiKey.isDirty('rawKey') && apiKey.rawKey) {
      // Use HMAC ou SHA256 com um salt vindo do ambiente para busca determinística
      apiKey.keyHash = crypto
        .createHmac('sha256', process.env.HASH_SALT || 'fallback-salt')
        .update(apiKey.rawKey)
        .digest('hex')
    }
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** armazene tokens de API, chaves OAuth ou credenciais de clientes em texto plano sob nenhuma circunstância.
- **NÃO** use criptografia determinística manualmente. Use o serviço padrão `encryption` do AdonisJS, que trata AES-256-CBC (com HMAC para integridade) e assinatura automaticamente.
- **NÃO** execute consultas diretas como `.where('encrypted_field', value)` no banco de dados. Se for necessário buscar, você deve implementar uma coluna de índice hasheado determinístico (blind index).
- **NÃO** exponha valores descriptografados em respostas de API ou logs. Garanta que colunas sensíveis sejam excluídas das serializações (por exemplo, usando `@column({ serializeAs: null })` ou removendo-as nos controllers).
