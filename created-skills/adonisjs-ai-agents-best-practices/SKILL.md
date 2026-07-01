---
name: adonisjs-ai-agents-best-practices
description: Use when creating, reviewing, debugging, or enhancing AI agent logic, AI tools with Zod schemas, BullMQ workers, or Ace CLI command workers in AdonisJS. Triggers on agent design patterns (AgentConfig, factory exports), system prompt structure, tool definitions with Vercel AI SDK, and BullMQ queue handlers. Use adonisjs-ai-sdk-google-gemini-best-practices for provider configuration, fallback chains, and cost tracking.
---

## Objetivo
Estabelecer padrões estritos e melhores práticas para a criação, depuração e manutenção de agentes de IA usando o Vercel AI SDK e a API do Google Gemini, definindo ferramentas de IA robustas com validação de esquema Zod, e tratando processamento em segundo plano utilizando workers BullMQ e comandos Ace no framework AdonisJS.

## Instruções

## 1. Design e Arquitetura de Agentes de IA
- **Padrão de Configuração:** Defina objetos de configuração usando a estrutura padrão de `AgentConfig`:
  ```typescript
  interface AgentConfig {
    agentName: string
    typeData: string
    systemPrompt: string
    tools: Record<string, Tool>
    initialModel: string
    maxSteps: number
    maxCalls: number
  }
  ```
- **Exportação de Factory:** Sempre exporte uma função factory para construir a configuração do agente, por exemplo, `create[AgentName]Agent(...args): AgentConfig`.
- **System Prompts:** Prompts direcionados ao agente devem ser estruturados com tags semânticas claras no estilo XML:
  - `<ENTRADA>`: Especificações de contexto e de dados de entrada.
  - `<TAREFA>`: Diretrizes detalhadas para a geração de saída.
  - `<REGRAS>`: Restrições de comportamento estritas.
- **Loop de Execução:** Utilize a função `executeAgent` de `#ai/agent_ai_request` para rodar o loop do agente. Ela gerencia o uso de tokens, tentativas de chamadas de API, modelos de fallback e disparos de ferramentas.

## 2. Definição de Ferramentas de IA (AI Tools)
- **Localização:** Defina todas as ferramentas em `app/ai/tools/`, nunca inline em controllers ou comandos.
- **Helper de Tool do Vercel AI SDK:** Crie ferramentas usando a função helper `tool` de `'ai'`.
- **Esquemas Zod:** Defina o `inputSchema` usando `zod` (`z.object({...})`). Cada parâmetro deve conter uma chamada descritiva `.describe(...)` para orientar o LLM de forma precisa.
- **Isolamento de Serviços:** Mantenha a lógica de execução da ferramenta limpa e concisa. Se a ferramenta precisar realizar gravações no banco de dados ou requisições externas, invoque os modelos ou serviços apropriados e retorne um objeto de resultado unificado:
  ```typescript
  export function myCustomTool() {
    return tool({
      description: 'Descrição detalhada do que a ferramenta faz.',
      inputSchema: z.object({
        id: z.string().describe('ID da entidade alvo'),
      }),
      execute: async ({ id }) => {
        try {
          // lógica
          return { status: 'success', message: 'Ação concluída com sucesso.' }
        } catch (error) {
          return { status: 'error', message: error.message }
        }
      }
    })
  }
  ```

## 3. Jobs em Segundo Plano com BullMQ
- **Estrutura de Jobs:** Crie jobs dedicados em `app/jobs/` nomeados como `[Name]Job.ts`.
- **Dispatcher Estático e Fila:** Defina um `queueName` estático e um método `dispatch` estático para enfileirar jobs com segurança usando as cargas úteis necessárias:
  ```typescript
  export default class CustomJob {
    static readonly queueName = 'custom-queue'
    static async dispatch(payload: { id: string }) {
      await customQueue.add('action', payload)
    }
  }
  ```
- **Implementação do Handler:** Implemente um método estático `handle(job: Job<Data>)` para buscar os registros, invocar `executeAgent` com a configuração de agente apropriada e persistir os resultados.
- **Registro de Custos:** Salve os tokens da API e os custos de processamento usando o helper `saveAiCost(costableType, costableId, result)`.

## 4. Workers via Comandos Ace CLI
- **Processo Worker:** Crie arquivos de comando em `commands/` estendendo `BaseCommand`.
- **Inicialização da Aplicação:** Configure `static options = { startApp: true }` para garantir que todos os provedores, serviços e modelos sejam carregados antes de iniciar os workers.
- **Graceful Shutdown:** Registre ouvintes para `SIGTERM` e `SIGINT` para fechar todas as instâncias ativas de `Worker` de forma limpa.

## Restrições
- Não defina ferramentas de forma inline dentro de controllers ou comandos; mantenha-as em `app/ai/tools/`.
- Todos os esquemas de entrada de ferramentas devem ter chamadas explícitas e detalhadas de `.describe()` em todos os campos.
- Não inicie múltiplos workers para a mesma fila no mesmo processo sem tratar adequadamente seu ciclo de vida de finalização.
- Nunca escreva credenciais, chaves de API ou segredos de conexão diretamente nos arquivos fonte; sempre os leia de `process.env`.
