---
name: adonisjs-ai-agents-observability-monitoring-best-practices
description: Use when implementing, reviewing, or debugging observability, logging, and monitoring systems for AI agents, Vercel AI SDK execution traces, tool-calling logs, and real-time agent execution tracking in AdonisJS v6. Triggers on agent execution telemetry, onStepFinish event tracing, Sentry AI error tracking, and log persistence.
---

## Objetivo
Estabelecer padrões robustos e melhores práticas para rastreamento (tracing), logging estruturado, monitoramento e depuração de agentes de IA baseados no Vercel AI SDK no ambiente backend do AdonisJS v6. Isso inclui telemetria de passos, logging de chamadas de ferramentas, persistência de custos e históricos no banco de dados, monitoramento de erros via Sentry e transmissão de progresso em tempo real usando Server-Sent Events (SSE).

## Instruções

## 1. Rastreamento de Steps (Passos) com `onStepFinish`
Ao chamar `generateText` ou `streamText` do Vercel AI SDK, utilize o callback `onStepFinish` para obter detalhes estruturados de cada passo executado.
- **Extrair Metadados de Tokens e Cache:** Para o Gemini, calcule os tokens servidos a partir do cache usando `providerMetadata.google.cachedContentTokenCount` e subtraia do total de `usage.inputTokens` para identificar os custos de entrada brutos.
- **Logs Estruturados de Telemetria:** Grave logs estruturados de cada passo no `logger` oficial do AdonisJS para simplificar o agrupamento e visualização de logs.
- **Rastreamento de Ferramentas:** Registre qual ferramenta foi chamada, seus argumentos e o retorno gerado.

Exemplo de implementação no loop de execução do agente:
```typescript
import logger from '@adonisjs/core/services/logger'
import { generateText } from 'ai'
import { google } from '@ai-sdk/google'

const { text } = await generateText({
  model: google('gemini-2.5-flash'),
  system: systemPrompt,
  prompt: prompt,
  tools: tools,
  onStepFinish: ({ text, toolCalls, toolResults, usage, providerMetadata, finishReason }) => {
    // 1. Calcular métricas de cache (providerMetadata é argumento separado do callback)
    const cacheRead = (providerMetadata?.google as any)?.cachedContentTokenCount ?? 0
    const rawInput = Math.max((usage.inputTokens ?? 0) - cacheRead, 0)
    
    // 2. Log estruturado da execução do passo
    logger.info({
      event: 'agent_step_finish',
      agent: agentName,
      usage: {
        total: usage.totalTokens,
        inputRaw: rawInput,
        inputCached: cacheRead,
        output: usage.outputTokens,
      },
      tools: toolCalls?.map((tc) => ({
        id: tc.toolCallId,
        name: tc.toolName,
        input: tc.input,
      })),
      finishReason,
    }, `AI Agent step finished`)

    // 3. Log detalhado dos retornos das ferramentas
    if (toolResults && toolResults.length > 0) {
      toolResults.forEach((tr) => {
        logger.debug({
          event: 'agent_tool_result',
          agent: agentName,
          tool: tr.toolName,
          toolCallId: tr.toolCallId,
          input: tr.input,
          output: tr.output,
        }, `Tool execution completed`)
      })
    }
  },
})
```

## 2. Telemetria e Persistência no Banco de Dados
Os logs de execução de IA devem ser salvos no banco de dados para fins de faturamento, auditoria de custos e histórico de auditoria.
- **Métricas de Custo:** Continue utilizando o modelo `AgentAiCost` para persistir a quantidade de tokens, preços estimados e durações via função `saveAiCost`.
- **Histórico Completo de Execução:** Para agentes complexos de longa duração, salve o histórico detalhado de passos (por exemplo, em uma tabela `AgentExecutionLog` ou tabela de metadados correspondente) associado ao modelo pai.

