---
name: adonisjs-mcp-server-integration-best-practices
description: Use when designing, configuring, implementing, securing, or debugging Model Context Protocol (MCP) server integrations, stdio/HTTP transports, and Bearer token authenticated API endpoints for MCP clients in AdonisJS v6 applications.
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
  * **SSE/HTTP (Integrações Remotas)**: Melhor para serviços baseados na web e microsserviços.

### 2. Servidor MCP Stdio via Comando Ace (`commands/mcp_server.ts`)
* O transporte Stdio utiliza a entrada/saída padrão (`stdin`/`stdout`). Para evitar que logs do framework ou declarações print poluam o stdout e quebrem a comunicação JSON-RPC:
  * Configure o logger do AdonisJS para gravar no `stderr` ou em um arquivo.
  * NÃO utilize `console.log()` dentro do código do comando ou serviço.
* Padrão de implementação:
  ```typescript
  import { BaseCommand } from '@adonisjs/core/ace'
  import { Server } from '@modelcontextprotocol/sdk/server/index.js'
  import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
  import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js'
  import app from '@adonisjs/core/services/app'

  export default class McpServerCommand extends BaseCommand {
    static commandName = 'mcp:server'
    static description = 'Starts the MCP Stdio server'

    async run() {
      // Direciona o logger para stderr para evitar quebrar o transporte stdio
      app.container.use('logger').destination = process.stderr

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

### 3. Servidor MCP HTTP & SSE com Autenticação de Token Bearer
* Ao expor o MCP via SSE (Server-Sent Events) sobre HTTP, proteja os endpoints usando Autenticação de Token Bearer (por exemplo, usando tokens OAT do `@adonisjs/auth` ou middleware de chave de API personalizado):
* Defina as rotas em `start/routes.ts`:
  ```typescript
  import router from '@adonisjs/core/services/router'
  import { middleware } from '#start/kernel'
  const McpController = () => import('#controllers/mcp_controller')

  router.group(() => {
    // Endpoint de conexão SSE (requer token de consulta de autenticação ou cabeçalho personalizado)
    router.get('/mcp/sse', [McpController, 'sse'])
    // Endpoint de postagem de mensagem (requer validação padrão de Token Bearer)
    router.post('/mcp/message', [McpController, 'message'])
  }).use(middleware.auth({ guards: ['api'] }))
  ```
* Implemente o Controller usando `SSEServerTransport`:
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'
  import { Server } from '@modelcontextprotocol/sdk/server/index.js'
  import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js'
  import app from '@adonisjs/core/services/app'

  export default class McpController {
    private mcpServer: Server
    private sseTransports = new Map<string, SSEServerTransport>()

    constructor() {
      this.mcpServer = new Server(
        { name: 'maxdmin-remote-mcp', version: '1.0.0' },
        { capabilities: { tools: {} } }
      )
      this.registerHandlers()
    }

    private registerHandlers() {
      // Registre as ferramentas e esquemas de recursos aqui
    }

    async sse({ response, auth }: HttpContext) {
      const user = auth.getUserOrFail()
      const transport = new SSEServerTransport('/api/mcp/message', response.response)
      
      this.sseTransports.set(user.id, transport)
      await this.mcpServer.connect(transport)

      // Mantém a resposta aberta para SSE
      response.response.on('close', () => {
        this.sseTransports.delete(user.id)
      })
    }

    async message({ request, response, auth }: HttpContext) {
      const user = auth.getUserOrFail()
      const transport = this.sseTransports.get(user.id)

      if (!transport) {
        return response.notFound('Conexão de transporte SSE não encontrada')
      }

      await transport.handlePostMessage(request.request, response.response)
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
* NÃO envie saídas usando `console.log()` no modo de transporte stdio. Apenas registre logs no `stderr` ou use um arquivo de log dedicado.
* NÃO exponha chaves primárias do banco de dados diretamente nas ferramentas MCP se forem IDs autoincrementados simples; use ULIDs/UUIDs e mapeie-os com segurança.
* NÃO permita acesso anônimo às rotas HTTP SSE/message. Aplique rigorosamente o middleware de autenticação do AdonisJS.
* NÃO execute consultas SQL puras diretamente dentro das ferramentas MCP. Mantenha a integridade das operações do banco de dados utilizando validação VineJS e Lucid ORM.
