---
name: adonisjs-auth-remember-me-best-practices
description: "Use when implementing, configuring, reviewing, or debugging login persistence ("Remember Me") in AdonisJS v6. Covers database sessions with 30-day age and remember flag on login, and dedicated remember-me tokens. Triggers on config/auth.ts, config/session.ts, auth controllers with remember field, and remember_me_tokens migrations."
---

# Boas Práticas de Autenticação "Lembrar de mim" no AdonisJS v6

## Objetivo
Documentar como funciona a persistência de login ("Lembrar de mim") no AdonisJS v6 usando `@adonisjs/auth`, refletindo o padrão real adotado neste projeto, e descrever a alternativa de remember-me tokens dedicados quando for desejada persistência independente da expiração da sessão.

## Mecanismo real atual (padrão do projeto)

Hoje a persistência de "lembrar de mim" **não** usa tokens dedicados. Em `config/auth.ts`, o session guard `web` está com `useRememberMeTokens: false`. A persistência de 30 dias vem da **própria sessão armazenada no banco**.

### 1. Sessão persistida no banco com `age: '30 days'`
- `config/session.ts` usa `store: 'database'` (tabela `sessions`), com `age: '30 days'`, `httpOnly: true`, `secure` em produção, `sameSite: 'lax'` e `clearWithBrowser: false`.
- O `age` define por quanto tempo o cookie/sessão permanece válido. Como `clearWithBrowser` é `false`, a sessão sobrevive ao fechamento do navegador até atingir os 30 dias.
  ```typescript
  // config/session.ts
  import { defineConfig, stores } from '@adonisjs/session'

  export default defineConfig({
    age: '30 days',
    enabled: true,
    cookieName: 'adonis-session',
    clearWithBrowser: false,
    cookie: {
      httpOnly: true,
      secure: app.inProduction,
      sameSite: 'lax',
    },
    store: env.get('SESSION_DRIVER'), // 'database' no .env
    stores: {
      cookie: stores.cookie(),
      database: stores.database(),
    },
  })
  ```

### 2. Guard de sessão sem tokens remember-me
- O guard `web` usa `sessionGuard` com `sessionUserProvider` apontando para `#models/user` (model com mixin `withAuthFinder(hash)`).
- `useRememberMeTokens` está **desligado** (`false`, padrão). Logo, a flag `remember` passada no login não cria token dedicado; a persistência continua governada pelo `age` da sessão.
  ```typescript
  // config/auth.ts (padrão atual)
  import { defineConfig } from '@adonisjs/auth'
  import { sessionGuard, sessionUserProvider } from '@adonisjs/auth/session'

  const authConfig = defineConfig({
    default: 'web',
    guards: {
      web: sessionGuard({
        useRememberMeTokens: false,
        provider: sessionUserProvider({
          model: () => import('#models/user'),
        }),
      }),
    },
  })
  ```

### 3. Fluxo de login no controller
- O validador VineJS aceita um campo `remember` opcional, e o login passa esse valor como segundo argumento de `auth.use('web').login()`:
  ```typescript
  // app/controllers/auth_controller.ts
  const loginValidator = vine.compile(
    vine.object({
      email: vine.string().email(),
      password: vine.string(),
      remember: vine.boolean().optional(),
    })
  )

  const { email, password, remember } = await request.validateUsing(loginValidator)
  const user = await User.verifyCredentials(email, password)
  await auth.use('web').login(user, remember ?? false)
  ```
- Comportamento com `useRememberMeTokens: false`:
  - A flag `remember` é aceita e repassada, mas **não** gera token dedicado.
  - A persistência efetiva (até 30 dias mesmo após fechar o navegador) vem do `age` + `clearWithBrowser: false` da sessão.
- Logout: `await auth.use('web').logout()` encerra a sessão atual.
  ```typescript
  async logout({ auth, response }: HttpContext) {
    await auth.use('web').logout()
    return response.json({ message: 'Sessão encerrada.' })
  }
  ```

## Opção: remember-me tokens dedicados

