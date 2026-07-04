---
name: laravel-database-eloquent-best-practices
description: Use when writing, refactoring, or reviewing Laravel Eloquent queries, database migrations, indexing strategy, handling relationships, scopes, database transactions, concurrency optimization, or configuring model pruning and data retention policies.
---

# Boas Práticas de Eloquent e Banco de Dados no Laravel

## Objetivo
Estabelecer diretrizes robustas e padrões estruturados para otimizar consultas Eloquent, prevenir consultas N+1, usar scopes, lidar com transações e concorrência, e executar operações de banco de dados de alta performance dentro do ecossistema Engeapp.

## Instruções

### 1. Otimização de Consultas e Eager Loading
- **Prevenir Consultas N+1**: Sempre carregue as relações necessárias usando `with()`, `load()` ou `loadMissing()`.
- **Colunas Seletivas**: Especifique apenas as colunas necessárias para manter o uso de memória baixo, incluindo a chave primária e a chave estrangeira (ex: `Project::with('client:id,name,email')->get()`).
- **Eager Loading com Restrições**: Passe uma closure para moldar/filtrar as relações carregadas, ex: `User::with(['posts' => fn ($q) => $q->latest()->where('published', true)])`. Selecione apenas as colunas necessárias na consulta da relação também.
- **Paginação e Carregamento em Lote**: NÃO use `all()` ou `get()` em tabelas com grandes volumes. Use `paginate()`, `cursorPaginate()`, `chunk()`/`chunkById()`, `lazy()` ou `cursor()`. Prefira `chunkById()` em vez de `chunk()` quando o callback altera as linhas sendo iteradas (evita registros pulados).
- **Operações em Massa a Nível de Banco de Dados**: NÃO carregue uma collection na memória apenas para atualizá-la em um loop. Use uma única consulta: `Post::where('status', 'draft')->update(['status' => 'archived'])`. Use `increment()`/`decrement()` para contadores em vez de read-modify-write.
- **Subqueries e Agregações**: Use `addSelect()` para subqueries. Use `withCount()`, `withSum()`, `withMax()` ou `withExists()` em vez de carregar collections completas para verificar existência, contar ou agregar.
- **Strict Loading**: Garanta que `Model::preventLazyLoading(! app()->isProduction())` esteja configurado.
- **Jobs**: Lembre-se de que models passados para Jobs perdem as relações carregadas. Chame `$this->model->loadMissing(...)` dentro do `handle()`.
- **Indexação Estratégica**: Defina índices em colunas frequentemente usadas em `where`, `orderBy`, `join` ou restrições de chave estrangeira nas migrations. Adicione índices compostos para filtros comuns de múltiplas colunas (ex: `$table->index(['status', 'published_at'])`).

### 2. Definições e Carregamento de Relações
- **Métodos de Relação Tipados**: Sempre declare o tipo de retorno nos métodos de relação (`: BelongsTo`, `: HasMany`, `: BelongsToMany`, etc.) para suporte a IDE/análise estática.
- **Filtrar por Existência de Relação**: Use `has()` / `whereHas()` (e `doesntHave()` / `whereDoesntHave()`) para restringir por registros relacionados em vez de carregar e filtrar no PHP.
- **Sincronização de Pivot / Muitos-para-Muitos**: Use `sync([...])` para uma substituição atômica, `syncWithoutDetaching([...])` para adicionar sem remover os vínculos existentes, e `attach()`/`detach()` para linhas de pivot individuais.
- **Consistência**: Mantenha os nomes das relações semânticos e pluralizados quando apropriado (`comments()` para `hasMany`, `author()` para `belongsTo`).

### 3. Configuração do Model: Mass Assignment, Casts e Eventos
- **Proteção contra Mass Assignment**: Sempre defina `$fillable` (whitelist, preferível) ou `$guarded`. NUNCA use `protected $guarded = []` — isso expõe todas as colunas ao mass assignment.
- **Casts de Atributos**: Declare `$casts` (ou o método `casts()` no Laravel 11+) para segurança de tipos — `datetime`, `array`, `boolean`, `integer`, `encrypted`, casts de enum, etc. Isso evita parsing manual e mantém os tipos consistentes.
- **Eventos do Model**: Registre hooks de ciclo de vida no `booted()` (`creating`, `saving`, `deleting`, ...) para atributos derivados ou limpeza em cascata, ex: geração de slug no `creating` ou limpeza de filhos no `deleting`. Para lógica pesada ou transversal, extraia para um Observer dedicado em vez de closures inline.

