---
name: adonisjs-ai-financial-insights-gemini-best-practices
description: Use when implementing, reviewing, or debugging AI-driven financial insights, automated budget analysis, financial health scoring, or generative financial reports in AdonisJS. Triggers on files handling transaction history summaries, savings goal projections, and Gemini-based prompts for financial advice.
---

## Objetivo
Padronizar a implementação de serviços de consultoria financeira orientados por IA, análise de gastos e pontuação de saúde financeira em aplicações AdonisJS usando o Google Gemini (via Vercel AI SDK), garantindo baixo consumo de tokens, privacidade de dados e confiabilidade determinística.

## Instruções

## 1. Otimização de Tokens via Agregação de Dados
* **Sem Envio de Transações Cruas:** Nunca envie listas de transações individuais diretamente para o LLM. Isso gera altos custos de tokens e dispersão do prompt.
* **Agregação no Banco de Dados:** Use o Lucid ORM para agregar os históricos de transações (receitas e despesas) por categoria, subcategoria e intervalos de datas diretamente no SQL antes de enviá-los ao prompt.
* **Formato de Contexto Estruturado:** Formate os dados financeiros agregados em uma estrutura JSON limpa e minimalista contendo:
  - Despesas e receitas agregadas por categoria (valores em centavos de BRL).
  - Saldo atual e limites de cartão de crédito.
  - Detalhes de metas de economia ativas (`SavingGoal` - valor alvo, valor economizado atual, prazo).

Exemplo de agregação no banco de dados:
```typescript
import Database from '@adonisjs/lucid/services/db'

// Agregar despesas por categoria nos últimos 30 dias
const monthlyExpenses = await Database.from('expenses')
  .where('user_profile_id', profileId)
  .where('date', '>=', DateTime.now().minus({ days: 30 }).toSQLDate())
  .groupBy('category_id')
  .select('category_id')
  .sum('amount as total')
```

## 2. Definição de Saída Estruturada (Schema Zod)
* Use a função `generateObject` do Vercel AI SDK para forçar respostas JSON estruturadas.
* Defina um schema Zod estrito onde cada campo contenha uma chamada `.describe()` explícita em inglês.
* Represente todos os campos monetários como **inteiros (centavos)** para evitar problemas de ponto flutuante.

```typescript
import { z } from 'zod'

export const financialInsightSchema = z.object({
  healthScore: z.number().int().min(0).max(100).describe('A score from 0 (poor) to 100 (excellent) representing the financial health based on income vs. expenses.'),
  insights: z.array(z.object({
    title: z.string().describe('Short title summarizing the spending anomaly or behavior observed.'),
    description: z.string().describe('Detailed explanation of the insight, with actionable advice.'),
    category: z.string().describe('The main financial category related to this insight (e.g., Alimentação, Assinaturas).'),
    severity: z.enum(['low', 'medium', 'high']).describe('The priority level of the insight.'),
    potentialSavingsCents: z.number().int().describe('Estimated potential savings in BRL cents if the user follows the advice.'),
  })).describe('List of customized spending insights for the user.'),
  savingsGoalProgress: z.array(z.object({
    goalId: z.string().describe('The ULID of the SavingGoal.'),
    status: z.enum(['on_track', 'at_risk', 'behind']).describe('The likelihood of achieving the goal on time based on current savings rate.'),
    recommendation: z.string().describe('Practical recommendation to accelerate progress towards this specific savings goal.'),
  })).describe('Analysis of active saving goals and progress.')
})
```

## 3. Prompt de Persona de Assessor Financeiro
* Configure explicitamente o prompt do sistema do LLM para assumir a persona de um assessor de finanças pessoais especialista no mercado brasileiro.
* Instrua o modelo a respeitar convenções de moeda brasileira (BRL, centavos), inflação, taxas de juros típicas (CDI, Selic) e comportamento do consumidor.
* Não permita que o modelo faça recomendações de investimentos que exijam certificações específicas (como recomendar ações específicas); foque no controle de orçamento, métricas de economia e otimização de hábitos.

```typescript
const systemPrompt = `You are "Dinheirou AI", an expert personal finance advisor for Brazilian users.
Analyze the user's aggregated financial summary (values in cents) and provide constructive, friendly, and actionable insights in Brazilian Portuguese.
Focus on budget optimization, saving habits, and general financial health. Do not suggest specific tickers, stocks, or investments requiring certification.`
```

## 4. Resiliência e Rastreamento de Custos
* Envolva as chamadas de geração de IA na cadeia de fallback padrão definida em `adonisjs-ai-agents-request-resilience-costs`.
* Registre o uso de tokens e o custo total de execução em `AgentAiCost` usando o mapeamento `COSTABLE_TYPES` associando ao perfil do usuário ou recurso de planejamento.

## Restrições
* Nunca exponha informações pessoais sensíveis (PII) (como números de conta, nomes legais ou descrições cruas de transações) para a API do LLM.
* Os valores monetários devem sempre ser calculados, transmitidos e armazenados em centavos (inteiros) para manter a precisão matemática absoluta.
* O LLM não deve realizar cálculos matemáticos brutos de somas de orçamentos; as consultas de banco de dados devem computar essas somas e fornecê-las ao LLM.
* Todos os prompts, mensagens do sistema e schemas devem forçar saídas traduzidas e localizadas em Português do Brasil para o usuário final, mesmo que os campos description do schema Zod estejam escritos em Inglês.
