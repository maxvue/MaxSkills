# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying or reviewing Laravel Eloquent Models in the Engeapp project. Triggers on model creation, relationships, scopes, casts, accessors, mutators and observers.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O ecossistema Engeapp requer Models padronizados com tipagem forte, casts corretos, escopos (scopes) documentados e uso consistente de traits específicas do projeto (como auditoria ou UUIDs).
* **Recursos:** Padrões para definição de relationships com tipagem estrita de retorno, formatação de casts (enum, datas), scopes reutilizáveis e propriedades de fillable/guarded.
* **Objetivo:** Fornecer diretrizes e convenções rigorosas para a criação e manutenção de Models do Eloquent no projeto.
* **Casos de uso:** Criação de novas tabelas/entidades, refatoração de models complexos e definição de relacionamentos entre tabelas.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções para casts customizados de propriedades direcionadas a objetos Data (Spatie Laravel Data).
* **Skills auxiliares:** laravel, laravel-specialist, eloquent-best-practices, laravel:eloquent-relationships
* **Skills beneficiadas:** laravel-code-generators-best-practices, laravel-services-best-practices
* **Benefícios:** Melhor legibilidade do código, maior consistência na manipulação do banco de dados, prevenção de erros (como N+1) nativamente através da correta definição de relacionamentos, centralização de lógicas de negócio no banco (scopes) e integração otimizada com a arquitetura geral do Engeapp.
