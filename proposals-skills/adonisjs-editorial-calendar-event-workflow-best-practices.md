# PROPOSTA DE SKILL: adonisjs-editorial-calendar-event-workflow-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when developing, reviewing, debugging, or maintaining the editorial calendar event lifecycle, event state transitions (planned, planning_approved, script_drafted, script_ready, art_ready, art_analysing, art_rejected, scheduled, published, failed, replanning), orchestrating AI copywriter, copywriter reviewer, graphic editor, or art analyst jobs, or handling publication queues and commands in AdonisJS. Triggers on editing calendar states, managing event job pipelines, and handling social media publishing flows.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema do SocialMediaApp possui uma orquestração complexa de múltiplos agentes de IA e jobs assíncronos que coordenam o ciclo de vida do evento de calendário (CalendarEvent), desde o planejamento estratégico inicial até a publicação final. Falhas ou inconsistências no fluxo de status impedem que os jobs executem na ordem correta, causando quebras na geração automatizada de scripts e artes de posts.
* **Recursos:** Mapeamento detalhado de todos os status de eventos (planned, planning_approved, script_drafted, script_ready, art_ready, art_analysing, art_rejected, scheduled, published, failed, replanning), diretrizes para transição de status em controllers e tools de IA (SaveDraftScript, SaveEventScript, GenerateEventArtwork, SaveArtAnalysis), regras de tratamento de fluxo de revisão/rejeição parcial de artes, e estrutura de jobs via BullMQ (StrategyManagerJob, CopywriterJob, CopywriterReviewerJob, GraphicEditorJob, ArtAnalystJob, PublishEventJob).
* **Objetivo:** Fornecer regras claras e padrões consistentes para implementar, depurar e alterar o fluxo de transições de status e a orquestração de jobs de eventos de calendário no SocialMediaApp.
* **Casos de uso:** Criação de novos status no ciclo de vida de publicações, depuração de jobs de IA travados ou executados fora de ordem, ajuste da lógica de aprovação/rejeição parcial de slides de carrossel, e implementação de novos publicadores automáticos.
* **Workflows:**
  - `/bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `adonisjs-best-practices` — Para convenções de estruturação do AdonisJS v6, padrões de injeção de dependência e controllers.
  - `adonisjs-bullmq-queue-management-best-practices` — Para estruturar e despachar corretamente os jobs assíncronos das filas BullMQ no AdonisJS.
  - `adonisjs-ai-agents-best-practices` — Para integração de prompts de IA e tools do Vercel AI SDK nos jobs do ciclo de vida.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `adonisjs-ai-agents-multi-agent-orchestration` — Será beneficiada ao dispor de uma especificação clara de qual status rege cada fase da orquestração dos subagentes.
* **Benefícios:** Prevenção de inconsistências de estado no banco de dados, garantia de execução correta dos jobs de IA na ordem cronológica de fluxo, e economia de recursos computacionais através da regeneração parcial de slides reprovados.
