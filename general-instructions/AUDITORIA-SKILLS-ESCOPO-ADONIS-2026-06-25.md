# AUDITORIA DE SKILLS — Escopo de Migração Laravel → AdonisJS/Node

> Gerada em 2026-06-25. Reauditoria das skills em `created-skills/` (184 skills, EN-only) contra o
> projeto-fonte **engeapp** (Laravel) e o **escopo-alvo** declarado da migração para Node/Adonis.
> Método: 4 auditorias paralelas (camada de IA vs Vercel AI SDK · camada de dados front-end vs MaxPinia ·
> realtime + tooling · cobertura feature→skill) + lint mecânico próprio. Complementa
> `PLANO-OTIMIZACAO-SKILLS.md` (Fases 0–2b concluídas).

## Escopo-alvo (referência da auditoria)
Backend: **AdonisJS**, **Vercel AI SDK** (`ai` + `@ai-sdk/*`), **AdonisJS Transmit (SSE)**.
Front-end: **Vite 8**, **Vue v3.6.0-beta.17** (vapor), **Vue Router v5**, **UnoCss + presetMaxUno** (de MaxComponentsUi),
**unplugin-auto-import + unplugin-vue-components**, libs locais **MaxUse**, **MaxComponentsUi**, **MaxPinia**.
Regra-âncora: **todo GET do front-end passa por uma store MaxPinia** (cache + auto-save; alterar dado → backend atualiza).

---

## 0. MUDANÇA ESTRUTURAL DESDE O PLANO ANTERIOR
- **`created-skills-pt-br/` foi removido.** A biblioteca é agora **EN-only** (184 skills, todas `CONCLUIDA` no yaml).
  → Todo o problema de "drift bilíngue / 164 pares EN↔PT" do `PLANO-OTIMIZACAO-SKILLS.md` §2 está **OBSOLETO**.
- Contagens atuais: `backend-node` 103 · `front-end-vue` 74 · `general` 7.

---

## 1. 🔴 ERROS CONCRETOS (corrigir já)

| # | Skill(s) | Erro | Correção |
|---|---|---|---|
| 1 | 7 skills de IA¹ | **Model IDs `gemini-3.5-flash` / `gemini-3.1-flash-lite` / `gemini-3.0-*`** — sub-versões inconsistentes; podem dar 404 em runtime. | **Verificar contra o catálogo atual do Google** e pinar IDs reais conhecidos (`gemini-2.5-flash/-pro`, `gemini-2.0-*`). Centralizar a lista num único ponto. |
| 2 | `adonisjs-ai-streaming-responses-gemini` | API depreciada `result.pipeDataStreamToResponse()` (linhas 18, 42). Não roda no `ai` atual. | Migrar para `toUIMessageStreamResponse()` / `pipeUIMessageStreamToResponse()`, idealmente via Transmit/SSE. |
| 3 | `adonisjs-ai-image-generation` × `adonisjs-ai-video-generation-heygen` | **Contradição de storage**: uma proíbe `fs` ("sempre `@adonisjs/drive`"), a outra manda `node:fs/promises`. | Unificar política de storage (`@adonisjs/drive`) nas duas. |
| 4 | `vue-max-use-development`, `vue-max-components-ui-development`, `vue-typescript-best-practices` | **Sem H1** — começam direto em `## Objetivo`. | Adicionar título H1 descritivo (padrão das demais). |
| 5 | `vue-vapor-mode` | **Zero blocos de código** — skill técnica de opt-in sem exemplos. | Adicionar exemplos (`defineVaporComponent`, `createVaporApp`, `vaporInteropPlugin`). |
| 6 | `vue-unocss-styling` | Ensina `presetWind3` **junto** de `presetMaxUno`; README do MaxComponentsUi mostra `presetMaxUno()` sozinho. | Confirmar o setup real do projeto e alinhar. |
| 7 | `adonisjs-audio-transcription-analysis` | Usa `@google/genai` + `openai` crus — **fura a abstração Vercel AI SDK**. | Reframe para `experimental_transcribe` + provider `@ai-sdk/*`. |
| 8 | `vue-max-components-ui-wizard-stepper-forms` | Risco de implicar componente `MaxWizard`/`MaxStepper` **inexistente** na lib. | Grep por `MaxStep`/`MaxWizard`/`Stepper`; reframe como "composição de multi-step com MaxModal/MaxGrid/MaxButton". |
| 9 | Vários `adonisjs-ai-agents-*` | Param `maxCalls` **não é** opção do Vercel AI SDK (`maxSteps`/`stopWhen: stepCountIs()` são). | Documentar como campo do wrapper custom ou remover. |

