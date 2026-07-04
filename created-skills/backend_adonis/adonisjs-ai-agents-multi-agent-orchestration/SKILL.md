---
name: adonisjs-ai-agents-multi-agent-orchestration
description: Use when designing, building, orchestrating, or debugging multi-agent AI workflows and pipelines in AdonisJS v6. Triggers on sequential agent chaining, feedback loops (rejection/revision cycles), passing conversational context between agents (e.g., Copywriter to Revisor), and monitoring multi-agent step states.
---

# Orquestração de Múltiplos Agentes de IA no AdonisJS v6

## Objetivo
Estabelecer diretrizes arquiteturais robustas e padrões de código para orquestrar a colaboração, o fluxo sequencial, os loops de feedback, a persistência de estados e as atualizações do frontend em tempo real entre múltiplos agentes de IA especializados em aplicações backend desenvolvidas com o AdonisJS v6.

---

## Instruções

### 1. Gerenciamento e Persistência de Estados
Evite manter o estado de execução de múltiplos agentes puramente em memória. Pipelines longos são propensos a timeouts e falhas.
- **Estado do Model Lucid:** Use o modelo da entidade principal (por exemplo, `CalendarEvent`, um evento de conteúdo no calendário de marketing da empresa fotovoltaica) para persistir a etapa atual do pipeline usando uma coluna `status`.
- **Progressão de Status:** Etapas típicas do fluxo:
  - `draft` -> `extracting_themes` -> `planning` -> `generating_copy` -> `script_drafted` -> `revising_copy` -> `script_ready` -> `generating_art` -> `art_ready` -> `analyzing_art` -> `approved` / `rejected`
- **Armazenamento de Loops de Feedback e Rejeição:** Persista o feedback de revisão diretamente no banco de dados (por exemplo, coluna `rejection_observations`) para permitir que os agentes recuperem a razão do retrabalho.
- **Segmentação das Saídas dos Agentes:** Armazene passos detalhados em tabelas separadas (por exemplo, `CalendarEventScriptDetail` para cópias e prompts slide por slide, `CalendarEventArtworkAnalysis` para resultados de validação).

### 2. Execução de Pipelines Baseada em Filas (BullMQ)
Para execuções assíncronas, não execute cadeias de agentes em uma única requisição HTTP ou comando Ace. Desacople cada passo do agente em jobs dedicados do BullMQ.
- **Jobs Dedicados:** Crie uma classe Job para cada estágio de agente (por exemplo, `CopywriterJob`, `CopywriterReviewerJob`, `GraphicEditorJob`, `ArtAnalystJob`).
- **Despacho Sequencial:** Um job deve processar a execução de seu agente e disparar o próximo passo despachando o job subsequente por meio de sua fila assim que a condição de conclusão (`isDone`) for atendida.
- **Recuperação e Resiliência de Jobs:** Aproveite os parâmetros de retentativa do BullMQ. Garanta que a função `executeAgent` use cadeias de modelos de fallback (por exemplo, migrando de `gemini-2.5-pro` para `gemini-2.5-flash` em caso de erro).
- **Camada de IA:** `executeAgent` deve invocar os modelos através do **Vercel AI SDK** (`generateText`/`generateObject` com o provider Gemini via `@ai-sdk/google`), e não SDKs diretos do provedor. Isso padroniza o roteamento de modelos, tool-calling e fallback.

### 3. Implementando Loops de Feedback
Quando um agente rejeitar a saída de um agente anterior (por exemplo, `ArtAnalyst` rejeita o briefing visual ou copy da arte):
1. Atualize o campo `rejectionObservations` da entidade pai com critérios claros sobre o que falhou.
2. Atualize o status da entidade (por exemplo, altere o status para `script_drafted` ou acione uma revisão parcial).
3. Despache o job correspondente de volta para a fila (por exemplo, `CopywriterJob` com instruções para focar apenas nos slides reprovados, evitando reprocessar os aprovados).

### 4. Sincronização de Cliente em Tempo Real (AdonisJS Transmit / SSE)
- Use **AdonisJS Transmit** (SSE) para transmitir eventos ao frontend sempre que um estado mudar ou um agente concluir um passo. Não use Pusher/Soketi/Reverb/Echo.
- Chame um método de serviço (por exemplo, `broadcastPipelineUpdate(agentId, companyId)`) que publica num canal Transmit após chamar `executeAgent`, notificando os componentes cliente do Vue 3 sobre o progresso.
- No frontend, a leitura do estado do pipeline (GET) deve passar por uma store `@maxvue/max-pinia`; o Transmit serve apenas para invalidar/atualizar essa store em tempo real, não para substituir o fluxo de dados de página.

Exemplo de broadcast com Transmit no backend:

