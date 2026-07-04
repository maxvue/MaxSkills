---
name: adonisjs-middleware-pipeline-best-practices
description: Use when creating, modifying, reviewing, or debugging custom route and global HTTP middlewares, configuring the middleware pipeline in start/kernel.ts, managing HttpContext modifications, or enforcing multitenancy, authentication, and subscription checks at the route layer in AdonisJS v6. Triggers on middleware declaration, router.use, kernel.ts, and middleware tests.
---

## Objetivo
Fornecer diretrizes, padrões de design e padrões de implementação para desenvolver, registrar e testar HTTP middlewares, gerenciar pipelines de middleware, estender as propriedades do `HttpContext` e aplicar preocupações transversais (autenticação, multitenancy, planos de assinatura) no AdonisJS v6.

## Instruções
Ao implementar ou modificar middlewares no AdonisJS v6, siga estas práticas:

### 1. Estrutura do Middleware
Os middlewares devem ser declarados como classes com um export default implementando o método `handle`.
- **Declarações de Import:** Use `@adonisjs/core/http` para referenciar o tipo `HttpContext` e `@adonisjs/core/types/http` para `NextFn`.
- **Execução Assíncrona:** Sempre chame `await next()` para delegar o controle ao próximo handler no pipeline. Capture ou modifique a resposta após o `next()` caso seja necessário pós-processamento.

*Exemplo:*
```typescript
import { HttpContext } from '@adonisjs/core/http'
import { NextFn } from '@adonisjs/core/types/http'

export default class RequestLoggerMiddleware {
  async handle(ctx: HttpContext, next: NextFn) {
    // Lógica de pré-requisição
    const startTime = Date.now()

    const result = await next()

    // Lógica de pós-requisição
    const duration = Date.now() - startTime
    ctx.logger.info(`${ctx.request.method()} ${ctx.request.url()} - ${duration}ms`)

    return result
  }
}
```

### 2. Registro de Middleware e Configuração do Kernel
O AdonisJS v6 usa o arquivo `start/kernel.ts` para registrar middlewares globais e nomeados.
- **Middlewares Globais:** Registre usando `server.use()`. Eles executam para toda requisição HTTP recebida.
- **Middlewares de Router:** Registre usando `router.use()`. Eles executam para requisições que correspondem às rotas definidas.
- **Middlewares Nomeados:** Defina-os usando `router.named()` e vincule-os com lazy-load via funções de import.

*Exemplo de `start/kernel.ts`:*
```typescript
import router from '@adonisjs/core/services/router'
import server from '@adonisjs/core/services/server'

server.use([
  () => import('#middleware/container_bindings_middleware'),
  () => import('#middleware/force_json_response_middleware'),
])

router.use([
  () => import('@adonisjs/core/bodyparser_middleware'),
  () => import('#middleware/silent_auth_middleware'),
])

export const middleware = router.named({
  auth: () => import('#middleware/auth_middleware'),
  tenant: () => import('#middleware/tenant_middleware'),
  subscription: () => import('#middleware/subscription_middleware'),
})
```

### 3. Middlewares Nomeados com Parâmetros
Ao passar opções/parâmetros para um middleware nomeado:
- Defina o terceiro parâmetro no método `handle` com um objeto de configuração tipado.
- Aplique-o às rotas usando o objeto de middleware carregado por lazy-load.

*Exemplo:*
```typescript
// middleware/role_middleware.ts
import { HttpContext } from '@adonisjs/core/http'
import { NextFn } from '@adonisjs/core/types/http'

export default class RoleMiddleware {
  async handle(ctx: HttpContext, next: NextFn, options: { allowedRoles: string[] }) {
    const user = ctx.auth.user
    if (!user || !options.allowedRoles.includes(user.role)) {
      return ctx.response.forbidden({ error: 'Access denied: Insufficient permissions.' })
    }
    return next()
  }
}
```

*Uso nas Rotas:*
```typescript
import router from '@adonisjs/core/services/router'
import { middleware } from '#start/kernel'

router
  .get('/admin', 'AdminController.index')
  .use(middleware.role({ allowedRoles: ['admin', 'superadmin'] }))
```

### 4. Estendendo o HttpContext com Declarações TypeScript
Quando middlewares anexam metadados ou entidades customizadas (ex: `tenant`, `currentUser`) ao `ctx`:
- Estenda a declaração da interface `HttpContext` para garantir a segurança de tipos.
- Coloque as declarações em um arquivo `.ts` (ex: `src/types/http.ts` ou `contracts/http.ts`).

*Exemplo:*
```typescript
import Tenant from '#models/tenant'

declare module '@adonisjs/core/http' {
  interface HttpContext {
    tenant?: Tenant
  }
}
```

### 5. Aplicação de Multitenancy e Assinaturas
- **Resolução de Multitenancy:** Use um middleware para detectar o tenant atual (ex: via header `X-Tenant-ID`, query parameter ou subdomínios). Resolva o model do tenant, anexe-o a `ctx.tenant` e falhe cedo com `404 Not Found` ou `400 Bad Request` se a resolução falhar.
- **Verificações de Assinatura:** Garanta que o tenant ou usuário tenha credenciais ou cotas ativas. Lance uma exceção customizada ou retorne `402 Payment Required` se as cotas forem excedidas.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill está escrito.
- Nunca mute o `HttpContext` sem estender sua declaração TypeScript, pois isso quebra a verificação do compilador e o autocomplete.
- Evite registrar processamento pesado, chamadas de rede externas ou execução síncrona bloqueante diretamente em middlewares globais; use queues ou eventos assíncronos quando aplicável.
- Não ignore o `await next()` nos caminhos de sucesso, pois isso interrompe a cadeia de execução e impede que middlewares e controllers subsequentes sejam executados.
