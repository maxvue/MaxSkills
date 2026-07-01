---
name: adonisjs-api-documentation-openapi-best-practices
description: Use when configuring, documenting, or generating REST API documentation using OpenAPI 3.0/3.1 specifications, Swagger UI, or Scalar inside an AdonisJS v6 application. Triggers on route annotations, custom schema definitions using VineJS or Zod, auto-generation scripts, and Scalar/Swagger router configurations.
---

# Boas Práticas para Documentação de API com OpenAPI no AdonisJS

## Objetivo
Estabelecer padrões robustos, automatizados e seguros para gerar, manter e servir documentações de API REST (OpenAPI/Swagger/Scalar) dentro de uma aplicação AdonisJS v6, integrando com validadores VineJS e protegendo endpoints de documentação.

## Instruções

### 1. Seleção e Instalação de Ferramentas
Para o AdonisJS v6, utilize o pacote `adonis-autoswagger` para extrair endpoints automaticamente a partir das definições do roteador e ler as anotações JSDoc dos métodos de controllers.
Instale a biblioteca e gere o arquivo de configuração:
```bash
npm i adonis-autoswagger
node ace configure adonis-autoswagger
```

### 2. Configuração do Swagger (`config/swagger.ts`)
Defina os metadados da API, esquemas de autenticação (sessão + cookie via guard web) e exclua rotas que não necessitam de documentação (como rotas genéricas de captura da SPA).
```typescript
import path from 'node:path'
import url from 'node:url'

export default {
  // Título da documentação da API
  title: 'EngeApp REST API',
  description: 'Documentação interativa de API para os serviços do EngeApp (fotovoltaico/solar)',
  version: '1.0.0',
  
  // Destino do arquivo Swagger JSON
  swaggerFilePath: path.join(path.dirname(url.fileURLToPath(import.meta.url)), '../public/swagger.json'),
  
  // Pastas onde buscar rotas e controllers
  scanDirs: ['app/controllers', 'start'],
  
  // Definição dos esquemas de segurança
  // O modelo de auth do projeto é sessão + cookie (guard web, sessões em DB, 30 dias).
  // O cookie de sessão é enviado automaticamente pelo browser; documente-o como apiKey em cookie.
  securitySchemes: {
    SessionCookie: {
      type: 'apiKey',
      in: 'cookie',
      name: 'adonis-session',
    },
    // OAT (Opaque Access Token) APENAS para endpoints MCP/M2M — nunca como padrão da API.
    BearerAuth: {
      type: 'http',
      scheme: 'bearer',
      bearerFormat: 'OAT',
    }
  },
  
  // Segurança padrão aplicada a todos os endpoints: sessão + cookie (guard web)
  security: [{ SessionCookie: [] }],
  
  // Definição de schemas globais/modelos
  schemas: {
    ErrorResponse: {
      type: 'object',
      properties: {
        errors: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              message: { type: 'string' },
              rule: { type: 'string' },
              field: { type: 'string' },
            }
          }
        }
      }
    }
  },
  
  // Ignorar rotas que coincidam com estes padrões
  ignore: ['/webhooks/meta', '/docs', '/swagger'],
  
  // Modo de persistência da interface (true para autogeração, false para manual)
  persistOnStart: true,
  showProtectedRoutes: true,
}
```

### 3. Servindo o Swagger JSON e a UI do Scalar
Em vez de servir arquivos estáticos diretamente, crie uma rota ou controlador dedicado para gerar e servir o JSON do Swagger em tempo real e renderizar um endpoint interativo elegante usando o Scalar ou Swagger UI.
Configure isto em `start/routes.ts`:
```typescript
import router from '@adonisjs/core/services/router'
import AutoSwagger from 'adonis-autoswagger'
import swagger from '#config/swagger'

// Servir o Swagger JSON gerado em tempo real
router.get('/swagger.json', async () => {
  return AutoSwagger.default.generate(swagger)
})

// Servir o Scalar UI usando template HTML da CDN para configuração simplificada
router.get('/docs', ({ response }) => {
  const html = `
    <!doctype html>
    <html>
      <head>
        <title>Referência da API</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          body { margin: 0; }
        </style>
      </head>
      <body>
        <script
          id="api-reference"
          data-url="/swagger.json"
          data-configuration='{"theme": "night"}'
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
  `
  return response.header('Content-Type', 'text/html').send(html)
})
```

