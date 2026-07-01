# PROPOSTA DE SKILL: laravel-lighthouse-graphql-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or debugging GraphQL schemas, queries, mutations, subscriptions, custom resolvers, or Lighthouse configuration in Laravel. Triggers on changes to GraphQL schema files (*.graphql), Lighthouse directives, and custom GraphQL resolver PHP classes.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui dependências para GraphQL utilizando o pacote nuwave/lighthouse. Há uma necessidade de padronizar a forma como estruturamos os schemas, a delegação de campos complexos para resolvers dedicados, o tratamento uniforme de erros do Lighthouse e a integração reativa no front-end.
* **Recursos:** Boas práticas de definição de schemas, uso de diretivas embutidas do Lighthouse (como @all, @find, @paginate, @eq, @belongsTo, @hasMany, @with), implementação de resolvers customizados estritos, gerenciamento de autorizações com @can/@guard, e interceptação de erros do GraphQL.
* **Objetivo:** Fornecer um guia conciso e consistente para o desenvolvimento e manutenção de APIs GraphQL utilizando Laravel Lighthouse no ecossistema Engeapp.
* **Casos de uso:** Desenvolvimento de queries complexas de relatórios paginados, criação de mutations para salvar dados do sistema com validação embutida, e customização de resolvers PHP para campos agregados.
* **Workflows:**
  - `bug-fix-back-end`
  - `bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models Eloquent e relacionamentos para mapear com precisão os tipos no schema GraphQL.
  - `laravel-exception-handling-logging` — Integrará o fluxo de captura e mapeamento de exceções com o formato esperado de erros do GraphQL.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Melhor legibilidade de APIs, redução de problemas de performance devido a queries N+1 por meio do uso correto das diretivas do Lighthouse, e maior consistência na comunicação cliente-servidor.
