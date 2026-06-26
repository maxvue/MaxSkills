# PLANO DE OTIMIZAÇÃO DE SKILLS — Ecossistema Engeapp

> Gerado em 2026-06-25 via auditoria estrutural + 4 agentes de auditoria de conteúdo (backend-laravel, backend-node/AdonisJS, front-end-vue, general-skills).
> Escopo: 435 skills próprias (`created-skills/`, `created-skills-pt-br/`, `general-skills/`). Não inclui `.agents/skills/` (terceiros).

---

## 1. DIAGNÓSTICO GERAL

**Saúde estrutural: BOA.** 435/435 com frontmatter válido, `name` presente e `name` = pasta. A coleção é madura e abrangente. Os problemas são de **consistência, duplicação e sobreposição** — não de quebra estrutural.

### Inventário
| Pasta | Conteúdo | Qtd |
|---|---|---|
| `created-skills-pt-br/backend-laravel` | Laravel (só existe em PT-BR) | 78 |
| `created-skills-pt-br/backend-node` | AdonisJS | 94 |
| `created-skills-pt-br/front-end-vue` | Vue 3/TS | 70 |
| `created-skills/backend-node` + `front-end-vue` | espelho EN (node 94 + vue 70) | 164 |
| `general-skills` | legadas/terceiros, fora do pipeline | 29 |

### Ciclo de vida (`list-skills.yaml`)
- 241 CONCLUIDA · 59 AGUARDANDO (28 adonisjs, 22 vue, 8 laravel) · 9 EXECUTANDO.
- As 29 `general-skills` **não estão no yaml** — vivem fora do pipeline de propostas.

---

## 2. PROBLEMAS POR SEVERIDADE

### 🔴 ALTA — Consistência sistêmica (afeta centenas de skills)

1. **Cabeçalhos misturando EN e PT.** Na pasta pt-br convivem `## Goal/Instructions/Constraints` (~179) e `## Objetivo/Instruções/Restrições` (~74), além de variação de nível (`#` vs `##`) e títulos descritivos livres (`# Boas Práticas de…`). É a inconsistência mais difundida (afeta as 3 categorias).

2. **Duplicação EN ↔ PT-BR (164 pares).** backend-node e front-end-vue são mantidos manualmente em dois idiomas; 0 pares idênticos (tradução real). **24 dos 164 pares têm `description`/wake-word divergente** — risco direto de triggering inconsistente entre os dois conjuntos.

3. **Assimetria de cobertura.** `backend-laravel` (78 skills) existe **só em pt-br**; não há espelho EN. Decisão pendente: criar espelho EN ou assumir laravel como PT-only.

### 🟡 MÉDIA — Sobreposição e redundância

4. **`general-skills` é um bucket legado redundante.** 29 → ~11-12 após limpeza:
   - **Remover (deprecated, já marcadas `deprecated: true`):** `typescript-advanced-types`, `typescript-pro`, `bug-hunter`, `systematic-debugging`, `echo-vue-development`.
   - **Remover (redundantes com o conjunto curado):** `laravel-best-practices`, `laravel-expert`, `laravel-pdf` (→ `laravel-pdf-handling-best-practices`), `laravel-security-audit` (→ `laravel-security-hardening-best-practices`), `configuring-horizon` (→ `laravel-jobs-queues-horizon-best-practices`), `pest-testing` (→ `laravel-pest-testing-best-practices`), `scout-development` (→ `laravel-scout-searchable-best-practices`), `vue-best-practices`, `vue-debug-guides`, `vue-pinia-best-practices`.
   - **Remover (fora de escopo):** `frontend-developer` (React/Next.js — projeto é Vue!), `frontend-design` (genérico).
   - **Preservar (únicas/processo/projeto):** `documentation-writer`, `debug-methodology`, `debug-using-debugbar`, `backend-bug-fixer`, `frontend-bug-fixer`, `php-pro`, `pinia`, `typescript-core`, `typescript-expert`, `typescript-docs`, `echo-development`.

