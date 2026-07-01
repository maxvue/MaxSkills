# PROPOSTA DE SKILL: laravel-jobs-queues-horizon-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, debugging, or refactoring Laravel queue Jobs, configuring queues and Horizon workers, handling job failures, or optimizing background task performance. Triggers on Job dispatching, queue configuration, retry policies, backoff mechanisms, transaction handling in queues, and Horizon monitoring dashboards.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp executa dezenas de tarefas assíncronas de longa duração em background, como chamadas de IA (Gemini), webhooks do Trello, envio de mensagens por WhatsApp e processamento de pagamentos. É essencial ter diretrizes rígidas para evitar falhas silenciosas, timeouts no processamento e exaustão de Rate Limits de APIs externas.
* **Recursos:**
  - Definição correta do número de tentativas (`public int $tries`) e políticas de backoff exponencial (`public array $backoff`).
  - Tratamento de falhas persistentes através do método `failed(\Throwable $exception)`.
  - Técnicas de controle de concorrência e prevenção de Jobs duplicados (`WithoutOverlapping` / `UniqueJobs`).
  - Encapsulamento correto de conexões de banco dentro dos Jobs para evitar locks, garantindo transações corretas.
  - Padrões para dispatching condicional (`dispatchIf`, `dispatchUnless`).
  - Integração com eventos de progresso e notificações WebSocket (Laravel Echo / Reverb).
* **Objetivo:** Fornecer diretrizes padronizadas e seguras de arquitetura para criação, manutenção e monitoramento de Jobs assíncronos no Laravel e filas supervisionadas pelo Horizon.
* **Casos de uso:**
  - Criação de novos Jobs de integração com LLMs de forma resiliente a rate limits.
  - Refatoração de Jobs de webhook para evitar concorrência ou repetição desnecessária de tarefas.
  - Configuração de políticas de retry para conexões instáveis com APIs externas.
* **Workflows:**
  - `bug-fix-back-end` — Auxiliará na identificação de gargalos de fila ou bugs em processamentos assíncronos.
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Para alinhar os Jobs que realizam chamadas a agentes de IA com as políticas de resiliência e timeouts necessárias.
* **Skills auxiliares:**
  - `laravel-specialist`
  - `laravel-best-practices`
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Fornecerá um mecanismo de processamento assíncrono muito mais robusto e tolerante a falhas para agentes que consomem tempo excessivo de resposta.
* **Benefícios:** Eliminação de execuções órfãs ou silenciosas, controle total sobre o consumo de APIs externas de IA e terceiros, e otimização do Horizon para balanceamento de carga em produção.
