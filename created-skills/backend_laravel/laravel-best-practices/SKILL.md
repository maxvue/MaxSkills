---
name: laravel-best-practices
description: "Aplique ao escrever, revisar ou refatorar código Laravel 13 / PHP 8.4: controllers, models, migrations, form requests, policies, jobs, comandos agendados, service classes e queries Eloquent. Aciona em performance de queries e N+1, cache, autorização e segurança, validação, tratamento de erros, filas, rotas e decisões de arquitetura. Também para code reviews e refatoração Laravel."
license: MIT
metadata:
  author: engeapp
---

# Boas Práticas de Laravel

Boas práticas para Laravel, priorizadas por impacto. Cada regra ensina o que fazer e por quê. Para a sintaxe exata da API, verifique com `search-docs`.

## Consistência Primeiro

Antes de aplicar qualquer regra, verifique o que a aplicação já faz. O Laravel oferece múltiplas abordagens válidas — a melhor escolha é aquela que o codebase já utiliza, mesmo que outro padrão fosse teoricamente melhor. Inconsistência é pior que um padrão subótimo.

Verifique arquivos irmãos, controllers, models ou testes relacionados em busca de padrões estabelecidos. Se algum existir, siga-o — não introduza uma segunda forma. Estas regras são defaults para quando ainda não existe um padrão, não substituições.

## Referência Rápida

### 1. Performance de Banco de Dados → `rules/db-performance.md`

- Faça eager load com `with()` para prevenir queries N+1
- Habilite `Model::preventLazyLoading()` em desenvolvimento
- Selecione apenas as colunas necessárias, evite `SELECT *`
- `chunk()` / `chunkById()` para grandes conjuntos de dados
- Indexe colunas usadas em `WHERE`, `ORDER BY`, `JOIN`
- `withCount()` em vez de carregar relações para contar
- `cursor()` para iteração somente-leitura com uso eficiente de memória
- Nunca faça queries em templates Blade

### 2. Padrões Avançados de Query → `rules/advanced-queries.md`

- Subqueries com `addSelect()` em vez de eager-loading de um has-many inteiro para um único valor
- Relacionamentos dinâmicos via FK em subquery + `belongsTo`
- Agregados condicionais (`CASE WHEN` em `selectRaw`) em vez de múltiplas queries de count
- `setRelation()` para prevenir queries N+1 circulares
- `whereIn` + `pluck()` em vez de `whereHas` para melhor uso de índices
- Duas queries simples podem superar uma query complexa
- Índices compostos que correspondam à ordem das colunas do `orderBy`
- Subqueries correlacionadas no `orderBy` para ordenação de has-many (evite joins)

### 3. Segurança → `rules/security.md`

- Defina `$fillable` ou `$guarded` em todos os models, autorize toda ação via policies ou gates
- Nenhum SQL bruto com entrada do usuário — use Eloquent ou o query builder
- `{{ }}` para escape de saída, `@csrf` em todos os forms POST/PUT/DELETE, `throttle` nas rotas de autenticação e de API
- Valide MIME type, extensão e tamanho para uploads de arquivos
- Nunca faça commit do `.env`, use `config()` para segredos, cast `encrypted` para campos sensíveis do banco

### 4. Caching → `rules/caching.md`

- `Cache::remember()` em vez de get/put manual
- `Cache::flexible()` para stale-while-revalidate em dados de alto tráfego
- `Cache::memo()` para evitar hits de cache redundantes dentro de uma requisição
- Cache tags para invalidar grupos relacionados
- `Cache::add()` para escritas condicionais atômicas
- `once()` para memoizar por requisição ou por tempo de vida do objeto
- `Cache::lock()` / `lockForUpdate()` para condições de corrida
- Failover de stores de cache em produção

### 5. Padrões Eloquent → `rules/eloquent.md`

- Tipos de relacionamento corretos com type hints de retorno
- Local scopes para restrições de query reutilizáveis
- Global scopes com parcimônia — documente sua existência
- Casts de atributos no método `casts()`
- Faça cast de colunas de data, use instâncias Carbon em templates
- `whereBelongsTo($model)` para queries mais limpas
- Nunca escreva nomes de tabela hardcoded — use `(new Model)->getTable()` ou queries Eloquent

### 6. Validação & Formulários → `rules/validation.md`

- Classes Form Request, não validação inline
- Notação de array `['required', 'email']` para código novo; siga a convenção existente
- Apenas `$request->validated()` — nunca `$request->all()`
- `Rule::when()` para validação condicional
- `after()` em vez de `withValidator()`

### 7. Configuração → `rules/config.md`

- `env()` apenas dentro de arquivos de config
- `App::environment()` ou `app()->isProduction()`
- Config, arquivos de lang e constantes em vez de texto hardcoded

### 8. Padrões de Teste → `rules/testing.md`

- `LazilyRefreshDatabase` em vez de `RefreshDatabase` por velocidade
- `assertModelExists()` em vez de `assertDatabaseHas()` bruto
- Factory states e sequences em vez de overrides manuais
- Use fakes (`Event::fake()`, `Exceptions::fake()`, etc.) — mas sempre após o setup da factory, não antes
- `recycle()` para compartilhar instâncias de relacionamento entre factories

