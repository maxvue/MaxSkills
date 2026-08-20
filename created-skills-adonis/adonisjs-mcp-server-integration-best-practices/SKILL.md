---
name: adonisjs-mcp-server-integration-best-practices
description: Use when designing, configuring, implementing, securing, or debugging Model Context Protocol (MCP) server integrations, stdio/Streamable HTTP transports, and Bearer (OAT) token authenticated API endpoints for MCP/M2M clients in AdonisJS v6 applications.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Integração do Servidor MCP no AdonisJS

## Objetivo
Estabelecer padrões seguros, performáticos e padronizados para a implementação de servidores e clientes do Model Context Protocol (MCP) em aplicações AdonisJS v6, protegendo a comunicação com tokens Bearer e mapeando modelos do Lucid ORM para ferramentas MCP.

## Instruções

### 1. Instalação e Configuração Inicial
* Instale o pacote oficial `@modelcontextprotocol/sdk`:
  ```bash
  npm i @modelcontextprotocol/sdk
  ```
* Escolha o transporte apropriado:
  * **Stdio (Integração de Linha de Comando/IDE)**: Melhor para integrações locais onde o servidor é executado como um subprocesso.
  * **Streamable HTTP (Integrações Remotas)**: Melhor para serviços baseados na web e microsserviços. Use o `StreamableHTTPServerTransport` (o transporte SSE legado está depreciado).

### 2. Servidor MCP Stdio via Comando Ace (`commands/mcp_server.ts`)
* O transporte Stdio utiliza a entrada/saída padrão (`stdin`/`stdout`). Para evitar que logs do framework ou declarações print poluam o stdout e quebrem a comunicação JSON-RPC:
  * Configure o logger do AdonisJS para gravar no `stderr` ou em um arquivo (via `config/logger.ts`, no transporte do pino). NÃO escreva no `stdout`.
  * NÃO utilize `console.log()` dentro do código do comando ou serviço.
* Padrão de implementação:
  ```typescript
  import { BaseCommand } from '@adonisjs/core/ace'
  import { Server } from '@modelcontextprotocol/sdk/server/index.js'
  import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
  import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js'
  import app from '@adonisjs/core/services/app'
  import logger from '@adonisjs/core/services/logger'

  export default class McpServerCommand extends BaseCommand {
    static commandName = 'mcp:server'
    static description = 'Starts the MCP Stdio server'

    async run() {
      // O logger é obtido via service do core (não há app.container.use()).
      // Para o transporte stdio, garanta em config/logger.ts que o destino do
      // pino seja stderr (pino.destination(2)) ou um arquivo — nunca stdout.
      logger.info('Iniciando servidor MCP via stdio')

      const server = new Server(
        { name: 'maxdmin-mcp-server', version: '1.0.0' },
        { capabilities: { tools: {} } }
      )

      // Registra a lista de ferramentas
      server.setRequestHandler(ListToolsRequestSchema, async () => {
        return {
          tools: [
            {
              name: 'get_admin_context',
              description: 'Retrieve administrative context and system health metrics from Maxdmin.',
              inputSchema: {
                type: 'object',
                properties: {
                  tenantId: { type: 'string', description: 'Target tenant identifier' }
                },
                required: ['tenantId']
              }
            }
          ]
        }
      })

      // Registra o manipulador de execução de ferramentas
      server.setRequestHandler(CallToolRequestSchema, async (request) => {
        if (request.params.name === 'get_admin_context') {
          try {
            const { tenantId } = request.params.arguments as { tenantId: string }
            // Resolve serviços via AdonisJS IoC container
            const maxdminService = await app.container.make('maxdmin/service')
            const context = await maxdminService.getContext(tenantId)
            
            return {
              content: [{ type: 'text', text: JSON.stringify(context) }]
            }
          } catch (error) {
            return {
              isError: true,
              content: [{ type: 'text', text: `Failed to retrieve context: ${error.message}` }]
            }
          }
        }
        throw new Error('Tool not found')
      })

      const transport = new StdioServerTransport()
      await server.connect(transport)
    }
  }
  ```

### 3. Servidor MCP HTTP (Streamable HTTP) com Autenticação de Token Bearer
* Para integrações remotas use o **Streamable HTTP transport** (`StreamableHTTPServerTransport`), que substituiu o antigo transporte SSE depreciado das versões recentes do `@modelcontextprotocol/sdk`. Proteja os endpoints com Token Bearer via tokens OAT do `@adonisjs/auth` (o uso de OAT/Bearer aqui é restrito a clientes MCP/M2M — não é o modelo de auth da aplicação web, que é sessão+cookie).
* **Pré-requisito — configurar o guard de access tokens.** O `config/auth.ts` do projeto define **apenas** o guard de sessão `web`; **não existe** guard `api`/access-tokens. Sem o passo abaixo, `guards: ['api']` falha na inferência de TypeScript contra a interface `Authenticators` e quebra em runtime. Este guard OAT é a exceção sancionada para MCP/M2M (o resto da aplicação continua sessão+cookie). Adicione o guard em `config/auth.ts`:
  ```typescript
  import { defineConfig } from '@adonisjs/auth'
  import { tokensGuard, tokensUserProvider } from '@adonisjs/auth/access_tokens'

  const authConfig = defineConfig({
    default: 'web',
    guards: {
      web: /* ...guard de sessão existente... */,
      api: tokensGuard({
        provider: tokensUserProvider({
          tokens: 'accessTokens',
          model: () => import('#models/user'),
        }),
      }),
    },
  })
  ```
  E adicione o mixin `DbAccessTokensProvider` ao model `User` (`app/models/user.ts`):
  ```typescript
  import { DbAccessTokensProvider } from '@adonisjs/auth/access_tokens'

  export default class User extends BaseModel {
    // ...colunas existentes...
    static accessTokens = DbAccessTokensProvider.forModel(User)
  }
  ```
  Rode a migration da tabela de tokens (`auth_access_tokens`) antes de usar o guard.