### 4. Padrão de Anotações JSDoc nos Controllers
Para documentar os endpoints, adicione anotações JSDoc diretamente acima dos métodos do controller. O `adonis-autoswagger` lê estes blocos para preencher os métodos HTTP, parâmetros, payloads de requisição e payloads de resposta.

Exemplo: `app/controllers/client_controller.ts`
```typescript
export default class ClientController {
  /**
   * @index
   * @operationId getClients
   * @description Recupera a lista de clientes (titulares de usinas fotovoltaicas) do usuário autenticado
   * @responseBody 200 - Lista de clientes - [{"id": "string", "name": "string", "cpf_cnpj": "string", "isActive": true}]
   * @responseBody 401 - Não autorizado
   */
  async index({ auth, response }: HttpContext) {
    // ...
  }

  /**
   * @store
   * @operationId createClient
   * @description Cria um novo cliente (titular de usina)
   * @requestBody {"name": "string", "cpf_cnpj": "string", "international_phone_number": "string", "email": "string"}
   * @responseBody 201 - Detalhes do cliente criado - {"id": "string", "name": "string"}
   * @responseBody 400 - Erro de validação - {"errors": [{"message": "string"}]}
   * @responseBody 401 - Não autorizado
   */
  async store({ request, auth, response }: HttpContext) {
    // ...
  }

  /**
   * @show
   * @operationId getClientById
   * @description Recupera os dados de um cliente específico pelo ID
   * @paramUse id - ID do cliente - true
   * @responseBody 200 - Detalhes do cliente - {"id": "string", "name": "string"}
   * @responseBody 403 - Proibido (Acesso negado ao cliente)
   * @responseBody 404 - Cliente não encontrado
   */
  async show({ params, auth, response }: HttpContext) {
    // ...
  }
}
```

#### Tags Principais de Anotação:
* `@operationId`: Identificador único do endpoint, útil para geradores de código frontend.
* `@description`: Explicação detalhada da finalidade do endpoint.
* `@paramUse nome - descrição - obrigatório (true/false)`: Documenta parâmetros de rota (path parameters).
* `@requestBody`: Exemplo em formato JSON representando o payload de entrada.
* `@responseBody statusCode - descrição - exemplo JSON`: Documenta os status de resposta HTTP esperados e seus respectivos payloads.

### 5. Integração com Validadores do VineJS
Como o VineJS define as regras de validação da aplicação, faça-as corresponder exatamente com a documentação da API:
1. Ao declarar schemas do VineJS em `app/validators/`, certifique-se de que os campos e restrições descritas correspondam diretamente às propriedades de `@requestBody` documentadas.
2. Nas anotações de `@requestBody` dos controllers, espelhe exatamente a estrutura de dados exigida pelo schema do VineJS correspondente.
3. Para objetos aninhados ou reutilizáveis, registre-os em `config/swagger.ts` dentro de `schemas` (ex: `ClientPayload`) e faça referência a eles no JSDoc se o processador de Swagger suportar referências (ex: `#definitions/ClientPayload`).

## Restrições
* NÃO exponha as rotas `/docs` ou `/swagger.json` em ambientes de produção sem a proteção devida (como middleware de autenticação `middleware.auth()`) se a API for privada ou contiver rotas internas de uso estrito da organização.
* NÃO duplique estruturas de payloads diretamente em anotações de múltiplos controllers. Caso uma estrutura seja compartilhada, defina um schema global em `config/swagger.ts` dentro do objeto `schemas`.
* NÃO documente endpoints de forma puramente manual escrevendo arquivos de especificação OpenAPI monolíticos em YAML ou JSON. Sempre priorize o JSDoc nos controllers e a autogeração baseada em rotas para manter a documentação próxima ao código de execução.
* NÃO permita divergências entre os tipos de retorno do TypeScript declarados ou inferidos nos controllers e as respostas descritas em `@responseBody`.
