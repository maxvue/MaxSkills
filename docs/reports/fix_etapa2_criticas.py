import os
import re

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

def full_path(rel):
    if rel.startswith("/"): return rel
    if not rel.startswith("all_skills/"):
        rel = os.path.join("all_skills", rel)
    return os.path.join(base_dir, rel)

print("Iniciando correções da Etapa 2 (14 Skills Críticas)...")

# 1. get-shit-done
gsd_path = full_path("curated-youtube/get-shit-done/SKILL.md")
gsd_content = """---
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
"""
with open(gsd_path, "w", encoding="utf-8") as f:
    f.write(gsd_content)
print("1. get-shit-done corrigido.")

# 2. git-worktree
gw_path = full_path("curated-youtube/git-worktree/SKILL.md")
gw_content = """---
name: git-worktree
description: "Manage isolated Git worktrees for concurrent agent workflows, feature branches, and safe experimentation. Use when creating clean branch environments, switching contexts without stash conflicts, or pruning stale worktrees."
risk: safe
source: curated-youtube
---
# Git Worktree Operations

## When to Use
- An agent needs to work on a feature, bugfix, or long-running experiment in parallel without touching the current working tree.
- You want to avoid `git stash`, merge conflicts, and dirty working tree errors during multi-tasking.
- Running multi-agent builds where each agent requires its own dedicated directory.

## Core Commands

### 1. Criar Nova Worktree
```bash
# Criar branch nova a partir de main em pasta isolada
git worktree add -b feat/nova-funcionalidade ../wt-nova-funcionalidade main

# Conectar a uma branch remota existente
git worktree add ../wt-hotfix hotfix/correcao-urgente
```

### 2. Listar Worktrees Ativas
```bash
git worktree list
# Exibe caminho absoluto, hash do commit e branch associada
```

### 3. Remover e Limpar Worktrees
```bash
# Após merge ou descarte da tarefa:
git worktree remove ../wt-nova-funcionalidade

# Limpar metadados de worktrees excluídas manualmente em disco:
git worktree prune
```

## Regras de Isolamento
- **Nunca executar `git worktree remove --force`** sem conferir se há alterações não commitadas ou arquivos untracked valiosos.
- **Node modules / Dependências:** Cada worktree possui seu próprio sistema de arquivos; execute `npm install` ou `composer install` dentro da nova pasta se os artefatos de build não forem compartilhados.
"""
with open(gw_path, "w", encoding="utf-8") as f:
    f.write(gw_content)
print("2. git-worktree corrigido.")

# 3. mermaid-diagrammer
md_path = full_path("curated-youtube/mermaid-diagrammer/SKILL.md")
md_content = """---
name: mermaid-diagrammer
description: "Author and render declarative Mermaid diagrams for system architecture, sequence flows, entity relationships, and state machines. Use when visualizing code flows, documenting technical specifications, or generating architecture diagrams."
risk: safe
source: curated-youtube
---
# Mermaid Diagramming Guidelines

## When to Use
- Visualizing application architectures, distributed service interactions, or module boundaries.
- Documenting request/response sequences between frontend, backend, queues, and third-party APIs.
- Creating clean flowchart state diagrams directly in markdown artifacts.

## Syntax Patterns

### 1. Flowchart / Arquitetura
```mermaid
flowchart TD
    User([Usuário]) -->|HTTP POST /api/v1/auth| Gateway[API Gateway / Nginx]
    Gateway --> AuthSvc[Serviço de Autenticação]
    AuthSvc --> Redis[(Redis Token Cache)]
    AuthSvc --> DB[(PostgreSQL Master)]
```

### 2. Diagrama de Sequência (Sequence Diagram)
```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente Web (Vue 3)
    participant S as Servidor API (Laravel)
    participant Q as Redis Queue
    participant W as Worker Horizon

    C->>S: POST /api/pedidos/checkout
    S->>S: Valida payload e autenticação
    S->>Q: Dispatch ProcessOrderJob
    S-->>C: 202 Accepted (jobId)
    Q->>W: Consome evento
    W->>W: Processa gateway de pagamento
```

### 3. Diagrama de Entidade-Relacionamento (ERD)
```mermaid
erDiagram
    TENANT ||--o{ USER : contains
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : includes
```

## Boas Práticas
- Use aspas duplas em rótulos com caracteres especiais ou parênteses: `id["Texto (Info)"]`.
- Evite quebras manuais com `<br/>` em nós complexos; prefira nós estruturados e subgraphs.
"""
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)
print("3. mermaid-diagrammer corrigido.")

