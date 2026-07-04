# Auditoria created-skills — Parte 2: Necessidade & Duplicatas

Data: 2026-07-04. 170 skills medidas por USO REAL (grep no código de engeapp + libs Max) via subagentes.

---
## A) SKILLS DUPLICADAS (mescláveis)

**Só 1 merge real em toda a coleção.** O resto são pares complementares (muitos back/front do mesmo
assunto, que tratam lados diferentes) — melhor resolver com cross-ref, não merge.

### MERGE recomendado (único DUPLICATA_FORTE)
- **`typescript/typescript-advanced-types` ⬅ absorve a seção type-level de `typescript/typescript-tooling-monorepo`.**
  Evidência: bloco de strict-config JSON idêntico byte-a-byte, branded types e `expectTypeOf` duplicados.
  Ação: advanced-types vira a fonte canônica type-level; tooling-monorepo fica só com perf/monorepo/migração/module-resolution + cross-ref.

### Limpezas de duplicação LITERAL (sem colapsar skills)
- Bloco Axios + interceptor 401/403/422/500 repetido em 3 skills de auth (`vue-axios-api-integration`,
  `vue-auth-session-state`, `laravel-vue-login-maxauthcard`) → tornar `vue-axios-api-integration` canônica; as outras apontam.
- `Cache::lock` repetido em `laravel-cache` ↔ `laravel-redis` → cross-ref recíproco; alinhar convenção de chave/tags.

### Contradições de consistência a reconciliar (não é merge, é bug)
- `vue-max-stack-frontend` ↔ `vue-pinia-state-management`: `options.key` e nomes de flags de status
  (`is_requested` vs `is_requesting`/`is_success`) divergem. Alinhar pela fonte real do MaxPinia.

### Complementares (MANTER, no máximo cross-ref)
Pares back/front (gemini file-api↔php-sdk, socialite↔token-lifecycle, livekit server/client, meta back/front,
code-generators back/front, image back/front); billing 4 camadas; ecossistema Max (stack/api-ref/components-dev);
AI backend (ecosystem + agentes de domínio); simuladores social; debugging (genérico/engeapp/agnóstico);
brazilian (data/localization/payments); testing (pest/vitest/playwright). NOTA: Efí aparece em 2 stacks
(TS `@maxvue/max-banks` mTLS vs PHP EfiPay SDK) — adicionar cross-ref entre as duas.

---
## B) SKILLS DESNECESSÁRIAS (pouco/nada usadas no projeto)

Dois grupos: **(1) instalado/nativo mas ~0 uso** e **(2) não instalado / feature ausente (aspiracional)**.
Dentro dos aspiracionais, separo os **de domínio/roadmap plausível** (candidatos a backlog) dos **fora do roadmap**.

### B1. Instalado (ou nativo) porém praticamente SEM USO — remover ou reescrever
| Skill | Evidência |
|---|---|
| backend/laravel-action-classes | sem `app/Actions`; projeto usa Services/Jobs |
| backend/laravel-context-metadata-tracking | `Context::` = 0 ocorrências |
| backend/laravel-docx-generation-phpword | phpword instalado, 0 uso (docs via dompdf/mpdf) |
| backend/laravel-excel-import-export | maatwebsite instalado, 0 uso (usa phpspreadsheet direto) |
| backend/laravel-lighthouse-graphql | instalado sem schema/config; API é REST |
| backend/laravel-hashids-obfuscation | vinkla/hashids instalado, 0 uso real |
| backend/laravel-image-processing-intervention | só 2 arquivos; projeto usa spatie/medialibrary | 
| backend/laravel-audio-processing-ffmpeg | só 1 serviço (AudioConverterService) |
| backend/laravel-pulse-custom-recorders-and-cards | Pulse é dashboard; 0 recorders/cards customizados |
| backend/laravel-slack-notifications | config existe mas única ref é linha COMENTADA |
| frontend/vue-flow-diagram-integration | @vue-flow/core instalado, 0 uso (unifilar é próprio) |
| frontend/vue-max-components-ui-wizard-stepper-forms | `useStepper` = 0 (só LoadStepper de load) |
| frontend/vue-uppy-file-upload | Uppy direto = 0 (uploads via VueFinder) |
| frontend/vue-voice-recording | lib não importada; app usa MediaRecorder custom (corrigir a skill) |
| frontend/vue-tenant-client-context | isolamento tenant/useSelectedClient inexistente |

### B2. NÃO instalado / feature ausente — FORA do roadmap → candidatos a remoção
| Skill | Evidência |
|---|---|
| backend/laravel-activity-log | spatie/laravel-activitylog NÃO instalado |
| backend/laravel-backup | spatie/laravel-backup NÃO instalado |
| backend/laravel-sentry-integration | NÃO instalado; obs. já é Telescope/Pulse/Clockwork |
| backend/laravel-rdstation-crm-integration | 0; sem pacote nem código nem sinal de roadmap |
| backend/laravel-google-calendar-integration | sem pacote; calendário é interno (fullcalendar) |
| frontend/vue-sentry-error-tracking | @sentry/* NÃO instalado |
| frontend/vue-tiptap-rich-text-editor | @tiptap NÃO instalado; sem editor rich-text |
| frontend/vue-playwright-e2e-testing | NÃO instalado; E2E real é Puppeteer |
| frontend/vue-zod-schema-validation | zod NÃO instalado; 0 uso |
| frontend/vue-3-dynamic-forms-schema-renderer | depende de Zod (ausente); sem schema-renderer |
| frontend/vue-image-cropping-resizing | Cropper.js NÃO instalado |
| frontend/vue-i18n-localization | vue-i18n NÃO instalado; app é pt-BR único |
| frontend/vue-ai-agent-playground | nenhuma página/feature de playground LLM |

### B3. Aspiracional de DOMÍNIO/roadmap plausível → manter como backlog (não remover)
- backend/laravel-pennant-feature-flags (skill já avisa "instale primeiro")
- backend/laravel-solar-inverter-telemetry-monitoring (domínio solar; telemetria não implementada)
- backend/laravel-solar-irradiance-cresesb-nasa (domínio solar; estimativa por coordenadas não implementada)
- backend/laravel-tiktok-api-integration (roadmap redes sociais; hoje só Meta)
- frontend/vue-social-post-preview-simulator (domínio social; simuladores ausentes)
- frontend/vue-solar-roi-calculator-dashboard (domínio FV; dashboard ROI/payback ausente)
- frontend/vue-instagram-comments-moderation-inbox (domínio social; inbox ausente)
- frontend/vue-instagram-stories-sticker-editor (domínio social; editor ausente)
- frontend/vue-billing-subscription-headless (billing existe só na lib MaxBanks, não integrado ao engeapp)

### B4. Genéricas/tooling (já sinalizadas na Parte 1) → decisão pendente do usuário
- caveman-suite/* (7) — hook `mode-tracker` ausente; inertes.
- agent-tooling/prompt-generator (coreano), find-skills, agent-browser (CLI não instalado).

### Marginais mas legítimas (KEEP) — uso pontual real, não remover
keep-alive/dynamic-components, cookie-consent-lgpd, chartjs, fullcalendar, html-to-image, splitpanes,
virtual-scroller, offline-localforage, pdf-viewer, vapor-mode, view-transitions (rebaixar seção GSAP não instalado).
