---
name: laravel-scout-searchable-best-practices
description: "Use when implementing or optimizing full-text search (Laravel Scout + Meilisearch) in Engeapp. Covers HasScoutMeilisearch trait, toSearchableArray, meilisearchSettings, index configuration, and searchSafe macro fallback."
---
# Objetivo
Padronizar busca textual rápida com Laravel Scout + Meilisearch no engeapp seguindo as abstrações reais do projeto: a trait `App\Traits\HasScoutMeilisearch`, as propriedades de configuração por model e a macro `searchSafe()`. Evite reimplementar `Searchable` cru — o projeto já tem uma camada própria que você deve reusar.

# Como o projeto faz (verdade-base)

## 1. Trait central: `HasScoutMeilisearch`
Models pesquisáveis novos devem usar `App\Traits\HasScoutMeilisearch` (não `Laravel\Scout\Searchable` diretamente). A trait já faz `use Searchable` internamente e fornece:

- `toSearchableArray()` pronto: percorre as chaves de `getScoutMeilisearchArray('array')`, resolve cada valor com `data_get($this, $key)`, faz `json_encode` de valores não-string, troca `.` por `_` nas chaves e força `id` como string. Por isso **você normalmente NÃO sobrescreve `toSearchableArray()`** — apenas declara as propriedades abaixo.
- `meilisearchSettings()`: retorna os `searchableAttributes`/`filterableAttributes`/`sortableAttributes`/`stopWords` do índice, consumido em `config/scout.php`.

Models reais que adotam a trait: `App\Models\Leads\Lead`, `App\Models\User`, `App\Models\SupportChat\SupportMessage`, `App\Models\SupportChat\SupportContact`, `App\Models\Client\Client`, `App\Models\Lists\City`.

Exceções legadas: `App\Models\Project\Project` e `App\Models\SupportChat\SupportProtocol` usam `Laravel\Scout\Searchable` cru com `toSearchableArray()` manual mínimo (poucos campos, ex.: `id`/`consumer_code`/`installation_code` em `Project`, `id`/`protocol` em `SupportProtocol`). O exemplo de busca da seção 4 (`SupportSearchDataController`) opera justamente sobre `SupportProtocol` (Searchable cru) — a macro `searchSafe()` funciona igual em ambos os padrões.

## 2. Configuração do índice por propriedades no model
Em vez de montar payload manual, declare arrays no model. A trait sempre mescla, incondicionalmente, os defaults `id`, `created_at`, `updated_at`; além disso mescla (só quando a coluna existir em `fillable`/`casts`/`hidden`/`appends` do model) os defaults extras `finished_at` (filterable), `name`/`created_at` (sortable) e `name`/`email`/`trade_name`/`phone_number`/`international_phone_number` (searchable). A stoplist pt-BR `['de', 'a', 'o', 'em', 'na', 'no', 'e', 'os', 'as']` é SEMPRE aplicada, independentemente do valor de `$scout_stop_words`.

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

Duas limitações importantes de `searchSafe()`:
- Filtros passados via `->where()` do `ScoutBuilder` NÃO sobrevivem ao fallback LIKE — a macro, no catch, só reaplica o closure registrado em `->query()`, nunca os `->where()` do Scout. Filtros que precisam valer nos dois caminhos devem ir dentro de `->query(fn ($q) => $q->where(...))`. Exemplo do risco real: `app/Services/ApiCepService.php` usa `City::search($this->city_name)->where('state_id', $this->state->id)->searchSafe(['name'])`, cujo filtro por estado desaparece no fallback.
- `searchSafe(array $fallbackColumns = [])` aceita array vazio (é o valor default do parâmetro); se o Meilisearch estiver offline e nenhuma coluna de fallback for informada, o catch retorna uma `Collection` vazia silenciosamente, sem erro. Sempre informe as colunas de fallback para evitar esse mascaramento de falha.

# Instruções
1. **Não indexe tabelas grandes inteiras.** Liste apenas as colunas necessárias para busca/filtro/ordenação nas propriedades da seção 2.

# Restrições
- Nunca inclua HTML cru grande, binários ou base64 no payload indexado.
- Não dispare consultas N+1 dentro do fluxo de indexação; carregue relações com `->query(...->with([...]))` na busca.
- Não use `LIKE` cru direto no controller quando o Scout cobrir o recurso — o fallback `LIKE` é responsabilidade da macro `searchSafe()`, não código duplicado.
- Comentários de código em pt-BR.
- `shouldBeSearchable(): bool` e `protected $touches = ['relacao']` existem no Scout mas não são usados em nenhum model do engeapp hoje.

# Exemplo — Model pesquisável (padrão do projeto)
```php
class City extends Model
{
    use HasScoutMeilisearch;

    // A trait deriva toSearchableArray() automaticamente a partir destas propriedades:
    protected array $scout_searchable = ['name_code']; // busca textual
    protected array $scout_filterable = ['state_id'];   // filtros / WHERE
}
```

---
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
