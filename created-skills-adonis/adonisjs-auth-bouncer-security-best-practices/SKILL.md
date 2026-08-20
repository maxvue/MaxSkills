---
name: adonisjs-auth-bouncer-security-best-practices
description: "Use when designing, creating, reviewing, or debugging authentication (session via web guard, database sessions), authorization (Bouncer abilities/policies), social logins (Ally OAuth with Google/Facebook), or security features (Shield CSRF/headers, cookie XSRF) in AdonisJS. Triggers on bouncer policies, auth middleware, session setup, shield configuration, ally integration, and CSRF protection."
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas de Autenticação, Bouncer e Segurança no AdonisJS

## Objetivo
Estabelecer diretrizes de código, padrões arquiteturais e padrões de implementação para o desenvolvimento seguro de autenticação (baseada em sessão via `web` guard, com sessões persistidas no banco), autorização granular de recursos (Bouncer), integração de logins sociais (Ally) e proteção contra vulnerabilidades web (Shield) no AdonisJS v6, garantindo a propagação adequada do contexto de multitenancy e a compatibilidade com o fluxo de CSRF do SPA (cookie XSRF).

## Instruções

### 1. Autenticação (baseada em Sessão)
* Utilize o pacote oficial `@adonisjs/auth` com o `sessionGuard` para a autenticação de usuários. O guard padrão é o `web`, configurado no arquivo `config/auth.ts` com `sessionUserProvider` apontando para `#models/user` (modelo que usa o mixin `withAuthFinder` com `hash`).
* A autenticação principal é **por sessão**, não por access tokens. Use `@adonisjs/session` com store `database` (tabela `sessions`, `SESSION_DRIVER=database`), `age` de `'30 days'` e cookie `httpOnly`, `secure` em produção e `sameSite: 'lax'`. Isso evita sequestro de sessão e mitiga XSS/CSRF.
* Access tokens só devem ser usados para integrações específicas (ex: MCP/integrações externas), nunca como mecanismo principal de login do SPA.
* Sempre use middleware de rotas para verificações de autenticação: `router.use(middleware.auth())` (ou `middleware.auth({ guards: ['web'] })`). Evite escrever verificações manuais nos controladores.

### 2. Autorização (Políticas e Abilities do Bouncer)
* Utilize o pacote oficial `@adonisjs/bouncer` para gerenciar o controle de acesso granular aos recursos.
* Dê preferência a **Políticas do Bouncer (Policies)** em vez de **Abilities** inline para modelos de domínio, mantendo a lógica de autorização desacoplada das definições de rotas. Crie-as utilizando `node ace make:policy <nome>`.
* **Isolamento de Multitenancy**: Em todas as políticas relacionadas a recursos (ex: Post, Comment), sempre compare o identificador do tenant do recurso (ex: `solar_company_id`) com o identificador do tenant do usuário autenticado antes de conceder acesso:
  ```typescript
  async view(user: User, post: Post) {
    return user.solarCompanyId === post.solarCompanyId
  }
  ```
* Imponha a autorização dentro dos controladores utilizando o helper de bouncer do contexto HTTP: `await bouncer.with(PostPolicy).authorize('view', post)`.
* Trate falhas de autorização de forma amigável. O Bouncer do AdonisJS lança uma exceção `E_AUTHORIZATION_FAILURE` (classe `AuthorizationException`), que deve ser tratada globalmente no manipulador de exceções da aplicação ou localmente com blocos try-catch para retornar uma resposta estruturada de `403 Forbidden`.

### 3. Login Social (AdonisJS Ally)
* Utilize o `@adonisjs/ally` para autenticação OAuth com os provedores sociais configurados no projeto: **Google** e **Facebook**. Após o callback bem-sucedido, autentique o usuário pela sessão (`auth.use('web').login(user)`).
* Sempre trate os erros de callback de forma robusta utilizando `ally.use(provider).hasError()`. Nunca presuma que o fluxo OAuth sempre será bem-sucedido.
* Trate o registro do usuário durante os fluxos de callback. Certifique-se de que um tenant padrão (ou empresa apropriada ao contexto) seja atribuído aos novos usuários criados por meio de logins sociais.
* Proteja os estados de redirecionamento e URLs contra ataques de CSRF.

### 4. Segurança do Shield e CSRF
* Mantenha o `@adonisjs/shield` ativo globalmente para defender a aplicação contra vulnerabilidades web comuns como CSRF, XSS e Clickjacking.
* Habilite a proteção CSRF do Shield com `enableXsrfCookie: true` no `config/shield.ts`, de modo que o backend envie o cookie `XSRF-TOKEN`. O SPA (Vue puro, consumindo `/api` via rota catch-all) usa axios com `withCredentials` e `withXSRFToken`, lendo esse cookie e reenviando-o no cabeçalho `X-XSRF-TOKEN`. Mantenha os nomes de cookie/cabeçalho padrão para garantir essa compatibilidade.
* Não desative a validação CSRF globalmente. Se rotas específicas de webhook ou API exigirem isenção, configure-as especificamente no array `csrf.exceptRoutes` dentro do arquivo `config/shield.ts`.

