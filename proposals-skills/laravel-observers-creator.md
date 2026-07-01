# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, registering, or optimizing Laravel Eloquent Observers, handling model lifecycle events (retrieved, creating, created, updating, updated, saving, saved, deleting, deleted, restoring, restored, forceDeleting), or managing asynchronous side-effects post-commit.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O Engeapp realiza processamentos assíncronos e reativos a alterações de modelos (como no Planner), necessitando garantir que esses efeitos colaterais ocorram sem gerar race conditions no banco (usando dispatch de jobs pós-commit) e mantendo a arquitetura limpa.
* **Recursos:** Estrutura padrão de Observers, registro correto utilizando provedores do Laravel ou atributos de Model, e diretrizes para prevenção de recursão infinita e race conditions.
* **Objetivo:** Definir diretrizes e padrões rigorosos para a criação, registro e gerenciamento de Eloquent Observers no ecossistema Engeapp/Laravel.
* **Casos de uso:** Atualização de logs de auditoria, limpeza automática de caches de listagens, despacho de Jobs pós-commit do banco de dados e atualização de agregações em tabelas relacionadas.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models para entender o ciclo de vida dos modelos que serão observados.
  - `laravel-jobs-queues-horizon-best-practices` — Integrará o envio de Jobs a partir de eventos do Observer com o tratamento correto pós-commit.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Garante consistência na execução de efeitos colaterais pós-persistência, previne race conditions com workers das filas (utilizando afterCommit) e reduz o acoplamento nos models Eloquent.
