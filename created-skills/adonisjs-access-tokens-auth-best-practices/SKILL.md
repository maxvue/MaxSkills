---
name: adonisjs-access-tokens-auth-best-practices
description: Use when implementing or reviewing Opaque Access Tokens (auth.use('api')) no AdonisJS v6 para casos máquina-a-máquina/integrações externas e o endpoint MCP do Maxdmin — NÃO para login de usuários da web/SPA (essa é autenticação por sessão). Triggers em gerar/revogar tokens de API, proteger rotas de integração com o guard `api` e o McpAuthMiddleware.
---

# Access Tokens no AdonisJS — Escopo Restrito (MCP / Máquina-a-Máquina)

## Importante: este NÃO é o padrão de auth do Maxdmin

A autenticação **principal** do Maxdmin é **baseada em SESSÃO**, não em access tokens:

* Guard padrão `web` (`sessionGuard` do `@adonisjs/auth`).
* Sessões persistidas no **banco de dados** (`store = database`, tabela `sessions` com `id`, `data`, `user_id`, `expires_at`), com `age: '30 days'`, cookies `httpOnly`, `secure` em produção e `sameSite: 'lax'` (ver `config/session.ts`).
* Login via `auth.use('web').login(user, remember ?? false)`; o model `User` usa `withAuthFinder(hash)`.
* O frontend é uma SPA Vue pura, servida por rota catch-all, que consome `/api` autenticada pela mesma sessão (cookie). **Não há Ziggy nem Inertia** (são do ecossistema Laravel).

Para configurar/depurar o login de usuários, sessões no banco, "remember me" e autorização, **use a skill de autenticação por sessão / Bouncer**, não esta.

## Quando usar access tokens (a exceção)

Opaque Access Tokens (`auth.use('api')`) no Maxdmin são restritos a:

* **Endpoint MCP**, autenticado pelo `McpAuthMiddleware`.
* Integrações **máquina-a-máquina** / API externa (clientes não-interativos que não carregam cookie de sessão do navegador).

Não use access tokens para o login da SPA web nem como mecanismo geral de auth da aplicação. O restante deste documento descreve o uso técnico correto de tokens **dentro desse escopo de exceção**.

## Instruções

### 1. Configuração do Guard e Model
* **Guard de Token**: Mantenha o guard `web` como `default` em `config/auth.ts`. Adicione o guard `api` (com `accessTokensGuard` e `accessTokensUserProvider`) **apenas** como guard adicional, usado explicitamente por MCP/integrações — nunca como padrão da aplicação.
  ```typescript
  import { defineConfig } from '@adonisjs/auth'
  import { sessionGuard, sessionUserProvider } from '@adonisjs/auth/session'
  import { accessTokensGuard, accessTokensUserProvider } from '@adonisjs/auth/access_tokens'

  const authConfig = defineConfig({
    default: 'web',
    guards: {
      web: sessionGuard({
        useRememberMeTokens: false,
        provider: sessionUserProvider({
          model: () => import('#models/user'),
        }),
      }),
      // Exceção: usado por MCP / integrações máquina-a-máquina
      api: accessTokensGuard({
        provider: accessTokensUserProvider({
          model: () => import('#models/user'),
        }),
      }),
    },
  })
  export default authConfig
  ```
* **Configuração do Model**: Para habilitar tokens, componha o model `User` com o mixin `withAccessTokens` (além do `withAuthFinder` já usado para a autenticação por sessão).
  ```typescript
  import { compose } from '@adonisjs/core/helpers'
  import hash from '@adonisjs/core/services/hash'
  import { BaseModel } from '@adonisjs/lucid/orm'
  import { withAuthFinder } from '@adonisjs/auth/mixins/lucid'
  import { withAccessTokens } from '@adonisjs/auth/access_tokens'

  const AuthFinder = withAuthFinder(() => hash.use('scrypt'), {
    uids: ['email'],
    passwordColumnName: 'password',
  })

  export default class User extends compose(BaseModel, AuthFinder, withAccessTokens) {
    // ... propriedades do model
  }
  ```

### 2. Gerenciamento do Ciclo de Vida de Tokens (Geração, Revogação e Expiração)
* **Geração Segura de Tokens**: Crie tokens para um cliente/integração chamando `User.accessTokens.create(user)`.
* **Resposta com Token**: Sempre retorne o valor limpo do token usando o método `.release()` do objeto de token. Esse valor está disponível apenas uma vez e não deve ser logado ou armazenado em texto plano em qualquer lugar, exceto na versão com hash do banco de dados.
  ```typescript
  const token = await User.accessTokens.create(user, ['*'], {
    expiresIn: '30 days'
  })

  return response.ok({
    type: 'bearer',
    token: token.value!.release(),
    expiresAt: token.expiresAt,
  })
  ```
* **Revogação de Tokens**: Revogue tokens individuais quando uma integração é desativada, e forneça opções para revogar todos os tokens ativos em caso de vazamento de credenciais.
  ```typescript
  // Revogar token atual
  const token = auth.user!.currentAccessToken
  await User.accessTokens.delete(auth.user!, token.identifier)

  // Revogar todos os tokens (aguarde todas as deleções com Promise.all)
  const tokens = await User.accessTokens.all(auth.user!)
  await Promise.all(
    tokens.map((t) => User.accessTokens.delete(auth.user!, t.identifier))
  )
  ```

### 3. Proteção de Rotas e Middleware
* **Uso de Middleware**: Proteja rotas de integração/MCP usando o middleware `auth` com o guard `api` explícito (já que o padrão é `web`). No caso do endpoint MCP, a autenticação é feita pelo `McpAuthMiddleware`.
  ```typescript
  import { middleware } from '#start/kernel'

  router.group(() => {
    router.get('me', ({ auth }) => auth.user!)
  })
  .use(middleware.auth({ guards: ['api'] }))
  ```

### 4. Tratamento de Exceções
* **Respostas JSON Padronizadas**: Capture exceções de autenticação (`errors.E_UNAUTHORIZED_ACCESS`) globalmente no Exception Handler (`app/exceptions/handler.ts`) e retorne um formato JSON padronizado `401 Unauthorized`.
  ```typescript
  import { HttpContext, ExceptionHandler } from '@adonisjs/core/http'
  import { errors } from '@adonisjs/auth'

  export default class HttpExceptionHandler extends ExceptionHandler {
    async handle(error: unknown, ctx: HttpContext) {
      if (error instanceof errors.E_UNAUTHORIZED_ACCESS) {
        return ctx.response.status(401).send({
          errors: [
            {
              message: 'Falha na autenticação. Por favor, forneça um token de acesso válido.',
              code: 'E_UNAUTHORIZED_ACCESS'
            }
          ]
        })
      }
      return super.handle(error, ctx)
    }
  }
  ```

## Restrições
* **Não** use access tokens como mecanismo de login da SPA web nem como auth padrão da aplicação — isso é responsabilidade do guard `web` (sessão no banco, 30 dias). Veja a skill de autenticação por sessão / Bouncer.
* **Não** torne o guard `api` o `default` em `config/auth.ts`; o padrão é `web`.
* **Não** exponha tokens em texto plano ou os armazene em formato de texto plano no lado do servidor.
* **Não** ignore os middlewares de rota para escrever consultas de token personalizadas no banco de dados dentro de controllers.
* **Não** se esqueça de limpar tokens expirados ou revogados do banco de dados (tabela `auth_access_tokens`) periodicamente para manter as tabelas leves.
