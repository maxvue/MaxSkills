---
name: vue-adonis-transmit-sse-best-practices
description: Use when implementing real-time updates, live notifications, or server-push communication in Vue 3 components that connect to an AdonisJS backend using @adonisjs/transmit (Server-Sent Events/SSE). This replaces Laravel Echo — do NOT use laravel-echo or WebSockets for server-push in this stack. Triggers on SSE channel subscriptions, TransmitClient singleton setup, real-time feed updates, live status indicators, and cleanup on component unmount.
---

# Boas Práticas: Vue 3 + AdonisJS Transmit (SSE)

## Objetivo
Padronizar a comunicação em tempo real entre o frontend Vue 3 e o backend AdonisJS usando Server-Sent Events (SSE) via `@adonisjs/transmit-client`. Este é o padrão de comunicação server-push neste projeto — **nunca use Laravel Echo, Pusher, Soketi ou WebSockets para este fim.**

---

## Arquitetura

```
AdonisJS Transmit (backend) ──SSE──► @adonisjs/transmit-client (frontend Vue 3)
```

- O backend publica eventos em canais via `transmit.broadcast()`.
- O frontend cria uma subscription ao canal e recebe os dados em tempo real.
- Canais privados são autenticados via endpoint de autorização no backend.

---

## Instruções

### 1. Singleton do TransmitClient (`resources/Functions/transmit.ts`)
Crie uma única instância do cliente Transmit para toda a aplicação. Evite instanciar múltiplas conexões SSE:

```typescript
import { Transmit } from '@adonisjs/transmit-client'

let transmitInstance: Transmit | null = null

export function useTransmitClient(): Transmit {
  if (!transmitInstance) {
    transmitInstance = new Transmit({
      baseUrl: window.location.origin,
    })
  }
  return transmitInstance
}
```

### 2. Composable `useTransmitChannel`
Crie um composable reutilizável para gerenciar subscriptions com cleanup automático:

```typescript
import { onUnmounted } from 'vue'
import { useTransmitClient } from '@/Functions/transmit'
import type { Subscription } from '@adonisjs/transmit-client'

export function useTransmitChannel(
  channel: string,
  onMessage: (data: unknown) => void
) {
  const transmit = useTransmitClient()
  let subscription: Subscription | null = null

  async function subscribe() {
    subscription = transmit.subscription(channel)
    await subscription.create()

    subscription.onMessage((data) => {
      onMessage(data)
    })
  }

  function unsubscribe() {
    subscription?.delete()
    subscription = null
  }

  // Cleanup automático ao desmontar o componente
  onUnmounted(() => {
    unsubscribe()
  })

  return { subscribe, unsubscribe }
}
```

### 3. Usando em Componentes Vue
```vue
<template>
  <div>
    <div v-for="notification in notifications" :key="notification.id">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTransmitChannel } from '@/Functions/composables/useTransmitChannel'

interface Notification {
  id: string
  message: string
}

const notifications = ref<Notification[]>([])

const { subscribe } = useTransmitChannel(
  'notifications/user/123', // canal do usuário
  (data) => {
    notifications.value.push(data as Notification)
  }
)

onMounted(async () => {
  await subscribe()
})
</script>
```

### 4. Canais Privados com Autorização
Para canais que exigem autenticação, configure a autorização no AdonisJS. **Não há token a passar no cliente** — o `@adonisjs/transmit-client` já envia `withCredentials: true`, portanto o cookie de sessão é incluído automaticamente nas requisições de subscribe/EventSource. O backend lê `ctx.auth.user` no callback `authorize`:

```typescript
// Frontend: transmit.ts
transmitInstance = new Transmit({
  baseUrl: window.location.origin,
  uidGenerator: () => crypto.randomUUID(),
})
```

```typescript
// Backend: start/transmit.ts
import transmit from '@adonisjs/transmit/services/main'
import { middleware } from '#start/kernel'

transmit.authorize<{ userId: string }>(
  'notifications/user/:userId',
  async (ctx, { userId }) => {
    // PKs são ULID/UUID (string) neste stack — compare como string, sem Number()
    return ctx.auth.user?.id === userId
  }
)
```

### 5. Backend: Publicando Eventos
No backend AdonisJS, publique eventos em canais a partir de controllers, services ou jobs:

```typescript
import transmit from '@adonisjs/transmit/services/main'

// Em qualquer lugar no backend
await transmit.broadcast(`notifications/user/${userId}`, {
  id: ulid(),
  message: 'Seu projeto foi aprovado!',
  type: 'success',
})
```

---

## Padrões de Canais

| Caso de uso | Padrão de canal |
|---|---|
| Notificações do usuário | `notifications/user/:userId` |
| Status de tarefa em background | `jobs/status/:jobId` |
| Chat de suporte | `support/chat/:ticketId` |
| Atualizações de projeto | `projects/:projectId/updates` |
| Feed global da empresa | `company/:companyId/feed` |

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca use `laravel-echo`, Pusher, Soketi ou qualquer lib de WebSocket** para comunicação server-push. Use exclusivamente `@adonisjs/transmit-client`.
- **Sempre limpe as subscriptions** no `onUnmounted` (o composable `useTransmitChannel` já faz isso automaticamente via `subscription.delete()`).
- **Singleton obrigatório**: nunca instancie `new Transmit()` diretamente nos componentes — use sempre `useTransmitClient()` para reutilizar a conexão.
- **Canais privados precisam de autorização** no backend via `transmit.authorize()`. Nunca exponha dados sensíveis em canais públicos.
- **SSE é unidirecional** (servidor → cliente). Para comunicação bidirecional (ex: envio de mensagens de chat), use requisições HTTP normais via axios/MaxPinia para o envio, e SSE apenas para receber atualizações do servidor.
