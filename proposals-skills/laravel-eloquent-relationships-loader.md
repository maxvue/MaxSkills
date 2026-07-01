# PROPOSTA DE SKILL: laravel-eloquent-relationships-loader

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when optimizing Eloquent relationship loading, preventing N+1 query performance issues, using eager loading (with, load), executing database subqueries (withCount, withExists), or configuring strict relationship loading in Laravel. Triggers on DB queries, Eloquent relation accesses, and N+1 troubleshooting.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** Evitar problemas graves de performance e queries N+1 no Engeapp, padronizando a forma como relacionamentos são carregados e manipulados no Laravel.
* **Recursos:** Eager loading (`with`), Lazy Eager Loading (`load`, `loadMissing`), prevenção ativa de N+1 (ex: `Model::preventLazyLoading()`), subconsultas eficientes (`withCount`, `withExists`, `withMax`, `withMin`), e carregamento seletivo de colunas nos relacionamentos.
* **Objetivo:** Fornecer diretrizes e padrões claros para o carregamento otimizado e seguro de relacionamentos do Eloquent no Laravel, assegurando a escalabilidade do banco de dados.
* **Casos de uso:** Otimização de listagens de APIs, carregamento sob demanda em Jobs e Services, e prevenção de sobrecarga em consultas complexas.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as definições de relacionamentos tipados e propriedades padrão `$with` estabelecidas nos Models Eloquent.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices, laravel:eloquent-relationships, laravel:performance-eager-loading
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Eliminação de consultas redundantes no banco de dados (queries N+1), redução do tempo de resposta de APIs e consumo de memória otimizado ao selecionar colunas específicas de relacionamentos.
