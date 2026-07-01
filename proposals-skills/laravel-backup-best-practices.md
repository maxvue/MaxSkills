# PROPOSTA DE SKILL: laravel-backup-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, executing, testing, or debugging backups in Laravel, setting up spatie/laravel-backup, managing backup destinations, defining backup schedules, or handling backup failure alerts.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp armazena dados críticos de engenharia solar e homologações de projetos, tornando essencial a existência de regras e diretrizes automatizadas para backup do banco de dados e arquivos, prevenindo perdas catastróficas de dados.
* **Recursos:** Configuração de agendamentos de backup, definição de destinos (local, S3, WebDAV), políticas de retenção (limpeza de backups antigos), notificações e alertas de falhas.
* **Objetivo:** Estabelecer diretrizes consistentes e seguras para a configuração, execução e monitoramento de rotinas de backup de banco de dados e arquivos no ecossistema Engeapp/Laravel.
* **Casos de uso:** Backups diários automatizados do banco de dados do Engeapp, backup de mídias e uploads no S3, monitoramento de integridade e notificação em canais de log de erros se um backup falhar.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de comandos Artisan para padronizar o agendamento e execução de rotinas de checagem.
  - `laravel-exception-handling-logging` — Utilizará as boas práticas de logging estruturado para capturar e canalizar erros ocorridos durante os processos de backup.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Garantia de continuidade de negócios, recuperação rápida em cenários de falha catastrófica e visibilidade sobre a saúde e sucesso dos backups.
