# PROPOSTA DE SKILL: laravel-activity-log-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, implementing, or debugging user activity logs, audit trails, or model change logs using spatie/laravel-activitylog. Triggers on tracking model events, storing custom log metadata, retrieving activity history for frontend views, and cleaning up old logs.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp necessita de um sistema estruturado de auditoria de dados para cumprir requisitos regulatórios e LGPD. Sem padrões definidos, as alterações críticas no banco de dados não são registradas ou são salvas de forma inconsistente, gerando falta de rastreabilidade sobre quem modificou ou excluiu registros do sistema.
* **Recursos:** Configuração do spatie/laravel-activitylog, trait de log automático nos models, customização do causer, logs de atividades personalizadas, queries otimizadas de recuperação de logs e tarefa de limpeza (cleanup) programada dos logs antigos.
* **Objetivo:** Estabelecer diretrizes e padrões de melhores práticas para auditoria, logging de alterações nos models Eloquent e registros de ações de usuários utilizando o pacote spatie/laravel-activitylog no ecossistema Engeapp/Laravel.
* **Casos de uso:** Rastrear alterações em modelos importantes como faturas, permissões e dados cadastrais de clientes; auditoria de exclusões de registros; visualização do histórico de atividades de um registro no painel administrativo.
* **Workflows:**
  - `bug-fix-back-end`
  - `bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as diretrizes de models para aplicar corretamente as traits e configurações de log automático no escopo do Eloquent.
  - `laravel-user-impersonation-best-practices` — Integrará o rastreamento do causador (causer) real (o administrador que está personificando) durante sessões de personificação de usuário.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada ao herdar regras de auditoria nativas na criação de novos models.
* **Benefícios:** Conformidade com regulamentos de auditoria (LGPD), facilidade de rastreamento de bugs operacionais causados por alterações de dados, e histórico transparente das ações de usuários no sistema.
