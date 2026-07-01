# PROPOSTA DE SKILL: laravel-eloquent-query-optimization-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when writing, refactoring, or reviewing Laravel Eloquent queries, database migrations, indexing strategy, or optimizing database performance. Triggers on eager loading, chunking large datasets, subqueries, and fixing N+1 query problems.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O banco de dados do ecossistema Engeapp é de grande porte (o dump local de dados ultrapassa dezenas de gigabytes), o que torna a otimização de consultas e a estratégia de indexação tópicos extremamente críticos para a performance. A falta de padrões de otimização pode resultar em consultas lentas, consumo excessivo de memória do servidor e locks de tabela prejudiciais à operação.
* **Recursos:** Diretrizes para evitar problemas de N+1 (uso de eager loading com `load` e `with`), paginação eficiente e carregamento em lotes (`chunk`, `lazy` e `cursor`), criação correta de índices em migrações (índices simples, compostos e chaves estrangeiras), utilização avançada de subqueries com `addSelect()` e `withWhereHas()`, e técnicas para identificar consultas lentas em produção.
* **Objetivo:** Estabelecer diretrizes consistentes e padrões práticos para a construção de consultas Eloquent otimizadas e modelagem de banco de dados eficiente no Laravel.
* **Casos de uso:** Refatoração de relatórios complexos que realizam loops de consultas ao banco, otimização de endpoints de listagem de registros pesados com paginação, e definição correta de índices na modelagem de novas tabelas.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models para mapear relacionamentos otimizados e scopes de busca adequados.
  - `laravel-code-generators-best-practices` — Utilizará as convenções de migrations para aplicar chaves estrangeiras e índices eficientemente.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-jobs-queues-horizon-best-practices` — Jobs que processam lotes de dados em background se beneficiarão de consultas de leitura e escrita rápidas.
  - `laravel-services-best-practices` — Classes de serviço que agregam regras de negócios complexas serão otimizadas.
* **Benefícios:** Aumento significativo na velocidade de carregamento de páginas e APIs, redução acentuada do uso de memória e CPU do servidor de banco de dados, e prevenção de gargalos de processamento em ambiente de produção.
