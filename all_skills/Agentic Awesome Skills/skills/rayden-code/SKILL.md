---
name: rayden-code
description: "Precision software engineering guidelines and clean architecture standards. Use when writing robust, production-ready code with strong modularity, defensive error handling, explicit type contracts, and zero unnecessary dependencies."
risk: safe
source: community
---
# Rayden Code: Production Engineering Standards

## When to Use
- Writing robust production components that require strict modular boundaries and high maintainability.
- Applying clean code practices, descriptive naming, single-responsibility principles, and typed interfaces.
- Hardening existing codebases against edge cases, unhandled promises, and memory leaks.

## Core Engineering Principles
1. **Explicit Over Implicit:** Prefer clear variable names and explicit function signatures over clever one-liners.
2. **Defensive Boundaries:** Validate input data at the boundary (APIs, user inputs, database queries) using schemas (Zod/Pydantic/FormRequest).
3. **Fail Fast:** Throw descriptive, actionable errors immediately upon invalid state detection rather than silently returning `null`.
4. **Locality of Behavior:** Keep related logic, types, and error handling as close to the call site as practical.

## Architecture Checklist
- [ ] O componente possui uma única responsabilidade bem definida?
- [ ] Todas as chamadas assíncronas tratam rejeições e timeouts?
- [ ] Não há acoplamento desnecessário com bibliotecas de terceiros?
- [ ] Os tipos estão totalmente definidos sem o uso de `any` injustificado?
