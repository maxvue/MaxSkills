# PROPOSTA DE SKILL: adonisjs-social-media-api-mocking-testing-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, reviewing, or debugging unit/integration tests for social media API integrations (Meta/Instagram, YouTube, TikTok, LinkedIn, Bluesky, X/Twitter, Pinterest) or external HTTP webhooks in AdonisJS v6 using Japa. Triggers on HTTP client mocking, api test suites, mocking Axios/fetch instances, and webhook payload signature simulation.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema SocialMediaApp integra-se intensamente com APIs externas de publicação de conteúdo. Testar esses fluxos sem disparar chamadas reais (o que causa rate limits e poluição de dados) exige padrões consistentes de mocking de rede e simulação de webhooks com Japa.
* **Recursos:** Padrões de mock de requisições HTTP (nock, msw, ou interceptores nativos), simulação de payloads e assinaturas de Webhooks, testes de resiliência (simulação de timeouts e erros HTTP 4xx/5xx), transações limpas no Lucid ORM para testes integrados.
* **Objetivo:** Fornecer diretrizes e padrões de projeto para mockar APIs de mídias sociais e testar fluxos de publicação e webhooks de forma resiliente no AdonisJS v6.
* **Casos de uso:** Testes de controladores que disparam postagens no Instagram/Facebook, testes de serviços de importação de métricas, simulação de Webhook do Instagram para moderação de comentários.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `adonisjs-japa-testing-best-practices` — Utilizará os padrões básicos de suíte de testes Japa, ciclo de vida de testes (setup/teardown) e assertions.
  - `adonisjs-social-media-apis-webhooks-best-practices` — Utilizará as especificações de assinatura de payload e URLs de webhooks para simular as requisições.
* **Skills auxiliares:** adonisjs-specialist, adonisjs-best-practices
* **Skills beneficiadas:** adonisjs-instagram-comments-ai-moderation-best-practices, adonisjs-instagram-meta-token-renewal-best-practices
* **Benefícios:** Testes de integração estáveis, menor risco de vazamento de dados de produção, cobertura de cenários de erro de rede difíceis de reproduzir manualmente.
