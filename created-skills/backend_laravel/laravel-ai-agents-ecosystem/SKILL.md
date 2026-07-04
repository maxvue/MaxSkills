---
name: laravel-ai-agents-ecosystem
description: >-
  Use when creating, testing, or monitoring AI agents in Laravel with the
  laravel/ai (aiSDK) ecosystem. Covers agent classes, function-calling tools,
  structured JSON outputs, Pest testing with fakeAgent, token cost tracking,
  and the B2B AgentHealthScore business rules. Triggers on Agent/Tool classes,
  HasStructuredOutput, HasAgentAiRequest, Ai::fakeAgent(), and cost persistence.
---

# Ecossistema de Agentes de IA no Laravel

## Objetivo

Consolidar as diretrizes, boas práticas e a arquitetura para criar, testar e monitorar agentes de IA usando `laravel/ai` (aiSDK) no ecossistema Engeapp.

## Instruções

Devido à amplitude e profundidade do ecossistema de IA, a documentação é modularizada. Você **DEVE** consultar os arquivos de referência abaixo conforme a sua necessidade atual:

### 1. Criação de Agentes (Agent Creator)

Como criar classes de agente (Simples, Com Tools, Structured Outputs), aplicar os atributos obrigatórios (Provider, Model, Temperature) e gerenciar a execução por meio de Jobs e do trait `HasAgentAiRequest`.
🔗 **Referência:** [Criação de Agentes](references/agent-creator.md)

### 2. Criação de Tools (Tools Creator)

Regras estritas para criar tools (Function Calling) em `app/Ai/Tools`, exigindo definições de schema precisas via `JsonSchema` e saídas padronizadas em formato JSON com `try-catch`.
🔗 **Referência:** [Criação de Tools](references/tools-creator.md)

### 3. Structured Outputs

Boas práticas para definir e validar retornos JSON (`HasStructuredOutput`), garantindo que não haja unidades de medida em números, que identificadores sejam sanitizados e que fallbacks sejam tratados corretamente.
🔗 **Referência:** [Structured Outputs](references/structured-outputs.md)

### 4. Testes & Validação (Testing Best Practices)

Padrões de Pest PHP para usar `Ai::fakeAgent()`, testar loops assíncronos (`isDone()`) e garantir conformidade sem invocar a API de LLM de produção.
🔗 **Referência:** [Testes de Agentes](references/testing.md)

### 5. Token Cost Tracking

Diretrizes para a arquitetura de banco de dados, tipos decimais de alta precisão, precificação orientada por configuração (evitando hardcoding) e persistência de custos com dispatchers assíncronos (Queues).
🔗 **Referência:** [Token Cost Tracking](references/token-cost-tracking.md)

### 6. B2B Health Score (AgentHealthScore)

Regras de negócio específicas, algoritmos matemáticos, ponderação de áreas (Business, Experience, Operation), a matriz de bônus/penalidade e o decaimento temporal (recência) do agente Health Score.
🔗 **Referência:** [B2B Health Score](references/health-score.md)

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NUNCA** faça chamadas reais (não mockadas) à API de LLM em testes automatizados.
- **SEMPRE** use os atributos obrigatórios (`Provider`, `Model`, `Temperature`, `MaxTokens`, `Timeout`) na classe do Agent.
- **NUNCA** pule a validação de limites e cotas antes da requisição usando `RateLimiter` ou Cache.
- **SEMPRE** produza prompts e respostas voltadas ao usuário final (como relatórios) em português brasileiro (pt-BR).
