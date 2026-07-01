---
name: adonisjs-best-practices
description: Use when creating, reviewing, or refactoring AdonisJS backend code, including controllers, models, routes, middleware, and services. Triggers on requests involving the AdonisJS framework, backend logic in Node.js, routing, and database interactions using Lucid ORM.
---

# Melhores Práticas do AdonisJS

## Objetivo
Estabelecer padrões sólidos e padronizados para o desenvolvimento, estruturação e manutenção de aplicações backend em Node.js utilizando o framework AdonisJS v6 no ecossistema Engeapp.

## Instruções

### 1. Definição de Rotas (`start/routes.ts`)
* Importe o roteador de `@adonisjs/core/services/router`:
  ```typescript
  import router from '@adonisjs/core/services/router'
  ```
* Sempre utilize importações dinâmicas para controllers a fim de habilitar o lazy loading:
  ```typescript
  const UsersController = () => import('#controllers/users_controller')
  ```
* Agrupe rotas relacionadas usando `router.group()` e defina prefixos lógicos de caminho:
  ```typescript
  router.group(() => {
    router.get('/users', [UsersController, 'index']).as('users.index')
  }).prefix('/api')
  ```
* Sempre atribua nomes às rotas utilizando o método `.as('nome')` para permitir a resolução segura de rotas.
* **Geração de URL server-side:** dentro de controllers, services ou jobs, use o router nativo do AdonisJS para gerar URLs (emails, notificações, redirects, links em respostas de API). NÃO existe Ziggy neste projeto — Ziggy é nativo do Laravel e foi descontinuado.
  ```typescript
  import router from '@adonisjs/core/services/router'

  const url = router.makeUrl('clients.show', [42]) // → '/clients/42'
  // ou, com params nomeados explícitos:
  // const url = router.makeUrl('clients.show', { params: { id: 42 } })
  ```
* Utilize o helper de middleware de `#start/kernel` para proteger rotas:
  ```typescript
  import { middleware } from '#start/kernel'
  
  router.get('/dashboard', [DashboardController, 'index'])
    .as('dashboard')
    .use(middleware.auth())
  ```

### 2. Desenvolvimento de Controllers (`app/controllers/`)
* Controllers devem lidar apenas com o parsing da requisição, formatação da resposta e delegação para as camadas de domínio/negócio.
* Sempre desestruture o parâmetro `HttpContext` nos métodos de ação:
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'

  export default class UsersController {
    async index({ request, response }: HttpContext) {
      // Lógica aqui
    }
  }
  ```
* Retorne objetos de resposta semânticos utilizando os métodos auxiliares:
  * Sucesso: `return response.json(data)`
  * Bad Request: `return response.badRequest({ message: 'Mensagem de erro' })`
  * Validação/Unprocessable: `return response.unprocessableEntity({ message: 'Validação falhou' })`
  * Erro Interno do Servidor: `return response.internalServerError({ message: 'Algo deu errado' })`

### 3. Lucid ORM e Models (`app/models/`)
* Utilize decoradores do ES7 para definir colunas e relacionamentos.
* Tipifique explicitamente as propriedades da classe com `declare`:
  ```typescript
  import { BaseModel, column } from '@adonisjs/lucid/orm'

  export default class User extends BaseModel {
    @column({ isPrimary: true })
    declare id: string

    @column()
    declare email: string
  }
  ```
* Defina explicitamente o nome da tabela: `static table = 'users'`.
* Para chaves primárias customizadas como ULIDs, defina `static selfAssignPrimaryKey = true` e utilize o gancho `@beforeCreate`:
  ```typescript
  import { beforeCreate } from '@adonisjs/lucid/orm'
  import { ulid } from 'ulid'

  @beforeCreate()
  static assignUlid(model: User) {
    if (!model.id) model.id = ulid()
  }
  ```
* Gerencie relacionamentos utilizando tipos explícitos:
  ```typescript
  import { belongsTo } from '@adonisjs/lucid/orm'
  import type { BelongsTo } from '@adonisjs/lucid/types/relations'
  import SolarCompany from '#models/solar_company'

  @belongsTo(() => SolarCompany, { foreignKey: 'solarCompanyId' })
  declare solarCompany: BelongsTo<typeof SolarCompany>
  ```
* Evite consultas SQL brutas (raw queries) sempre que possível; dê preferência ao construtor de consultas do Lucid ORM.

### 4. Validação com VineJS (`app/validators/` ou inline)
* Importe `vine` de `@vinejs/vine`.
* Compile os schemas de validação fora do ciclo de tratamento de requisições para maximizar a performance:
  ```typescript
  import vine from '@vinejs/vine'

  const createUserValidator = vine.compile(
    vine.object({
      email: vine.string().email(),
      password: vine.string().minLength(6),
    })
  )
  ```
* Execute a validação usando `request.validateUsing()`:
  ```typescript
  const payload = await request.validateUsing(createUserValidator)
  ```

### 5. Importações de Dependências e Aliases
* Utilize importações via aliases (subpaths) configurados em vez de caminhos relativos com vários níveis de `../`:
  * `#controllers/*` para Controllers
  * `#models/*` para Models
  * `#services/*` para Serviços
  * `#start/*` para Configurações de inicialização

## Restrições
* NÃO utilize referências de controllers baseadas em string antigas nas rotas (ex: `'UsersController.index'`). Utilize apenas importações dinâmicas com o padrão de tupla `[UsersController, 'index']`.
* NÃO execute lógica de negócios complexa ou integrações com APIs externas diretamente nos controllers. Implemente-as em Serviços ou na lógica de Domínio.
* NÃO ignore a validação de entrada. Sempre valide o payload das requisições de entrada utilizando o VineJS.
* NÃO escreva instruções SQL brutas (raw SQL) no código sem aprovação; aproveite a API fluente do Lucid ORM.
* NÃO utilize importações relativas padrão (`../../`) para classes dentro da pasta app; utilize sempre `#models/*` ou outras importações de subpath configuradas.
