---
name: get-shit-done
description: "High-velocity execution and task delivery engine for engineering workflows. Use when breaking down complex user goals into atomic steps, tracking execution loops, avoiding premature optimization, and driving rapid task completion."
risk: safe
source: curated-youtube
---
# Get Shit Done (GSD) Workflow Engine

## When to Use
- You have an ambitious or complex feature request and need to deconstruct it into executable, verifiable micro-tasks.
- The workflow demands ruthless focus on working software, avoiding analysis paralysis and unnecessary abstraction layers.
- You need a structured execution loop: Spec -> Decompose -> Implement -> Verify -> Ship.

## Core Principles
1. **Bias for Action:** Prefer working code over speculative architecture.
2. **Atomic Slices:** Keep every task small enough to verify in under 5 minutes.
3. **Continuous Verification:** Run tests or execute scripts immediately after every modification.
4. **No Unrequested Refactoring:** Fix only what is in scope for the current milestone.

## Execution Loop
```bash
# 1. Define Milestone Goal
# State the single acceptance criterion for the current step.

# 2. Implement Smallest Working Diff
# Touch only the files required to satisfy the criterion.

# 3. Verify Immediately
npm test -- -t "target-feature" || pytest tests/test_target.py

# 4. Review Diff
git diff --stat

# 5. Check off and proceed to next atomic task.
```

## Checklist de Conclusão Rápida
- [ ] O código cumpre a solicitação sem criar débitos técnicos evidentes?
- [ ] A suíte de testes passou ou foi validada a execução manual?
- [ ] Arquivos temporários e logs de depuração foram limpos?
