---
name: adonisjs-ai-sdk-google-gemini-best-practices
description: Use when configuring the Vercel AI SDK provider setup, model parameters (temperature, topP, stopWhen/stepCountIs), fallback chains, structured JSON outputs with Zod, or tracking token costs/caching with Google Gemini in AdonisJS v6. This is the standard AI provider skill — always use Vercel AI SDK (@ai-sdk/google). Triggers on provider instantiation, model degradation strategies, token budget control, and Gemini context caching. Use adonisjs-ai-agents-best-practices for agent logic and tool design.
---

## Objetivo
Estabelecer diretrizes e convenções de código estritas para a integração robusta e resiliente do Vercel AI SDK e provedores da API Google Gemini em aplicações baseadas no AdonisJS v6.

## Instruções

## 1. Instanciação e Configuração do Provedor
- **Importações de Pacotes:** Sempre importe `google` de `@ai-sdk/google` e as funções/tipos utilitários de `ai`.
  ```typescript
  import { generateText, streamText, stepCountIs, type Tool } from 'ai'
  import { google } from '@ai-sdk/google'
  ```
- **Referência ao Provedor:** Instancie o provedor do Google usando `google('nome-do-modelo')` dentro das funções de geração, em vez de manter uma instância global que possa vazar estados entre requisições.
- **Parâmetros do Modelo:** Padronize parâmetros que equilibrem qualidade e custo:
  - Use `temperature` (padrão 0.7 para tarefas criativas, 0.2 para tarefas analíticas).
  - Controle o multi-step (loops de ferramentas agentícias, AI Tools) com `stopWhen: stepCountIs(N)` na chamada de `generateText`/`streamText`. No Vercel AI SDK v7 não existe `maxSteps`; a parada é definida via `stopWhen`.
  ```typescript
  const result = await generateText({
    model: google('gemini-2.5-flash'),
    stopWhen: stepCountIs(5),
    // tools, prompt, etc...
  })
  ```

## 2. Cadeia de Fallback e Resiliência
- **Array de Modelos:** Mantenha um array de modelos de fallback para tratar limites de taxa (429) ou falhas temporárias na API:
  ```typescript
  const FALLBACK_CHAIN = [
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
  ]
  ```
- **Loop de Fallback:** Implemente um mecanismo de retentativa com degradação dinâmica de modelo. Se uma chamada falhar, capture a exceção, aguarde 5 segundos, mude para o próximo modelo na cadeia e tente novamente.
  ```typescript
  let currentModel = initialModel ?? 'gemini-2.5-flash'
  // Dentro do loop:
  try {
    const result = await generateText({
      model: google(currentModel),
      // parâmetros...
    })
  } catch (error) {
    const idx = FALLBACK_CHAIN.indexOf(currentModel)
    if (idx !== -1 && idx < FALLBACK_CHAIN.length - 1) {
      currentModel = FALLBACK_CHAIN[idx + 1]
    }
    await new Promise((r) => setTimeout(r, 5000))
  }
  ```

## 3. Respostas Estruturadas com Zod
- **Tipagem Estrita:** Ao exigir saídas estruturadas, utilize `generateObject`/`streamObject` (importados de `ai`) com `output: 'object'` ou `output: 'array'` e o `schema` Zod correspondente ao formato desejado.
- **Campos Autodescritivos:** Cada campo no esquema Zod deve conter uma chamada `.describe()` explicativa para garantir que o LLM entenda e gere os valores corretamente.
  ```typescript
  import { z } from 'zod'

  const outputSchema = z.object({
    title: z.string().describe('O título conciso da postagem, no máximo 60 caracteres.'),
    body: z.string().describe('O texto do corpo da postagem em formato markdown.'),
    hashtags: z.array(z.string()).describe('Um array de 3 a 5 hashtags relevantes.'),
  })
  ```

## 4. Injeção de Dependências de Ferramentas de IA no AdonisJS
- **Padrão de Fábrica por Closure:** Evite definir ferramentas com escopo global ou instâncias fixas. Em vez disso, exporte uma função fábrica que aceite os models, serviços ou contextos necessários:
  ```typescript
  import { tool } from 'ai'
  import { z } from 'zod'
  import SocialMediaAgent from '#models/calendar/social_media_agent'

  export function getBrandPositioningTool(agent: SocialMediaAgent) {
    return tool({
      description: 'Obtém as informações de posicionamento de marca para a empresa.',
      inputSchema: z.object({
        companyId: z.string().optional().describe('ID (ULID) opcional da empresa para sobrescrever.'),
      }),
      execute: async ({ companyId }) => {
        const id = companyId ?? agent.idSolarCompany
        // Busca usando o Lucid ORM
        const data = await BrandPositioning.query().where('solar_company_id', id).first()
        return data ? { status: 'success', data } : { status: 'error', message: 'Não encontrado' }
      }
    })
  }
  ```
- **Isolamento:** Mantenha a lógica de execução das ferramentas simples, delegando operações complexas do banco de dados para os models do Lucid ou classes de serviço do AdonisJS.

## 5. Rastreamento de Cache de Tokens e Cálculo de Custos
- **Metadados de Cache do Google:** O Google Gemini suporta cache de contexto. Recupere os tokens lidos do cache a partir do `providerMetadata` no callback `onStepFinish` para registrar os custos exatos:
  ```typescript
  let totalInputNotCached = 0
  let totalInputCached = 0
  let totalOutput = 0

  onStepFinish: ({ usage, providerMetadata }) => {
    // Em @ai-sdk/google@4 o contador fica aninhado sob `usageMetadata`, não no topo da chave `google`.
    // Em v7 prefira `usage.inputTokenDetails.cacheReadTokens` diretamente.
    const cacheRead = ((providerMetadata as any)?.google?.usageMetadata?.cachedContentTokenCount as number) ?? 0
    const promptNonCached = Math.max((usage.inputTokens ?? 0) - cacheRead, 0)
    totalInputNotCached += promptNonCached
    totalInputCached += cacheRead
    totalOutput += usage.outputTokens ?? 0
  }
  ```
- **Cálculo de Custo:** Calcule o preço dinamicamente com base nas taxas de entrada normal e de cache por milhão de tokens, conforme o catálogo de precificação definido (ex. tabela `AgentAiCost`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Nunca declare ferramentas inline dentro de controllers ou jobs de segundo plano; mantenha-as sempre modularizadas em `app/ai/tools/`.
- Não ignore a cadeia de fallback de modelos em tarefas de segundo plano críticas voltadas para produção.
- Jamais insira credenciais ou chaves de API diretamente nos arquivos de código fonte; recupere-as sempre de variáveis de ambiente através de `process.env`.
- Todos os campos nos esquemas do Zod utilizados por ferramentas ou na geração estruturada de objetos devem possuir uma chamada `.describe()` explícita.
