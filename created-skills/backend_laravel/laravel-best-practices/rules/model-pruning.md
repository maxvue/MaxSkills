# Pruning de Model e Retenção de Dados

> **Referência genérica do framework — sem uso no engeapp.** Nenhum model do projeto usa as traits
> `Prunable`/`MassPrunable` nem o comando `model:prune` hoje. Aplique ao introduzir uma política de
> retenção nova, não como padrão já instalado.

## Escolhendo a Trait

- `Prunable` — quando o model tem recursos associados que exigem limpeza via eventos do model ou
  observers (ex.: deletar arquivos do Spatie MediaLibrary, despachar jobs de limpeza em
  `deleting`/`deleted`).
- `MassPrunable` — ao deletar grandes volumes onde a performance é crítica e não são necessários
  eventos do model, observers ou limpezas em cascata.

## Definindo `prunable()`

Sempre declare o tipo de retorno. Retorne um query builder com o critério de registros obsoletos.

```php
public function prunable(): Builder
{
    // Remove registros com mais de 3 meses
    return static::where('created_at', '<=', now()->subMonths(3));
}
```

## Hook `pruning()` (apenas com `Prunable`)

Opcionalmente defina `pruning(): void`, chamado antes de CADA model ser podado, para efeitos
colaterais/limpeza:

```php
public function pruning(): void
{
    // Remove o arquivo físico antes de apagar a linha
    Storage::disk('s3')->delete($this->file_path);
}
```

A trait `MassPrunable` também usa `prunable()`, mas NÃO invoca o hook `pruning()` por model.

## Agendamento

Em `routes/console.php`:

```php
Schedule::command('model:prune')->dailyAt('03:00');
```

- Indexe as colunas usadas em `prunable()` (tipicamente `created_at`) para evitar full-table scans.
- Use `--chunk` em tabelas enormes para evitar esgotamento de memória ou locks prolongados.
- NÃO agende pruning intensivo durante o horário comercial de pico.
- NÃO use `Prunable` em models que apagam milhares de registros diariamente sem necessidade de
  eventos — use `MassPrunable`.
