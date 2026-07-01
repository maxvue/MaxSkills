# PROPOSTA DE SKILL: laravel-model-pruning-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, reviewing, or configuring Laravel Model Pruning (using Prunable or MassPrunable traits), defining data retention policies for Eloquent models, and scheduling database cleanup commands in the task scheduler.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O banco de dados do Engeapp possui tabelas de grande volume que acumulam dados históricos expirados (como logs de depuração, registros de rastreamento, notificações antigas e tokens Sanctum revogados). A ausência de uma rotina automática e padronizada de limpeza causa o inchaço desnecessário do banco de dados (que atualmente possui dezenas de gigabytes), prejudicando o desempenho de queries e aumentando custos de armazenamento.
* **Recursos:** Diretrizes detalhadas para implementação das traits `Prunable` e `MassPrunable`, definição segura de consultas de expiração usando query builder no método `pruning()`, configuração e agendamento do comando Artisan nativo `model:prune` no scheduler do Laravel, e boas práticas para evitar travamentos de tabelas (table locks) em deleções de grandes volumes.
* **Objetivo:** Fornecer diretrizes de melhores práticas para configurar, agendar e monitorar a exclusão automática de registros obsoletos de Eloquent Models no backend Laravel do Engeapp de forma segura e performática.
* **Casos de uso:** Limpeza de notificações lidas antigas, descarte de tokens de API expirados, remoção de registros antigos de auditoria de jobs, exclusão de rascunhos de propostas expirados ou logs temporários.
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de design de models para adicionar corretamente a trait `Prunable`/`MassPrunable` e o método de query `pruning`.
  - `laravel-code-generators-best-practices` — Utilizará os conceitos de comando CLI para gerenciar e executar de forma segura o comando nativo `model:prune` e logar seus resultados.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada ao expandir o ciclo de vida dos models com estratégias de descarte e limpeza automática.
* **Benefícios:** Redução do tamanho e inchaço do banco de dados, aumento da performance em consultas de tabelas transacionais críticas, automação simplificada e nativa sem dependências externas complexas, e conformidade com políticas de retenção de dados exigidas pela LGPD.
