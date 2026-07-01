---
name: adonisjs-ai-agents-structured-outputs-zod-best-practices
description: Use when implementing, reviewing, or debugging structured outputs from AI models using Zod schemas with Vercel AI SDK and Gemini in AdonisJS. Triggers on generateObject, jsonSchema, zod schemas for AI, and validation of LLM structured responses.
---

# Boas Práticas para Saídas Estruturadas com Zod e IA no AdonisJS

## Objetivo
Estabelecer padrões limpos, otimizados para desempenho e seguros quanto a tipos para o uso de `generateObject` do Vercel AI SDK com esquemas Zod e Google Gemini dentro de aplicações AdonisJS v6, garantindo validação sem falhas, resiliência a erros e persistência direta no Lucid ORM.

## Instruções

### 1. Importações e Configuração Básica
Sempre importe `generateObject` da biblioteca `ai`, o provedor Google de `@ai-sdk/google` e `z` do `zod`.
```typescript
import { generateObject } from 'ai'
import { google } from '@ai-sdk/google'
import { z } from 'zod'
```

### 2. Definição de Esquemas Zod Otimizados para IA
Os modelos Google Gemini dependem fortemente de metadados do esquema para gerar JSONs corretos. Defina esquemas seguindo estas regras:
* **Campos Autodescritivos:** Cada campo do esquema DEVE ter uma chamada `.describe()` explicando o formato esperado, regras e significado semântico em inglês claro.
* **Restrições Estritas com Enums:** Use `z.enum([...])` para restringir campos a valores específicos esperados (ex: tipos de proposta, segmentos de cliente, flags de status).
* **Estruturas Rasas e Planas:** Mantenha os esquemas abaixo de 3 níveis de aninhamento. Objetos muito aninhados aumentam as falhas de parsing e o consumo de tokens.
* **Opcionalidade:** Declare claramente os campos opcionais usando `.optional()` ou `.nullable()` para que o modelo saiba que pode omitir ou retornar nulo.

```typescript
export const proposalSummarySchema = z.object({
  title: z.string().describe('A clear, concise title for the solar energy proposal, max 60 characters.'),
  summary: z.string().describe('The main proposal summary in Brazilian Portuguese. Include 2-3 line breaks and a clear next step for the customer.'),
  segment: z.enum(['residential', 'commercial']).describe('The customer segment this proposal targets.'),
  items: z.array(
    z.object({
      itemNumber: z.number().describe('1-indexed number representing the line item position.'),
      label: z.string().describe('Short label for the equipment or service line item. Max 50 characters.'),
      detail: z.string().describe('Detailed description for the engineer: equipment specs, sizing assumptions, and installation notes.')
    })
  ).describe('An array of line items making up the proposal scope. Max 7 items.')
})

export type ProposalSummaryPayload = z.infer<typeof proposalSummarySchema>
```

### 3. Executando `generateObject`
* Use `generateObject` em vez de `generateText` com parsing manual de JSON.
* Especifique `schemaName` e `schemaDescription` nos parâmetros do Vercel AI SDK para dar ao LLM um contexto de alto nível sobre o objeto que está sendo gerado.
* Configure a `temperature` de acordo com a tarefa: temperaturas mais baixas (ex: 0.2) para dados estruturados rígidos (como calendários/agendamentos) e mais altas (ex: 0.7) para geração criativa (como rascunhos de copy).

```typescript
const result = await generateObject({
  model: google('gemini-2.5-flash'),
  schema: proposalSummarySchema,
  schemaName: 'ProposalSummary',
  schemaDescription: 'A complete summary structure for a solar energy proposal including segment, summary text, and individual scope line items.',
  system: 'You are an expert solar energy sales engineer. Always output in Brazilian Portuguese.',
  prompt: 'Create a proposal summary about the benefits of solar energy for businesses in high tariff regions.',
  temperature: 0.7,
})

const proposalSummary: ProposalSummaryPayload = result.object
```

