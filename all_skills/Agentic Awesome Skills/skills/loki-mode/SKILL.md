---
name: loki-mode
description: "Autonomous end-to-end engineering execution mode for full-stack tasks. Use when orchestrating complex feature workflows requiring multi-phase planning, automated test execution, self-healing code loops, and rigorous verification."
risk: critical
source: community
---
# Loki Mode: Autonomous Engineering Execution

## When to Use
- Orchestrating complex end-to-end engineering workflows across multiple directories or stacks.
- Running autonomous test-driven loops with clear architectural boundaries.
- Deconstructing large architectural features into planned, verified execution steps.

## Safety & Governance Guidelines
1. **Human Confirmation Gate:** Never bypass user authorization for destructive actions (`rm -rf`, database drops, force push, or unreviewed production deployments).
2. **Deterministic Gating:** Always run test verification or compiler diagnostics (`npm test`, `pytest`, `tsc --noEmit`) before reporting completion.
3. **No Phantom Code:** Never hallucinate packages or internal APIs. Validate all imports against `package.json` or `composer.json`.

## Standard 4-Phase Execution Workflow

```
1. DISCOVERY & CONTEXT GATHERING
   └── Map affected files, read architecture rules, identify existing tests.

2. SPECIFICATION & TEST SCAFFOLDING
   └── Write failing test cases or define formal interfaces for the new feature.

3. ATOMIC IMPLEMENTATION
   └── Implement minimal working code satisfying all test assertions.

4. REGRESSION VERIFICATION & CLEANUP
   └── Run full test suites, verify formatting, and remove temporary debug artifacts.
```
