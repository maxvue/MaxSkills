---
name: adonisjs-ai-financial-insights-gemini-best-practices
description: Use when implementing, reviewing, or debugging AI-driven financial insights, automated cost analysis, project health scoring, or generative reports for solar/photovoltaic projects in AdonisJS. Triggers on files handling project cost summaries, payment/installment projections, and Gemini-based prompts for financial and project advisory.
---

## Objetivo
Padronizar a implementação de serviços de insights financeiros orientados por IA, análise de custos e pontuação de saúde financeira de projetos fotovoltaicos (EngeApp) em aplicações AdonisJS usando o Google Gemini (via Vercel AI SDK), garantindo baixo consumo de tokens, privacidade de dados e confiabilidade determinística.

## Instruções

## 1. Otimização de Tokens via Agregação de Dados
* **Sem Envio de Lançamentos Crus:** Nunca envie listas de lançamentos financeiros ou itens de orçamento individuais diretamente para o LLM. Isso gera altos custos de tokens e dispersão do prompt.
* **Agregação no Banco de Dados:** Use o Lucid ORM para agregar os históricos financeiros do projeto (custos de equipamentos, mão de obra, pagamentos/parcelas) por categoria, etapa e intervalos de datas diretamente no SQL antes de enviá-los ao prompt.
* **Formato de Contexto Estruturado:** Formate os dados financeiros agregados em uma estrutura JSON limpa e minimalista contendo:
  - Custos e receitas agregados por categoria/etapa do projeto (valores em centavos de BRL).
  - Saldo a receber e cronograma de parcelas/pagamentos.
  - Detalhes de metas de margem ou prazos de homologação ativos (`ProjectFinancialGoal` - valor alvo, valor realizado atual, prazo).

Exemplo de agregação no banco de dados (Lucid v6):
```typescript
import db from '@adonisjs/lucid/services/db'
import { DateTime } from 'luxon'

// Agregar custos do projeto por categoria nos últimos 30 dias
const monthlyCosts = await db
  .from('project_costs')
  .where('project_id', projectId)
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
  healthScore: z.number().int().min(0).max(100).describe('A score from 0 (poor) to 100 (excellent) representing the financial health of the photovoltaic project based on budget vs. actual costs and receivables.'),
  insights: z.array(z.object({
    title: z.string().describe('Short title summarizing the cost anomaly or financial behavior observed in the project.'),
    description: z.string().describe('Detailed explanation of the insight, with actionable advice.'),
    category: z.string().describe('The main financial category related to this insight (e.g., Equipamentos, Mão de obra, Homologação).'),
    severity: z.enum(['low', 'medium', 'high']).describe('The priority level of the insight.'),
    potentialSavingsCents: z.number().int().describe('Estimated potential savings in BRL cents if the recommendation is followed.'),
  })).describe('List of customized financial insights for the photovoltaic project.'),
  goalProgress: z.array(z.object({
    goalId: z.string().describe('The ULID of the ProjectFinancialGoal.'),
    status: z.enum(['on_track', 'at_risk', 'behind']).describe('The likelihood of achieving the financial/margin goal on time based on current realized values.'),
    recommendation: z.string().describe('Practical recommendation to keep the project margin or homologation deadline on track.'),
  })).describe('Analysis of active project financial goals and progress.')
})
```

## 3. Prompt de Persona de Consultor Financeiro de Projetos
* Configure explicitamente o prompt do sistema do LLM para assumir a persona de um consultor financeiro especialista em projetos de energia solar fotovoltaica no mercado brasileiro.
* Instrua o modelo a respeitar convenções de moeda brasileira (BRL, centavos), inflação, taxas de juros típicas (CDI, Selic) e o ciclo de execução de projetos fotovoltaicos (orçamento, compra de equipamentos, instalação, homologação, recebimento).
* Não permita que o modelo faça recomendações de investimentos que exijam certificações específicas; foque no controle de custos do projeto, margem, fluxo de caixa e otimização de prazos.

```typescript
const systemPrompt = `You are "EngeApp AI", an expert financial advisor for Brazilian photovoltaic/solar engineering projects.
Analyze the project's aggregated financial summary (values in cents) and provide constructive, friendly, and actionable insights in Brazilian Portuguese.
Focus on cost control, project margin, cash flow, and homologation timelines. Do not suggest specific tickers, stocks, or investments requiring certification.`
```

## 4. Resiliência e Rastreamento de Custos
* Envolva as chamadas de geração de IA na cadeia de fallback padrão definida em `adonisjs-ai-agent-cost-analytics-and-budget-control-best-practices`.
* Registre o uso de tokens e o custo total de execução em `AgentAiCost` usando o mapeamento `COSTABLE_TYPES` associando ao projeto ou recurso de planejamento.

## Restrições
* Nunca exponha informações pessoais sensíveis (PII) (como números de conta, documentos do cliente ou descrições cruas de lançamentos) para a API do LLM.
* Os valores monetários devem sempre ser calculados, transmitidos e armazenados em centavos (inteiros) para manter a precisão matemática absoluta.
* O LLM não deve realizar cálculos matemáticos brutos de somas de orçamentos; as consultas de banco de dados devem computar essas somas e fornecê-las ao LLM.
* Todos os prompts, mensagens do sistema e schemas devem forçar saídas traduzidas e localizadas em Português do Brasil para o usuário final, mesmo que os campos description do schema Zod estejam escritos em Inglês.