### 4. Tratamento de Erros e Resiliência
A geração de saídas estruturadas pode falhar devido a erros de rede, incompatibilidades de validação com o Zod ou problemas de parsing. Envolva a execução em try-catch e trate os erros específicos do AI SDK:
* **`TypeValidationError`:** Ocorre quando o modelo gera o JSON, mas ele não passa na validação do esquema Zod.
* **`NoObjectGeneratedError`:** Ocorre quando o modelo falha em produzir qualquer JSON.
* **Estratégia de Fallback:** Se a validação falhar, registre os erros, degrade para um modelo mais forte (ex: de `gemini-2.5-flash-lite` para `gemini-2.5-pro`) e tente novamente.

```typescript
import { TypeValidationError, NoObjectGeneratedError } from 'ai'
import logger from '@adonisjs/core/services/logger'

async function generateWithFallback(prompt: string): Promise<ProposalSummaryPayload> {
  const models = ['gemini-2.5-flash', 'gemini-2.5-pro']
  let lastError: any = null

  for (const modelName of models) {
    try {
      const { object } = await generateObject({
        model: google(modelName),
        schema: proposalSummarySchema,
        prompt,
      })
      return object
    } catch (error) {
      lastError = error
      if (error instanceof TypeValidationError) {
        // Registra erros de validação (ex: campos ausentes ou com tipo incorreto)
        // Use o logger do Adonis; o valor rejeitado fica em `error.value` e a causa em `error.cause`.
        logger.error({ value: error.value, cause: error.cause }, `Validation failed using ${modelName}`)
      } else if (error instanceof NoObjectGeneratedError) {
        logger.error({ err: error }, `No object generated using ${modelName}`)
      }
      // Aguarda antes de tentar novamente com um modelo mais forte
      await new Promise((resolve) => setTimeout(resolve, 2000))
    }
  }

  throw new Error(`Failed to generate structured proposal summary. Last error: ${lastError?.message}`)
}
```

### 5. Mapeamento de Banco de Dados e Integração com Lucid ORM
Mapeie o objeto TypeScript gerado e validado diretamente para as propriedades do Lucid ORM.
* **Colunas JSON:** Para colunas serializadas como JSON no banco de dados, passe diretamente os subobjetos ou arrays do Zod. Certifique-se de que o modelo Lucid use decoradores adequados para tratar a serialização/deserialização.
* **Transações Seguras:** Ao salvar múltiplos modelos (ex: salvar uma `Proposal` e suas linhas associadas de `ProposalItem`), envolva as operações em uma transação de banco de dados do Lucid para evitar gravações parciais em caso de falha.

```typescript
import db from '@adonisjs/lucid/services/db'
import Proposal from '#models/proposal/proposal'
import ProposalItem from '#models/proposal/proposal_item'

async function saveProposalToDatabase(proposalId: string, data: ProposalSummaryPayload) {
  await db.transaction(async (trx) => {
    // 1. Atualiza a proposta com o resumo gerado
    const proposal = await Proposal.findOrFail(proposalId, { client: trx })
    proposal.title = data.title
    proposal.summary = data.summary
    proposal.segment = data.segment
    await proposal.save()

    // 2. Remove os itens de escopo antigos e insere os novos
    await ProposalItem.query({ client: trx }).where('proposal_id', proposalId).delete()

    const items = data.items.map((item) => ({
      proposalId: proposal.id,
      itemNumber: item.itemNumber,
      label: item.label,
      detail: item.detail,
    }))

    await ProposalItem.createMany(items, { client: trx })
  })
}
```

## Restrições
* NUNCA use expressões regulares manuais ou `JSON.parse` em saídas de texto bruto para extrair dados estruturados. Sempre use o método nativo `generateObject`.
* NUNCA omita a chamada `.describe()` em nenhum campo do esquema Zod enviado ao modelo de linguagem.
* NÃO crie esquemas Zod recursivos ou excessivamente profundos; mantenha as relações planas para evitar alucinações de LLM e erros de falta de memória.
* NÃO realize gravações no banco de dados ou operações complexas de I/O dentro de transformadores de esquemas Zod ou regras de validação; mantenha ações de banco em serviços ou controllers.
