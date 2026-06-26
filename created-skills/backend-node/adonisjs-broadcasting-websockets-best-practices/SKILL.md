---
name: adonisjs-broadcasting-websockets-best-practices
description: Use when creating, configuring, or debugging WebSocket connections, event broadcasting, and real-time communication in AdonisJS. Triggers on private/public channel authorization, HMAC sha256 signature generation for Pusher/Soketi, event dispatching, and integrating with laravel-echo or Vue frontends.
---

# Melhores Práticas de Broadcasting e WebSockets no AdonisJS

## Objetivo
Padronizar a transmissão de eventos em tempo real usando o protocolo Pusher/Soketi no AdonisJS v6, protegendo canais privados com assinaturas HMAC personalizadas e integrando de forma eficiente com frontends Vue 3 através da biblioteca `@laravel/echo-vue`.

## Instruções

### 1. Integração do Cliente Pusher no Backend
* Sempre utilize um helper singleton em cache para inicializar o cliente `Pusher`. Isso evita vazamentos de recursos e instâncias duplicadas de conexão:
  ```typescript
  import Pusher from 'pusher'
  import env from '#start/env'

  let pusherInstance: Pusher | null = null

  export function getPusher(): Pusher {
    if (!pusherInstance) {
      pusherInstance = new Pusher({
        appId: env.get('SOKETI_APP_ID') || process.env.SOKETI_APP_ID!,
        key: env.get('SOKETI_APP_KEY') || process.env.SOKETI_APP_KEY!,
        secret: env.get('SOKETI_APP_SECRET') || process.env.SOKETI_APP_SECRET!,
        host: env.get('SOKETI_HOST') || process.env.SOKETI_HOST!,
        port: env.get('SOKETI_PORT') || process.env.SOKETI_PORT!,
        useTLS: false,
        cluster: 'mt1',
      })
    }
    return pusherInstance
  }
  ```

* Dispare eventos com segurança dentro de serviços, controllers ou comandos:
  ```typescript
  const pusher = getPusher()
  await pusher.trigger('private-channel-name', 'EventName', {
    someData: 'value'
  })
  ```

### 2. Autorização de Canais Privados
* Registre a rota de autenticação de broadcasting em `start/routes.ts`:
  ```typescript
  const BroadcastingController = () => import('#controllers/broadcasting_controller')

  router.post('/broadcasting/auth', [BroadcastingController, 'auth'])
    .as('broadcasting.auth')
    .use(middleware.auth())
  ```

* Implemente autorização segura dentro do `BroadcastingController`:
  ```typescript
  import { createHmac } from 'node:crypto'
  import type { HttpContext } from '@adonisjs/core/http'
  import env from '#start/env'

  export default class BroadcastingController {
    async auth({ request, auth, response }: HttpContext) {
      const user = auth.user!
      const socketId = request.input('socket_id')
      const channelName = request.input('channel_name')

      if (!socketId || !channelName) {
        return response.badRequest({ message: 'socket_id e channel_name são obrigatórios.' })
      }

      // Autoriza o acesso ao canal combinando estritamente com os identificadores do usuário/empresa
      const isAuthorized =
        channelName === `private-system.${user.id}` ||
        channelName === `private-live.company.${user.solarCompanyId}`

      if (!isAuthorized) {
        return response.forbidden({ message: 'Acesso negado ao canal.' })
      }

      // Gera a assinatura HMAC exigida pelo servidor Pusher/Soketi
      const appKey = env.get('SOKETI_APP_KEY')
      const appSecret = env.get('SOKETI_APP_SECRET')
      const signature = createHmac('sha256', appSecret)
        .update(`${socketId}:${channelName}`)
        .digest('hex')

      return response.json({ auth: `${appKey}:${signature}` })
    }
  }
  ```

### 3. Integração com Frontend usando Vue 3 e Laravel Echo
* Inicialize o Echo em `configureReverbEcho.js` (o Reverb utiliza o protocolo Pusher):
  ```javascript
  import { configureEcho } from '@laravel/echo-vue'

  export function configureReverbEcho() {
    configureEcho({
      broadcaster: 'reverb',
      key: import.meta.env.VITE_REVERB_APP_KEY,
      wsHost: import.meta.env.VITE_REVERB_HOST,
      wsPort: 80,
      wssPort: 443,
      forceTLS: true,
      enabledTransports: ['ws', 'wss'],
      disableStats: true,
    })
  }
  ```

* Escute eventos nos componentes Vue usando o composable `useEcho`. Note que a biblioteca `@laravel/echo-vue` adiciona o prefixo `private-` automaticamente ao se inscrever com visibilidade privada (padrão):
  ```typescript
  import { useEcho } from '@laravel/echo-vue'

  // Se inscreve no canal 'private-live.company.XYZ' automaticamente
  useEcho(`live.company.${companyId}`, 'SocialMediaNewsImported', (payload: { count: number }) => {
    console.log(`${payload.count} novos itens importados.`)
  })
  ```

## Restrições
* NÃO exponha credenciais críticas de WebSocket (como `SOKETI_APP_SECRET`) no aplicativo frontend.
* NÃO adicione manualmente o prefixo `private-` aos nomes dos canais dentro do composable `useEcho` do frontend, a menos que esteja substituindo o parâmetro de visibilidade padrão para `'public'`. Fazer isso levará a inscrições incorretas (ex: `private-private-channel`).
* NÃO pule a verificação de usuário dentro do `BroadcastingController` do backend. O acesso aos canais `private-` deve ser verificado explicitamente contra o objeto de usuário autenticado.
* NÃO instancie `new Pusher(...)` múltiplas vezes; sempre obtenha a instância através da função de fábrica em cache.
