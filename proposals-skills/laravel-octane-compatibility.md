# PROPOSTA DE SKILL: laravel-octane-compatibility

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when writing, refactoring, or reviewing PHP code in the context of Laravel Octane to ensure compatibility with stateless request cycles. Triggers when modifying Singletons, static properties, container bindings, or dealing with memory leak preventions.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é executado em um ambiente de alto desempenho utilizando Laravel Octane com FrankenPHP. Como o Octane inicializa a aplicação apenas uma vez em memória e reutiliza a mesma instância do container de serviços entre requisições, injeções diretas indesejadas (como Request, Config ou Session) ou o uso incorreto de propriedades estáticas podem introduzir vazamentos de memória e poluição de estado entre requisições de diferentes usuários.
* **Recursos:** Diretrizes de programação stateless, uso correto do escopo `scoped` no container em vez de `singleton`, técnicas de injeção de dependência segura usando closures resolvedores (`fn() => request()`), prevenção de acumulação de dados em propriedades estáticas.
* **Objetivo:** Garantir a total compatibilidade do código-fonte do Engeapp com o Laravel Octane, prevenindo problemas de vazamento de memória e contaminação de estado entre requisições.
* **Casos de uso:** Criação de Services singletons, registro de Service Providers customizados, manipulação de estados globais, refatoração de classes com propriedades estáticas.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Utilizará as boas práticas de Services para garantir que os serviços injetados respeitem o ciclo de vida stateless do Octane.
  - `laravel-exception-handling-logging` — Para logs corretos de problemas e vazamentos de estado sem reter instâncias de objetos pesados.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-services-best-practices`
  - `laravel-code-generators-best-practices`
* **Benefícios:** Estabilidade em produção com FrankenPHP, eliminação de vazamentos de memória (memory leaks) e prevenção de contaminação de sessões/dados de requisição entre usuários distintos.
