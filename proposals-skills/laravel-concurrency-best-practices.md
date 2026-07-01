# PROPOSTA DE SKILL: laravel-concurrency-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when implementing concurrent or parallel tasks in Laravel, utilizing the Concurrency facade, managing parallel execution flow, configuring concurrency drivers, or handling race conditions and exceptions in parallel tasks.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp realiza múltiplas requisições pesadas a APIs externas (como NASA POWER, CRESESB, concessionárias de energia e gateways de pagamento) e tarefas de processamento de IA. Executar essas operações de forma sequencial causa gargalos de desempenho e latência nas requisições.
* **Recursos:** Uso correto da facade `Concurrency::run`, gerenciamento de drivers (`process`, `fork`), tratamento resiliente de exceções em subprocessos, limites de timeout e controle de vazamento de memória (memory leaks) em tarefas paralelas.
* **Objetivo:** Estabelecer diretrizes e padrões de implementação para execução concorrente e paralela de tarefas no backend Laravel, garantindo segurança e alto desempenho.
* **Casos de uso:** Busca concorrente de dados de irradiação solar em múltiplas APIs, validação em paralelo de dados cadastrais de concessionárias, chamadas concorrentes de processamento de texto na API Gemini.
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizada para capturar e registrar de forma estruturada as falhas que ocorrem em subprocessos paralelos.
  - `laravel-base-api-integration-patterns` — Utilizada para padronizar e estruturar as chamadas concorrentes a APIs externas.
* **Skills auxiliares:** php-pro, laravel-best-practices, laravel-expert
* **Skills beneficiadas:** laravel-solar-irradiance-cresesb-nasa-integration, laravel-ai-datasheet-extraction-best-practices
* **Benefícios:** Redução significativa do tempo de processamento de requisições complexas, melhor experiência do usuário final com respostas mais rápidas e isolamento seguro de subprocessos paralelos.