¹ `adonisjs-ai-sdk-google-gemini`, `-ai-agents-request-resilience-costs`, `-ai-agents-event-replanning`, `-ai-agents-structured-outputs-zod`, `-ai-agents-graphic-editor-and-art-analyst`, `-ai-agents-strategy-manager`, `-ai-agents-protocol-extractor`.

**Inconsistências cruzadas de config (realtime + tooling):**
| # | Skill(s) | Erro | Correção |
|---|---|---|---|
| 10 | `vue-adonis-transmit-sse` (front) | Usa `transmit.authorizeChannel()` (legado); a skill backend usa o correto `transmit.authorize()`. | Padronizar em `authorize()`. |
| 11 | `adonisjs-vite8-full-config` × `vue-vite-bundling-optimization` | `chunkSizeWarningLimit: 4000` (vite8) vs aviso explícito contra `4000` (bundling); + dois formatos divergentes de `manualChunks` p/ o mesmo `vite.config.ts`. | Reconciliar; eleger config canônica. |
| 12 | `adonisjs-vite8-full-config` × `vue-auto-import-components` | Import de `MaxComponentsUiResolver` divergente: `'@maxvue/max-components-ui'` vs `'@maxvue/max-components-ui/resolver'` (correto = `/resolver`); + contrato de `maxUseAutoImport` (função vs array) inconsistente. | Alinhar pelo `/resolver`; fonte única no skill de auto-import. |
| 13 | `adonisjs-vite8-full-config` | Pins velhos: `unplugin-auto-import ^0.18.0`, `unplugin-vue-components ^0.27.0`, `@vitejs/plugin-vue ^5`; Vue não pinado em `3.6.0-beta.17`. | Atualizar pins ao alvo. |
| 14 | `adonisjs-vite-local-https-ssl` | Entrypoint JS-era `resources/js/app.js` + `reload:true`; vite8 usa `resources/app.ts` + `reloadServer:false`. | Alinhar ao config TS/alvo. |

✅ Sem code fences abertos · sem H1 = nome-da-pasta · sem drift de wake-word (PT-BR removido).

---

## 2. 🟡 CORREÇÕES DE ESCOPO (reframe para a nova stack)