* Defina as rotas em `start/routes.ts`. O Streamable HTTP usa um único endpoint que atende POST (mensagens cliente→servidor), GET (stream servidor→cliente) e DELETE (encerramento de sessão):
  ```typescript
  import router from '@adonisjs/core/services/router'
  import { middleware } from '#start/kernel'
  const McpController = () => import('#controllers/mcp_controller')

  router.group(() => {
    // Endpoint único do Streamable HTTP transport (Token Bearer obrigatório)
    router.post('/mcp', [McpController, 'handle'])
    router.get('/mcp', [McpController, 'handle'])
    router.delete('/mcp', [McpController, 'handle'])
  }).use(middleware.auth({ guards: ['api'] }))
  ```
* Implemente o Controller usando `StreamableHTTPServerTransport`, mantendo um transporte por sessão MCP:
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'
  import { Server } from '@modelcontextprotocol/sdk/server/index.js'
  import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js'
  import { randomUUID } from 'node:crypto'

  export default class McpController {
    // Transportes ativos indexados pelo Mcp-Session-Id
    private transports = new Map<string, StreamableHTTPServerTransport>()

    private buildServer() {
      const server = new Server(
        { name: 'maxdmin-remote-mcp', version: '1.0.0' },
        { capabilities: { tools: {} } }
      )
      this.registerHandlers(server)
      return server
    }

    private registerHandlers(server: Server) {
      // Registre as ferramentas e esquemas de recursos aqui
    }

    async handle({ request, response, auth }: HttpContext) {
      // Garante autenticação do cliente MCP (token OAT) antes de qualquer I/O
      await auth.authenticate()

      const sessionId = request.header('mcp-session-id')
      let transport = sessionId ? this.transports.get(sessionId) : undefined

      if (!transport) {
        transport = new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (id) => this.transports.set(id, transport!),
        })
        transport.onclose = () => {
          if (transport!.sessionId) this.transports.delete(transport!.sessionId)
        }
        await this.buildServer().connect(transport)
      }

      // Delega o ciclo de requisição/streaming ao transporte
      await transport.handleRequest(request.request, response.response, request.body())
    }
  }
  ```

### 4. Mapeamento de Modelos Lucid ORM para Ferramentas MCP
* Sempre valide os argumentos de entrada das ferramentas usando VineJS antes de consultar os modelos Lucid.
* Use modelos Lucid de forma segura para impor isolamento de dados (por exemplo, restringindo consultas ao tenant atual):
  ```typescript
  import User from '#models/user'
  import vine from '@vinejs/vine'

  const listUsersValidator = vine.compile(
    vine.object({
      role: vine.string().optional(),
      limit: vine.number().min(1).max(100).optional()
    })
  )

  // Dentro do manipulador da chamada da ferramenta:
  const payload = await listUsersValidator.validate(request.params.arguments)
  const users = await User.query()
    .where('tenantId', currentTenantId)
    .if(payload.role, (query) => query.where('role', payload.role!))
    .limit(payload.limit || 20)
  ```

### 5. Tratamento de Erros e Mapeamento de Respostas
* Mapeie exceções de banco de dados e erros de validação para estruturas de erro padrão do MCP/JSON-RPC:
  ```typescript
  import { errors as vineErrors } from '@vinejs/vine'
  import { errors as lucidErrors } from '@adonisjs/lucid'

  function handleMcpError(error: any) {
    if (error instanceof vineErrors.E_VALIDATION_ERROR) {
      return {
        isError: true,
        content: [{ type: 'text', text: `Erro de Validação: ${JSON.stringify(error.messages)}` }]
      }
    }
    // Evita o vazamento de detalhes internos
    return {
      isError: true,
      content: [{ type: 'text', text: 'Ocorreu um erro interno ao processar a requisição.' }]
    }
  }
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO envie saídas usando `console.log()` no modo de transporte stdio. Apenas registre logs no `stderr` ou use um arquivo de log dedicado.
* NÃO exponha chaves primárias do banco de dados diretamente nas ferramentas MCP se forem IDs autoincrementados simples; use ULIDs/UUIDs e mapeie-os com segurança.
* NÃO permita acesso anônimo às rotas HTTP do MCP. Aplique rigorosamente o middleware de autenticação do AdonisJS (guard `api`/OAT, restrito a clientes MCP/M2M).
* NÃO execute consultas SQL puras diretamente dentro das ferramentas MCP. Mantenha a integridade das operações do banco de dados utilizando validação VineJS e Lucid ORM.