## Exemplos

### Definindo uma Política do Bouncer com Verificações de Multitenancy
Crie políticas na pasta `app/policies/` seguindo o seguinte padrão:

```typescript
import User from '#models/user'
import Post from '#models/post'
import { BasePolicy } from '@adonisjs/bouncer'
import { AuthorizationResponse } from '@adonisjs/bouncer'

export default class PostPolicy extends BasePolicy {
  /**
   * Autoriza um usuário a visualizar um post. Deve pertencer ao mesmo tenant (solar_company_id).
   */
  async view(user: User, post: Post): Promise<AuthorizationResponse | boolean> {
    if (user.solarCompanyId !== post.solarCompanyId) {
      return AuthorizationResponse.deny('Você não pertence ao tenant proprietário deste recurso.', 403)
    }
    return true
  }

  /**
   * Autoriza a edição/exclusão. Deve ser o proprietário E pertencer ao mesmo tenant.
   */
  async edit(user: User, post: Post): Promise<AuthorizationResponse | boolean> {
    if (user.solarCompanyId !== post.solarCompanyId) {
      return AuthorizationResponse.deny('Incompatibilidade de tenant.', 403)
    }
    
    return user.id === post.userId
      ? true
      : AuthorizationResponse.deny('Apenas o autor pode modificar este post.', 403)
  }
}
```

### Executando Autorização dentro de um Controlador
Autorizando o acesso a um recurso dentro de um controlador HTTP:

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import Post from '#models/post'
import PostPolicy from '#policies/post_policy'

export default class PostsController {
  async show({ params, bouncer, response }: HttpContext) {
    const post = await Post.findOrFail(params.id)
    
    // Verificação de autorização explícita
    await bouncer.with(PostPolicy).authorize('view', post)

    return response.ok(post)
  }
}
```

### Controlador de Callback Seguro com Ally OAuth
Tratamento do fluxo de login social com tratamento robusto de erros e exceções:

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import User from '#models/user'
import logger from '@adonisjs/core/services/logger'

export default class SocialAuthController {
  async redirect({ ally }: HttpContext) {
    return ally.use('google').redirect()
  }

  async callback({ ally, auth, response }: HttpContext) {
    const google = ally.use('google')

    // 1. Verifica erros no fluxo do provedor/usuário
    if (google.hasError()) {
      if (google.accessDenied()) {
        logger.info('Fluxo OAuth cancelado pelo usuário.')
        return response.redirect().toRoute('login', {}, { qs: { q: 'auth_canceled' } })
      }
      logger.error('Erro de autenticação OAuth: ' + google.getError())
      return response.redirect().toRoute('login', {}, { qs: { q: 'auth_failed' } })
    }

    try {
      const googleUser = await google.user()

      // 2. Obtém ou cria o usuário atribuindo-o a um tenant
      const user = await User.firstOrCreate(
        { email: googleUser.email },
        {
          fullName: googleUser.name,
          avatarUrl: googleUser.avatarUrl,
          // Sempre garanta o mapeamento de isolamento de tenant aqui
          solarCompanyId: 1, // Exemplo: Atribui um tenant padrão ou derivado do contexto
        }
      )

      // 3. Autentica a sessão do usuário
      await auth.use('web').login(user)

      return response.redirect().toRoute('dashboard')
    } catch (error) {
      logger.error(`SocialAuthError no callback: ${error.message}`)
      return response.redirect().toRoute('login', {}, { qs: { q: 'auth_exception' } })
    }
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Não** escreva regras de autorização inline nos controladores para objetos que exijam isolamento de tenant. Sempre delegue para as Políticas do Bouncer (Policies).
* **Não** ignore a verificação de multitenancy (ex: verificar apenas a propriedade do recurso, mas esquecer de comparar o contexto de tenant `solar_company_id`).
* **Não** armazene senhas em texto puro. Utilize o hashing do AdonisJS (mixin `withAuthFinder` com `hash` / `hash.make()`). Access tokens, quando usados para integrações (ex: MCP), também devem ser persistidos com hash.
* **Não** adote access tokens como mecanismo principal de autenticação do SPA — a sessão (`web` guard, sessões no banco, 30 dias) é o fluxo padrão.
* **Não** desative a proteção de CSRF de forma global. As exceções de rotas devem ser minimizadas e restritas a APIs específicas ou webhooks externos no arquivo `config/shield.ts`.
* **Não** processe callbacks de OAuth sem antes validar explicitamente se ocorreram erros por meio de `ally.use(provider).hasError()`.
