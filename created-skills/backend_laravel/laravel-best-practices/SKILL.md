---
name: laravel-best-practices
description: "Use when writing or refactoring Laravel 13 / PHP 8.5 code: controllers, models, migrations, requests, policies, jobs, commands, and Eloquent queries. Covers design consistency, DB performance, caching, security, and N+1 prevention."
license: MIT
metadata: {'author': 'engeapp', 'source': 'laravel/boost — .ai/laravel/skill/laravel-best-practices/SKILL.md'}
---
# Boas Práticas de Laravel

## Objetivo
Use when writing or refactoring Laravel 13 / PHP 8.5 code: controllers, models, migrations, requests, policies, jobs, commands, and Eloquent queries. Covers design consistency, DB performance, caching, security, and N+1 prevention.

Boas práticas para Laravel, priorizadas por impacto. Cada regra ensina o que fazer e por quê. Para a sintaxe exata da API, consulte a documentação da versão instalada (vendor/ ou docs oficiais); se o MCP do Laravel Boost estiver habilitado, use `search-docs`.

## Instruções

### Consistência Primeiro

Antes de aplicar qualquer regra, verifique o que a aplicação já faz. O Laravel oferece múltiplas abordagens válidas — a melhor escolha é aquela que o codebase já utiliza, mesmo que outro padrão fosse teoricamente melhor. Inconsistência é pior que um padrão subótimo.

Verifique arquivos irmãos, controllers, models ou testes relacionados em busca de padrões estabelecidos. Se algum existir, siga-o — não introduza uma segunda forma. Estas regras são defaults para quando ainda não existe um padrão, não substituições.

### Referência Rápida

### 1. Performance de Banco de Dados → `rules/db-performance.md`

- Faça eager load com `with()` para prevenir N+1; `Model::preventLazyLoading()` em dev
- `chunk()`/`cursor()`, colunas selecionadas e índices em `WHERE`/`ORDER BY`/`JOIN`

### 2. Padrões Avançados de Query → `rules/advanced-queries.md`

- Subqueries (`addSelect`, agregados condicionais, `orderBy` correlacionado) em vez de eager-load pesado
- `whereIn`+`pluck()` sobre `whereHas`; duas queries simples podem superar uma complexa

### 3. Segurança → `rules/security.md`

- `$fillable`/`$guarded` em todos os models; autorize toda ação via policies/gates
- Sem SQL bruto com entrada do usuário; `throttle` em auth/API; valide uploads; segredos via `config()`, cast `encrypted`

### 4. Caching → `rules/caching.md`

- `Cache::remember()`/`flexible()`/`memo()` em vez de get/put manual
- Cache tags para invalidar grupos; `Cache::lock()` para condições de corrida

### 5. Padrões Eloquent → `rules/eloquent.md`

- Relacionamentos tipados, local scopes e casts no método `casts()`
- Nunca hardcode nome de tabela — use `(new Model)->getTable()` ou Eloquent
- Pivot via `sync()`/`syncWithoutDetaching()`/`attach()`/`detach()`; eventos de model no `booted()`

### 6. Validação & Formulários → `rules/validation.md`

- Form Requests, nunca validação inline; apenas `$request->validated()`, nunca `$request->all()`
- `Rule::when()` para condicional; `after()` em vez de `withValidator()`

### 7. Configuração → `rules/config.md`

- `env()` apenas em arquivos de config; leia via `config()` no resto da app
- `App::environment()`/`app()->isProduction()` em vez de checar `env()`

### 8. Padrões de Teste → `rules/testing.md`

- `LazilyRefreshDatabase`, factory states/sequences e `assertModelExists()`
- Fakes (`Event::fake()`, etc.) sempre após o setup da factory

### 9. Padrões de Queue & Job → `rules/queue-jobs.md`

- `retry_after` > `timeout`; backoff exponencial; sempre implemente `failed()`
- `ShouldBeUnique` contra duplicatas; `RateLimited` para APIs externas

### 10. Roteamento & Controllers → `rules/routing.md`

- Route model binding implícito; `Route::resource()`/`apiResource()`
- Type-hint de Form Requests; métodos curtos, extraia para `app/Services/`

### 11. HTTP Client → `rules/http-client.md`

- `timeout`/`connectTimeout` e `retry()` com backoff em toda requisição externa
- Verifique status (`throw()`); `Http::fake()`+`preventStrayRequests()` em testes

### 12. Events, Notifications & Mail → `rules/events-notifications.md`, `rules/mail.md`

- Descoberta de events; `afterCommit()` dentro de transações
- Notifications/mailables com `ShouldQueue`; `assertQueued()` para os enfileirados

### 13. Tratamento de Erros → `rules/error-handling.md`

- `report()`/`render()` em classes de exception ou `bootstrap/app.php` — siga o padrão
- `ShouldntReport`/throttle para exceptions de alto volume; contexto via `context()`

### 14. Agendamento de Tarefas → `rules/scheduling.md`

- `withoutOverlapping()` e `onOneServer()` conforme duração/topologia
- `environments()` para restringir; `runInBackground()` para tarefas longas

### 15. Arquitetura → `rules/architecture.md`

- Classes de propósito único em `app/Services/` (o engeapp não usa `app/Actions/`); injeção de dependência sobre o helper `app()`
- `defer()` para pós-resposta; `Context` para dados com escopo de requisição

### 16. Migrations → `rules/migrations.md`

- `make:migration` + `constrained()`; índices na própria migration
- Nunca altere migrations já rodadas em produção; uma preocupação por migration (sem misturar DDL/DML)

### 17. Collections → `rules/collections.md`

- Higher-order messages para operações simples; `cursor()` vs. `lazy()` conforme relações
- `lazyById()` ao atualizar durante iteração; `toQuery()` para operações em massa

### 18. Convenções & Estilo → `rules/style.md`

- Siga as convenções de nomenclatura do Laravel para todas as entidades
- Prefira helpers (`Str`, `Arr`, `Number`, `Uri`, `$request->string()`) sobre funções PHP puras

### 19. Transações & Concorrência → `rules/transactions.md`

- `DB::transaction()` com retry de deadlock; `lockForUpdate()`/`sharedLock()` sempre dentro da transação
- Nunca despache job/evento/chamada de API dentro da transação antes do commit

### 20. Pruning de Model & Retenção → `rules/model-pruning.md`

- **Referência genérica:** o engeapp não usa `Prunable`/`MassPrunable` hoje
- `prunable(): Builder`, hook `pruning()` (só em `Prunable`) e `Schedule::command('model:prune')`

### Como Aplicar

Prefira delegar a leitura dos arquivos de regras a um sub-agent quando forem muitos arquivos ou §, para não inflar o contexto principal — carregue no fluxo principal apenas as regras da(s) seção(ões) que a tarefa exige.

1. Identifique o tipo de arquivo e selecione as seções relevantes (ex.: migration → §16, controller → §1, §3, §5, §6, §10)
2. Verifique arquivos irmãos em busca de padrões existentes — siga-os primeiro, conforme Consistência Primeiro
3. Verifique a sintaxe da API na documentação da versão do Laravel instalada; se o MCP do Laravel Boost estiver habilitado, use `search-docs`

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
