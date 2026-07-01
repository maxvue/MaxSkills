# PROPOSTA DE SKILL: laravel-ai-agent-testing-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging tests for AI agents, mocking LLM API responses (such as Gemini/aiSDK), validating agent tool executions, and ensuring structural schema compliance in Laravel.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui múltiplos agentes de IA no diretório app/Ai/Agents. Para garantir testes rápidos, determinísticos e confiáveis, e evitar custos de API com chamadas reais ao Gemini/aiSDK em ambientes de teste e CI/CD, é indispensável estabelecer diretrizes claras para mockar respostas de IA e testar a execução de AI Tools e payloads estruturados.
* **Recursos:** Mocks para o aiSDK, asserções de seleção de AI Tools corretas, validação de retornos de dados estruturados (Structured Outputs) e testes de resiliência a falhas ou timeouts de requisições de LLM.
* **Objetivo:** Estabelecer diretrizes sólidas e padrões consistentes para escrever testes unitários e de integração para agentes de IA no backend Laravel utilizando Pest PHP.
* **Casos de uso:** Testar se o AgentAiBilletReader executa e mocka adequadamente as chamadas da LLM; testar se as AI Tools certas são ativadas em cenários específicos de automação; validar a estrutura final dos dados extraídos antes de persistir no banco de dados.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará os padrões de escrita de testes e asserções idiomáticas com o Pest PHP.
  - `laravel-ai-agent-creator` — Utilizará as definições dos agentes e a trait `HasAgentAiRequest` para mapear o fluxo a ser testado.
* **Skills auxiliares:**
  - `laravel-specialist`
  - `laravel-best-practices`
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Fornecerá cobertura de testes automatizados rápida e confiável para todos os novos agentes criados.
* **Benefícios:** Eliminação de chamadas de API reais em testes, redução de custos de desenvolvimento, maior velocidade no CI/CD e garantia de resiliência do fluxo de IA contra alterações de schema.
