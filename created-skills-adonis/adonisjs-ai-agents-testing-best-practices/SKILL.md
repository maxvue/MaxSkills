---
name: adonisjs-ai-agents-testing-best-practices
description: Use when writing, debugging, or configuring unit and functional tests for AI agents in AdonisJS v6. Triggers on testing LLM calls, mocking Vercel AI SDK (@ai-sdk/google), verifying Zod structured outputs, or writing integration tests for AI agents with Japa.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer padrões claros, diretrizes e exemplos para a escrita de testes unitários e funcionais automatizados, rápidos e isolados para agentes de IA no AdonisJS v6 usando o framework de testes Japa e as ferramentas de simulação (mock) do Vercel AI SDK, evitando chamadas reais à API e dependências externas.

## Instruções

## 1. Preparando o Wrapper de Execução de Agentes para Testabilidade
Para permitir testes sem chamadas reais aos endpoints de LLM, a função de execução do agente (`executeAgent` dentro de `#ai/agent_ai_request`) deve aceitar um parâmetro opcional de modelo `customModel`:
```typescript
// app/ai/agent_ai_request.ts
import { type LanguageModel } from 'ai'

export interface AgentExecuteOptions {
  agentName: string
  typeData?: string
  systemPrompt: string
  prompt: string
  tools: Record<string, Tool>
  initialModel?: string
  maxSteps?: number
  maxCalls?: number
  isDone: () => Promise<boolean>
  customModel?: LanguageModel // Modelo mockado injetável
}

// Dentro do executeAgent:
// Use customModel se fornecido, caso contrário use o provedor real:
const modelToUse = opts.customModel ?? google(currentModel)
```

## 2. Configurando Testes Unitários com MockLanguageModelV4
Use a classe `MockLanguageModelV4` de `ai/test` para interceptar as chamadas e retornar respostas determinísticas:
1. Importe `MockLanguageModelV4` no seu arquivo de teste `.spec.ts`.
2. Inicialize-o definindo uma implementação para `doGenerate` que retorne os tokens de uso e o conteúdo desejado.
3. Passe esse modelo mockado para a função que executa o agente.
4. Faça as asserções usando o helper `assert` do contexto do Japa.

Veja o exemplo completo em [examples/mock-gemini-test.md](examples/mock-gemini-test.md).

## 3. Testando Saídas Estruturadas com Validação de Schemas Zod
Quando se espera que o agente retorne uma saída estruturada (por exemplo, JSON validado por um schema Zod):
1. No `doGenerate` do seu modelo mockado, defina o campo `content` como a string JSON representativa da estrutura de dados esperada.
2. Após a execução, valide o texto resultante com o schema Zod: `schema.safeParse(JSON.parse(resultText))`.
3. Certifique-se de que a validação foi bem-sucedida (`success` é `true`) e que os campos contêm os valores simulados corretos.

Veja o exemplo completo em [examples/structured-output-test.md](examples/structured-output-test.md).

## 4. Limpeza de Banco de Dados de Teste e Custos de IA
Os testes funcionais e de integração que disparam agentes reais podem persistir registros de custo na tabela usando o model `AgentAiCost`.
* Sempre limpe os registros criados em banco nos hooks de ciclo de vida do Japa (`group.each.setup` ou retornando uma função de cleanup no `setup` do grupo):
  ```typescript
  test.group('Integração de Agente de IA', (group) => {
    group.each.setup(async () => {
      // Configuração inicial de mocks
      return async () => {
        // Limpeza dos custos criados pelo agente de teste
        await AgentAiCost.query().where('agent', 'agente-de-teste').delete()
      }
    })
  })
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **SEM Chamadas Reais de API:** Nunca execute testes automatizados que façam requisições HTTP reais para o Google Gemini ou outras APIs de IA.
* **SEM Segredos Hardcoded:** Nunca inclua chaves de API reais nos arquivos de teste; utilize variáveis de ambiente ou mocks.
* **SEM Resíduos no Banco:** Limpe todos os registros de teste gerados no banco de dados antes que o processo de teste seja finalizado.
* **Aliases de Caminho:** Não utilize caminhos relativos como `../../app`; use sempre os aliases configurados no AdonisJS (ex: `#ai/agent_ai_request` ou `#models/agent_ai_cost`).
