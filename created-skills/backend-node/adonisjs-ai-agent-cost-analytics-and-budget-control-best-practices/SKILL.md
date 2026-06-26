---
name: adonisjs-ai-agent-cost-analytics-and-budget-control-best-practices
description: Use when implementing, reviewing, or debugging backend logic for AI agent requests in AdonisJS v6 — executeAgent execution with model fallback chains, capturing token/cost metrics and persisting them via saveAiCost into the AgentAiCost model, analyzing/aggregating AgentAiCost records (sums grouped by dates, agents, or clients), converting values using DolarService, applying tenant budget limits to restrict LLM calls, and broadcasting real-time updates via Pusher/Soketi or Transmit.
---

## Objetivo
Fornecer diretrizes, estruturas e padrões de implementação para a execução resiliente de agentes de IA, o rastreamento/agregação dos custos e a aplicação de controle de orçamento (budget) em um backend AdonisJS v6. Cobre cadeias de fallback de modelos, registro de custos no momento da requisição (`saveAiCost` → model `AgentAiCost`), análises financeiras agregadas, conversão de câmbio (USD para BRL via `DolarService`) e feedback em tempo real ao usuário. Isso garante continuidade do serviço sob rate-limit, supervisão financeira confiável e evita loops de execução descontrolados.

> **Fluxo de tracking de custo (visão única):** cada execução de `executeAgent` calcula tokens/custo no momento da requisição e chama `saveAiCost`, que persiste um registro na tabela `agents_ai_cost` através do model `AgentAiCost`. As análises agregadas, relatórios e a checagem de budget (seções de análise e `AiBudgetService`) consultam exatamente esses mesmos registros. Ou seja: `saveAiCost` é a fonte de escrita; `AgentAiCost` é a fonte de leitura.

## Instruções