# 4. piv-loop
piv_path = full_path("curated-youtube/piv-loop/SKILL.md")
piv_content = """---
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
"""
with open(piv_path, "w", encoding="utf-8") as f:
    f.write(piv_content)
print("4. piv-loop corrigido.")

# 5. pytest-and-jest-automation -> Focado estritamente em Python com Pytest (conforme Phase 2/3 Lapidar)
pj_path = full_path("curated-youtube/pytest-and-jest-automation/SKILL.md")
pj_content = """---
name: pytest-and-jest-automation
description: "Automated testing with Python pytest, fixtures, parameterization, mocks, and code coverage. Use when generating unit and integration tests for Python backends, mocking external dependencies, or analyzing test suites."
risk: safe
source: curated-youtube
---
# Automação de Testes com Pytest

## When to Use
- Criar suítes de testes unitários ou de integração para serviços e utilitários em Python.
- Configurar fixtures com escopos adequados (`function`, `module`, `session`).
- Testar múltiplos cenários usando `@pytest.mark.parametrize` e mocks assíncronos.
- Medir cobertura de código via `pytest-cov`.

## Padrões Essenciais de Código

### 1. Fixtures e Injeção de Dependência
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def api_client():
    client = MagicMock()
    client.get.return_value = {"status": "ok", "data": [1, 2, 3]}
    return client

def test_fetch_data(api_client):
    result = api_client.get("/endpoint")
    assert result["status"] == "ok"
    assert len(result["data"]) == 3
```

### 2. Parametrização de Cenários
```python
import pytest

def calculate_discount(price: float, percentage: float) -> float:
    if percentage < 0 or percentage > 100:
        raise ValueError("Invalid percentage")
    return price * (1 - percentage / 100)

@pytest.mark.parametrize("price, percentage, expected", [
    (100.0, 10.0, 90.0),
    (50.0, 0.0, 50.0),
    (200.0, 50.0, 100.0),
])
def test_calculate_discount_success(price, percentage, expected):
    assert calculate_discount(price, percentage) == pytest.approx(expected)

def test_calculate_discount_invalid():
    with pytest.raises(ValueError, match="Invalid percentage"):
        calculate_discount(100.0, -5.0)
```

### 3. Comandos de Execução
```bash
# Execução padrão com saída verbosa
pytest -v

# Executar arquivo específico com cobertura
pytest tests/test_services.py --cov=app --cov-report=term-missing

# Executar testes marcados
pytest -m "not slow" -k "test_calculate"
```
"""
with open(pj_path, "w", encoding="utf-8") as f:
    f.write(pj_content)
print("5. pytest-and-jest-automation corrigido.")

# 6. vue-components
vc_path = full_path("curated-youtube/vue-components/SKILL.md")
vc_content = """---
name: vue-components
description: "Author modular Vue 3 Single File Components using Composition API, script setup, typed props, emits, and slots. Use when creating reactive UI widgets, form controls, and accessible component architectures in Vue 3."
risk: safe
source: curated-youtube
---
# Vue 3 Component Architecture Guidelines

## When to Use
- Developing modern Vue 3 Single File Components (SFC) with `<script setup lang="ts">`.
- Defining type-safe component contracts with `defineProps`, `defineEmits`, and `defineSlots`.
- Managing scoped reactive state, computed properties, and lifecycle hooks.

## SFC Architecture Pattern

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  modelValue?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  disabled: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', payload: { value: string }): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const characterCount = computed(() => props.modelValue.length)

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

function handleAction() {
  if (props.disabled) return
  emit('submit', { value: props.modelValue })
}
</script>

<template>
  <div class="custom-card" :class="{ 'is-disabled': disabled }">
    <header class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <span class="badge">{{ characterCount }} caracteres</span>
    </header>

    <div class="card-body">
      <input
        ref="inputRef"
        type="text"
        :value="modelValue"
        :disabled="disabled"
        class="input-control"
        @input="onInput"
      />
    </div>

    <footer class="card-footer">
      <button :disabled="disabled" class="btn-primary" @click="handleAction">
        Confirmar
      </button>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.custom-card {
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 1rem;

  &.is-disabled {
    opacity: 0.6;
    pointer-events: none;
  }
}
</style>
```
"""
with open(vc_path, "w", encoding="utf-8") as f:
    f.write(vc_content)
