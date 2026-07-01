# PROPOSTA DE SKILL: laravel-rate-limiting-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, optimizing, or debugging rate limits for HTTP routes, APIs, login endpoints, or queues in Laravel. Triggers on defining rate limiters in bootstrap/app.php, using RateLimiter facade, applying throttle middleware, customizing 429 response, and testing route throttling.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp expõe APIs para o frontend Vue 3 e integrações externas. É necessário ter diretrizes claras para configurar limites de requisições (rate limiting) para prevenir abusos, ataques de força bruta em telas de login e evitar que bots façam chamadas repetidas e caras a agentes de IA ou gateways de pagamento.
* **Recursos:** Configuração de limitadores de requisições no bootstrap/app.php, limites dinâmicos por IP, ID do usuário ou API Key, tratamento do erro HTTP 429 (Too Many Requests), bypassing de limites em ambiente de teste local/CI, e testes de rate limiting com Pest.
* **Objetivo:** Fornecer diretrizes e padrões de boas práticas para a implementação, configuração e testes de rate limiting no Laravel v13.
* **Casos de uso:** Proteção do endpoint de login e recuperação de senha, limite de chamadas de IA (Agent/Gemini), controle de envios de Pix/Boleto, e proteção das rotas de API consumidas pelo frontend.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará os padrões de testes Pest para validar os limites de requisições nas rotas protegidas.
  - `laravel-exception-handling-logging` — Integrará o tratamento customizado de exceções HTTP 429 com o fluxo de log padronizado.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-ai-agent-creator, laravel-inter-payments-integration, laravel-efi-payments-integration
* **Benefícios:** Redução de custos operacionais com APIs de IA e pagamentos, maior segurança contra ataques de força bruta, prevenção de sobrecarga do servidor web e melhor conformidade de segurança.
