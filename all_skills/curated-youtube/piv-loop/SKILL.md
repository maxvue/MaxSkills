---
name: piv-loop
description: "Plan-Implement-Verify engineering feedback loop for autonomous coding tasks. Use when executing multi-step refactors, feature builds, or bugfixes requiring structured task decomposition and rigorous verification gating."
risk: safe
source: curated-youtube
---
# Plan-Implement-Verify (PIV) Loop

## When to Use
- Executing non-trivial code modifications that span multiple files or layers.
- Preventing regression errors through mandatory verification gates before marking tasks complete.
- Structuring subagent delegations with clear input criteria, execution boundaries, and test validation.

## Protocol Phases

### 1. Plan (Planejamento)
- Inspecione a base de código e identifique os arquivos exatos a serem modificados.
- Defina o critério de aceitação observável (teste automatizado, comando CLI ou validação de tipo).
- Mapeie riscos potenciais e efeitos colaterais.

### 2. Implement (Implementação)
- Faça alterações cirúrgicas e contíguas.
- Siga estritamente as convenções de estilo do repositório.
- Não refatore código não relacionado fora do escopo do plano.

### 3. Verify (Verificação Obrigatória)
- Execute a suíte de testes relevante para a alteração.
- Valide checagem estática de tipos (`tsc --noEmit` ou `phpstan`).
- Se houver falha, analise o traceback e retorne à fase de Implementação sem reescrever todo o plano.