5. **Sobreposições intra-categoria (fusões):**
   - **Vue — vídeo vertical:** `vue-tiktok-video-preview-simulator` + `vue-youtube-shorts-preview-simulator` + `vue-instagram-reels-preview-simulator` têm descrição/arquitetura quase idênticas (9:16, safe zones) → fundir em `vue-vertical-video-simulators`.
   - **Vue — ecossistema Max:** `vue-max-ecosystem` + `vue-max-components-ui-development` + `vue-maxvue-frontend` (escopo sobreposto) → consolidar em 2.
   - **Vue — Pinia:** `vue-max-pinia-integration` ≈ `vue-pinia-state-management` → fundir.
   - **Laravel — mídia/storage:** `laravel-media-library` + `laravel-vuefinder-media-library-integration` + `laravel-cloud-storage-integrations` → 2 skills.
   - **Laravel — documentos:** `laravel-image-processing-intervention` + `laravel-pdf-handling` + `laravel-docx-generation-phpword` → avaliar "Document & Media Processing".
   - **AdonisJS — ai-agents (16 skills):** fundir `adonisjs-ai-agents-tool-calling` + `adonisjs-ai-agents-prompt-injection-defense` → `…-tool-calling-security`; deduplicar Zod/factory entre `ai-agents-best-practices` e `tool-calling`.

6. **Skills inchadas (dividir/enxugar exemplos):** `vue-tiktok-…` (446 ln) e `vue-youtube-shorts-…` (413 ln) carregam ~140-150 linhas de SFC repetitivo. `laravel-jobs-queues-horizon` (340 ln) e `laravel-database-eloquent` cobrem temas demais.

### 🟢 BAIXA — Bugs pontuais e polimento

7. **Bug concreto:** `vue-floating-vue-tooltips-popovers-best-practices` tem **code block ``` não fechado** (EOF) — em **ambas** as versões EN e PT.
8. **Títulos H1 = nome da pasta** (sem formatação): `laravel-power-of-attorney-generation`, `laravel-docx-generation-phpword`.
9. **Seção vazia:** `vue-code-generators-best-practices` (seção "Componentes" sem conteúdo).
10. **Wake-words vagos:** `adonisjs-best-practices`, `adonisjs-api-integration-patterns` (genéricos demais — quase tudo casa).
11. **Frontmatter YAML `>-` sem "Use when" claro:** `vue-max-ecosystem`, `vue-vitest-testing`, `laravel-context-metadata-tracking`.
12. **Poucas referências cruzadas** ("Related Skills") entre skills da mesma família (<5%).

---

## 3. PLANO DE EXECUÇÃO (faseado)

### Fase 0 — Correções rápidas (baixo risco, alto retorno) ✅ CONCLUÍDA (2026-06-25)
- [x] Fechar o code block de `vue-floating-vue-tooltips-popovers` (EN + PT). ✅
- [x] Corrigir os 2 títulos H1 = nome-da-pasta. ✅ (títulos descritivos PT)
- [x] ~~Preencher seção vazia de `vue-code-generators`~~ → **falso positivo**, a seção tem conteúdo.
- [x] ~~Corrigir 5 `description: >-`~~ → eram **YAML válido** (folded scalar). Restam 2 skills **PT-only** sem EN (`vue-max-stack-frontend`, `laravel-excel-import-export`) com wake-word em PT → tratar na Fase 3.
- [x] Sincronizar **25 wake-words divergentes** PT ← EN (EN é canônico). ✅ 0 divergentes restantes; frontmatter 100% válido; corpos PT intactos.

> **Decisões do usuário (2026-06-25):** EN é a pasta **original/canônica**; PT é **espelho traduzido**. Cabeçalhos: bilíngues por pasta (EN→Goal/Instructions/Constraints; PT→Objetivo/Instruções/Restrições). Manter em PT apenas o que existir em EN. Implicação: **`backend-laravel` precisa ter seus originais em EN** (hoje só 2 de 78 existem em `created-skills/backend-laravel/`).

### Fase 1 — Padronização de cabeçalhos ✅ CONCLUÍDA (2026-06-25)
- [x] Padrão definido (bilíngue por pasta): EN → `## Goal/Instructions/Constraints`; PT → `## Objetivo/Instruções/Restrições`, sempre nível `##`.
- [x] Script de normalização rodado: **252 SKILL.md + 5 reference docs alterados, 757 cabeçalhos normalizados**. Resultado: **0 cabeçalhos cross-idioma** em ambas as pastas. Conversão segura (pulou cabeçalhos descritivos legítimos e blocos de código).
- [x] `execute.md` atualizado (Fase 3.1 + checklist Fase 4) para fixar o padrão e impedir regressão em skills futuras.