| Skill | Problema de escopo | Ação |
|---|---|---|
| **`adonisjs-broadcasting-websockets`** | Ensina **Pusher/Soketi + `@laravel/echo-vue`** — porta o modelo Laravel Echo/Reverb; **contradiz Transmit-SSE**. | **DEPRECAR** (ou estreitar a um caso bidirecional documentado). Mover usuários p/ `adonisjs-transmit-sse-realtime`. |
| **`adonisjs-ai-sdk-google-gemini`** | É de fato a skill **fundacional do Vercel AI SDK**, mas o nome a prende a "gemini". | **RENOMEAR → `adonisjs-vercel-ai-sdk-best-practices`**; tornar a escolha de provider explícita. |
| `adonisjs-ai-financial-insights-gemini`, `adonisjs-ai-streaming-responses-gemini` | Nomes presos a "gemini" sendo provider-agnósticos. | Remover "gemini" do nome. |
| **`vue-pinia-state-management`** | É a skill **MaxPinia** (já manda "todo GET via store"), mas o nome sugere Pinia puro. | **RENOMEAR → `vue-maxpinia-state-management`** (descoberta + evita implicar pinia vanilla). |
| **`vue-max-use-usecachedapi-state-cache`** | Ensina **2º mecanismo de cache de GET** (`useRefCachedApi`→localStorage) que **compete com a regra MaxPinia**. | **DEPRECAR ou reframe**: usar só p/ caches efêmeros fora de store; deixar claro que GET de dados = MaxPinia. |
| `vue-offline-storage-localforage` | MaxPinia já usa LocalForage internamente. | Manter só p/ uso direto idb-keyval/localforage; notar sobreposição. |
| `vue-router-best-practices` | Não menciona **v5** (conteúdo estilo v4). | Reframe p/ Vue Router v5. |
| `vue-vite-bundling-optimization`, `adonisjs-vite8-full-config` | Sem menção a **Vite 8** / Rolldown. | Pinar e revisar p/ Vite 8. |
| `vue-axios-api-integration` | ✅ **Já alinhado** (proíbe GET via axios, escopo POST/PUT/DELETE + transporte interno do MaxPinia). | KEEP. |

---

## 3. 🟢 FUSÕES / DEDUPLICAÇÃO

- **Trio guarda-chuva Max** (`vue-max-stack-frontend`, `vue-max-ecosystem`, `vue-maxvue-frontend`): cobrem o mesmo terreno (SFC + componentes + MaxUse + MaxPinia + UnoCss).
  → **Canônico = `vue-max-stack-frontend`** (mais completo). **Fundir `vue-maxvue-frontend` nele** (é um índice raso que se auto-delega). Manter `vue-max-ecosystem` só se reescopado como **catálogo de API** de componentes/utils.
  → Manter separadas as 2 skills *de desenvolvimento da lib* (`vue-max-use-development`, `vue-max-components-ui-development`) — são maintainer-facing.
- **IA — resiliência/custo**: `adonisjs-ai-agents-request-resilience-costs` repete `FALLBACK_CHAIN`/tracking já em `adonisjs-vercel-ai-sdk` §2/§5 → consolidar no fundacional.
- **IA — tool calling**: `adonisjs-ai-agents-tool-calling` sobrepõe `adonisjs-ai-agents-best-practices` (`tool()`+Zod) → fundir seção.
- **IA — copywriter**: `adonisjs-ai-agents-copywriter` + `-copywriter-reviewer` (config/fluxo quase idênticos) → fundir em pipeline único.
- **IA — catálogo de agents**: os 7 agents específicos do app (copywriter, reviewer, event-replanning, graphic-editor/art-analyst, protocol-extractor, strategy-manager, theme-extractor) seguem o mesmo template `AgentConfig`+prompt-XML+BullMQ → avaliar **1 skill "catálogo de agents"** regida pela `adonisjs-ai-agents-best-practices`.

---

## 4. ⚪ SKILLS POSSIVELMENTE MORTAS (zero sinal no engeapp/plano de migração — confirmar com grep antes de retirar)
- `adonisjs-ai-video-generation-heygen` (heygen: 0 hits, sem dep)
- `adonisjs-ai-text-to-speech-elevenlabs` (app faz *gravação* de voz e *transcrição*, não TTS)
- `adonisjs-mcp-server-integration` (sem MCP no engeapp)
- `adonisjs-google-business-profile-api-integration` + `vue-google-business-profile-post-preview-simulator`
- `adonisjs-google-analytics-ga4-integration`
- Simuladores fora do escopo social do app: `vue-threads-post-preview-simulator`, `vue-youtube-shorts-preview-simulator`, `vue-instagram-comments-moderation-inbox`, `vue-instagram-stories-sticker-editor`
- `vue-cookie-consent-lgpd`, `vue-i18n-localization` / `adonisjs-i18n-brazilian-localization` (sem feature i18n/consent encontrada — especulativo)

---

