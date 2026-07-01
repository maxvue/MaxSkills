# PROPOSTA DE SKILL: laravel-ai-token-cost-tracking-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, implementing, or optimizing AI token usage tracking, cost calculations, and API quota limits for LLM integrations (like Gemini or OpenAI) within the Laravel/Engeapp ecosystem. Triggers on tracking prompt/completion tokens, database logging for AI costs, and background queue jobs for usage metrics.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é centrado em integrações com agentes de IA. A falta de controle detalhado de consumo de tokens pode acarretar custos imprevistos e abusos de uso de cota.
* **Recursos:**
  - Padrões de banco de dados para persistência de tokens (prompt, completion e total).
  - Cálculo de custos com base na precificação oficial de provedores (Gemini, OpenAI).
  - Uso de Listeners ou Middlewares no ciclo do aiSDK para captura automática.
  - Gravação de logs assíncrona usando Jobs em background (evitando overhead na resposta do usuário).
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para o monitoramento, rastreamento de uso de tokens e controle de custos de chamadas de modelos de linguagem de inteligência artificial no ecossistema Engeapp/Laravel.
* **Casos de uso:** Registro de consumo de tokens por usuário/tenant, relatórios de faturamento baseados em uso de IA, limites de cotas diárias por usuário.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Integrará o hook de gravação nos agentes criados.
  - `laravel-jobs-queues-horizon-best-practices` — Utilizará as filas supervisionadas para processar a gravação assíncrona dos registros de custos.
  - `laravel-code-generators-best-practices` — Guiará a criação da estrutura de tabelas segura.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Os agentes gerados passarão a registrar o consumo de tokens automaticamente.
* **Benefícios:** Transparência de faturamento, detecção precoce de anomalias/loops de requisições de IA e controle rigoroso de despesas operacionais da infraestrutura.
