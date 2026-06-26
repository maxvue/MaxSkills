---
name: adonisjs-broadcasting-websockets-best-practices
description: Use when creating, configuring, or debugging real-time event broadcasting and server-sent events in AdonisJS using @adonisjs/transmit. Triggers on Transmit channel authorization, broadcasting events from controllers/services, the @adonisjs/transmit-client (EventSource), and integrating real-time streams with Vue 3 frontends.
---

# Melhores Práticas de Broadcasting e Real-time no AdonisJS (Transmit)

## Objetivo
Padronizar a transmissão de eventos em tempo real usando o **AdonisJS Transmit** (Server-Sent Events / SSE) no AdonisJS v6, protegendo canais privados com autorização baseada na sessão autenticada (guard `web`) e integrando de forma eficiente com frontends Vue 3 através do cliente oficial `@adonisjs/transmit-client`.

> Transmit usa SSE sobre HTTP, sem servidor de WebSocket externo. NÃO há Pusher, Soketi, Reverb nem `laravel-echo` neste stack.

## Instruções

### 1. Configuração do Transmit no Backend
* Instale e configure o pacote oficial. O broadcasting de eventos é feito pelo serviço singleton `transmit` exportado pelo container:
  ```typescript
  // config/transmit.ts
  import { defineConfig } from '@adonisjs/transmit'

  export default defineConfig({
    pingInterval: false,
    transport: null,
  })
  ```

* Dispare eventos com segurança de dentro de serviços, controllers ou comandos usando o serviço `transmit`:
  ```typescript
  import transmit from '@adonisjs/transmit/services/main'

  // Publica no canal; o payload é serializado como JSON automaticamente
  await transmit.broadcast(`live/company/${companyId}`, {
    event: 'GenerationReportImported',
    count: 42,
  })
  ```

### 2. Autorização de Canais Privados
* Registre as rotas do Transmit e autorize canais privados em `start/transmit.ts`. A autorização usa a sessão autenticada (guard `web`), não tokens nem assinaturas HMAC:
  ```typescript
  import transmit from '@adonisjs/transmit/services/main'

  // Canal privado por usuário
  transmit.authorize<{ id: string }>('system/:id', (ctx, { id }) => {
    return ctx.auth.user?.id === Number(id)
  })

  // Canal privado por empresa solar (multi-tenant)
  transmit.authorize<{ companyId: string }>('live/company/:companyId', (ctx, { companyId }) => {
    return ctx.auth.user?.solarCompanyId === Number(companyId)
  })
  ```

* Registre as rotas HTTP do Transmit em `start/routes.ts`, protegidas pelo middleware de autenticação por sessão:
  ```typescript
  import transmit from '@adonisjs/transmit/services/main'
  import { middleware } from '#start/kernel'

  transmit.registerRoutes((route) => {
    // Garante que apenas usuários autenticados (sessão+cookie) assinem canais
    route.use(middleware.auth())
  })
  ```

### 3. Integração com Frontend usando Vue 3 e o Transmit Client
* Inicialize o cliente em um módulo dedicado (ex.: `app/transmit.ts`). O `@adonisjs/transmit-client` usa `EventSource` por baixo dos panos, então o cookie de sessão acompanha a conexão automaticamente:
  ```typescript
  import { Transmit } from '@adonisjs/transmit-client'

  export const transmit = new Transmit({
    baseUrl: window.location.origin,
  })
  ```

* Escute eventos nos componentes Vue assinando o canal e registrando o callback. Lembre-se de cancelar a inscrição ao desmontar o componente:
  ```typescript
  import { onUnmounted } from 'vue'
  import { transmit } from '@/transmit'

  // Assina o canal privado 'live/company/XYZ' (autorizado via sessão no backend)
  const subscription = transmit.subscription(`live/company/${companyId}`)
  await subscription.create()

  const unsubscribe = subscription.onMessage((payload: { event: string; count: number }) => {
    console.log(`${payload.count} novos itens importados.`)
  })

  onUnmounted(() => {
    unsubscribe()
    subscription.delete()
  })
  ```

> Dados de página (GET/save) continuam passando por stores `@maxvue/max-pinia`. O Transmit é apenas o canal de notificação/push; ao receber um evento, dispare o refetch pela store correspondente em vez de montar requisições manuais.

## Restrições
* NÃO use Pusher, Soketi, Reverb ou `@laravel/echo-vue` — o realtime do stack-alvo é exclusivamente AdonisJS Transmit (SSE).
* NÃO gere assinaturas HMAC nem exponha segredos de WebSocket no frontend; a autorização de canais é feita pela sessão autenticada no backend via `transmit.authorize`.
* NÃO leia variáveis de ambiente com `process.env.*`; use sempre `env.get(...)` (validado em `start/env.ts`) quando precisar de configuração.
* NÃO pule a verificação de usuário dentro de `transmit.authorize`. O acesso a canais privados deve ser verificado explicitamente contra a sessão/usuário autenticado (`ctx.auth.user`).
* NÃO esqueça de cancelar a inscrição (`unsubscribe` / `subscription.delete()`) ao desmontar componentes Vue, evitando vazamentos de conexões SSE.
