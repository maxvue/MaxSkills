---
name: adonisjs-security-shield-rate-limiting-best-practices
description: Use when configuring security middleware, protecting routes against CSRF, configuring CORS or Content Security Policy (CSP) with AdonisJS Shield, or implementing Redis-based rate limiting on AdonisJS API routes to prevent API abuse and token exhaustion.
---

## Objetivo
Estabelecer políticas robustas de segurança e prevenir o abuso de recursos em aplicações AdonisJS v6, configurando o AdonisJS Shield para proteção contra CSRF/CORS/CSP, registrando limites de taxa (Rate Limit) baseados em Redis para rotas críticas e tratando exceções de segurança de forma limpa.

## Instruções

### 1. Proteção CSRF e Exclusão de Webhooks
O AdonisJS Shield fornece proteção global contra Cross-Site Request Forgery (CSRF). No entanto, endpoints externos como Webhooks da Meta (`/webhooks/meta`) não possuem um token CSRF e falharão com erro `403 Forbidden` se não forem explicitamente excluídos.
- **Configuração de CSRF (`config/shield.ts`):**
  Garanta que o CSRF esteja ativo e adicione as rotas de webhooks externos em `exceptRoutes`.
  ```typescript
  csrf: {
    enabled: true,
    exceptRoutes: [
      '/webhooks/meta', // Exclui o endpoint de callback de webhook da Meta
      '/api/webhooks/*' // Exclui quaisquer outros webhooks de terceiros da API
    ],
    enableXsrfCookie: true, // Crucial para que o frontend Vue 3 SPA consiga recuperar o token
    methods: ['POST', 'PUT', 'PATCH', 'DELETE'],
  }
  ```

### 2. Limitação de Taxa Baseada em Redis (AdonisJS Limiter)
Para operações dispendiosas, como chamadas de LLM/Agentes de IA, rotas suscetíveis a força bruta (ex: `/login`) ou manipuladores de webhook, implemente limitação de taxa baseada em Redis.
- **Configuração do Limiter (`config/limiter.ts`):**
  Configure o armazenamento Redis para compartilhar os limites de taxa em arquiteturas com múltiplos nós ou workers.
  ```typescript
  import env from '#start/env'
  import { defineConfig, stores } from '@adonisjs/limiter'

  const limiterConfig = defineConfig({
    default: 'redis',
    stores: {
      redis: stores.redis({
        connectionName: 'main', // Deve corresponder à conexão definida em config/redis.ts
        keyPrefix: 'limiter_',
      }),
    },
  })

  export default limiterConfig
  ```
- **Definindo Limites de Taxa (`start/limiter.ts`):**
  Defina as regras usando o serviço `limiter`.
  ```typescript
  import limiter from '@adonisjs/limiter/services/main'

  // Limita rotas de IA a 10 requisições por minuto por usuário autenticado (ou IP)
  export const aiLimiter = limiter.define('ai_calls', (ctx) => {
    const user = ctx.auth.user
    const key = user ? `user_${user.id}` : `ip_${ctx.request.ip()}`
    
    return limiter
      .allowRequests(10)
      .every('1 minute')
      .usingKey(key)
  })

  // Limita tentativas de login a 5 requisições a cada 15 minutos por IP
  export const loginLimiter = limiter.define('login', (ctx) => {
    return limiter
      .allowRequests(5)
      .every('15 mins')
      .usingKey(`login_${ctx.request.ip()}`)
  })
  ```
- **Registrando o Middleware do Limiter (`start/kernel.ts`):**
  Adicione o middleware na coleção de middlewares nomeados.
  ```typescript
  export const middleware = router.named({
    // ...outros middlewares
    limiter: () => import('@adonisjs/limiter/limiter_middleware'),
  })
  ```
- **Aplicando o Limiter às Rotas (`start/routes.ts`):**
  Vincule o middleware do limiter a rotas específicas.
  ```typescript
  import { aiLimiter, loginLimiter } from '#start/limiter'

  router.post('/login', [AuthController, 'login'])
    .use(middleware.limiter({ throttle: 'login' }))

  router.group(() => {
    router.post('/calendar/run/strategy', [CalendarExecuteController, 'runStrategy'])
    router.post('/calendar/event/:event/run/copywriter', [CalendarExecuteController, 'runCopywriter'])
  })
    .use(middleware.auth())
    .use(middleware.limiter({ throttle: 'ai_calls' }))
  ```

### 3. Tratamento Limpo de Exceções de Segurança
Certifique-se de que as exceções de segurança sejam capturadas e formatadas como respostas JSON estruturadas. Isso evita o vazamento de detalhes internos da arquitetura do servidor e fornece mensagens amigáveis para a SPA Vue 3.
- **Tratamento no Exception Handler (`app/exceptions/handler.ts`):**
  Capture `E_TOO_MANY_REQUESTS` (do Limiter) e `E_BAD_CSRF_TOKEN` (do Shield).
  ```typescript
  import { errors as limiterErrors } from '@adonisjs/limiter'
  import { errors as shieldErrors } from '@adonisjs/shield'
  import { type HttpContext, ExceptionHandler } from '@adonisjs/core/http'

  export default class HttpExceptionHandler extends ExceptionHandler {
    async handle(error: unknown, ctx: HttpContext) {
      // Trata violações de limite de taxa
      if (error instanceof limiterErrors.E_TOO_MANY_REQUESTS) {
        return ctx.response.status(429).send({
          errors: [
            {
              message: 'Muitas requisições. Por favor, tente novamente mais tarde.',
              code: 'E_TOO_MANY_REQUESTS',
              retryAfter: error.retryAfter,
            }
          ]
        })
      }

      // Trata token CSRF inválido ou expirado
      if (error instanceof shieldErrors.E_BAD_CSRF_TOKEN) {
        return ctx.response.status(403).send({
          errors: [
            {
              message: 'Token CSRF inválido ou expirado. Por favor, atualize a página.',
              code: 'E_BAD_CSRF_TOKEN',
            }
          ]
        })
      }

      return super.handle(error, ctx)
    }
  }
  ```

## Restrições
- **Nunca desative o CSRF globalmente:** Não desligue a proteção contra CSRF em `config/shield.ts` para resolver problemas de Webhooks/APIs. Sempre exclua as rotas específicas usando o array `exceptRoutes`.
- **Nunca use o Memory Store do Limiter em produção:** O armazenamento em memória padrão para limites de taxa não é compartilhado entre processos ou após reinicializações. Sempre force o driver `redis` em produção para consistência.
- **Nunca exponha stack traces em erros de segurança:** Ocultar stack traces para `E_TOO_MANY_REQUESTS` e `E_BAD_CSRF_TOKEN` mesmo em desenvolvimento ao simular requisições de clientes de produção.
- **Não ignore a identificação do usuário no rate limit:** A chave de limitação de taxa deve priorizar o ID do usuário autenticado (`user_id`) em vez do IP bruto, evitando bloqueios indevidos de IPs compartilhados.
- **Certifique-se de que o cookie XSRF-TOKEN está ativo:** Nunca defina `enableXsrfCookie` como `false` ao criar endpoints consumidos por uma SPA Vue 3, pois ela depende desse cookie para autenticar requisições do tipo POST/PUT/PATCH/DELETE.