### Fase 2 — Limpeza de `general-skills` + REMOÇÃO TOTAL DE LARAVEL ✅ CONCLUÍDA (2026-06-25)
**Decisão do usuário (confirmada 3×, com ciência de produção e irreversibilidade): apagar TODO o Laravel.**
- [x] Arquivadas 7 skills (6 `deprecated:true` + `frontend-developer`/React) em `general-skills/_archived/`.
- [x] **Apagadas (rm) todas as skills Laravel:** `created-skills-pt-br/backend-laravel/` (80) + `created-skills/backend-laravel/` (3) + 10 general-skills laravel/php. **Backup compactado** em `scratchpad/laravel-backup-20260625.tar.gz` (226K) + cópia do yaml.
- [x] Preservada a skill **não-Laravel** que estava na pasta: `python-concessionarias-automation-best-practices` → movida para `general-skills/`.
- [x] `list-skills.yaml`: removidas **92 entradas `laravel-*`** (321→229 itens). YAML revalidado.
- [x] `execute.md`: removida a categoria `backend-laravel/` da instrução de criação.

**Limpezas pós-remoção ✅ CONCLUÍDAS (2026-06-25):**
1. [x] **Workflows** (symlink `global-workflows/`): removidas **142 linhas `- laravel-*`** em 6 arquivos (bug-fix-back-end −111, bug-fix-front-end −13, deploy −9, typescript-new-type −4, types-update-frontend −3, agent-ai-create −2). Workflows seguem coerentes (skills adonisjs/vue mantidas; bug-fix-back-end ficou com 78 skills AdonisJS). Backup em `scratchpad/workflows-backup-20260625.tar.gz`. Prosa sobre runtime Laravel em produção (`bugs-reports.md`, `comments-controllers.md`) **preservada**.
2. [x] **`agent-creator.md`** removido (ponteiro morto p/ skill Laravel apagada); exemplo em `execute.md` trocado para AdonisJS. Backup no scratchpad.

**Vue/órfãos ✅ CONCLUÍDOS:**
- [x] `vue-max-stack-frontend`: **versão EN canônica criada** (tradução fiel), descrição PT alinhada ao inglês, registrada no yaml (CONCLUIDA). Par EN/PT agora balanceado (72/72).
- [x] Artefatos do skill-creator removidos da pasta vue PT (`.skill` + `-workspace/`), backup no scratchpad.

**Estado de `general-skills/` agora:** 13 ativas + 7 em `_archived/`.

