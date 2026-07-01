---
name: adonisjs-ai-agents-tool-calling-best-practices
description: Use when designing, implementing, configuring, securing, or debugging tool calling functionality (AI Tools) for LLM agents using the Vercel AI SDK (provider Gemini via Vercel AI SDK) in AdonisJS v6. Triggers on files modifying AI tools, tool schemas, input validations with Zod, database access inside tools, and tool execution error handling.
---

# Boas Práticas de Chamada de Ferramentas (Tool Calling) para Agentes de IA no AdonisJS

## Objetivo
Estabelecer padrões claros, seguros e robustos para a implementação de ferramentas de IA (tool calling) no AdonisJS v6 utilizando a Vercel AI SDK e Zod, garantindo operações de banco de dados seguras, injeção de dependências adequada e tratamento de erros resiliente.

## Instruções

### 1. Estrutura de Ferramentas e Padrão Factory
- Armazene todas as definições de ferramentas no diretório `app/ai/tools/`.
- Defina as ferramentas usando uma função fábrica (factory function) que aceita as dependências necessárias (models, services ou contexto do agente) e retorna a instância `tool` da Vercel AI SDK.
- Evite estados globais mutáveis dentro dos arquivos das ferramentas.

Exemplo de padrão:
```typescript
import { tool } from 'ai'
import { z } from 'zod'
import type SocialMediaAgent from '#models/calendar/social_media_agent'
import BrandPositioning from '#models/calendar/brand_positioning'

export function getBrandPositioningTool(agent: SocialMediaAgent) {
  return tool({
    description: 'Obtém o guia completo de posicionamento de marca da empresa solar...',
    inputSchema: z.object({
      solar_company_id: z
        .string()
        .optional()
        .describe('O ULID da empresa solar.'),
    }),
    execute: async ({ solar_company_id }) => {
      const companyId = solar_company_id ?? agent.idSolarCompany
      try {
        const positioning = await BrandPositioning.query()
          .where('solar_company_id', companyId)
          .first()

        if (!positioning) {
          return {
            status: 'error',
            message: 'Posicionamento de marca não encontrado para esta empresa.',
          }
        }

        return {
          status: 'success',
          data: positioning.toJSON(),
        }
      } catch (error) {
        return {
          status: 'error',
          message: 'Ocorreu um erro inesperado no banco de dados ao buscar o posicionamento de marca.',
        }
      }
    },
  })
}
```

### 2. Validação Estrita de Entrada (Zod)
- Sempre use o `zod` para validar as entradas. Defina tipos específicos, limites e restrições.
- Forneça mensagens descritivas usando o método `.describe()` em cada propriedade. O LLM utiliza essas descrições para entender quais valores deve enviar.
- Exemplos de validação:
  - Para ULIDs: `z.string().length(26).describe('O ULID exclusivo da entidade')`
  - Para listas: `z.array(z.string()).describe('Lista de tags')`

### 3. Segurança do Banco de Dados e Transações
- Ao executar operações de escrita (criar, atualizar, deletar), sempre utilize transações do banco de dados ou o suporte a transações integrado do Lucid caso múltiplas operações estejam envolvidas.
- Execute consultas no contexto do inquilino (tenant) ou agência atual para garantir o isolamento de dados (Multi-Tenancy).

### 4. Tratamento de Erros Resiliente
- Nunca permita que erros de banco de dados (`LucidException`, `DatabaseException`) se propaguem diretamente para o loop de execução do agente de IA. Isso pode travar a execução ou fazer o agente alucinar relatórios de erro.
- Sempre envolva as consultas de banco de dados em blocos `try/catch`.
- Retorne mensagens de status estruturadas: `{ status: 'success', data: ... }` ou `{ status: 'error', message: 'Mensagem amigável para o usuário' }`.

### 5. Retornos Estruturados para o LLM
- Retorne objetos limpos e compactos ou resumos em Markdown.
- Evite retornar instâncias brutas de models do banco de dados que possam conter campos confidenciais (como hashes de senha, tokens, flags internas). Filtre ou mapeie a estrutura de saída cuidadosamente.

## Restrições
- **Sem SQL Puro Inseguro:** Nunca execute consultas SQL brutas montadas por interpolação de strings dentro das ferramentas. Utilize o Query Builder do Lucid ou parâmetros de consulta vinculados (bindings).
- **Sem Vazamento de Dados Sensíveis:** Nunca retorne rastreamentos de pilha de erro (stack traces), caminhos internos do sistema ou variáveis de ambiente para o LLM na resposta de `error`.
- **Isolamento de Dados:** Sempre valide se o recurso solicitado pertence ao tenant/empresa ativo antes de atualizá-lo ou lê-lo.
- **Sem Loops Infinitos:** Garanta que as ferramentas não chamem outras ferramentas diretamente de forma a criar um ciclo de feedback infinito. Mantenha a lógica de execução das ferramentas síncrona ou assíncrona linear.
