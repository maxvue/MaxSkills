# PROPOSTA DE SKILL: laravel-service-providers-dependency-injection-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or registering Laravel Service Providers, binding services (bind, singleton, scoped) to the Service Container, resolving dependencies via dependency injection, or ensuring memory safety and Octane compatibility in singleton bindings.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp utiliza extensamente o container de serviços do Laravel para gerenciar dependências. Há a necessidade de estabelecer padrões rígidos de binding e injeção, especialmente respeitando as diretrizes de compatibilidade do Laravel Octane (prevenção de vazamento de memória e acúmulo de dados).
* **Recursos:** Convenções de criação de Service Providers, assinaturas de binding (`bind`, `singleton`, `scoped`), injeção via construtor, resolução lazy com closures, conformidade com o Laravel Octane e testes de resolução no container.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para o registro e a resolução de dependências através de Service Providers e injeção de dependências no Laravel.
* **Casos de uso:** Registro de gateways de pagamento customizados, injeção de clientes HTTP de terceiros, resolução dinâmica de agentes de IA de acordo com o contexto e desacoplamento de classes de serviço.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Utilizará as definições e convenções de classes de serviço para demonstrar como vinculá-las e injetá-las no container.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `laravel-services-best-practices` — Melhorará a forma como os serviços são instanciados e consumidos na aplicação.
  - `laravel-ai-agent-creator` — Auxiliará na injeção correta das dependências de agentes de IA.
* **Benefícios:** Melhor desacoplamento do código, facilidade na escrita de mocks para testes, conformidade total com o Laravel Octane (evitando bugs de concorrência e memória) e padronização arquitetural no backend.
