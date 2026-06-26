---
name: adonisjs-transmit-sse-realtime-best-practices
description: Use when implementing, configuring, or debugging real-time notifications, event broadcasting, or Server-Sent Events (SSE) using @adonisjs/transmit on the backend, or when subscribing to channels, handling stream connections, and listening to events with @adonisjs/transmit-client in Vue 3 frontends.
---

# Boas Práticas para AdonisJS Transmit e SSE em Tempo Real

## Objetivo
Padronizar a comunicação em tempo real usando Server-Sent Events (SSE) via `@adonisjs/transmit` no backend AdonisJS v6 e `@adonisjs/transmit-client` no frontend Vue 3, garantindo canais privados seguros e evitando vazamentos de memória.

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
- Proteja os canais declarando rotas privadas usando `transmit.authorize<Params>`. Aproveite a autenticação de sessão registrada globalmente (ex: `ctx.auth.user`) para autorizar as requisições de inscrição.

**Exemplo:**
```typescript
import transmit from '@adonisjs/transmit/services/main'

transmit.registerRoutes()

// Canal privado do usuário
transmit.authorize<{ id: string }>('users/:id/calendar', (ctx, { id }) => {
  return ctx.auth.user?.id === id
})

// Canal privado da empresa
transmit.authorize<{ id: string }>('companies/:id/news', (ctx, { id }) => {
  return ctx.auth.user?.solarCompanyId === id
})
```

### 3. Disparo de Eventos pelo Backend
Importe o serviço do Transmit e chame `broadcast` informando o caminho do canal e um payload JSON estruturado:
```typescript
import transmit from '@adonisjs/transmit/services/main'

// Disparo para um canal de empresa
await transmit.broadcast(`companies/${companyId}/news`, { count: newNewsCount })
```

### 4. Instanciação do Cliente no Frontend (`resources/Js/transmit.ts`)
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
  <div class="notifications-panel">
    <!-- Elementos de interface -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useTransmit } from '@js/transmit'

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
  
  newsSubscription = transmit.subscription(`companies/${companyId}/news`)
  await newsSubscription.create()

  newsSubscription.onMessage<{ count: number }>((payload) => {
    console.log('Quantidade de novas notícias:', payload.count)
    // Atualizar reativamente o estado ou store
  })
}
</script>

<style scoped lang="scss">
.notifications-panel {
  padding: 1rem;
}
</style>
```

## Restrições
- **NÃO utilizar Echo/Soketi/Pusher:** Não use Laravel Echo, Soketi ou pacotes WebSocket crus para funcionalidades em tempo real em novos desenvolvimentos no AdonisJS v6. Sempre dê preferência ao `@adonisjs/transmit`.
- **Limpeza OBRIGATÓRIA:** Nunca se esqueça de chamar `.delete()` e anular a referência da inscrição dentro do hook `onUnmounted` do Vue 3.
- **Autorização Estrita:** Nunca exponha curingas (wildcards) ou canais públicos para dados de recursos sensíveis. Sempre valide se o usuário autenticado (`ctx.auth.user`) é o proprietário ou tem acesso ao ID do canal solicitado em `transmit.authorize`.