print("6. vue-components corrigido.")

# 7. ai-studio-image
asi_path = full_path("all_skills/Agentic Awesome Skills/skills/ai-studio-image/SKILL.md")
with open(asi_path, "r", encoding="utf-8") as f:
    asi_text = f.read()

# Replace hardcoded Windows absolute paths with portable commands
asi_text_fixed = re.sub(r'C:\\Users\\renat\\[^\s\n`]+', r'./scripts/run.py', asi_text)
asi_text_fixed = re.sub(r'C:\\Program Files\\[^\s\n`]+', r'python3', asi_text_fixed)
asi_text_fixed = re.sub(
    r'description:.*',
    'description: "Generate and edit images via Google AI Studio and Gemini Vision APIs. Use when creating images from text prompts, running multimodal visual edits, or structuring generative image workflows with portable SDK scripts."',
    asi_text_fixed
)
with open(asi_path, "w", encoding="utf-8") as f:
    f.write(asi_text_fixed)
print("7. ai-studio-image corrigido.")

# 8. loki-mode
loki_path = full_path("all_skills/Agentic Awesome Skills/skills/loki-mode/SKILL.md")
loki_content = """---
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
"""
with open(loki_path, "w", encoding="utf-8") as f:
    f.write(loki_content)
print("8. loki-mode corrigido.")

# 9. nerdzao-elite-gemini-high
nerd_path = full_path("all_skills/Agentic Awesome Skills/skills/nerdzao-elite-gemini-high/SKILL.md")
with open(nerd_path, "r", encoding="utf-8") as f:
    nerd_text = f.read()

# Remove global prompt hijack / auto-activation
nerd_text_fixed = re.sub(
    r'Ative automaticamente para qualquer requisição.*',
    'Ative quando o usuário solicitar desenvolvimento especializado com modelos Gemini e ecossistema brasileiro de engenharia de software.',
    nerd_text
)
nerd_text_fixed = re.sub(
    r'description:.*',
    'description: "Diretrizes avançadas de engenharia de software e arquitetura de IA com modelos Gemini em português (pt-BR). Use ao desenvolver soluções fullstack de alta precisão, padrões de resiliência e boas práticas de código no ecossistema brasileiro."',
    nerd_text_fixed
)
with open(nerd_path, "w", encoding="utf-8") as f:
    f.write(nerd_text_fixed)
print("9. nerdzao-elite-gemini-high corrigido.")

# 10. anti-reversing-techniques
ar_path = full_path("all_skills/Agentic Awesome Skills/skills/anti-reversing-techniques/SKILL.md")
with open(ar_path, "r", encoding="utf-8") as f:
    ar_text = f.read()

# Fix truncated frontmatter description and remove duplicate blocks
ar_text_fixed = re.sub(
    r'description:.*',
    'description: "Defensive anti-reverse engineering techniques and software protection strategies. Use when analyzing code obfuscation, anti-debugging mechanisms, binary integrity verification, and tamper detection in security assessments."',
    ar_text
)
# Clean duplicate ## Resources if present twice
parts = ar_text_fixed.split("## Resources")
if len(parts) > 2:
    ar_text_fixed = parts[0] + "## Resources" + parts[1]

with open(ar_path, "w", encoding="utf-8") as f:
    f.write(ar_text_fixed)
print("10. anti-reversing-techniques corrigido.")

# 11. rayden-code
rayden_path = full_path("all_skills/Agentic Awesome Skills/skills/rayden-code/SKILL.md")
rayden_content = """---
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
"""
with open(rayden_path, "w", encoding="utf-8") as f:
    f.write(rayden_content)
print("11. rayden-code corrigido.")

