# PROPOSTA DE SKILL: laravel-pint-code-formatting-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when formatting PHP code with Laravel Pint, configuring code style rules, running the Pint formatter on backend files, or ensuring PHP files adhere to the project's styling guidelines. Triggers on Pint execution, code styling fixes, and pre-commit formatting checks.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui múltiplos desenvolvedores e subagentes modificando a base de código do Laravel. Sem a padronização do Laravel Pint, commits contendo formatações mistas (espaciamento, chaves, importações) poluem o histórico de alterações do Git e violam a regra do Pint estabelecida em GEMINI.md.
* **Recursos:** Execução do formatador via CLI (`vendor/bin/pint`), uso da flag `--dirty` para otimizar a execução apenas nos arquivos modificados, regras de estilo pré-configuradas no Laravel Pint e integração prática com o ciclo de commit/deploy.
* **Objetivo:** Fornecer diretrizes e padrões de formatação automatizada de código PHP utilizando o Laravel Pint, garantindo consistência visual e conformidade com os padrões de estilo definidos para o projeto.
* **Casos de uso:** Formatação automática de novos models, controllers, requests e migrations antes de realizar commits, correção de inconsistências de formatação legadas e alinhamento do estilo de código gerado por diferentes subagentes.
* **Workflows:**
  - bug-fix-back-end
  - deploy
* **Skills próprias utilizadas:**
  - `laravel-larastan-static-analysis-best-practices` — Utilizada para guiar a conformidade do código estático, garantindo que o código formatado pelo Pint também passe sem avisos no Larastan.
  - `laravel-rector-refactoring-best-practices` — Utilizada para garantir que refatorações automatizadas em massa geradas pelo Rector sejam limpas pelo Pint para manter o estilo uniforme.
* **Skills auxiliares:** php-pro, laravel-best-practices
* **Skills beneficiadas:** Todas as skills de criação de código PHP no backend (ex: `laravel-code-generators-best-practices`, `laravel-code-generators-best-practices`, `laravel-services-best-practices`).
* **Benefícios:** Código backend limpo e consistente, histórico de commits limpo e livre de alterações de estilo irrelevantes, e automação eficiente da formatação do código no fluxo de desenvolvimento.