```typescript
// app/services/pipeline_broadcaster.ts
import transmit from '@adonisjs/transmit/services/main'

export async function broadcastPipelineUpdate(agentId: string, companyId: string) {
  // Canal por empresa/agente; o front assina e revalida a store MaxPinia ao receber.
  transmit.broadcast(`companies/${companyId}/agents/${agentId}/pipeline`, {
    updatedAt: new Date().toISOString(),
  })
}
```

### 5. Auditoria de Custos e Uso
- Armazene o uso de tokens de prompt e conclusão, o tempo de execução e o nome do modelo usado após cada execução de agente.
- Use o model `AgentAiCost` (ou equivalente) associado ao evento/agente para registrar os custos em USD de acordo com a tabela de preços do provedor.

---

## Code Examples

### Exemplo de Coordenação de Jobs Multiagente (BullMQ + Lucid)
Abaixo está um exemplo de um orquestrador/job tratando o loop de feedback pós-análise de arte:

```typescript
// app/jobs/art_analyst_job.ts
import type { Job } from 'bullmq'
import { artAnalystQueue } from '#services/queue_service'
import CalendarEvent from '#models/calendar/event'
import { executeAgent, saveAiCost, COSTABLE_TYPES } from '#ai/agent_ai_request'
import { broadcastPipelineUpdate } from '#services/pipeline_broadcaster'
import { createArtAnalystAgent } from '#ai/agents/art_analyst'
import CopywriterJob from '#jobs/copywriter_job'

export interface ArtAnalystJobData {
  eventId: string
  agentId: string
  solarCompanyId: string
}

export default class ArtAnalystJob {
  static readonly queueName = 'art-analyst'

  static async dispatch(event: CalendarEvent, agentId: string, solarCompanyId: string) {
    await artAnalystQueue.add('run', { eventId: event.id, agentId, solarCompanyId })
  }

  static async handle(job: Job<ArtAnalystJobData>) {
    const { eventId, agentId, solarCompanyId } = job.data
    const event = await CalendarEvent.findOrFail(eventId)
    
    // Cria configuração para o Agente Analista de Arte
    const agentConfig = createArtAnalystAgent(event)

    const result = await executeAgent({
      ...agentConfig,
      prompt: `Analise as artes geradas para o evento ID: ${eventId}. Verifique se as diretrizes visuais foram atendidas.`,
      isDone: async () => true,
    })

    // Persiste uso de API e custo
    await saveAiCost(COSTABLE_TYPES.Event, eventId, result)

    // Atualiza o estado local do evento após execuções das ferramentas do agente
    await event.refresh()

    if (event.status === 'art_rejected') {
      // Loop de feedback de volta para o Copywriter (ou Replanejador se for repetido)
      // O CopywriterJob lerá o campo rejectionObservations para reescrever os briefings visuais
      await CopywriterJob.dispatch(event, agentId, solarCompanyId)
    } else if (event.status === 'approved') {
      // Finaliza ou envia para a fila de publicação
    }

    // Transmite o status para o frontend Vue em tempo real (AdonisJS Transmit / SSE)
    await broadcastPipelineUpdate(agentId, solarCompanyId)
  }
}
```

### Passando Contexto de Estado Entre Agentes
Quando o `CopywriterJob` é despachado novamente, o agente deve verificar os campos do modelo pai para alternar entre geração completa ou revisão parcial:

```typescript
// app/ai/agents/copywriter.ts
import type CalendarEvent from '#models/calendar/event'

export function createCopywriterAgent(event: CalendarEvent) {
  const isRevision = event.status === 'art_rejected' && event.rejectionObservations
  
  return {
    agentName: 'AgentSolarCopywriter',
    typeData: 'structured-data',
    initialModel: 'gemini-2.5-flash',
    systemPrompt: `Você é o Agente Redator de conteúdo de marketing da empresa fotovoltaica.
    
    ${isRevision ? `
    [ATENÇÃO: MODO REVISÃO]
    A arte ou texto deste post foi REJEITADA. Você deve corrigir o briefing visual com base no feedback:
    "${event.rejectionObservations}"
    NÃO modifique detalhes de slides aprovados ou que não tenham relação com o feedback. Foque apenas em resolver os problemas de rejeição.
    ` : 'Gere uma nova copy e briefing visual para todos os slides.'}
    `,
    tools: {
      // Definição das ferramentas para buscar contexto e salvar detalhes do script...
    }
  }
}
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** mantenha estados de execução dos agentes em variáveis globais ou memória temporária por longos períodos; persista sempre no banco de dados.
- **NÃO** encadeie chamadas de execução de forma síncrona usando `await executeAgent` dentro do loop de execução de outro agente. Sempre separe as etapas através de jobs de filas.
- **NÃO** dispare replanejamentos automáticos sem verificar limites de tentativas/rejeições. Falhas consecutivas repetidas devem parar o fluxo e notificar operadores humanos em vez de criar loops infinitos entre os agentes.
