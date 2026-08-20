---
name: adonisjs-ai-agent-cost-analytics-and-budget-control-best-practices
description: Use when implementing, reviewing, or debugging backend logic for AI agent requests in AdonisJS v6 — executeAgent execution with model fallback chains, capturing token/cost metrics and persisting them via the HasAiCost mixin (addAiCost) then reading them back through the AgentAiCost model, analyzing/aggregating AgentAiCost records (sums grouped by dates, agents, or clients), converting USD→BRL via ExchangeRateService, applying tenant budget limits to restrict LLM calls, and broadcasting real-time updates via AdonisJS Transmit (SSE).
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer diretrizes, estruturas e padrões de implementação para a execução resiliente de agentes de IA, o rastreamento/agregação dos custos e a aplicação de controle de orçamento (budget) em um backend AdonisJS v6. Cobre cadeias de fallback de modelos, registro de custos no momento da requisição (`saveAiCost` → model `AgentAiCost`), análises financeiras agregadas, conversão de câmbio (USD para BRL via `ExchangeRateService` em `#services/bank/exchange_rate_service`) e feedback em tempo real ao usuário. Isso garante continuidade do serviço sob rate-limit, supervisão financeira confiável e evita loops de execução descontrolados.

> **Fluxo de tracking de custo (visão única):** cada execução de `executeAgent` calcula tokens/custo no momento da requisição e persiste um registro de custo. A persistência **nativa** do projeto é feita pelo mixin `HasAiCost` (método `addAiCost(tokens, costUsd)`) — **não existe** uma função `saveAiCost` no código; se você adotar esse nome, trate-o como um helper a ser criado que apenas encapsula `addAiCost`. **Atenção à divergência de esquema:** o insert de fallback do mixin grava na tabela `agent_ai_costs` com a coluna `total_price_usd_micro` (microdólares), enquanto o model `AgentAiCost` mapeia a tabela `agents_ai_cost` com `totalPrice`. Não trate escrita e leitura como um único caminho contínuo sem reconciliar essa diferença. As análises agregadas, relatórios e a checagem de budget (seções de análise e `AiBudgetService`) consultam esses registros de leitura via `AgentAiCost`.

## Instruções