### 4. Scopes do Eloquent e Filtragem Dinâmica
- **Local Scopes**: Prefixe os métodos com `scope` (ex: `scopeUnread`), tipe `$query` como `Illuminate\Database\Eloquent\Builder` e declare explicitamente o tipo de retorno `: Builder`. Ou use o atributo `#[Scope]` (introduzido no Laravel 12).
- **Documentação**: Escreva blocos PHPDoc claros acima dos scopes em **português brasileiro (pt-BR)**.
- **Dynamic Scopes**: Aceite parâmetros após o argumento `$query` para customizar as restrições.
- **Global Scopes**: Defina no `booted()` usando `static::addGlobalScope` ou extraia para classes dedicadas.
- **Padrão de Filtragem**: Substitua longos blocos `if`/`switch` nos controllers por scopes de filtro dinâmicos no model usando o helper `when()`.
- **Restrições**: NÃO execute métodos de terminação (`get()`, `first()`, `paginate()`) dentro de métodos de scope. NÃO omita os type-hints.

### 5. Transações de Banco de Dados e Locks de Concorrência
- **Transações Automáticas**: Use `DB::transaction()` como padrão. Ela lida com `commit`/`rollback` e permite especificar tentativas de retry.
- **Transações Manuais**: Use `DB::beginTransaction()`, `DB::commit()` e `DB::rollBack()` apenas para fluxos complexos. Sempre envolva em `try-catch`.
- **Locking Pessimista**: Use `lockForUpdate()` (Exclusivo) para impedir que linhas sejam modificadas ou selecionadas com shared lock. Use `sharedLock()` para impedir modificações mas permitir leitura. Sempre use dentro de transações.
- **Retries de Deadlock**: Especifique uma contagem de retry como segundo argumento em `DB::transaction(..., 3)`.
- **Ações Pós-Commit**: Nunca despache queue jobs, dispare eventos ou chame APIs externas dentro de um bloco de transação antes que ele faça commit. Use a propriedade ou método `afterCommit` nos Jobs.

### 6. Execução Concorrente
- **Processamento Paralelo**: Use `Concurrency::run` para executar um array de closures em paralelo. Use `Concurrency::defer` para tarefas fire-and-forget.
- **Drivers**: Especifique explicitamente o driver (`process`, `fork`, `sync`) via `Concurrency::driver()`.
- **Timeouts**: Sempre imponha timeouts estritos em tarefas concorrentes (`timeout: 10`).
- **Tratamento de Exceções**: Envolva os blocos em `try-catch` capturando `Illuminate\Concurrency\Exceptions\ExecutionException`.
- **Gerenciamento de Estado**: Não altere propriedades de classe ou singletons dentro das closures. Closures serializam variáveis; mantenha os escopos importados pequenos (passe IDs escalares, não models Eloquent).
- **Restrições**: NUNCA modifique variáveis estáticas ou o estado de configuração da app dentro das closures. NUNCA execute transações de banco de dados envolvendo uma chamada `Concurrency::run`.

### 7. Pruning de Model e Retenção de Dados
- **Escolhendo a Trait Correta**:
  - Use `Prunable` quando o model tiver recursos associados que exigem limpeza via eventos do model ou observers (ex: deletar arquivos do Spatie MediaLibrary, despachar jobs de limpeza em `deleting`/`deleted`).
  - Use `MassPrunable` ao deletar grandes volumes de dados onde a performance é crítica e não são necessários eventos do model, observers ou limpezas em cascata.
- **Definindo o Método `prunable`**: Sempre declare o tipo de retorno (`: Builder`). Retorne um query builder definindo os critérios de registros obsoletos.
  ```php
  public function prunable(): Builder
  {
      return static::where('created_at', '<=', now()->subMonths(3));
  }
  ```
- **Hook de Pruning** (apenas com `Prunable`): Opcionalmente defina um método `pruning(): void`, chamado antes de CADA model ser podado, para efeitos colaterais/limpeza (ex: `Storage::disk('s3')->delete($this->file_path)`). A trait `MassPrunable` também usa `prunable()` mas NÃO invoca o hook `pruning()` por model.
- **Agendamento em `routes/console.php`**: Execute `Schedule::command('model:prune')->daily()`. Para tabelas com volume extremo, agende em horários de baixo movimento: `->dailyAt('03:00')`.
- **Otimização de Banco de Dados**: Indexe as colunas usadas em `prunable()` (tipicamente `created_at`) para evitar full-table scans. Use `--chunk` para tabelas enormes para evitar esgotamento de memória ou locks prolongados.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO execute consultas dentro de loops.
- NÃO escreva comentários a nível de classe ou descrições de scope em inglês. Sempre use pt-BR.
- Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em português brasileiro (pt-BR).
- NÃO use `Prunable` em models que deletam milhares de registros diariamente sem necessidade de eventos — use `MassPrunable` em vez disso.
- NÃO agende comandos de pruning intensivos durante o horário comercial de pico.
