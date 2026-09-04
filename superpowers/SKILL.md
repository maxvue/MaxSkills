---
name: superpowers
description: "Complete agentic engineering workflow framework enforcing structured planning, technical specs, TDD, and subagent review cycles. Coordinates modular skills: brainstorming, test-driven-development, systematic-debugging, writing-plans, executing-plans, and verification."
---

# Superpowers — Agentic Engineering Workflow Framework

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this meta-orchestrator skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

---

## 1. A Regra Fundamental (The Core Rule)

**Invoque a skill relevante ou solicitada ANTES de qualquer resposta ou ação** — incluindo perguntas de esclarecimento, exploração do codebase ou inspeção de arquivos. Se depois verificar que não era o caso, você não precisa continuar a usá-la.

- **Antes de entrar em modo de planejamento:** se você ainda não fez o brainstorming inicial, invoque [`brainstorming`](./skills/brainstorming/SKILL.md) primeiro.
- **Antes de escrever qualquer linha de código de produção:** invoque [`test-driven-development`](./skills/test-driven-development/SKILL.md).
- **Ao investigar ou tentar consertar qualquer defeito/erro:** invoque [`systematic-debugging`](./skills/systematic-debugging/SKILL.md) antes de alterar arquivos.

Anuncie sempre: `"Usando [skill] para [propósito]"` e siga a skill rigorosamente. Se ela possuir um checklist, crie um item para cada passo.

---

## 2. Prioridade de Skills e Roteamento Operacional

Quando múltiplas habilidades se aplicarem, as skills de processo vêm primeiro — elas definem a metodologia de abordagem; em seguida, as skills de implementação a executam:

- `"Vamos construir X"` / Nova Funcionalidade → [`brainstorming`](./skills/brainstorming/SKILL.md) primeiro → [`writing-plans`](./skills/writing-plans/SKILL.md) → implementação com [`test-driven-development`](./skills/test-driven-development/SKILL.md).
- `"Corrija esse erro / bug"` → [`systematic-debugging`](./skills/systematic-debugging/SKILL.md) primeiro → refatoração e correção com [`test-driven-development`](./skills/test-driven-development/SKILL.md).
- `"Execute esse plano"` → [`executing-plans`](./skills/executing-plans/SKILL.md) ou [`subagent-driven-development`](./skills/subagent-driven-development/SKILL.md).
- `"Revise este código / PR"` → [`requesting-code-review`](./skills/requesting-code-review/SKILL.md) e [`receiving-code-review`](./skills/receiving-code-review/SKILL.md).
- `"Conclua / finalize"` → [`verification-before-completion`](./skills/verification-before-completion/SKILL.md) seguido por [`finishing-a-development-branch`](./skills/finishing-a-development-branch/SKILL.md).

---

## 3. Catálogo das 14 Skills Modulares Integradas

Todas as 14 sub-skills especializadas estão localizadas no diretório [`./skills/`](./skills/) e possuem especificações detalhadas:

