# PROPOSTA DE SKILL: laravel-ai-agent-health-score-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, modifying, debugging, or testing the AgentHealthScore AI agent in Laravel. Triggers on changes to calculation logic for businesses, experience, or operation areas, changes to prompt instructions, custom tools (GetClientData, SetHealth), and persistence of health scores.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp utiliza um agente de IA especializado (AgentHealthScore) para calcular a saúde comercial de integradores solares B2B. A alteração indevida de pesos, penalidades ou estruturas de relatórios pode comprometer o faturamento e as tomadas de decisões automatizadas de Customer Success.
* **Recursos:** Diretrizes de cálculo matemático das áreas (negócios, experiência, operação), normalização e tratamento de dados insuficientes, formatação estrita do modelo de relatório em Markdown, e padrões de testes com Pest para validar cálculo de notas.
* **Objetivo:** Fornecer diretrizes consistentes para o desenvolvimento, manutenção, calibração de prompts e testes do agente AgentHealthScore no Laravel.
* **Casos de uso:** Atualização da lógica de cálculo do Health Score B2B, modificação no fluxo de tools do agente de IA, e escrita de testes automatizados para simulação de relatórios de CS.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará os padrões de estrutura de agentes Laravel aiSDK, definição de tools e trait `Promptable`.
  - `laravel-pest-testing-best-practices` — Utilizará as convenções de testes do Pest para validar o cálculo matemático e as asserções de logs de saúde comercial.
  - `laravel-services-best-practices` — Utilizará as boas práticas de encapsulamento de lógica de serviços de disparadores de agentes de IA.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-ai-agent-testing-best-practices` — O agente de testes se beneficiará das diretrizes específicas para testar o fluxo complexo do AgentHealthScore.
* **Benefícios:** Garantia de integridade nos cálculos de saúde dos clientes, relatórios gerados corretamente pelo LLM sem erros de formatação em Markdown, e facilidade para evoluir o prompt do agente sem regressões.
