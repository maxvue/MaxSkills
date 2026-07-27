# Transações de Banco de Dados e Concorrência

## Prefira `DB::transaction()`

`DB::transaction()` cuida do `commit`/`rollBack` automaticamente e aceita uma contagem de tentativas
para casos de deadlock.

```php
// Executa o bloco e refaz até 3 vezes em caso de deadlock
DB::transaction(function () use ($project) {
    $project->update(['status' => 'approved']);
    $project->protocol()->create(['number' => $number]);
}, 3);
```

Use `DB::beginTransaction()` / `DB::commit()` / `DB::rollBack()` apenas em fluxos complexos que
precisem de controle manual — e sempre dentro de `try-catch`:

```php
DB::beginTransaction();

try {
    // ... operações
    DB::commit();
} catch (\Throwable $e) {
    DB::rollBack();

    throw $e;
}
```

## Locking Pessimista

Sempre dentro de uma transação:

- `lockForUpdate()` — lock exclusivo: impede que as linhas sejam modificadas ou selecionadas com
  shared lock por outras conexões.
- `sharedLock()` — impede modificações, mas permite leitura concorrente.

```php
DB::transaction(function () {
    $balance = Wallet::where('user_id', $userId)->lockForUpdate()->first();

    $balance->decrement('amount', $value);
});
```

## Nunca dispare efeitos externos antes do commit

NUNCA despache queue jobs, dispare eventos ou chame APIs externas dentro do bloco da transação antes
que ela faça commit — o worker pode processar o job antes de os dados existirem, e uma chamada
externa não pode ser desfeita pelo rollback.

```php
// Incorreto
DB::transaction(function () use ($project) {
    $project->save();

    ProcessProject::dispatch($project); // pode rodar antes do commit
});

// Correto
DB::transaction(function () use ($project) {
    $project->save();
});

ProcessProject::dispatch($project);
```

Alternativamente, use `afterCommit` no Job (propriedade `$afterCommit = true` ou
`->afterCommit()` no dispatch) e `ShouldDispatchAfterCommit` em events — ver
`rules/events-notifications.md` e `rules/mail.md`.

## Execução Concorrente (referência genérica do framework — sem uso no engeapp)

> Nenhum model ou serviço do engeapp usa `Concurrency::` atualmente. Trate como orientação genérica
> do Laravel, não como padrão verificável do projeto.

- `Concurrency::run` executa um array de closures em paralelo; `Concurrency::defer` para tarefas
  fire-and-forget.
- Especifique o driver explicitamente via `Concurrency::driver()` (`process`, `fork`, `sync`).
- Imponha timeouts estritos (`timeout: 10`).
- Capture `\Throwable`: NÃO existe classe de exceção dedicada de concorrência no Laravel 13 — o
  `ProcessDriver` lança uma `\Exception` genérica (falha de processo/exit code) ou relança a própria
  classe de exceção serializada da closure filha. Inspecione a mensagem/tipo real, não uma
  `ExecutionException`.
- Closures serializam as variáveis importadas: passe IDs escalares, não models Eloquent, e mantenha
  o escopo pequeno.
- NUNCA altere variáveis estáticas, singletons ou estado de configuração dentro das closures.
- NUNCA execute transações de banco de dados envolvendo uma chamada `Concurrency::run`.