### 1. Referência do Model do Banco de Dados
Sempre referencie o model `AgentAiCost` (`#models/openai/agent_ai_cost`) ao escrever consultas de custos. Ele mapeia para a tabela `agents_ai_cost` e armazena o consumo de tokens das LLMs e o preço final em USD. Os campos chave incluem:
- `costableType`: identificador da entidade relacionada (string curta, ex: `ProjectSolar`, `ProposalEnergy`). Use um enum/string simples do domínio Adonis — **não** FQCN PHP estilo `App\Models\...`.
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
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
  ]
  ```

### 3. Métricas de Token/Custo no Momento da Requisição
Ao retornar de `executeAgent`, calcule o custo financeiro com base no status de cache dos tokens de entrada (tokens em cache são muito mais baratos que os não cacheados).
- Extraia a quantidade de tokens lidos em cache de `providerMetadata.google.cachedContentTokenCount`.
- Diferencie rigorosamente custos com e sem cache. Tabela oficial em USD por 1M de tokens:
  - `gemini-2.5-flash-lite`: `notCached: 0.25`, `cached: 0.025`, `outputReasoning: 1.5`
  - `gemini-2.5-flash`: `notCached: 0.3`, `cached: 0.03`, `outputReasoning: 2.5`
  - `gemini-2.5-pro`: `notCached: 1.25`, `cached: 0.125`, `outputReasoning: 10`

### 4. Persistência dos Custos (mixin HasAiCost / addAiCost)
Após cada execução, grave as métricas calculadas usando o mixin nativo `HasAiCost` (método `addAiCost(tokens, costUsd)`). Se preferir centralizar a lógica em um helper `saveAiCost`, **crie-o você mesmo** como um wrapper de `addAiCost` — não há função `saveAiCost` nativa no projeto. Lembre da divergência de tabela/coluna descrita na visão única (`agent_ai_costs`/`total_price_usd_micro` na escrita vs. `agents_ai_cost`/`totalPrice` na leitura via `AgentAiCost`).
- Preencha todos os campos necessários: `costableType`, `costableId`, `agent`, `typeData`, `model`, `totalTokens`, `tokensInput`, `tokensCached`, `tokensInputTotal`, `tokensOutput`, `toolsUses`, `toolsAmount`, `totalPrice`, `totalDuration`.
- Mapeie as associações polimórficas de `costableType` usando identificadores de domínio simples (strings do Adonis, nunca FQCN PHP):
  ```typescript
  export const COSTABLE_TYPES = {
    ProjectSolar: 'ProjectSolar',
    ProposalEnergy: 'ProposalEnergy',
    SolarSimulation: 'SolarSimulation',
  } as const
  ```
- Capture exceções em `addAiCost`/`AgentAiCost`: uma falha de banco ao registrar o custo **não** deve quebrar o fluxo principal do agente.

### 5. Broadcast em Tempo Real (AdonisJS Transmit / SSE)
Notifique os usuários vinculados à empresa de forma assíncrona e segura usando exclusivamente AdonisJS Transmit (SSE). Não use Pusher/Soketi/Reverb nem Laravel Echo.
- Use `transmit.broadcast` em canais no formato `users/${user.id}/ai-budget` (usado, por exemplo, nos alertas de orçamento da seção `AiBudgetService`).
- Sempre encapsule o broadcast em `try/catch`: a falha do canal SSE nunca deve interromper o fluxo de execução principal.

### 6. Agregação Eficiente de Custos
Ao construir relatórios financeiros ou painéis de uso:
- Agrupe registros por data, agente ou tenant (usando consultas JOIN com tabelas relacionadas).
- Evite consultas do tipo N+1. Sempre agregue os custos utilizando funções SQL de agregação (`sum`, `count`) diretamente no banco de dados, em vez de carregar os registros e percorrê-los na memória do TypeScript.
- **Exemplo de Consulta Lucid (Custos Agrupados):**
  ```typescript
  import db from '@adonisjs/lucid/services/db'
  import { ExchangeRateService } from '#services/bank/exchange_rate_service'
  import AgentAiCost from '#models/openai/agent_ai_cost'

  async function getMonthlyCostReport(clientId: string, startDate: string, endDate: string) {
    const rawCosts = await db
      .from('agents_ai_cost')
      .join('projects_solar', 'agents_ai_cost.costable_id', '=', 'projects_solar.id')
      .where('agents_ai_cost.costable_type', 'ProjectSolar')
      .where('projects_solar.solar_company_id', clientId)
      .whereBetween('agents_ai_cost.created_at', [startDate, endDate])
      .select('agents_ai_cost.agent')
      .sum('agents_ai_cost.total_price as totalUsd')
      .groupBy('agents_ai_cost.agent')

    const usdToBrlRate = await new ExchangeRateService().getRate('USD', 'BRL')

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
        .join('projects_solar', 'agents_ai_cost.costable_id', '=', 'projects_solar.id')
        .where('agents_ai_cost.costable_type', 'ProjectSolar')
        .where('projects_solar.solar_company_id', solarCompanyId)
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
          transmit.broadcast(`users/${user.id}/ai-budget`, {
            type,
            spent,
            limit,
          })
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err)
        logger.error(`Falha ao transmitir alerta de orçamento para o tenant ${solarCompanyId}: ${message}`)
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
- **Exemplo de verificação no fluxo de execução do agente (`app/ai/agent_ai_request.ts`):**
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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca contorne a checagem de orçamento:** A validação do orçamento deve ser executada antes de disparar qualquer chamada de API de IA que seja tarifável.
- **Sem consultas externas de câmbio em loop:** Use sempre `ExchangeRateService` (`#services/bank/exchange_rate_service`, método `getRate('USD','BRL')`) para obter a cotação do dólar em reais. Nunca faça requisições HTTP ad-hoc de cotação de moedas em loops.
- **Eficiência de Banco de Dados:** Sempre execute operações de soma (SUM) diretamente no motor de banco de dados. Nunca traga todos os registros de `AgentAiCost` para somá-los na memória do TypeScript.
- **Resiliência obrigatória:** Nunca pule a `FALLBACK_CHAIN` em produção; degrade os modelos progressivamente em caso de falha.
- **Segurança de credenciais:** Nunca escreva chaves ou credenciais estaticamente; use sempre `process.env`.
- **Custos com/sem cache:** Diferencie rigorosamente tokens cacheados e não cacheados ao calcular e inserir métricas via `addAiCost` (mixin `HasAiCost`).
- **Tracking não pode quebrar o fluxo:** Capture exceções em `addAiCost`/`AgentAiCost` e nos broadcasts; falhas de persistência ou websocket não devem interromper a execução do agente.
