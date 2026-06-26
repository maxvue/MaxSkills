---
name: adonisjs-events-listeners-best-practices
description: Use when declaring, dispatching, or subscribing to events and listeners in AdonisJS v6. Triggers on emitter.emit calls, creating events in app/events, creating listeners in app/listeners, configuring start/events.ts, or managing asynchronous event workflows.
---

# Boas Práticas de Eventos e Ouvintes (Listeners) no AdonisJS v6

## Objetivo
Estabelecer padrões claros, desacoplados e de alta performance para a implementação de arquitetura orientada a eventos no AdonisJS v6. Esta skill garante segurança de tipos, carregamento sob demanda (lazy-loading) de ouvintes, tratamento robusto de erros, integração com transmissões (broadcasting) e processamento em segundo plano para evitar o bloqueio de requisições HTTP.

## Instruções

### 1. Declaração de Eventos Baseados em Classes
Sempre prefira **Eventos Baseados em Classes** a eventos baseados em strings para obter segurança de tipo nativa do TypeScript, sem necessidade de configurações adicionais.
- Armazene os eventos dentro do diretório `app/events/`.
- Crie as classes de eventos estendendo `BaseEvent` do pacote `@adonisjs/core/events`.
- Mantenha a classe focada puramente na carga de dados do evento (padrão DTO), sem lógica de negócios.

*Exemplo (`app/events/campaign_created.ts`):*
```typescript
import { BaseEvent } from '@adonisjs/core/events'
import type Campaign from '#models/campaign'

export default class CampaignCreated extends BaseEvent {
  constructor(public campaign: Campaign) {
    super()
  }
}
```

### 2. Implementação de Ouvintes (Listeners) Baseados em Classes
Implemente os ouvintes como classes no diretório `app/listeners/`. Utilize o comando gerador do Ace: `node ace make:listener <nome_do_listener>`.
- Mantenha os ouvintes enxutos; delegue a lógica complexa de negócios para os Services.
- Indique o tipo correto no parâmetro do evento no método `handle` para garantir a tipagem estrita.

*Exemplo (`app/listeners/notify_subscribers.ts`):*
```typescript
import type CampaignCreated from '#events/campaign_created'
import { inject } from '@adonisjs/core'
import Logger from '@adonisjs/core/services/logger'

@inject()
export default class NotifySubscribers {
  constructor(protected logger: Logger) {}

  async handle(event: CampaignCreated) {
    const { campaign } = event
    try {
      this.logger.info({ campaignId: campaign.id }, 'Enviando notificações da campanha para os inscritos...')
      // Chame a lógica do serviço aqui...
    } catch (error) {
      this.logger.error({ error, campaignId: campaign.id }, 'Falha ao notificar inscritos')
    }
  }
}
```

### 3. Registro de Inscrições (start/events.ts)
Registre as associações entre eventos e ouvintes no arquivo `start/events.ts`.
- Utilize **caminhos de string para carregamento sob demanda (lazy loading)** (ex: `'#listeners/notify_subscribers.handle'`) em vez de importar diretamente as classes dos ouvintes. Isso garante que os ouvintes só sejam instanciados em memória quando o evento for de fato disparado.
- Importe o emitter de `@adonisjs/core/services/emitter`.

*Exemplo (`start/events.ts`):*
```typescript
import emitter from '@adonisjs/core/services/emitter'
import CampaignCreated from '#events/campaign_created'

emitter.on(CampaignCreated, '#listeners/notify_subscribers.handle')
```
*(Certifique-se de que os aliases de caminho como `#listeners/*` estejam configurados no `tsconfig.json` e nos mapeamentos do `package.json`).*

### 4. Habilitando o Pré-carregamento (Preload) de Eventos no AdonisJS
Para que os eventos sejam processados, o arquivo `start/events.ts` precisa ser carregado durante a inicialização da aplicação:
- Abra o arquivo `adonisrc.ts` e adicione `#start/events` ao array `preloads`:

```typescript
preloads: [
  () => import('#start/routes'),
  () => import('#start/kernel'),
  () => import('#start/events') // Garante que os ouvintes de eventos sejam vinculados na inicialização
]
```

### 5. Disparando Eventos
Para disparar um evento, instancie a classe do evento e execute o método `dispatch()`:
```typescript
import CampaignCreated from '#events/campaign_created'

// Dentro de um controller ou service:
const campaign = await Campaign.create(data)
await CampaignCreated.dispatch(campaign)
```
*Nota:* No AdonisJS v6, a classe `BaseEvent` gerencia o disparo do evento, tornando as importações do emitter opcionais no local da chamada.

### 6. Testes e Falsificação (Faking) de Eventos
Nunca dispare efeitos colaterais reais durante os testes. Use o emitter fake para verificar se os eventos foram disparados sem de fato executar os ouvintes:
```typescript
import { test } from '@japa/runner'
import emitter from '@adonisjs/core/services/emitter'
import CampaignCreated from '#events/campaign_created'

test('criação de campanha dispara evento', async ({ assert }) => {
  const fakeEmitter = emitter.fake()

  // Executa a lógica que dispara o evento
  await createCampaignService()

  assert.true(fakeEmitter.hasTriggered(CampaignCreated))
  emitter.restore()
})
```

### 7. Integração com Transmissões (Broadcasting / WebSockets)
Para atualizações de progresso em tempo real, dispare eventos que se propagam para o frontend via Soketi/Pusher utilizando as convenções de transmissão:
- De dentro do ouvinte, utilize o serviço de transmissão WebSocket configurado para notificar os usuários nos canais adequados.

*Exemplo:*
```typescript
import type JobProgressUpdated from '#events/job_progress_updated'
// import broadcast service...
// broadcastService.toChannel(`jobs.${event.jobId}`).emit('progress', event.progress)
```

## Restrições
- **NÃO importe as classes dos ouvintes no arquivo `start/events.ts`:** Sempre use o formato de string com lazy loading (`'#listeners/nome.handle'`) para evitar sobrecarga de memória e lentidão no boot.
- **NÃO execute tarefas síncronas pesadas e não resilientes diretamente nos ouvintes:** Para tarefas que necessitam de retentativas automáticas ou execuções demoradas (como processamento de vídeo ou envio massivo de e-mails), delegue a execução para uma fila do BullMQ a partir do ouvinte, em vez de processá-la de forma síncrona.
- **NÃO se esqueça do tratamento e registro de exceções:** Todo ouvinte DEVE envolver seu bloco de execução em um `try/catch` e registrar falhas usando o serviço de `Logger` do AdonisJS.
- **NÃO defina eventos baseados em strings** sem a devida extensão de módulo TypeScript no arquivo de definições de tipo. Dê preferência absoluta a eventos baseados em classes.
