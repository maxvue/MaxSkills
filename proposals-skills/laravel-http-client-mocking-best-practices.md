# PROPOSTA DE SKILL: laravel-http-client-mocking-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when writing tests for components that make HTTP requests to external APIs, utilizing Laravel's HTTP Client (Http facade) mocking capabilities, or validating mock responses in Pest. Triggers on Http::fake, Http::sequence, mock API responses, and external integration tests.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp se integra com múltiplos serviços externos (Efí, Inter, Autentique, LiveKit, WhatsApp Cloud API). Para testar essas integrações de forma confiável e ágil, sem realizar chamadas de rede reais, é essencial possuir padrões de simulação (mocking) e asserções robustas com o HTTP Client nativo do Laravel.
* **Recursos:** Configurações de `Http::fake()`, uso de sequências de respostas (`Http::sequence()`), validações com `Http::assertSent()`, simulação de erros HTTP (4xx, 5xx), mock de payloads JSON complexos e boas práticas para simular chamadas em testes concorrentes.
* **Objetivo:** Fornecer diretrizes consistentes de como mockar requisições HTTP e validar integrações com APIs externas no ecossistema Engeapp usando Pest.
* **Casos de uso:** Testes de integração de pagamentos (Efí, Inter), assinaturas de documentos (Autentique), envio de mensagens (WhatsApp) e inicialização de salas de conferência (LiveKit).
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará as boas práticas e padrões gerais de escrita de testes com Pest PHP.
  - `laravel-base-api-integration-patterns` — Utilizará os padrões estruturais de integração com a classe `BaseApi` para demonstrar como mockar as respostas no nível de serviço.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-inter-payments-integration` — Permitirá testar de forma robusta e isolada a integração com o Banco Inter.
  - `laravel-efi-payments-integration` — Facilitará a escrita de testes unitários e de feature para o fluxo de pagamentos com a Efí.
  - `laravel-digital-signatures-integration` — Assegurará o teste do fluxo de envio e callback de contratos pelo Autentique e Clicksign.
  - `laravel-whatsapp-cloud-api-integration` — Ajudará na simulação de envio e webhooks da API de nuvem do WhatsApp.
  - `laravel-livekit-server-sdk-best-practices` — Auxiliará na criação de cenários de teste para geração de tokens e conexão com o LiveKit.
* **Benefícios:** Aceleração do tempo de execução dos testes, aumento da cobertura de código nas integrações externas, eliminação de dependência de rede em ambiente de CI/CD e facilidade de simular cenários de erro e instabilidade de serviços de terceiros.
