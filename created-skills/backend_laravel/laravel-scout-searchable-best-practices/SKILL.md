---
name: laravel-scout-searchable-best-practices
description: Use ao criar, revisar ou otimizar busca textual (Laravel Scout + Meilisearch) no engeapp. Cobre a trait HasScoutMeilisearch (que gera toSearchableArray automaticamente via data_get), as propriedades $scout_searchable/$scout_filterable/$scout_stop_words, o registro de índices via meilisearchSettings::getSettings() e buscas com ->query() + macro searchSafe() (fallback LIKE).
---

# Objetivo
Padronizar busca textual rápida com Laravel Scout + Meilisearch no engeapp seguindo as abstrações reais do projeto: a trait `App\Traits\HasScoutMeilisearch`, as propriedades de configuração por model e a macro `searchSafe()`. Evite reimplementar `Searchable` cru — o projeto já tem uma camada própria que você deve reusar.

# Como o projeto faz (verdade-base)

## 1. Trait central: `HasScoutMeilisearch`
Todo model pesquisável usa `App\Traits\HasScoutMeilisearch` (não `Laravel\Scout\Searchable` diretamente). A trait já faz `use Searchable` internamente e fornece:

- `toSearchableArray()` pronto: percorre as chaves de `getScoutMeilisearchArray('array')`, resolve cada valor com `data_get($this, $key)`, faz `json_encode` de valores não-string, troca `.` por `_` nas chaves e força `id` como string. Por isso **você normalmente NÃO sobrescreve `toSearchableArray()`** — apenas declara as propriedades abaixo.
- `meilisearchSettings()`: retorna os `searchableAttributes`/`filterableAttributes`/`sortableAttributes`/`stopWords` do índice, consumido em `config/scout.php`.

Models reais que adotam a trait: `App\Models\Leads\Lead`, `App\Models\User`, `App\Models\SupportChat\SupportMessage`, `App\Models\SupportChat\SupportContact`, `App\Models\Client\Client`, `App\Models\Lists\City`.

## 2. Configuração do índice por propriedades no model
Em vez de montar payload manual, declare arrays no model. A trait combina esses arrays com os defaults (`id`, `created_at`, `updated_at`) e com campos padrão que existirem em `fillable`/`casts`/`hidden`/`appends`:

```php
protected array $scout_searchable = ['name_code']; // colunas de busca textual extras
protected array $scout_filterable = ['state_id'];   // colunas usadas em WHERE/facets
// opcional:
protected array $scout_stop_words = [];             // palavras ignoradas na busca
```

(exemplo real: `app/Models/Lists/City.php`). A trait também aceita as variantes camelCase `$scoutSearchable`/`$scoutFilterable`/`$scoutStopWords`.

## 3. Registro dos índices em `config/scout.php`
O bloco `meilisearch.index-settings` é preenchido automaticamente por `App\Classes\meilisearchSettings::getSettings()`, que varre `app/Models`, encontra todos os models com a trait (`class_uses_recursive`), cacheia a lista no Redis por 30s e chama `meilisearchSettings()` de cada um. Ou seja: adotar a trait + declarar as propriedades já basta para o índice ser configurado — não edite `index-settings` à mão.

## 4. Execução de busca: `->query()` + `searchSafe()`
O padrão real NÃO é `->paginate(15)`. Use a macro `searchSafe($fallbackColumns)` (definida em `app/Providers/AppServiceProvider.php`), que executa a busca no Meilisearch e, **se o servidor estiver offline, faz fallback para uma consulta Eloquent com `LIKE`** nas colunas informadas. Combine com `->query(fn ($q) => $q->with([...]))` para eager loading das relações:

```php
$contacts = SupportContact::search($search)
    ->query(fn ($query) => $query->with(['last_support']))
    ->searchSafe(['name', 'phone']); // colunas de fallback se o Meilisearch cair
```

`searchSafe()` retorna uma `Collection` (não um paginator). Referência real: `app/Http/Controllers/Support/SupportSearchDataController.php`.

# Instruções
1. **Torne o model pesquisável** usando `use App\Traits\HasScoutMeilisearch;` (que já inclui `Searchable`). Não use `Laravel\Scout\Searchable` cru.
2. **Configure o índice via propriedades** `$scout_searchable` / `$scout_filterable` / `$scout_stop_words`, não sobrescrevendo `toSearchableArray()`. Só sobrescreva `toSearchableArray()` se precisar de um payload que a trait não consegue derivar (caso raro).
3. **Não indexe tabelas grandes inteiras.** Liste apenas as colunas necessárias para busca/filtro/ordenação nas propriedades acima.
4. **Ao buscar, use `->searchSafe([...])`** informando as colunas de fallback (as mesmas usadas na busca textual), e `->query(fn ($q) => $q->with([...]))` para carregar relações e evitar N+1.
5. **Não edite `meilisearch.index-settings` manualmente** em `config/scout.php` — a descoberta é automática via `meilisearchSettings::getSettings()`.

# Restrições
- Nunca inclua HTML cru grande, binários ou base64 no payload indexado.
- Não dispare consultas N+1 dentro do fluxo de indexação; carregue relações com `->query(...->with([...]))` na busca.
- Não use `LIKE` cru direto no controller quando o Scout cobrir o recurso — o fallback `LIKE` é responsabilidade da macro `searchSafe()`, não código duplicado.
- Comentários de código em pt-BR.

# Recursos genéricos do Scout (NÃO são convenção do engeapp)
Os itens abaixo existem no Scout, mas **não são usados em nenhum model do projeto hoje**. Use apenas se realmente precisar, ciente de que fogem do padrão atual:
- `shouldBeSearchable(): bool` para indexação condicional — nenhum model do engeapp implementa.
- `protected $touches = ['relacao']` para reindexar o pai quando o filho muda — nenhum model Scout do engeapp declara.

# Exemplo — Model pesquisável (padrão do projeto)
```php
<?php

namespace App\Models\Lists;

use App\Traits\HasScoutMeilisearch;
use Illuminate\Database\Eloquent\Model;

class City extends Model
{
    use HasScoutMeilisearch;

    // A trait deriva toSearchableArray() automaticamente a partir destas propriedades:
    protected array $scout_searchable = ['name_code']; // busca textual
    protected array $scout_filterable = ['state_id'];   // filtros / WHERE

    public function state()
    {
        return $this->belongsTo(State::class, 'state_id', 'id');
    }
}
```

# Exemplo — Busca resiliente com fallback
```php
// Retorna uma Collection; se o Meilisearch estiver offline,
// searchSafe cai para LIKE nas colunas informadas.
$results = SupportContact::search($search)
    ->query(fn ($query) => $query->with(['last_support']))
    ->searchSafe(['name', 'phone']);
```

---
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