Use esta opção **apenas** se quiser persistência de login **independente da expiração da sessão** (ex.: re-login automático via cookie mesmo após a sessão expirar). Não é o padrão atual do projeto. Ative deliberadamente os três pontos abaixo em conjunto; ativar apenas um deles quebra o fluxo.

### A. Ativar no session guard
- Defina `useRememberMeTokens: true` no `sessionGuard`. Opcionalmente, ajuste a validade dos tokens com `rememberMeTokensAge` (ex.: `'30 days'`):
  ```typescript
  // config/auth.ts (opção com tokens dedicados)
  web: sessionGuard({
    useRememberMeTokens: true,
    rememberMeTokensAge: '30 days',
    provider: sessionUserProvider({
      model: () => import('#models/user'),
    }),
  }),
  ```

### B. Configurar o provider de tokens no model User
- O model deve expor um `DbRememberMeTokensProvider` para persistir/verificar os tokens:
  ```typescript
  // app/models/user.ts
  import { DbRememberMeTokensProvider } from '@adonisjs/auth/session'

  export default class User extends compose(BaseModel, AuthFinder) {
    // ...colunas...
    static rememberMeTokens = DbRememberMeTokensProvider.forModel(User)
  }
  ```

### C. Migration da tabela `remember_me_tokens`
- Crie e execute a migration. Garanta `tokenable_id` compatível com a PK de `users` (ex.: `CHAR(26)` para ULID, `BIGINT` para auto-increment, `UUID` para UUID) e `onDelete('CASCADE')`:
  ```typescript
  import { BaseSchema } from '@adonisjs/lucid/schema'

  export default class extends BaseSchema {
    protected tableName = 'remember_me_tokens'

    async up() {
      this.schema.createTable(this.tableName, (table) => {
        table.increments('id')
        table
          .specificType('tokenable_id', 'CHAR(26)')
          .notNullable()
          .references('id')
          .inTable('users')
          .onDelete('CASCADE')
        table.string('hash').notNullable()
        table.timestamp('created_at').notNullable()
        table.timestamp('updated_at').notNullable()
        table.timestamp('expires_at').notNullable()
      })
    }

    async down() {
      this.schema.dropTable(this.tableName)
    }
  }
  ```

Com os três pontos ativos, `auth.use('web').login(user, true)` passa a emitir um cookie de remember-me dedicado e `logout()` revoga o token correspondente.

### Revogação de tokens em ações sensíveis (apenas se a opção estiver ativa)
- Ao redefinir senha ou em mudanças críticas de segurança, revogue os tokens do usuário para mitigar sequestro de sessão:
  ```typescript
  import db from '@adonisjs/lucid/services/db'

  user.password = newPassword
  await user.save()
  await db.from('remember_me_tokens').where('tokenable_id', user.id).delete()
  ```

### Limpeza periódica de tokens expirados (apenas se a opção estiver ativa)
- Agende um comando Ace/Cron para remover tokens vencidos:
  ```typescript
  import db from '@adonisjs/lucid/services/db'

  await db.from('remember_me_tokens').where('expires_at', '<', new Date()).delete()
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- O padrão atual do projeto é a persistência via `age: '30 days'` da sessão no banco com `useRememberMeTokens: false`. Não ative tokens dedicados sem necessidade real e sem aplicar os três pontos (guard + provider no model + migration) em conjunto.
- **Nunca** salve o valor bruto do token (texto simples) no banco. O `@adonisjs/auth` hasheia o token automaticamente; não contorne isso.
- **Nunca** crie ou manipule os cookies de sessão/remember-me manualmente no frontend ou backend. Deixe o `@adonisjs/auth` e o `@adonisjs/session` gerenciarem os cookies nativamente.
- Não exponha dados ou hashes das tabelas `sessions` ou `remember_me_tokens` em endpoints públicos.
- Garanta que `tokenable_id` em `remember_me_tokens` seja estritamente compatível com a PK de `users` (ex.: `CHAR(26)` para ULID).