| Skill | Gatilho e Propósito Principal | Caminho Relativo |
| :--- | :--- | :--- |
| **`brainstorming`** | Refinamento de requisitos e criação de especificações técnicas antes de codificar. | [`skills/brainstorming/SKILL.md`](./skills/brainstorming/SKILL.md) |
| **`writing-plans`** | Elaboração de planos de engenharia detalhados, organizados e orientados a TDD. | [`skills/writing-plans/SKILL.md`](./skills/writing-plans/SKILL.md) |
| **`executing-plans`** | Execução de planos passo a passo com paradas de validação empírica. | [`skills/executing-plans/SKILL.md`](./skills/executing-plans/SKILL.md) |
| **`test-driven-development`** | Regra de Ouro: nenhum código de produção sem um teste falhando primeiro. | [`skills/test-driven-development/SKILL.md`](./skills/test-driven-development/SKILL.md) |
| **`systematic-debugging`** | Rastreamento rigoroso de causa-raiz sem adivinhações ou tentativas aleatórias. | [`skills/systematic-debugging/SKILL.md`](./skills/systematic-debugging/SKILL.md) |
| **`using-git-worktrees`** | Criação e isolamento seguro de workspaces e branches temporárias de trabalho. | [`skills/using-git-worktrees/SKILL.md`](./skills/using-git-worktrees/SKILL.md) |
| **`subagent-driven-development`** | Delegação supervisionada de tarefas para subagentes com revisão obrigatória. | [`skills/subagent-driven-development/SKILL.md`](./skills/subagent-driven-development/SKILL.md) |
| **`dispatching-parallel-agents`** | Disparo e coordenação concorrente de subagentes em tarefas desacopladas. | [`skills/dispatching-parallel-agents/SKILL.md`](./skills/dispatching-parallel-agents/SKILL.md) |
| **`requesting-code-review`** | Empacotamento de diffs e solicitação de revisão independente de código. | [`skills/requesting-code-review/SKILL.md`](./skills/requesting-code-review/SKILL.md) |
| **`receiving-code-review`** | Recepção, análise crítica e incorporação disciplinada de feedback técnico. | [`skills/receiving-code-review/SKILL.md`](./skills/receiving-code-review/SKILL.md) |
| **`verification-before-completion`** | Provas empíricas e testes automatizados antes de alegar que a tarefa está pronta. | [`skills/verification-before-completion/SKILL.md`](./skills/verification-before-completion/SKILL.md) |
| **`finishing-a-development-branch`** | Higienização, verificação e finalização segura de branches de trabalho. | [`skills/finishing-a-development-branch/SKILL.md`](./skills/finishing-a-development-branch/SKILL.md) |
| **`writing-skills`** | Elaboração, calibração e teste adversarial de novas skills para agentes. | [`skills/writing-skills/SKILL.md`](./skills/writing-skills/SKILL.md) |
| **`using-superpowers`** | Meta-protocolo original de bootstrapping e disciplina operacional. | [`skills/using-superpowers/SKILL.md`](./skills/using-superpowers/SKILL.md) |

---

## 4. Tabela de Red Flags & Combate a Racionalizações

Pensar em qualquer uma das frases abaixo é sinal de alerta: **PARE imediatamente**, você está caindo em racionalização:

| Pensamento Racionalizador | Realidade Operacional |
| :--- | :--- |
| *"Esta é apenas uma pergunta simples"* | Perguntas são tarefas técnicas. Cheque as skills primeiro. |
| *"Preciso de mais contexto do projeto antes"* | A checagem de skill ocorre ANTES de perguntas de esclarecimento. |
| *"Deixe-me explorar os arquivos do codebase primeiro"* | As skills dizem COMO explorar com segurança. Consulte antes. |
| *"Posso checar arquivos/git rapidamente"* | Arquivos soltos não têm contexto de conversa. Verifique as skills. |
| *"Não preciso de uma skill formal para isso"* | Se a skill existe, seu uso é obrigatório. |
| *"Eu me lembro das regras dessa skill de cor"* | Skills evoluem e possuem detalhes críticos. Leia a versão atual. |
| *"A skill é exagerada para este caso"* | Tarefas simples tornam-se complexas rapidamente. Use a skill. |
| *"Vou só fazer esse ajuste rápido antes"* | Validação e verificação ocorrem ANTES de qualquer alteração. |
| *"Isso parece muito produtivo"* | Ação não disciplinada gera retrabalho e bugs. Skills previnem isso. |

---

## 5. Mapeamento de Ferramentas no MaxCode / Antigravity

- **Subagentes:** Use `invoke_subagent` com `TypeName: "self"` para implementações completas com isolamento ou `TypeName: "research"` para leitura/exploração sem efeitos colaterais.
- **Isolamento Git:** Utilize a worktree ativa designada pelo MaxCode (`.max-code-worktrees/wt-*`).
- **Verificação Contínua:** Execute comandos de teste (`npm test`, `npx vitest`, `php artisan test`) após cada ciclo TDD.
