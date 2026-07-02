---
name: adonisjs-transmit-sse-realtime-best-practices
description: Use when implementing, configuring, or debugging real-time notifications, event broadcasting, or Server-Sent Events (SSE) using @adonisjs/transmit on the backend, including channel authorization, broadcasting events from controllers/services/commands, and protecting Transmit routes with session auth middleware, or when subscribing to channels, handling stream connections, and listening to events with @adonisjs/transmit-client (EventSource) in Vue 3 frontends. Replaces Pusher/Soketi/Reverb/laravel-echo WebSocket setups.
---

# Boas Práticas para AdonisJS Transmit e SSE em Tempo Real

## Objetivo
Padronizar a comunicação em tempo real usando Server-Sent Events (SSE) via `@adonisjs/transmit` no backend AdonisJS v6 e `@adonisjs/transmit-client` no frontend Vue 3, garantindo canais privados seguros e evitando vazamentos de memória.

> O Transmit usa SSE sobre HTTP, sem servidor de WebSocket externo. NÃO há Pusher, Soketi, Reverb nem `laravel-echo` neste stack. A autorização de canais é baseada na sessão autenticada (guard `web`), não em tokens nem assinaturas HMAC.

## Instruções

### 1. Configuração do Backend (`config/transmit.ts`)
Garanta que o `@adonisjs/transmit` esteja configurado corretamente. Para requisições de mesma origem ou sessões baseadas em cookies, mantenha o transport como `null` (SSE nativo) e desative o `pingInterval` se os buffers de proxy causarem desconexões:
```typescript
import { defineConfig } from '@adonisjs/transmit'

export default defineConfig({
  pingInterval: false,
  transport: null
})
```

### 2. Registro de Rotas e Autorização de Canais (`start/transmit.ts`)
- Sempre chame `transmit.registerRoutes()` para expor os endpoints internos de SSE (`/__transmit/*`).
- Proteja as próprias rotas HTTP do Transmit aplicando o middleware de autenticação por sessão, garantindo que apenas usuários autenticados (sessão+cookie) possam abrir o stream e assinar canais.
- Proteja os canais declarando rotas privadas usando `transmit.authorize<Params>`. Aproveite a autenticação de sessão registrada globalmente (ex: `ctx.auth.user`) para autorizar as requisições de inscrição.

**Exemplo:**
```typescript
import transmit from '@adonisjs/transmit/services/main'
import { middleware } from '#start/kernel'

// Garante que apenas usuários autenticados (sessão+cookie) assinem canais
transmit.registerRoutes((route) => {
  route.use(middleware.auth())
})

// Canal privado do usuário
transmit.authorize<{ id: string }>('users/:id/calendar', (ctx, { id }) => {
  // O param `id` chega como string; o PK do User é numérico. Coaja para número
  // antes de comparar, senão `number === string` é sempre false e ninguém assina.
  return ctx.auth.user?.id === Number(id)
})

// Canal privado da empresa
transmit.authorize<{ id: string }>('companies/:id/news', (ctx, { id }) => {
  return ctx.auth.user?.solarCompanyId === Number(id)
})
```

### 3. Disparo de Eventos pelo Backend
Importe o serviço do Transmit e chame `broadcast` informando o caminho do canal e um payload JSON estruturado:
```typescript
import transmit from '@adonisjs/transmit/services/main'

// Disparo para um canal de empresa
await transmit.broadcast(`companies/${companyId}/news`, { count: newNewsCount })
```

### 4. Instanciação do Cliente no Frontend (`src/lib/transmit.ts`)
Exponha uma instância singleton do cliente configurada com a origem atual. Os cookies de sessão são encaminhados automaticamente pelo navegador:
```typescript
import { Transmit } from '@adonisjs/transmit-client'

let _transmit: Transmit | null = null

export function useTransmit(): Transmit {
  if (!_transmit) {
    _transmit = new Transmit({
      baseUrl: window.location.origin
    })
  }
  return _transmit
}
```

### 5. Integração com Componente Vue 3 no Frontend (Composition API)
Sempre limpe as inscrições quando os componentes forem desmontados para evitar vazamentos de memória e ouvintes (listeners) duplicados.

**Exemplo de Estrutura de Componente:**
```vue
<template>
  <div p-4>
    <!-- Elementos de interface (UnoCSS attributify via presetMaxUno) -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useTransmit } from '@/lib/transmit'
import { useNewsStore } from '@/stores/news'

let newsSubscription: ReturnType<ReturnType<typeof useTransmit>['subscription']> | null = null

onMounted(() => {
  setupNewsListener()
})

onUnmounted(() => {
  // CRÍTICO: Limpar a inscrição para evitar vazamentos de memória
  if (newsSubscription) {
    newsSubscription.delete()
    newsSubscription = null
  }
})

async function setupNewsListener(): Promise<void> {
  const companyId = '123' // Obter dinamicamente
  const transmit = useTransmit()
  const newsStore = useNewsStore()

  newsSubscription = transmit.subscription(`companies/${companyId}/news`)
  await newsSubscription.create()

  // O payload do SSE NÃO substitui o fluxo MaxPinia: o GET dos dados continua
  // vindo da store @maxvue/max-pinia. Aqui apenas atualizamos reativamente a store
  // (ou disparamos um refresh dela) com a contagem recebida em tempo real.
  newsSubscription.onMessage<{ count: number }>((payload) => {
    newsStore.unreadCount = payload.count
  })
}
</script>
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO utilizar Echo/Soketi/Pusher/Reverb:** Não use Laravel Echo, Soketi, Pusher, Reverb (`@laravel/echo-vue`) ou pacotes WebSocket crus para funcionalidades em tempo real em novos desenvolvimentos no AdonisJS v6. Sempre dê preferência ao `@adonisjs/transmit`.
- **SEM HMAC nem segredos no frontend:** Nunca gere assinaturas HMAC nem exponha segredos de WebSocket no frontend. A autorização de canais é feita exclusivamente pela sessão autenticada no backend via `transmit.authorize`.
- **Configuração via `env.get(...)`:** Nunca leia variáveis de ambiente com `process.env.*`; use sempre `env.get(...)` (validado em `start/env.ts`) quando precisar de configuração.
- **Limpeza OBRIGATÓRIA:** Nunca se esqueça de chamar `.delete()` e anular a referência da inscrição dentro do hook `onUnmounted` do Vue 3, evitando vazamentos de memória e de conexões SSE.
- **Autorização Estrita:** Nunca exponha curingas (wildcards) ou canais públicos para dados de recursos sensíveis. Sempre valide se o usuário autenticado (`ctx.auth.user`) é o proprietário ou tem acesso ao ID do canal solicitado em `transmit.authorize`.
