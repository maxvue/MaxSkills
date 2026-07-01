# PROPOSTA DE SKILL: laravel-scout-searchable-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or optimizing Laravel Scout searchable models, customizing toSearchableArray payloads, configuring conditional indexing, handling database relationships indexing (e.g., using touches), or executing search queries with Meilisearch.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O Engeapp possui modelos como Project, SupportProtocol e Lead que utilizam busca rápida via Laravel Scout. É necessário garantir que a carga de dados enviada para o índice seja limpa, rápida e que relacionamentos sejam atualizados devidamente para evitar dados desatualizados na busca.
* **Recursos:** Configuração da trait Searchable, payload customizado com toSearchableArray, indexação condicional com shouldBeSearchable, atualização de índices vinculados via $touches, paginação de buscas e testes unitários/recursos para buscas.
* **Objetivo:** Fornecer diretrizes e padrões robustos para a implementação e otimização de busca rápida de texto usando o Laravel Scout com Meilisearch no ecossistema Engeapp.
* **Casos de uso:** Busca de projetos por nome/código, busca em protocolos de chat de suporte, busca de leads por contatos ou histórico.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os padrões de models do Eloquent para integrar a trait de busca e formatar o array de forma limpa.
  - `laravel-eloquent-relationships-loader` — Utilizará as boas práticas de carregamento de relacionamentos para evitar queries N+1 durante o toSearchableArray.
  - `laravel-pest-testing-best-practices` — Utilizará as boas práticas de testes para validar a indexação e resultados de busca usando mocks ou drivers locais.
* **Skills auxiliares:** laravel, laravel-specialist, eloquent-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Melhora na performance de busca, garantia de dados de busca sempre em sincronia com o banco de dados e prevenção de queries N+1 no envio de payloads de índices.