```typescript
import AgentAiCost from '#models/agent_ai_cost'

export async function saveAiCost(
  costableType: string,
  costableId: string,
  result: AgentExecuteResult
) {
  await AgentAiCost.create({
    costableType,
    costableId,
    agent: result.agent,
    typeData: result.typeData,
    model: result.model,
    totalTokens: result.totalTokens,
    tokensInput: result.tokensInput,
    tokensCached: result.tokensCached,
    tokensInputTotal: result.tokensInputTotal,
    tokensOutput: result.tokensOutput,
    toolsUses: result.toolsUses,
    toolsAmount: result.toolsAmount,
    totalPrice: result.totalPriceUsdRaw,
    totalDuration: result.totalDurationS,
  })
}
```

## 3. Integração com Sentry para Monitoramento de Erros de IA
Falhas na execução dos agentes (limites de taxa/quota da API, timeouts, erros de parser de Zod schema ou exceções internas em ferramentas) devem ser enviadas ao Sentry para evitar falhas silenciosas.
- **Enriquecer o Contexto:** Adicione metadados sobre a configuração do agente ativo, contexto do prompt e tokens consumidos até o momento no escopo do Sentry.
- **Não Silencie Erros:** Envie o erro para o Sentry, mas mantenha a propagação do erro (throw) para que o BullMQ ou o controller trate a falha de forma visível e execute fluxos de recuperação ou falha de job apropriados.

```typescript
import * as Sentry from '@sentry/node'

try {
  // executa o agente
} catch (error) {
  Sentry.withScope((scope) => {
    scope.setTag('system', 'ai-agent')
    scope.setTag('agent_name', agentName)
    scope.setTag('model', currentModel)
    scope.setExtra('prompt_context', prompt)
    scope.setExtra('total_steps_executed', stepsCount)
    
    // Se o erro originar-se de uma resposta HTTP de API externa, logue o status
    if (error.status) {
      scope.setExtra('api_status_code', error.status)
    }

    Sentry.captureException(error)
  })
  
  // Propaga o erro para o fallback do modelo ou falha do worker
  throw error
}
```

## 4. Transmissão de Progresso em Tempo Real com Transmit (SSE)
Para agentes rodando em tarefas em segundo plano ou em múltiplos passos, envie atualizações de status e progresso em tempo real para a interface de usuário.
- **Estruturação de Canais do Transmit:** Padronize caminhos de canal como `users/{userId}/agents/progress` ou `users/{userId}/calendar`.
- **Payloads Padronizados:** Envie eventos contendo:
  - `agent_id` or `event_id`
  - `status` (ex. `running`, `completed`, `failed`)
  - `step_index` and `total_steps`
  - `current_action` (ex. `Chamando GetBrandPositioning...`, `Escrevendo legenda...`)

```typescript
import transmit from '@adonisjs/transmit/services/main'

export function broadcastAgentProgress(userId: string, payload: {
  eventId: string
  status: 'running' | 'completed' | 'failed'
  step?: number
  action?: string
}) {
  transmit.broadcast(`users/${userId}/calendar`, {
    type: 'agent_progress_update',
    event_id: payload.eventId,
    status: payload.status,
    step: payload.step,
    action: payload.action,
  })
}
```

## Restrições
- Não utilize console.log simples para rastrear a execução de agentes; sempre utilize o AdonisJS `logger` aplicando níveis corretos (`info` para passos, `debug` para parâmetros/retornos de ferramentas e `error` para falhas).
- Não envie credenciais, chaves privadas ou tokens confidenciais fornecidos pelo usuário aos campos extras do Sentry; sanitize as informações antes de enviar.
- Não deixe que falhas no broadcast do Transmit (SSE) travem a execução do agente. Envolva as chamadas de broadcast em try/catch para garantir resiliência.
- Não ignore o registro de custos em caso de falha no meio da execução; registre custos parciais referentes aos tokens consumidos até o momento da falha.