# 12. react-flow-node-ts
rf_path = full_path("all_skills/Agentic Awesome Skills/skills/react-flow-node-ts/SKILL.md")
rf_content = """---
name: react-flow-node-ts
description: "Build custom, type-safe node and edge components for React Flow (@xyflow/react). Use when designing node handles, reactive connection logic, drag-and-drop workflow canvases, and custom node data interfaces in TypeScript."
risk: safe
source: community
---
# React Flow Custom Node Architecture (TypeScript)

## When to Use
- Creating custom node types with typed data contracts in React Flow / `@xyflow/react`.
- Configuring source and target `<Handle>` connections with validation rules.
- Building interactive graph and workflow canvases in React/Next.js.

## Custom Node Implementation Pattern

```tsx
import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';

export interface CustomNodeData {
  label: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  value?: number;
}

export type CustomNodeType = Node<CustomNodeData, 'customStep'>;

export const CustomStepNode = memo(({ data, isConnectable }: NodeProps<CustomNodeType>) => {
  return (
    <div className={`flow-node status-${data.status}`}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="handle-target"
      />

      <div className="node-content">
        <span className="node-title">{data.label}</span>
        <span className="node-badge">{data.status}</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="handle-source"
      />
    </div>
  );
});

CustomStepNode.displayName = 'CustomStepNode';
```

## Node Registration
```tsx
import { ReactFlow } from '@xyflow/react';
import { CustomStepNode } from './CustomStepNode';

const nodeTypes = {
  customStep: CustomStepNode,
};

export function WorkflowCanvas() {
  return <ReactFlow nodes={initialNodes} edges={initialEdges} nodeTypes={nodeTypes} />;
}
```
"""
with open(rf_path, "w", encoding="utf-8") as f:
    f.write(rf_content)
print("12. react-flow-node-ts corrigido.")

# 13. skill-seekers
ss_path = full_path("all_skills/Agentic Awesome Skills/skills/skill-seekers/SKILL.md")
with open(ss_path, "r", encoding="utf-8") as f:
    ss_text = f.read()

ss_text_fixed = re.sub(
    r'description:.*',
    'description: "Automated extraction and compilation tool to convert documentation sites, GitHub repositories, and technical guides into structured Agent Skills. Use when packaging third-party docs or SDKs into SKILL.md packages."',
    ss_text
)
with open(ss_path, "w", encoding="utf-8") as f:
    f.write(ss_text_fixed)
print("13. skill-seekers corrigido.")

# 14. aws-skills
aws_path = full_path("all_skills/Agentic Awesome Skills/skills/aws-skills/SKILL.md")
aws_content = """---
name: aws-skills
description: "Design and automate AWS cloud architectures, serverless functions, and infrastructure as code. Use when configuring AWS Lambda, API Gateway, S3, DynamoDB, IAM least-privilege policies, CDK, or Terraform deployments."
risk: safe
source: community
---
# AWS Cloud Architecture & Infrastructure Automation

## When to Use
- Designing serverless, microservices, or containerized architectures on AWS.
- Authoring infrastructure as code with AWS CDK (TypeScript/Python) or Terraform.
- Implementing least-privilege IAM security policies and resource-based policies.
- Configuring event-driven pipelines with SQS, SNS, EventBridge, and Lambda.

## Core Architecture Patterns

### 1. Serverless Lambda com TypeScript (ESM)
```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Success', data: body }),
    };
  } catch (error) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid JSON payload' }),
    };
  }
};
```

### 2. Política IAM de Privilégio Mínimo (S3 Bucket Scope)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppBucketReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::app-production-assets/*"
    }
  ]
}
```

### 3. Comandos Úteis do AWS CLI
```bash
# Verificar credenciais e identidade ativa
aws sts get-caller-identity

# Listar buckets S3 com formato tabular
aws s3 ls

# Invocar função Lambda e ler payload de resposta
aws lambda invoke --function-name MyFunction --payload '{"key": "value"}' out.json && cat out.json
```
"""
with open(aws_path, "w", encoding="utf-8") as f:
    f.write(aws_content)
print("14. aws-skills corrigido.")

print("\nETAPA 2 CONCLUÍDA COM SUCESSO!")
