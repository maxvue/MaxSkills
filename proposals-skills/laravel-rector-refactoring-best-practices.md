# PROPOSTA DE SKILL: laravel-rector-refactoring-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, running, or troubleshooting Rector for automated PHP refactoring and upgrades, writing custom Rector rules, or ensuring code compatibility with PHP 8.4+ and Laravel 13.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui um codebase que evolui e utiliza o Rector (`rector/rector` versão `^2.3`) de forma restrita, focada apenas em remover comandos de debug (`ds()`). Há uma necessidade clara de regras estruturadas para aplicar refatorações automáticas seguras (Dead Code, Code Quality, Type Declaration) sem quebrar o Eloquent, DTOs e compatibilidade stateless do Octane.
* **Recursos:** Boas práticas de configuração do `rector.php`, listas de conjuntos de regras seguras (sets), regras customizadas (ex: remoção de `ds()`), mitigação de riscos em models Eloquent e controllers Inertia, e comandos CLI seguros.
* **Objetivo:** Fornecer diretrizes sólidas e padrões para refatoração e modernização automatizada de código utilizando o Rector de forma segura no Engeapp.
* **Casos de uso:** Modernização segura para PHP 8.4, limpeza de código morto (dead code), padronização de tipos de retorno e parâmetros, remoção de funções de debug em produção e migração gradual para novas regras do Laravel.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as regras de tipagem e relacionamentos de models para garantir que o Rector não danifique declarações mágicas ou tipagem do Eloquent.
  - `laravel-octane-compatibility` — Garantirá que nenhuma refatoração automática introduza estados estáticos (static variables) ou poluição de memória incompatível com o Octane.
  - `laravel-code-generators-best-practices` — Assegurará que propriedades promovidas pelo construtor e anotações TypeScript em DTOs permaneçam consistentes após passarem pelo Rector.
* **Skills auxiliares:** php-best-practices, laravel-specialist
* **Skills beneficiadas:**
  - `laravel-services-best-practices`
  - `laravel-code-generators-best-practices`
* **Benefícios:** Automatização de refatorações complexas, modernização de código sem regressões, eliminação eficiente de código morto e manutenção de alta performance e compatibilidade stateless.