### 9. Padrões de Queue & Job → `rules/queue-jobs.md`

- `retry_after` deve exceder o `timeout` do job; use backoff exponencial `[1, 5, 10]`
- `ShouldBeUnique` para prevenir duplicatas; `ShouldBeUniqueUntilProcessing` para liberação antecipada do lock
- Sempre implemente `failed()`; com `retryUntil()`, defina `$tries = 0`
- Middleware `RateLimited` para chamadas a APIs externas; `Bus::batch()` para jobs relacionados
- Horizon para cenários complexos de múltiplas filas

### 10. Roteamento & Controllers → `rules/routing.md`

- Route model binding implícito
- Scoped bindings para recursos aninhados
- `Route::resource()` ou `apiResource()`
- Métodos com menos de 10 linhas — extraia para actions/services
- Type-hint de Form Requests para auto-validação

### 11. HTTP Client → `rules/http-client.md`

- `timeout` e `connectTimeout` explícitos em toda requisição
- `retry()` com backoff exponencial para APIs externas
- Verifique o status da resposta ou use `throw()`
- `Http::pool()` para requisições independentes concorrentes
- `Http::fake()` e `preventStrayRequests()` em testes

### 12. Events, Notifications & Mail → `rules/events-notifications.md`, `rules/mail.md`

- Descoberta de events em vez de registro manual; `event:cache` em produção
- `ShouldDispatchAfterCommit` / `afterCommit()` dentro de transações
- Enfileire notifications e mailables com `ShouldQueue`
- Notifications on-demand para destinatários que não são usuários
- `HasLocalePreference` em models notificáveis
- `assertQueued()` e não `assertSent()` para mailables enfileirados
- Mailables em Markdown para e-mails transacionais

### 13. Tratamento de Erros → `rules/error-handling.md`

- `report()`/`render()` em classes de exception ou em `bootstrap/app.php` — siga o padrão existente
- `ShouldntReport` para exceptions que nunca devem ser logadas
- Faça throttle de exceptions de alto volume para proteger os sinks de log
- `dontReportDuplicates()` para cenários de múltiplos catch
- Force renderização em JSON para rotas de API
- Contexto estruturado via `context()` em classes de exception

### 14. Agendamento de Tarefas → `rules/scheduling.md`

- `withoutOverlapping()` em tarefas de duração variável
- `onOneServer()` em deployments multi-servidor
- `runInBackground()` para tarefas longas concorrentes
- `environments()` para restringir aos ambientes apropriados
- `takeUntilTimeout()` para processamento com limite de tempo
- Grupos de schedule para configuração compartilhada

### 15. Arquitetura → `rules/architecture.md`

- Classes Action de propósito único; injeção de dependência em vez do helper `app()`
- Prefira pacotes oficiais do Laravel e siga as convenções, não sobrescreva os defaults
- Padrão de `ORDER BY id DESC` ou `created_at DESC`; `mb_*` para segurança com UTF-8
- `defer()` para trabalho pós-resposta; `Context` para dados com escopo de requisição; `Concurrency::run()` para execução paralela

### 16. Migrations → `rules/migrations.md`

- Gere migrations com `php artisan make:migration`
- `constrained()` para chaves estrangeiras
- Nunca modifique migrations que já rodaram em produção
- Adicione índices na migration, não como algo posterior
- Espelhe os defaults de colunas em `$attributes` do model
- `down()` reversível por padrão; migrations de forward-fix para migrations intencionalmente irreversíveis
- Uma preocupação por migration — nunca misture DDL e DML

### 17. Collections → `rules/collections.md`

- Higher-order messages para operações simples de collection
- `cursor()` vs. `lazy()` — escolha com base nas necessidades de relacionamento
- `lazyById()` ao atualizar registros durante a iteração
- `toQuery()` para operações em massa sobre collections

### 18. Blade & Views → `rules/blade-views.md`

- `$attributes->merge()` em templates de componentes
- Componentes Blade em vez de `@include`; `@pushOnce` para scripts por componente
- View Composers para dados de view compartilhados
- `@aware` para props de componentes profundamente aninhados

### 19. Convenções & Estilo → `rules/style.md`

- Siga as convenções de nomenclatura do Laravel para todas as entidades
- Prefira helpers do Laravel (`Str`, `Arr`, `Number`, `Uri`, `Str::of()`, `$request->string()`) em vez de funções PHP puras
- Sem JS/CSS em Blade, sem HTML em classes PHP
- O código deve ser legível; comentários apenas para arquivos de config

## Como Aplicar

Prefira delegar a leitura dos arquivos de regras a um sub-agent quando forem muitos arquivos ou §, para não inflar o contexto principal — carregue no fluxo principal apenas as regras da(s) seção(ões) que a tarefa exige.

1. Identifique o tipo de arquivo e selecione as seções relevantes (ex.: migration → §16, controller → §1, §3, §5, §6, §10)
2. Verifique arquivos irmãos em busca de padrões existentes — siga-os primeiro, conforme Consistência Primeiro
3. Verifique a sintaxe da API com `search-docs` para a versão do Laravel instalada

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
