---
name: laravel-scout-searchable-best-practices
description: Use when creating, modifying, or optimizing Laravel Scout searchable models, customizing toSearchableArray payloads, configuring conditional indexing, handling database relationships indexing (e.g., using touches), or executing search queries with Meilisearch.
---

# Objetivo
Fornecer diretrizes robustas e padrões consistentes para implementar e otimizar busca textual rápida usando Laravel Scout com Meilisearch no ecossistema Engeapp.

# Instruções
1. **Integração da Trait:**
   - Importe e use a trait `Laravel\Scout\Searchable` no model Eloquent alvo.

2. **Otimização do Payload (`toSearchableArray`):**
   - Customize o payload usando o método `toSearchableArray()`.
   - NÃO indexe tabelas grandes inteiras. Inclua apenas os campos necessários para busca full-text, filtragem e ordenação.
   - Para evitar consultas N+1 ao carregar (eager load) atributos de relações, carregue as relações previamente ao indexar em massa ou verifique se a relação está carregada. Use métodos como `$this->relationLoaded('relation')` para verificar se uma relação está carregada, ou consulte colunas específicas diretamente caso não esteja carregada.

3. **Indexação Condicional (`shouldBeSearchable`):**
   - Implemente `shouldBeSearchable()` quando os models devem ser pesquisáveis apenas sob condições específicas (ex: apenas projetos ativos, protocolos de suporte que não sejam rascunho).

4. **Sincronização Relacional (`$touches`):**
   - Quando mudanças em um model filho afetam os resultados de busca de um model pai, defina a propriedade `$touches` no model filho: `protected $touches = ['parentRelation'];`. Isso garante que o model pai seja "tocado" (atualizando seu timestamp `updated_at`) e reindexado automaticamente pelo Scout.

5. **Executando Consultas de Busca:**
   - Execute buscas usando `Model::search($query)`.
   - Use paginação: `Model::search($query)->paginate(15)`.
   - Para aplicar recursos específicos do Meilisearch (filtros, facets, ordenação), passe um callback como segundo argumento para `search()`.

6. **Testando Busca e Indexação:**
   - Use Pest para testar o comportamento de busca (searchable).
   - Use `Mockery` ou os fake engines do Scout se precisar afirmar que models foram importados ou que a busca foi acionada sem atingir uma instância real do Meilisearch em testes unitários.

# Restrições
- Nunca inclua HTML cru grande, dados binários ou arquivos base64 no payload de `toSearchableArray()`.
- Nunca dispare consultas N+1 dentro de `toSearchableArray()`. Se precisar acessar uma relação, garanta que ela esteja com eager load ou recupere apenas o valor específico usando consultas de banco de dados de forma eficiente.
- Não use consultas `LIKE` cruas no banco de dados quando a busca do Scout estiver disponível para o recurso.

# Exemplos

### Implementação do Model Searchable
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

### Teste de Integração com Pest
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

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