## 5. 🔵 LACUNAS — TOP propostas de novas skills (risco × tamanho do gap)
1. **`adonisjs-solar-electrical-engineering-calc`** — motor de cálculo FV/elétrico (Isc/Voc, queda de tensão, NBR 16149). **Crítico de segurança** ("CUIDADO MÁXIMO" no plano), alimenta o AgentDesignEngineer. *Sem skill.*
2. **`adonisjs-browser-automation-rpa-playwright`** (+ anti-captcha) — bloco 13 só tem puppeteer-image (não-RPA). 13 tools de browser sem skill.
3. **`adonisjs-ai-document-datasheet-extraction`** — AgentDatasheetReader/DocumentReader/BilletReader (extração estruturada Gemini).
4. **`adonisjs-bank-ticket-payment-agent-efi`** — AgentBankTicketProcessor + Pay/CheckBankTicket (pagamentos irreversíveis; precisa guardrails).
5. **`adonisjs-geolocation-cep-cnpj-maps`** — ViaCEP/ReceitaWS/Correios + Google Places + proj4/UTM (bloco 11 só tem ORM genérico).
6. **`adonisjs-technical-document-generation`** — diagramas unifilar/multifilar, memoriais, formulários por concessionária (mPDF/TCPDF/PhpWord).
7. **`adonisjs-digital-signature-autentique`** — PowerAttorney + webhook Autentique → SignatureService.
8. **`adonisjs-livekit-server-integration`** — sala/token/status (front já tem skill; backend não).
9. **`adonisjs-trello-bidirectional-sync`** — TrelloService + webhook + board Kanban.
10. **`adonisjs-banco-inter-pj-integration`** — `inter-co/pj-sdk-php` (só EFI está coberto).
11. **`stryker-mutation-testing`** (general) — todo bloco do plano pede `mutation_tests`; sem skill.
12. **`adonisjs-customer-success-health-score-ai`** — AgentHealthScore + MessageAnalyzer.

**Fundacionais de escopo também faltando:** skill de **streaming SSE via AdonisJS Transmit + Vercel AI SDK** (`streamText`→Transmit); **`vue-maxpinia`** dedicada (hoje embutida em `vue-pinia-state-management`, ver §2).
Secundárias: WhapiCloud (2º provider WhatsApp), OnlyOffice/VueFinder, processamento raster de imagem de inversor, SEO/SSR do site público, editor de diagrama unifilar (Vue).

---

## 6. 🛠️ GOVERNANÇA / DOCS DESATUALIZADOS
- **`execute.md`** ainda **manda criar cópia PT-BR** em `created-skills-pt-br/` (linhas 5, 31, 64, 78) — pasta **inexistente**. Cada nova execução tentaria recriar a árvore. **Remover etapa bilíngue.**
- **`proposal.md`** e `general-instructions/vue-components.md` referenciam pt-br/Laravel — revisar.
- **`list-skills.yaml`**: ainda contém item de backlog **Laravel Echo** (`vue-laravel-echo-broadcasting-best-practices`, linha 1828) e `resumo`s citando Laravel Echo (1972/2088) — **incompatível com Transmit-SSE**; e `update-list.md` tem 1 ref Laravel.
- `PLANO-OTIMIZACAO-SKILLS.md` §2 (drift bilíngue) está obsoleto — anotar.

---

## 7. ORDEM SUGERIDA DE EXECUÇÃO
1. **Erros §1** (model IDs, API depreciada, H1 faltando, contradição de storage) — baixo risco, alto retorno.
2. **Governança §6** (parar de gerar PT-BR; limpar backlog Laravel-Echo do yaml).
3. **Correções de escopo §2** (deprecar broadcasting-websockets; renomes IA + MaxPinia; deprecar usecachedapi).
4. **Fusões §3** (trio Max; consolidações de IA).
5. **Revisar skills mortas §4** (grep no `engeapp/app/` antes de retirar).
6. **Propostas de lacunas §5** via pipeline `proposal.md` (priorizar solar-calc e RPA).
