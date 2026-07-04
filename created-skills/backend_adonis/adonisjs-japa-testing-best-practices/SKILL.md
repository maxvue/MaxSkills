---
name: adonisjs-japa-testing-best-practices
description: Use when creating, reviewing, or refactoring automated tests in AdonisJS v6 with the Japa framework — unit and functional tests, test.group lifecycle hooks, the HTTP client and loginAs auth, asserting status/body, faking mail and the emitter, and isolating the test database via testUtils.db() migrations/truncation. Triggers on .spec.ts files, `node ace test`, mocking external services, and PostgreSQL test-data cleanup.
---

# Melhores Práticas de Teste com Japa no AdonisJS

## Objetivo
Estabelecer padrões consistentes e robustos para a escrita de testes automatizados (unitários e funcionais) em aplicações AdonisJS v6 utilizando o framework de testes Japa.

## Instruções

### 1. Estrutura de Suites e Arquivos de Teste
* Coloque os arquivos de teste nas pastas corretas em `tests/`:
  * Testes Unitários: `tests/unit/**/*.spec.ts` (Para regras de negócio puras, classes utilitárias e serviços isolados)
  * Testes Funcionais: `tests/functional/**/*.spec.ts` (Para rotas, requisições HTTP, middlewares, controllers e APIs)
* Utilize o sufixo `.spec.ts` para todos os arquivos de teste.
* Execute os testes pelo Ace CLI usando: `node ace test` ou filtre testes específicos com `node ace test --files=tests/functional/leads.spec.ts`.

### 2. Agrupamento de Testes e Ciclo de Vida (Lifecycles)
* Envolva os testes em um grupo nomeado usando `test.group()`:
  ```typescript
  import { test } from '@japa/runner'

  test.group('Nome do Grupo', (group) => {
    // Testes aqui
  })
  ```
* Gerencie a lógica de setup e teardown de forma limpa no grupo através de hooks de ciclo de vida (`setup`, `teardown`, `each.setup`, `each.teardown`).
* Prefira retornar uma função de limpeza (cleanup) diretamente no hook `setup` em vez de separar setup e teardown, garantindo a higiene dos dados:
  ```typescript
  group.setup(async () => {
    const user = await User.create({ name: 'Usuário Teste', email: 'test@example.com', password: 'password' })

    // Retorna a função de limpeza que será executada ao final do grupo
    return async () => {
      await User.query().where('id', user.id).delete()
    }
  })
  ```

### 3. Testes Funcionais (Requisições HTTP)
* Desestruture a propriedade `{ client: http }` do contexto do teste para fazer requisições HTTP contra a aplicação.
* Desestruture `{ assert }` para realizar asserções na resposta:
  ```typescript
  test('retorna status 200 e lista de entidades', async ({ client: http, assert }) => {
    const response = await http.get('/api/v1/entities')
    
    response.assertStatus(200)
    assert.isArray(response.body())
  })
  ```
* Para endpoints autenticados, utilize o helper `loginAs(user)` integrado com o cliente do Japa/AdonisJS para simular usuários logados:
  ```typescript
  test('retorna perfil privado do usuário', async ({ client: http }) => {
    const user = await User.first()
    const response = await http.get('/api/v1/profile').loginAs(user)
    
    response.assertStatus(200)
  })
  ```

### 4. Interações com Banco de Dados e Isolamento
* Use sempre um banco de dados de teste dedicado (PostgreSQL), separado do banco de desenvolvimento. Configure-o via `NODE_ENV=test`/`.env.test`. NUNCA rode testes contra o banco de desenvolvimento.
* Garanta o isolamento global no `tests/bootstrap.ts` usando os utilitários do Adonis em vez de limpeza manual:
  ```typescript
  import testUtils from '@adonisjs/core/services/test_utils'

  export const runnerHooks = {
    setup: [
      // Roda as migrations antes da suite e faz rollback ao final
      () => testUtils.db().migrate(),
    ],
    teardown: [],
  }
  ```
* Para resetar dados entre testes/grupos, prefira `testUtils.db().truncate()` (trunca todas as tabelas, preservando o schema) ou `testUtils.db().withGlobalTransaction()` em vez de `delete()` manual tabela por tabela:
  ```typescript
  group.each.setup(() => testUtils.db().truncate())
  ```
* Aliases de Importação: Sempre importe models e serviços utilizando aliases configurados (ex: `#models/user`, `#services/some_service`).

### 5. Mocking e Stubbing (Simulações)
* Para APIs externas, disparos de e-mail ou agentes de IA de terceiros, utilize mocks ou fakes para manter os testes rápidos, previsíveis e desacoplados de serviços externos.
* Use fakes integrados do framework (no Adonis v6 a API é em camelCase, via serviços do container): `mail.fake()` (de `@adonisjs/mail/services/main`) e `emitter.fake()` (de `@adonisjs/core/services/emitter`) para validar os efeitos colaterais sem de fato enviar e-mails ou disparar handlers de eventos:
  ```typescript
  import mail from '@adonisjs/mail/services/main'
  import emitter from '@adonisjs/core/services/emitter'

  const mails = mail.fake()
  const events = emitter.fake()
  // ... ação que dispara e-mail/evento
  mails.assertSent(VerifyEmail)
  events.assertEmitted('user:registered')
  // Restaure ao final
  mail.restore()
  emitter.restore()
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO rode testes contra o banco de desenvolvimento; use sempre o banco de teste dedicado com isolamento via `testUtils.db()` (migrate/truncate/transaction global).
* NÃO utilize importações relativas padrão (`../../`) para classes dentro da pasta app; utilize sempre `#models/*`, `#services/*` ou outras importações de subpath configuradas.
* NÃO ignore testes de cenários de erro. Sempre escreva asserções para validações e falhas (ex: 400 Bad Request, 422 Unprocessable Entity, 401 Unauthorized, 404 Not Found).
* NÃO teste múltiplos recursos não relacionados em um único caso de teste. Mantenha cada teste focado e de propósito único.
