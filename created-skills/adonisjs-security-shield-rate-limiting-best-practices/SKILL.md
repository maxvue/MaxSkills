---
name: adonisjs-security-shield-rate-limiting-best-practices
description: Use when configuring security middleware, protecting routes against CSRF, configuring CORS or Content Security Policy (CSP) with AdonisJS Shield, or implementing Redis-based rate limiting on AdonisJS API routes to prevent API abuse and token exhaustion.
---

## Objetivo
Estabelecer políticas robustas de segurança e prevenir o abuso de recursos em aplicações AdonisJS v6, configurando o AdonisJS Shield para proteção contra CSRF/CORS/CSP, registrando limites de taxa (Rate Limit) baseados em Redis para rotas críticas e tratando exceções de segurança de forma limpa.

## Instruções

### 1. Proteção CSRF e Exclusão de Webhooks
O AdonisJS Shield fornece proteção global contra Cross-Site Request Forgery (CSRF). No entanto, endpoints externos como webhooks de inversores/integrações de terceiros (`/webhooks/inverter`) não possuem um token CSRF e falharão com erro `403 Forbidden` se não forem explicitamente excluídos.
- **Configuração de CSRF (`config/shield.ts`):**
  Garanta que o CSRF esteja ativo e adicione as rotas de webhooks externos em `exceptRoutes`. No `@adonisjs/shield` v8, `exceptRoutes` aceita um array de strings — que casa contra o **padrão de rota registrado** (`ctx.route.pattern`, com placeholders de parâmetro como `/projects/:id`), não contra a URL concreta da requisição — OU uma função para lógica dinâmica. Não há suporte nativo a glob (`*`). Para excluir um prefixo de rotas (ex.: `/api/webhooks/...`), use a forma de callback, que recebe o `ctx` e pode inspecionar `ctx.request.url()`.
  ```typescript
  csrf: {
    enabled: true,
    // Use callback para excluir prefixos; o array de strings casa o padrão de rota (ctx.route.pattern), não a URL da requisição.
    exceptRoutes: (ctx) => {
      const url = ctx.request.url()
      return url === '/webhooks/inverter' // callback de webhook do inversor
        || url.startsWith('/api/webhooks/') // demais webhooks de terceiros da API
    },
    enableXsrfCookie: true, // Crucial para que o frontend Vue 3 SPA consiga recuperar o token
    methods: ['POST', 'PUT', 'PATCH', 'DELETE'],
  }
  ```

### 2. Limitação de Taxa Baseada em Redis (AdonisJS Limiter)
Para operações dispendiosas, como chamadas de LLM/Agentes de IA, rotas suscetíveis a força bruta (ex: `/login`) ou manipuladores de webhook, implemente limitação de taxa baseada em Redis.

> **Pré-requisito (obrigatório):** o `@adonisjs/limiter` e uma conexão Redis (`@adonisjs/redis`) **não** fazem parte das dependências base deste projeto. Instale-os antes de usar o código abaixo: `node ace add @adonisjs/limiter` e `node ace add @adonisjs/redis` (configure a conexão em `config/redis.ts`). Sem esses pacotes, os imports `@adonisjs/limiter`/`@adonisjs/redis` a seguir não resolvem.
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
    router.post('/projects/:project/run/sizing', [ProjectAiController, 'runSizing'])
    router.post('/projects/:project/run/report', [ProjectAiController, 'runReport'])
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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca desative o CSRF globalmente:** Não desligue a proteção contra CSRF em `config/shield.ts` para resolver problemas de Webhooks/APIs. Sempre exclua as rotas específicas usando o array `exceptRoutes`.
- **Nunca use o Memory Store do Limiter em produção:** O armazenamento em memória padrão para limites de taxa não é compartilhado entre processos ou após reinicializações. Sempre force o driver `redis` em produção para consistência.
- **Nunca exponha stack traces em erros de segurança:** Sempre oculte stack traces e detalhes internos nas respostas de `E_TOO_MANY_REQUESTS` e `E_BAD_CSRF_TOKEN`, retornando apenas a mensagem amigável e o `code`. Isso vale inclusive ao testar localmente simulando o comportamento de um cliente de produção.
- **Não ignore a identificação do usuário no rate limit:** A chave de limitação de taxa deve priorizar o ID do usuário autenticado (`user_id`) em vez do IP bruto, evitando bloqueios indevidos de IPs compartilhados.
- **Certifique-se de que o cookie XSRF-TOKEN está ativo:** Nunca defina `enableXsrfCookie` como `false` ao criar endpoints consumidos por uma SPA Vue 3, pois ela depende desse cookie para autenticar requisições do tipo POST/PUT/PATCH/DELETE.
