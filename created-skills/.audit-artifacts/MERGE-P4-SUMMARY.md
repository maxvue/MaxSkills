# Consolidação de Merges de Cluster — EngeApp → AdonisJS

## Cluster 1 — AdonisJS + BullMQ
**Skill consolidada:** `/home/johnattas/GitHub/Skills/created-skills/backend-node/adonisjs-bullmq-best-practices/SKILL.md`

**Arquivadas (4):**
- `adonisjs-bullmq-queue-management-best-practices` (master/esqueleto)
- `adonisjs-bullmq-job-idempotency-deduplication-best-practices`
- `adonisjs-bullmq-job-resilience-retries-best-practices`
- `adonisjs-bullmq-multi-tenant-job-isolation-best-practices`

**Perda de conteúdo / revisão:** Nenhuma perda técnica — apenas deduplicação (comando Ace de worker unificado em 1 exemplo, config attempts/backoff mantida uma vez). Ponto de atenção: ressalva BullMQ Pro vs open-source no throttling por tenant (verificar se a edição usada suporta).

## Cluster 2 — AdonisJS + Puppeteer / Rendering
**Skill consolidada:** `/home/johnattas/GitHub/Skills/created-skills/backend-node/adonisjs-puppeteer-rendering-best-practices/SKILL.md`

**Arquivadas (2):**
- `adonisjs-reporting-pdf-excel-best-practices`
- `adonisjs-puppeteer-image-generation-best-practices`

**Não tocada (cross-link):** `adonisjs-pdf-coordinate-editing-best-practices`

**Perda de conteúdo / revisão:** Nenhuma perda. Decisão de design: adotado padrão singleton headless em vez de launch-por-requisição (reporting); o try/finally por requisição foi preservado como guidance. Confirmar que nenhum fluxo pontual de relatório dependia do launch direto.

## Cluster 3 — Vue / Simuladores de Preview de Post Social
**Skill consolidada:** `/home/johnattas/GitHub/Skills/created-skills/front-end-vue/vue-social-post-preview-simulator-best-practices/SKILL.md`

**Arquivadas (8):**
- `vue-facebook-post-preview-simulator-best-practices`
- `vue-google-business-profile-post-preview-simulator-best-practices`
- `vue-instagram-feed-grid-simulator-best-practices`
- `vue-instagram-reels-preview-simulator-best-practices`
- `vue-instagram-stories-preview-simulator-best-practices`
- `vue-threads-post-preview-simulator-best-practices`
- `vue-tiktok-video-preview-simulator-best-practices`
- `vue-youtube-shorts-preview-simulator-best-practices`

**Não tocada (cross-link):** `vue-draggable-next-best-practices`

**Perda de conteúdo / revisão:** 3 simuladores de vídeo (Reels/TikTok/Shorts) colapsados em 1 exemplo canônico 9:16 — diferenças por rede preservadas em tabela + nota "Particularidades". **Requer revisão humana:** correções de aderência ao escopo (conversão de Tailwind/Aura → UnoCSS attributify + tokens de tema no Threads e GBP; cores de marca isoladas em `<style scoped>`) — validar fidelidade visual de cada rede após a conversão.

## Cluster 4 — Vue / Max Stack Frontend
**Skill consolidada (master, editada in-place):** `/home/johnattas/GitHub/Skills/created-skills/front-end-vue/vue-max-stack-frontend-best-practices/SKILL.md`

**Arquivada (1):**
- `vue-max-ecosystem-best-practices`

**Perda de conteúdo / revisão:** Maior parte do ecosystem era duplicata (descartada por já existir, com mais detalhe, no master). Conteúdo único absorvido (imports modulares de `@maxvue/max-use/routes`, interface `_`, `useCachedApi`/`useRefCachedApi`). Corrigida divergência de escopo: ecosystem dizia "frontend do Engeapp" (origem Laravel), reescrito para Maxdmin/Adonis. Refs remanescentes a `vue-max-ecosystem` apenas em arquivos de auditoria/workflow, não em outras SKILL.md.

## Cluster 5 — Documentação Técnica
**Skill consolidada (master, editada in-place):** `/home/johnattas/GitHub/Skills/created-skills/general/technical-documentation-best-practices/SKILL.md`

**Arquivada (1):**
- `typescript-documentation-best-practices` (com todo o `references/`: jsdoc-patterns, framework-patterns, examples, typedoc-configuration, adr-patterns, pipeline-setup, validation)

**Perda de conteúdo / revisão — descarte deliberado (fora de escopo):**
- `references/framework-patterns.md` inteiro: exemplos NestJS (Guard/Decorator JWT), React, Angular, Express middleware — fora do stack-alvo.
- `references/jsdoc-patterns.md` e exemplos com auth via **JWT/RS256**, **bcrypt** e Redis-para-sessão — contradizem o modelo de auth do escopo (sessão+cookie, scrypt). Valor genérico reescrito sem os exemplos.
- `references/adr-patterns.md` ADR "NestJS Framework Selection" — template de ADR do master (mais rico, em PT) foi mantido.

**Atenção:** descarte de todo o diretório `references/` da fonte; se algum exemplo genérico (interfaces/generics/uniões) tinha valor além do que foi reescrito como tabela de tags, confirmar com humano.

---

## Resumo geral
- **5 skills consolidadas** (3 novas criadas do zero, 2 masters editadas in-place).
- **16 skills arquivadas** (movidas via `mv` para `_archived/`, nada deletado): 4 + 2 + 8 + 1 + 1.
- **2 skills não tocadas, apenas cross-linkadas:** `adonisjs-pdf-coordinate-editing-best-practices`, `vue-draggable-next-best-practices`.
- **Sem perda técnica nos clusters 1, 2, 4.** Deduplicação pura.
- **Pontos que exigem revisão humana:**
  1. **Cluster 3:** fidelidade visual pós-conversão Tailwind→UnoCSS (Threads, GBP) e colapso dos 3 simuladores de vídeo num exemplo único.
  2. **Cluster 5:** descarte completo do `references/` TypeScript (frameworks fora de escopo + exemplos de auth JWT/bcrypt) — confirmar que nenhum valor genérico foi perdido além do reescrito.
  3. **Cluster 1:** ressalva de throttling por tenant depender de BullMQ Pro vs open-source.