---
name: laravel-ai-agents-ecosystem
description: >-
  Use when creating, testing, or monitoring AI agents in Laravel with the
  laravel/ai (aiSDK) ecosystem. Covers agent classes, function-calling tools,
  structured JSON outputs, Pest testing with fakeAgent, token cost tracking,
  and the B2B AgentHealthScore business rules. Triggers on Agent/Tool classes,
  HasStructuredOutput, HasAgentAiRequest, Ai::fakeAgent(), and cost persistence.
---

# Laravel AI Agents Ecosystem

## Goal

Consolidate the guidelines, best practices, and architecture for creating, testing, and monitoring AI agents using `laravel/ai` (aiSDK) in the Engeapp ecosystem.

## Instructions

Because of the breadth and depth of the AI ecosystem, the documentation is modularized. You **MUST** consult the reference files below depending on your current need:

### 1. Agent Creation (Agent Creator)

How to create agent classes (Simple, With Tools, Structured Outputs), apply the required attributes (Provider, Model, Temperature), and manage execution through Jobs and the `HasAgentAiRequest` trait.
🔗 **Reference:** [Agent Creation](references/agent-creator.md)

### 2. Tools Creation (Tools Creator)

Strict rules for creating tools (Function Calling) in `app/Ai/Tools`, requiring precise schema definitions via `JsonSchema` and standardized JSON-formatted outputs with `try-catch`.
🔗 **Reference:** [Tools Creation](references/tools-creator.md)

### 3. Structured Outputs

Best practices for defining and validating JSON returns (`HasStructuredOutput`), ensuring there are no units of measurement in numbers, identifiers are sanitized, and fallbacks are handled correctly.
🔗 **Reference:** [Structured Outputs](references/structured-outputs.md)

### 4. Testing & Validation (Testing Best Practices)

Pest PHP patterns for using `Ai::fakeAgent()`, testing asynchronous loops (`isDone()`), and ensuring compliance without invoking the production LLM API.
🔗 **Reference:** [Agent Testing](references/testing.md)

### 5. Token Cost Tracking

Guidelines for the database architecture, high-precision decimal types, configuration-driven pricing (avoiding hardcoding), and cost persistence with asynchronous dispatchers (Queues).
🔗 **Reference:** [Token Cost Tracking](references/token-cost-tracking.md)

### 6. B2B Health Score (AgentHealthScore)

Specific business rules, mathematical algorithms, area weighting (Business, Experience, Operation), the bonus/penalty matrix, and the temporal decay (recency) of the Health Score agent.
🔗 **Reference:** [B2B Health Score](references/health-score.md)

## Constraints

- **NEVER** make real (non-mocked) calls to the LLM API in automated tests.
- **ALWAYS** use the required attributes (`Provider`, `Model`, `Temperature`, `MaxTokens`, `Timeout`) on the Agent class.
- **NEVER** skip validating limits and quotas before the request using `RateLimiter` or Cache.
- **ALWAYS** produce prompts and end-user-facing responses (such as reports) in Brazilian Portuguese (pt-BR).
