# PROPOSTA DE SKILL: laravel-eloquent-scopes-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or reviewing Laravel Eloquent query scopes, dynamic filter methods, or applying reusable search constraints on models. Triggers on local scopes definition, dynamic scopes, scope method chaining, and writing search filter classes.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp lida com complexas regras de busca e listagens de dados (orçamentos, ordens de serviço, clientes) e necessita de padrões de Query Scopes e filtros dinâmicos limpos no Laravel para manter os Controllers enxutos e reutilizar a lógica de banco de dados.
* **Recursos:** Convenções de nomenclatura de scopes, scopes locais vs globais, passagem de parâmetros em scopes dinâmicos, tipos de retorno (`Builder`), e implementação de padrões de filtro reutilizáveis (como Filter classes ou métodos de filtragem dinâmica baseados em arrays/requests).
* **Objetivo:** Estabelecer diretrizes consistentes de como criar, documentar e utilizar Query Scopes e filtros dinâmicos no Laravel.
* **Casos de uso:** Filtros complexos em tabelas de listagem, escopos de segurança padrão (ex: registros ativos, pertencentes ao usuário ou inquilino), e encadeamento de filtros dinâmicos na busca global.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções gerais de models (como tipagem de retorno e PHPDocs) para complementar as definições de escopo nos Eloquent Models.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices, eloquent-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices`
  - `laravel-code-generators-best-practices`
* **Benefícios:** Centralização da lógica de consultas SQL, eliminação de duplicação nos controllers, maior testabilidade da lógica de banco de dados e melhor legibilidade do código.