### Fase 2b — Esvaziamento do `general-skills` (decisão: created-skills é o que importa) ✅ CONCLUÍDA (2026-06-25)
Regra do usuário: o que falta em created-skills → migrar; o resto → limpar. 3 agentes auditaram cobertura das 13 ativas.
- [x] **4 cobertas → arquivadas** em `_archived/`: `vue` (@json-render, 0 usos), `vue-best-practices`, `vue-pinia-best-practices`, `pinia` (já cobertas pelas curadas).
- [x] **9 únicas → migradas** para created-skills (EN canônico + espelho PT, reformatadas ao padrão, decisão "reformat completo + PT"):
  - → `created-skills/general/` (categoria NOVA): `typescript-advanced-types-best-practices` (ex typescript-core), `typescript-tooling-monorepo-best-practices` (ex typescript-expert, +`scripts/`+`references/`), `typescript-documentation-best-practices` (ex typescript-docs, +`references/`), `systematic-debugging-best-practices` (ex debug-methodology), `technical-documentation-best-practices` (ex documentation-writer), `frontend-design-best-practices`, `python-concessionarias-automation-best-practices`.
  - → `created-skills/front-end-vue/`: `vue-debugging-best-practices` (ex vue-debug-guides, +`reference/` 139 arquivos), `vue-frontend-bug-fixing-best-practices` (ex frontend-bug-fixer, **atualizada Laravel→AdonisJS**: removidos Pint, Reverb, `@backend-bug-fixer`, backend Laravel).
- [x] 9 originais removidos de `general-skills/` (backup no scratchpad). 8 novas entradas no `list-skills.yaml` (python já existia) → 238 itens.

**Estado FINAL:** `general-skills/` = **0 ativas, 11 arquivadas**. `created-skills/` = **179 EN + 179 PT** (backend-node 98, front-end-vue 74, general 7), 0 órfãos, 0 cabeçalhos cross-idioma. A pasta `general-skills/` pode ser removida de vez (só resta `_archived/`).

### Fase 3 — Fusões e divisões ⏱️ ~1-2 dias
- [ ] Executar as fusões do §2.5 (começar pelas de maior sobreposição: simuladores de vídeo vertical e ecossistema Max).
- [ ] Enxugar/dividir as skills inchadas do §2.6 (mover exemplos longos para o corpo final ou reduzir).
- [ ] Cada fusão = atualizar `list-skills.yaml` + replicar no espelho EN.

### Fase 4 — Sincronização EN↔PT e governança ⏱️ contínuo
- [ ] **Decidir o modelo de manutenção bilíngue** (§4). Hoje são 2 cópias manuais — caro e propenso a drift.
- [ ] Adicionar verificação automatizada (script de lint): cercas pares, `description` idêntica entre pares, cabeçalho no padrão, H1 ≠ nome-da-pasta. Rodar como gate antes de marcar CONCLUIDA.

### Fase 5 — Lacunas (backlog de novas propostas)
- **Laravel:** middleware, events/listeners, model observers, api-resources, db-transactions/locks, form-requests, accessors/mutators.
- **AdonisJS:** debugging de agents, monitoring/observability de agents, cost estimation/budget, performance (paralelização/streaming).
- **Vue:** e2e-testing, a11y, i18n, performance-debugging, responsive, ci-cd.
- (Tratar via `proposal.md` no pipeline normal; priorizar contra o backlog de 59 AGUARDANDO.)

---

## 4. DECISÕES PENDENTES (precisam do usuário)

1. **Padrão de cabeçalho:** inglês (Goal/Instructions/Constraints) uniforme para tudo, OU bilíngue (EN headings na pasta EN, PT headings na pt-br)?
2. **Modelo bilíngue:** manter 2 cópias manuais, gerar EN a partir do PT (ou vice-versa) via script/tradução, OU abandonar um dos idiomas?
3. **backend-laravel sem espelho EN:** criar espelho ou assumir PT-only?
4. **general-skills:** remover de vez as redundantes ou apenas marcar `deprecated: true` e ocultar?

---

## 5. MÉTRICAS DE IMPACTO ESTIMADO
- `general-skills`: 29 → ~11 (−62%).
- Fusões: ~−10 a −14 skills (vue + laravel + adonisjs).
- Drift de wake-word: 24 → 0.
- Cabeçalhos inconsistentes: ~253 ocorrências → padrão único.
- Bugs concretos: 4 corrigidos (Fase 0).