### 1. Referência do Model do Banco de Dados
Sempre referencie o model `AgentAiCost` ([agent_ai_cost.ts](file:///home/johnattas/GitHub/Skills/projects/SocialMediaApp/app/models/agent_ai_cost.ts)) ao escrever consultas de custos. Ele mapeia para a tabela `agents_ai_cost` e armazena o consumo de tokens das LLMs e o preço final em USD. Os campos chave incluem:
- `costableType`: FQCN da entidade relacionada (ex: `App\\Models\\Calendar\\Event`).
- `costableId`: A chave primária da entidade relacionada.
- `agent`: O nome do agente de IA que executou.
- `totalPrice`: O custo calculado em USD.
- `totalTokens`, `tokensInput`, `tokensCached`, `tokensOutput`.

### 2. Execução Resiliente do Agente (executeAgent + Cadeia de Fallback)
A função `executeAgent` é o executor nativo das chamadas de IA. Ela deve degradar modelos progressivamente em caso de rate-limit ou indisponibilidade da API.
- Use a ordem definida em `FALLBACK_CHAIN`, percorrendo os modelos com tentativas e atraso (delay) no bloco de captura de erros. **Nunca** pule a cadeia de fallback em produção.
- Carregue chaves/credenciais sempre via variáveis de ambiente (`process.env`), nunca estáticas no código.
  ```typescript
  const FALLBACK_CHAIN = [
    'gemini-3.1-flash-lite',
    'gemini-2.5-flash',
    'gemini-3.5-flash',
    'gemini-2.5-pro',
  ]
  ```

### 3. Métricas de Token/Custo no Momento da Requisição
Ao retornar de `executeAgent`, calcule o custo financeiro com base no status de cache dos tokens de entrada (tokens em cache são muito mais baratos que os não cacheados).
- Extraia a quantidade de tokens lidos em cache de `providerMetadata.google.cachedContentTokenCount`.
- Diferencie rigorosamente custos com e sem cache. Tabela oficial em USD por 1M de tokens:
  - `gemini-3.1-flash-lite`: `notCached: 0.25`, `cached: 0.025`, `outputReasoning: 1.5`
  - `gemini-2.5-flash`: `notCached: 0.3`, `cached: 0.03`, `outputReasoning: 2.5`
  - `gemini-3.5-flash`: `notCached: 1.5`, `cached: 0.15`, `outputReasoning: 9.0`
  - `gemini-2.5-pro`: `notCached: 1.25`, `cached: 0.125`, `outputReasoning: 10`
  - `gemini-3.1-pro-preview`: `notCached: 2.0`, `cached: 0.2`, `outputReasoning: 12`
  - `gemini-2.5-flash-lite`: `notCached: 0.1`, `cached: 0.01`, `outputReasoning: 0.4`

### 4. Persistência dos Custos (saveAiCost → AgentAiCost)
Após cada execução, grave as métricas calculadas chamando `saveAiCost`, que insere o registro na tabela `agents_ai_cost` via model `AgentAiCost` (ver seção 1). Esses registros são exatamente os consumidos pelas análises e pela checagem de budget.
- Preencha todos os campos necessários: `costableType`, `costableId`, `agent`, `typeData`, `model`, `totalTokens`, `tokensInput`, `tokensCached`, `tokensInputTotal`, `tokensOutput`, `toolsUses`, `toolsAmount`, `totalPrice`, `totalDuration`.
- Mapeie as associações polimórficas de `costableType` conforme o backend Laravel:
  ```typescript
  export const COSTABLE_TYPES = {
    Event: 'App\\Models\\Calendar\\Event',
    SocialMediaTheme: 'App\\Models\\Calendar\\SocialMediaTheme',
    SocialMediaAgent: 'App\\Models\\Calendar\\SocialMediaAgent',
  } as const
  ```
- Capture exceções em `saveAiCost`/`AgentAiCost`: uma falha de banco ao registrar o custo **não** deve quebrar o fluxo principal do agente.

### 5. Broadcast em Tempo Real (Pusher/Soketi e Transmit)
Notifique os usuários vinculados à empresa do evento de forma assíncrona e segura.
- Via Pusher/Soketi: envie em canais privados no formato `private-system.${userId}` (ex.: `broadcastCalendarUpdate`).
- Via Transmit: canais no formato `users/${user.id}/calendar` (usado, por exemplo, nos alertas de orçamento da seção `AiBudgetService`).
- Sempre encapsule o broadcast em `try/catch`: a falha de um websocket nunca deve interromper o fluxo de execução principal.

### 6. Agregação Eficiente de Custos
Ao construir relatórios financeiros ou painéis de uso:
- Agrupe registros por data, agente ou tenant (usando consultas JOIN com tabelas relacionadas).
- Evite consultas do tipo N+1. Sempre agregue os custos utilizando funções SQL de agregação (`sum`, `count`) diretamente no banco de dados, em vez de carregar os registros e percorrê-los na memória do TypeScript.
- **Exemplo de Consulta Lucid (Custos Agrupados):**
  ```typescript
  import db from '@adonisjs/lucid/services/db'
  import { dolarReal } from '#services/dolar_service'
  import AgentAiCost from '#models/agent_ai_cost'

  async function getMonthlyCostReport(clientId: string, startDate: string, endDate: string) {
    const rawCosts = await db
      .from('agents_ai_cost')
      .join('calendar_events', 'agents_ai_cost.costable_id', '=', 'calendar_events.id')
      .join('calendar_social_media_agent', 'calendar_events.agent_id', '=', 'calendar_social_media_agent.id')
      .where('agents_ai_cost.costable_type', 'App\\Models\\Calendar\\Event')
      .where('calendar_social_media_agent.id_solar_company', clientId)
      .whereBetween('agents_ai_cost.created_at', [startDate, endDate])
      .select('agents_ai_cost.agent')
      .sum('agents_ai_cost.total_price as totalUsd')
      .groupBy('agents_ai_cost.agent')

    const usdToBrlRate = await dolarReal()

    return rawCosts.map((row) => {
      const usd = parseFloat(row.totalUsd || 0)
      return {
        agent: row.agent,
        totalUsd: Math.round(usd * 1000000) / 1000000,
        totalBrl: Math.round(usd * usdToBrlRate * 100) / 100,
      }
    })
  }
  ```

### 7. Implementando o Serviço de Orçamento de IA (AiBudgetService)
Crie um serviço dedicado `AiBudgetService` para computar o consumo mensal e aplicar as cotas dos tenants antes de acionar tarefas dispendiosas de LLM.
- **Implementação do Serviço:**
  ```typescript
  import db from '@adonisjs/lucid/services/db'
  import logger from '@adonisjs/core/services/logger'
  import transmit from '@adonisjs/transmit/services/main'
  import User from '#models/user'

  export class AiBudgetService {
    /**
     * Obtém o gasto mensal em USD de uma determinada SolarCompany (tenant)
     */
    static async getMonthlySpent(solarCompanyId: string): Promise<number> {
      const now = new Date()
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)

      const result = await db
        .from('agents_ai_cost')
        .join('calendar_events', 'agents_ai_cost.costable_id', '=', 'calendar_events.id')
        .join('calendar_social_media_agent', 'calendar_events.agent_id', '=', 'calendar_social_media_agent.id')
        .where('calendar_social_media_agent.id_solar_company', solarCompanyId)
        .whereBetween('agents_ai_cost.created_at', [firstDay, lastDay])
        .sum('agents_ai_cost.total_price as total')
        .first()

      return parseFloat(result?.total ?? '0')
    }

    /**
     * Valida o limite de orçamento e dispara alertas em patamares de 80%, 90% e 100% de uso.
     */
    static async checkAndNotifyBudget(solarCompanyId: string, limitUsd: number): Promise<boolean> {
      const currentSpent = await this.getMonthlySpent(solarCompanyId)

      if (currentSpent >= limitUsd) {
        logger.warn(`Tenant ${solarCompanyId} excedeu o limite mensal de orçamento de IA de $${limitUsd}. Gasto atual: $${currentSpent}`)
        await this.broadcastWarning(solarCompanyId, 'budget_exceeded', currentSpent, limitUsd)
        return false
      }

      const ratio = currentSpent / limitUsd
      if (ratio >= 0.9) {
        logger.info(`Tenant ${solarCompanyId} atingiu 90% do orçamento de IA. Gasto: $${currentSpent}/$${limitUsd}`)
        await this.broadcastWarning(solarCompanyId, 'budget_warning_90', currentSpent, limitUsd)
      } else if (ratio >= 0.8) {
        logger.info(`Tenant ${solarCompanyId} atingiu 80% do orçamento de IA. Gasto: $${currentSpent}/$${limitUsd}`)
        await this.broadcastWarning(solarCompanyId, 'budget_warning_80', currentSpent, limitUsd)
      }

      return true
    }

    private static async broadcastWarning(
      solarCompanyId: string,
      type: string,
      spent: number,
      limit: number
    ) {
      try {
        const users = await User.query().where('solar_company_id', solarCompanyId).select(['id'])
        for (const user of users) {
          transmit.broadcast(`users/${user.id}/calendar`, {
            type,
            spent,
            limit,
          })
        }
      } catch (err) {
        logger.error(`Falha ao transmitir alerta de orçamento para o tenant ${solarCompanyId}: ${err.message}`)
      }
    }
  }
  ```

### 8. Exceção Personalizada para Limite Excedido
Declare uma exceção personalizada e reutilizável para formatar uma resposta HTTP padrão quando a cota limite for atingida.
- **Classe da Exceção (`app/exceptions/ai_budget_exceeded_exception.ts`):**
  ```typescript
  import { Exception } from '@adonisjs/core/exceptions'
  import type { HttpContext } from '@adonisjs/core/http'

  export default class AiBudgetExceededException extends Exception {
    static status = 402 // Payment Required
    static code = 'E_AI_BUDGET_EXCEEDED'

    constructor(message = 'Limite mensal de orçamento de IA excedido para este tenant.') {
      super(message)
    }

    async handle(error: this, ctx: HttpContext) {
      ctx.response.status(error.status).send({
        errors: [
          {
            code: error.code,
            message: error.message,
            status: error.status,
          },
        ],
      })
    }
  }
  ```

### 9. Integração com os Fluxos de Execução
Garanta que os gerenciadores de execução validem o orçamento antes de processar qualquer requisição:
- **Em requisições HTTP / Controllers:** Verifique o orçamento utilizando o serviço e dispare `AiBudgetExceededException` se a verificação falhar.
- **Em Jobs de Fila (ex: workers BullMQ):** Valide o orçamento antes de invocar o loop de execução. Se excedido, encerre o job de forma amigável e registre o motivo no log.
- **Exemplo de verificação no fluxo [agent_ai_request.ts](file:///home/johnattas/GitHub/Skills/projects/SocialMediaApp/app/ai/agent_ai_request.ts):**
  ```typescript
  import AiBudgetExceededException from '#exceptions/ai_budget_exceeded_exception'
  import { AiBudgetService } from '#services/ai_budget_service'

  export async function executeAgentWithBudgetControl(
    solarCompanyId: string,
    limitUsd: number,
    opts: AgentExecuteOptions
  ) {
    const isBudgetOk = await AiBudgetService.checkAndNotifyBudget(solarCompanyId, limitUsd)
    if (!isBudgetOk) {
      throw new AiBudgetExceededException()
    }

    // Chama o executor nativo executeAgent
    return await executeAgent(opts)
  }
  ```

## Restrições
- **Nunca contorne a checagem de orçamento:** A validação do orçamento deve ser executada antes de disparar qualquer chamada de API de IA que seja tarifável.
- **Sem consultas externas de câmbio em loop:** Use sempre `#services/dolar_service` (`dolarReal()`) para obter a cotação do dólar em reais. Nunca faça requisições HTTP ad-hoc de cotação de moedas em loops.
- **Eficiência de Banco de Dados:** Sempre execute operações de soma (SUM) diretamente no motor de banco de dados. Nunca traga todos os registros de `AgentAiCost` para somá-los na memória do TypeScript.
- **Resiliência obrigatória:** Nunca pule a `FALLBACK_CHAIN` em produção; degrade os modelos progressivamente em caso de falha.
- **Segurança de credenciais:** Nunca escreva chaves ou credenciais estaticamente; use sempre `process.env`.
- **Custos com/sem cache:** Diferencie rigorosamente tokens cacheados e não cacheados ao calcular e inserir métricas via `saveAiCost`.
- **Tracking não pode quebrar o fluxo:** Capture exceções em `saveAiCost`/`AgentAiCost` e nos broadcasts; falhas de persistência ou websocket não devem interromper a execução do agente.
