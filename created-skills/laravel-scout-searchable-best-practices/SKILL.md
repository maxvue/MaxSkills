---
name: laravel-scout-searchable-best-practices
description: Use when creating, modifying, or optimizing Laravel Scout searchable models, customizing toSearchableArray payloads, configuring conditional indexing, handling database relationships indexing (e.g., using touches), or executing search queries with Meilisearch.
---

# Goal
Provide robust guidelines and consistent patterns for implementing and optimizing rapid text search using Laravel Scout with Meilisearch in the Engeapp ecosystem.

# Instructions
1. **Trait Integration:**
   - Import and use the `Laravel\Scout\Searchable` trait in the target Eloquent model.

2. **Payload Optimization (`toSearchableArray`):**
   - Customize the payload using the `toSearchableArray()` method.
   - Do NOT index entire large tables. Include only the fields required for full-text search, filtering, and sorting.
   - To prevent N+1 database queries when eager loading attributes from relationships, load relationships beforehand when bulk indexing or check if the relation is loaded. Use methods like `$this->relationLoaded('relation')` to check if a relation is loaded, or query specific columns directly if not loaded.

3. **Conditional Indexing (`shouldBeSearchable`):**
   - Implement `shouldBeSearchable()` when models should only be searchable under specific conditions (e.g., only active projects, non-draft support protocols).

4. **Relational Synchronization (`$touches`):**
   - When child model changes affect search results of a parent model, define the `$touches` property on the child model: `protected $touches = ['parentRelation'];`. This ensures the parent model is touched (updating its `updated_at` timestamp) and automatically reindexed by Scout.

5. **Executing Search Queries:**
   - Execute searches using `Model::search($query)`.
   - Use pagination: `Model::search($query)->paginate(15)`.
   - To apply Meilisearch-specific features (filters, facets, sorting), pass a callback as the second argument to `search()`.

6. **Testing Search & Indexing:**
   - Use Pest to test searchable behavior.
   - Use `Mockery` or Scout's fake engines if you need to assert that models were imported or search was triggered without hitting a real Meilisearch instance in unit tests.

# Constraints
- Never include large, raw HTML, binary data, or base64 files in the `toSearchableArray()` payload.
- Never trigger N+1 queries inside `toSearchableArray()`. If you need to access a relationship, ensure it is either eager loaded or retrieve only the specific value using database queries efficiently.
- Do not use raw database `LIKE` queries when Scout search is available for the resource.

# Examples

### Searchable Model Implementation
```php
<?php

namespace App\Models\Project;

use Illuminate\Database\Eloquent\Model;
use Laravel\Scout\Searchable;

class Project extends Model
{
    use Searchable;

    // Garante que o projeto seja atualizado e reindexado se uma relação filha mudar
    // protected $touches = [...];

    /**
     * Determina se o modelo deve ser indexado no Meilisearch.
     */
    public function shouldBeSearchable(): bool
    {
        // Apenas indexar se o projeto não estiver arquivado
        return ! $this->is_archived;
    }

    /**
     * Define a representação estruturada de busca para Scout/Meilisearch.
     */
    public function toSearchableArray(): array
    {
        // Retorna apenas dados estritamente necessários para a busca rápida
        return [
            'id' => $this->id,
            'consumer_code' => $this->consumer_code,
            'installation_code' => $this->installation_code,
            // Evita N+1 verificando se a relação está carregada
            'client_name' => $this->relationLoaded('client') 
                ? $this->client->name 
                : $this->client()->value('name'),
        ];
    }
}
```

### Pest Integration Test
```php
<?php

use App\Models\Project\Project;

it('indexa corretamente apenas quando o projeto nao estiver arquivado', function () {
    // Configura o fake do Scout se necessário, ou testa a lógica condicional diretamente
    $activeProject = new Project(['is_archived' => false]);
    $archivedProject = new Project(['is_archived' => true]);

    expect($activeProject->shouldBeSearchable())->toBeTrue();
    expect($archivedProject->shouldBeSearchable())->toBeFalse();
});
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
