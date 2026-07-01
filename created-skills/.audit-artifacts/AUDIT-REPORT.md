# Relatório de Auditoria — 173 Skills (Migração EngeApp Laravel → AdonisJS Node)

## 1. Resumo executivo

**Contagens por severidade** (sobre as 137 skills presentes no dataset):

| Severidade | Qtd | % |
|---|---|---|
| high | 12 | ~9% |
| medium | 35 | ~26% |
| low | 70 | ~51% |
| ok | 20 | ~15% |

**Saúde geral:** O conjunto é tecnicamente competente e majoritariamente aderente ao stack-alvo. As skills-âncora do contrato (MaxPinia endpoint patterns, pinia-state-management, complex-modal-forms-autosave, transmit-sse, auth session) são corretas e bem fundamentadas no código-fonte real. Porém há três classes sistêmicas de problema que precisam de varredura coordenada:

1. **Resíduo Laravel/projeto-anterior:** realtime via Pusher/Soketi/Reverb e Laravel Echo (em vez de Transmit/SSE), auth Bearer/JWT e `/sanctum/csrf-cookie` (em vez de sessão+cookie), e domínio "SocialMediaApp/Instagram/MarketingAgency" vazado em dezenas de exemplos (em vez de fotovoltaico/solar_company).
2. **Violações da regra central MaxPinia:** várias skills de front ainda ensinam `axios.get/post` manual e save por submit em vez de delegar GET/save à store `@maxvue/max-pinia`.
3. **Erros de API factuais:** APIs estilo Eloquent/Laravel inexistentes no Lucid v6 (`addGlobalScope`, `Event.dispatch`, `Mail.fake()`), divergências PostgreSQL vs MariaDB, e nomes de rota estilo Ziggy (`'user.data'`) nos exemplos de `apiGetRoute`.

As 12 skills `high` exigem reescrita parcial ou total; as 35 `medium` exigem correções pontuais relevantes.

---

## 2. Violações de escopo (severity high/medium)

| Skill | Problema | Correção sugerida |
|---|---|---|
| `adonisjs-broadcasting-websockets` (high) | Skill inteira recomenda Pusher/Soketi/Reverb + `@laravel/echo-vue` no front | Reescrever do zero para `@adonisjs/transmit` (SSE) + `@adonisjs/transmit-client`; remover Echo/Reverb |
| `vue-frontend-bug-fixing` (high) | Lista `@laravel/echo-vue` como realtime e ferramentas MCP do Laravel Boost (`browser-logs`, `last-error`) | Trocar Echo→Transmit; remover tools Laravel Boost; corrigir versões (Vue Router v4, não v5); referir `@maxvue/max-pinia` em vez de Pinia genérico |
| `adonisjs-ai-agents-multi-agent-orchestration` (high) | Seção 4 "Sincronização em Tempo Real (Soketi/Pusher)" | Reescrever seção para broadcast via Transmit |
| `adonisjs-ai-agent-cost-analytics` (high) | Seção 5/description instruem broadcast via Pusher/Soketi (`private-system.${userId}`) | Remover Pusher/Soketi; usar Transmit; realinhar domínio (FQCN Laravel `App\Models\...`) |
| `vue-axios-api-integration` (high) | GET `/sanctum/csrf-cookie` antes do login + header `Authorization` baseado em token | Trocar para Shield + `withXSRFToken` (cookie XSRF-TOKEN); remover modelo de token |
| `adonisjs-multitenancy-data-isolation` (high) | `addGlobalScope`/`static boot()` são Eloquent, não existem no Lucid v6 | Reescrever com named scopes (`scope()`) + query hooks reais do Lucid |
| `adonisjs-edge-templates` (high) | Edge para layouts de página + hidratação de SPA (padrão Blade/Inertia) | Restringir Edge a emails e PDF/Puppeteer; deixar claro que páginas são Vue+MaxPinia |
| `adonisjs-events-listeners` (high) | Seção 7 recomenda broadcasting via Soketi/Pusher | Trocar para Transmit; corrigir DI do Logger |
| `vue-zod-schema-validation` (high) | Submit via `axios.post('/api/events')` manual | Reescrever submit para fluir pela store `@maxvue/max-pinia`/`apiPostRoute` |
| `vue-draggable-next` (high) | Persistência via `axios.post` manual no `@change` | Direcionar reordenação para store MaxPinia; corrigir import da lib |
| `vue-facebook-post-preview-simulator` (high) | Classes Tailwind (`bg-white`, `dark:bg-zinc-900`) | Migrar para UnoCSS attributify (presetMaxUno); usar MaxTitle/MaxButton |
| `vue-google-business-profile-post-preview-simulator` (high) | Classes Tailwind via `class="..."` | Idem Facebook (migrar para UnoCSS attributify) |
| `vue-3-dynamic-forms-schema-renderer` (high) | Imports manuais de componentes Max, grid/heading manuais, save por submit | Auto-import; `<MaxGrid>`/`<MaxTitle>`; save via store MaxPinia; `error.issues` (Zod 4) |
| `adonisjs-api-documentation-openapi` (medium) | Esquema padrão BearerAuth/JWT + ignore `/sanctum/csrf-cookie` | Documentar auth por cookie/sessão; ignorar catch-all da SPA, não rota Sanctum |
| `adonisjs-audio-transcription-analysis` (medium) | Usa SDK `openai` e `@google/genai` direto | Rotear transcrição/análise via Vercel AI SDK |
| `adonisjs-ai-agents-domain-catalog` (medium) | "SSE/WebSocket"; domínio quase todo Instagram | Citar só Transmit/SSE; realinhar agentes ao domínio solar (só Protocol Extractor casa) |
| `adonisjs-instagram-meta-token-renewal` (medium) | Cita "AdonisJS v6/v7" (v7 inexistente); `Event.dispatch()` estilo Laravel | Corrigir versão para v6; usar `emitter.emit(EventClass, data)` |
| `vue-inputs-masks-validation` (medium) | Cita "backend Laravel" como destino atual em vários pontos | Trocar para "backend AdonisJS"; direcionar save via MaxPinia |
| `vue-livekit-client-integration` (medium) | "Solicite o token ao backend Laravel" | Trocar para AdonisJS; obter token via store/`apiGetRoute` |
| `vue-rss-news-moderation-dashboard` (medium) | GET/POST manual via axios; IA não ancorada no Vercel AI SDK | MaxPinia para CRUD; explicitar Vercel AI SDK |
| `vue-instagram-comments-moderation-inbox` (medium) | "Use REST com Axios para despachar ações ao AdonisJS" | Ações de dados via MaxPinia |
| `vue-instagram-feed-grid-simulator` (medium) | Persistência "via axios manual" + imports manuais @maxvue | MaxPinia exclusivo; auto-import; corrigir import vue-draggable-next |
| `vue-instagram-stories-sticker-editor` (medium) | Seção de estilos cita Tailwind como opção | Remover Tailwind; restrição anti-Tailwind explícita |
| `vue-meta-api-oauth-integration` (medium) | Store/caminhos do SocialMediaApp; rota sem `/api`; GET manual | Realinhar domínio; prefixo `/api`; GET via MaxPinia |
| `vue-solar-roi-calculator-dashboard` (medium) | Cita skill backend Laravel como normativa | Referir a regra Adonis equivalente |
| `adonisjs-whatsapp-passwordless-authentication` (medium) | OAT/token apresentado como alternativa equivalente à sessão | Marcar sessão como padrão; OAT só para MCP/M2M; `auth.use('api').generate()` não existe |
| `technical-documentation` (medium) | Badges PHP/Laravel, auth Bearer nos templates | Trocar para Node/Adonis; auth por sessão |
| `typescript-documentation` (medium) | Exemplos NestJS/React/Angular + auth Bearer/JWT | Reancorar em Vue 3.6/Adonis; auth sessão |
| `frontend-design` (low→escopo) | Exemplos React/Framer/Tailwind/ShadCN | Reancorar em Vue/UnoCSS/MaxComponentsUi |

---

## 3. Lacunas de MaxPinia (front que deveria usar store para GET/save)

**Violações fortes (ensina caminho manual em vez de MaxPinia):**
- `vue-zod-schema-validation` — submit via `axios.post` manual (high)
- `vue-draggable-next` — persistência de ordem via axios (high)
- `vue-3-dynamic-forms-schema-renderer` — save por submit
- `vue-rss-news-moderation-dashboard` — GET/POST axios manual
- `vue-instagram-comments-moderation-inbox` — ações via Axios REST
- `vue-instagram-feed-grid-simulator` — reordenação "via axios"
- `vue-axios-api-integration` — mantém `useAuthStore` com axios.get/post manual (conflita com auth-session)
- `vue-tenant-client-context` — Pinia puro + `useCachedApi` solto em vez de MaxPinia
- `vue-meta-api-oauth-integration` — `axios.get('/social_media/.../auth-url')` direto
- `vue-max-use-usecachedapi-state-cache` — ensina cache/save manual (localStorage + apiPostRoute) que compete com MaxPinia
- `vue-offline-storage-localforage` — duplica o que MaxPinia já faz internamente
- `vue-max-stack-frontend` — contradição interna: `axios.get` manual nos exemplos vs regra MaxPinia da seção 6

**Lacunas brandas (deveria nomear `@maxvue/max-pinia` em vez de "Pinia genérico"/refs locais):**
- `vue-billing-subscription-headless`, `vue-brand-positioning-character-management`, `vue-flow-diagram-integration`, `vue-fullcalendar-integration`, `vue-image-cropping-resizing`, `vue-uppy-file-upload`, `vue-s3-presigned-urls` (backend), `vue-bouncer-roles-permissions-integration`, `vue-two-factor-authentication`, `vue-instagram-stories/reels-preview`, `vue-whatsapp-interactive-messages-simulator`, `vue-youtube-shorts-preview`, `vue-voice-recording`, `vue-ai-agent-playground`, `vue-typescript`, `vue-max-components-ui-wizard-stepper-forms`, `vue-solar-roi-calculator-dashboard`, `vue-splitpanes` (UI-local, aceitável), `vue-vitest-testing` (deveria mockar store MaxPinia, não só axios).

---

## 4. Erros técnicos relevantes (agrupados)

**A. APIs estilo Laravel/Eloquent inexistentes no Adonis v6 (graves):**
- `adonisjs-multitenancy-data-isolation`: `addGlobalScope`/`static boot()` — não existem no Lucid.
- `adonisjs-auth-bouncer-security`: `AuthorizeResult.deny()` — correto é `AuthorizationResponse.deny()`.
- `adonisjs-instagram-meta-token-renewal` & vários: `Event.dispatch()` — usar `emitter.emit(EventClass, data)`.
- `adonisjs-japa-testing`: `Mail.fake()`/`Event.fake()` — correto `mail.fake()`/`emitter.fake()`.
- `adonisjs-whatsapp-passwordless-authentication`: `auth.use('api').generate(user)` — usar `User.accessTokens.create(user)`.

**B. Imports/caminhos de pacote errados:**
- `adonisjs-puppeteer-image-generation`: `@adonisjs/core/services/drive` → correto `@adonisjs/drive/services/main`.
- `vue-max-components-ui-popovers-confirmations` & `wizard-stepper`: `@maxvue/components` / `max-components-ui` → correto `@maxvue/max-components-ui`.
- `vue-auto-import-components`: `maxUseAutoImport` usado como valor; é **função** (`maxUseAutoImport()`).
- `vue-draggable-next` / `vue-instagram-feed-grid`: `import { draggable }` named não existe.
- `adonisjs-vite8-full-config`: bloco `adonisrc.ts` com chave `vite` inexistente e import path errado.

**C. Divergência de banco (PostgreSQL vs MariaDB 11 do EngeApp):**
- `adonisjs-postgresql-jsonb`, `adonisjs-ai-agents-rag-vector-database` (pgvector), `adonisjs-activity-log-audit-trail` (JSONB/GIN), `adonisjs-vue-timezone-datetime` (timestamptz), `adonisjs-docker-development-environment`. Conflitam com `adonisjs-meilisearch` (usa `FIELD()` MySQL). **Confirmar o SGBD-alvo** e padronizar todas as skills.

**D. Rotas estilo Ziggy nos exemplos `apiGetRoute` (contradiz "caminhos string `/api/...`"):**
- `vue-pinia-state-management`: `apiGetRoute('user.data')`.
- `vue-max-use-usecachedapi-state-cache`: `'api.clients.index'`, `'api.data'`.
- Correção: usar `apiGetRoute('/api/...')` em todos.

**E. APIs do Vercel AI SDK inconsistentes entre skills:**
- `parameters` vs `inputSchema` (prompt-injection-defense vs base); `tc.args` vs `input/output` (observability); `experimental_objectGeneration` inexistente (sdk-google-gemini); modelos fictícios (`gemini-3.1-flash-lite`); `pipeDataStreamToResponse` a validar; `MockLanguageModelV3` (correto V2). **Padronizar contra a versão instalada.**

**F. APIs `@adonisjs/drive` incorretas:**
- `adonisjs-media-processing-ffmpeg`: ordem de args do `put(key, contents, opts)` invertida; `get()` tratado como Buffer.
- `adonisjs-s3-presigned-urls`: `s3Driver.client`/`config.bucket` não são API pública.

**G. APIs front desatualizadas/Zod legado:**
- `error.errors` → `error.issues` (Zod 4) em `vue-zod-schema-validation`, `vue-3-dynamic-forms`, `wizard-stepper`.
- `vue-livekit`: `room.participants` → `remoteParticipants`.
- `useTimeAgo()` dentro de `computed` (Facebook/Google preview simulators).
- `apiGetRoute`/`apiPostRoute` usados de forma síncrona em `vue-auth-session-state` (são async).

**H. Segurança:** `adonisjs-whatsapp-cloud-api` compara HMAC sem `crypto.timingSafeEqual`; `process.env` direto em vez de `env.get()` em várias skills (whatsapp, social-media-webhooks, google-business-profile, brazilian-payments-asaas).

**I. Env API:** `adonisjs-brazilian-payments-asaas`: `Env.schema({...})` errado (correto `Env.create(...)`); cita `@adonisjs/core/services/http` (inexistente).

---

## 5. Sobreposições e mesclagens propostas

**Cluster 1 — BullMQ (4 skills):** `bullmq-job-idempotency-deduplication` + `bullmq-job-resilience-retries` + `bullmq-multi-tenant-job-isolation` + `bullmq-queue-management`. → **Merge** numa skill-hub `adonisjs-bullmq-best-practices` (config/Worker base) com seções para idempotência, resiliência e multi-tenancy. A `queue-management` absorve as demais.

**Cluster 2 — Google OAuth (3 skills):** `google-analytics-ga4` + `google-business-profile` + `google-calendar`. → Extrair skill-base `adonisjs-google-oauth-token-service` (refresh token criptografado, padrão comum) e deixar cada integração focada na API específica.

**Cluster 3 — Auth/sessão (2 skills):** `auth-bouncer-security` + `auth-remember-me`. → A parte de sessão do remember-me é absorvida por auth-bouncer; manter remember-me só como nota sobre `useRememberMeTokens:false`.

**Cluster 4 — Lucid (3 skills):** `lucid-orm` (hub) + `lucid-brazilian-data-queries` + `lucid-soft-deletes-cascade`. → Manter `lucid-orm` como fundação e cross-linkar; sem merge total (escopos distintos).

**Cluster 5 — PDF/Puppeteer/render (3 skills):** `puppeteer-image-generation` + `reporting-pdf-excel` + `pdf-coordinate-editing`. → `reporting-pdf-excel` e `puppeteer-image-generation` compartilham Puppeteer+Edge+BullMQ+Drive → **merge** numa `adonisjs-puppeteer-rendering`. `pdf-coordinate-editing` fica separada (pdf-lib/coordenadas).

**Cluster 6 — Notificações (2 skills):** `slack-notifications` + `telegram-bot-notifications-approval`. → Mesmo padrão (serviço+fila+retry+payload rico) → cross-link ou skill-base `adonisjs-outbound-notifications`.

**Cluster 7 — MaxMoney (2 skills):** `maxmoney-bank-reconciliation` + `maxmoney-recurring-transactions`. → Agrupar sob guarda-chuva MaxMoney; cross-link.

**Cluster 8 — Billing core/EFI (2 skills):** `typescript-billing-core-architecture` + `typescript-max-banks-efi-gateway`. → Par natural (contrato vs adaptador); cross-link, não merge.

**Cluster 9 — Simuladores de social preview (6 skills):** `facebook-post-preview` + `google-business-profile-post-preview` + `instagram-feed-grid` + `instagram-reels-preview` + `instagram-stories-preview` + `tiktok-video-preview` + `threads-post-preview` + `youtube-shorts-preview`. → **Consolidar** numa skill genérica `vue-social-post-preview-simulator` com variantes (feed/stories-reels-9:16/link-card). Reduz ~8 skills de domínio externo a 1-2.

**Cluster 10 — MaxPinia/cache front (3 skills):** `pinia-state-management` (hub) + `max-use-usecachedapi-state-cache` + `offline-storage-localforage`. → As duas últimas devem **subordinar-se** ao hub (MaxPinia primeiro; localforage/useCachedApi só casos de borda).

**Cluster 11 — Ecossistema Max front (2 skills):** `vue-max-ecosystem` + `vue-max-stack-frontend`. → Forte sobreposição → **merge** (stack-frontend como master absorve ecosystem).

**Cluster 12 — Debugging front (2 skills):** `vue-debugging` (catálogo) + `vue-frontend-bug-fixing` (processo). → Cross-link, não merge (ângulos distintos).

**Cluster 13 — TS geral (2 skills):** `typescript-advanced-types` + `typescript-tooling-monorepo`. → Delimitar fronteira (tooling não deve duplicar branded types/condicionais).

**Cluster 14 — Documentação (2 skills):** `technical-documentation` + `typescript-documentation`. → Sobrepõem ADR/JSDoc/doc-API → consolidar.

---

## 6. Problemas de description/triggering

- **Bilíngue/desleixado:** `adonisjs-access-tokens-auth`, `adonisjs-ally-oauth` (PT+EN no meio da frase).
- **Reforça escopo errado:** `adonisjs-broadcasting-websockets` (cita Pusher/Soketi/laravel-echo como gatilho); `adonisjs-ai-agents-tool-calling` (cita "Google Gemini SDK"); `adonisjs-whatsapp-passwordless` (lista "Auth: Session or OAT"); `adonisjs-ai-agent-cost-analytics` (cita Pusher/Soketi).
- **Domínio errado (SocialMediaApp em projeto EngeApp):** `adonisjs-google-business-profile` (cita "SocialMediaApp"), `vue-max-components-ui-wizard-stepper-forms`, `vue-vue-timezone-datetime` ("scheduling social media posts"), `vue-rss-news-moderation`.
- **Referências cruzadas quebradas:** `vue-max-ecosystem` aponta `vue-maxvue-frontend-best-practices` (nome real é `vue-max-stack-frontend`); várias citam skills não presentes no lote (`adonisjs-ai-agents-request-resilience-costs`, `vue-tenant-client-context` em alguns, `vue-max-pinia-integration`).
- **Triggers fracos:** `adonisjs-japa-testing` (description curta/genérica); `vue-brand-positioning-character-management` (muito acoplada a nomes internos de arquivo).
- **Inconsistência de nome de projeto:** `vue-vitest-testing` (mistura "Maxdmin" no frontmatter e "Engeapp" no corpo).
- **Sem H1:** `vue-eslint-stylelint-quality-standards` (corpo começa em `## Objetivo`).

---

## 7. Plano de ação priorizado

**P0 — Reescritas de violação de escopo (bloqueiam o stack-alvo):**
1. `adonisjs-broadcasting-websockets` → reescrever 100% para Transmit/SSE.
2. `vue-frontend-bug-fixing` → remover Echo + Laravel Boost MCP; corrigir versões; MaxPinia.
3. `vue-axios-api-integration` → remover `/sanctum/csrf-cookie` e token; Shield + withXSRFToken.
4. `adonisjs-multitenancy-data-isolation` → reescrever sem `addGlobalScope` (named scopes Lucid).
5. Remover Pusher/Soketi de `ai-agent-cost-analytics`, `multi-agent-orchestration`, `events-listeners`.
6. `adonisjs-edge-templates` → restringir Edge a email/PDF.

**P1 — Correções de API que quebram exemplos:**
7. `auth-bouncer-security` (`AuthorizationResponse`); `japa-testing` (`mail.fake()`/`emitter.fake()`); `whatsapp-passwordless` (`accessTokens.create`); `instagram-meta-token-renewal` (`emitter.emit` + v6).
8. Imports: `puppeteer-image-generation` (drive path), `max-components-ui-popovers`/`wizard` (`@maxvue/max-components-ui`), `auto-import-components` (`maxUseAutoImport()`), `vite8-full-config` (adonisrc).
9. `brazilian-payments-asaas` (`Env.create`, remover services/http); `media-processing-ffmpeg` & `s3-presigned-urls` (Drive API).

**P2 — Conformidade MaxPinia (regra central):**
10. Converter para store MaxPinia: `vue-zod-schema-validation`, `vue-draggable-next`, `vue-3-dynamic-forms`, `vue-rss-news-moderation`, `vue-instagram-comments-moderation`, `vue-instagram-feed-grid`, `vue-tenant-client-context`, `vue-meta-api-oauth`.
11. Corrigir rotas Ziggy → string `/api/...` em `pinia-state-management` e `usecachedapi-state-cache`.
12. Subordinar `usecachedapi-state-cache` e `offline-storage-localforage` ao MaxPinia.

**P3 — Decisão de infraestrutura transversal:**
13. **Confirmar SGBD-alvo (MariaDB vs PostgreSQL)** e alinhar `postgresql-jsonb`, `rag-vector-database`, `activity-log`, `vue-timezone-datetime`, `docker-dev`, `meilisearch`.
14. **Fixar versão do Vercel AI SDK** e padronizar `inputSchema`, campos de tool, nomes de modelo reais, `generateObject` em todas as skills de AI.
15. Migrar simuladores social (Facebook/GBP) de Tailwind → UnoCSS attributify.

**P4 — Higiene (merges + descriptions):**
16. Executar os merges dos Clusters 1, 2, 5, 9, 11, 14.
17. Realinhar domínio "SocialMediaApp/Instagram/MarketingAgency" → "solar_company/EngeApp" nos exemplos e descriptions.
18. Corrigir referências cruzadas quebradas e descriptions bilíngues/fracas.

**Caminho de menor risco:** P0 e P1 primeiro (desbloqueiam o stack e impedem código quebrado), depois a decisão de SGBD/versão AI (P3, transversal), em seguida P2 (MaxPinia) e por fim a consolidação (P4).

**Skills de referência a usar como gabarito** ao corrigir as demais: `adonisjs-maxpinia-endpoint-patterns`, `vue-pinia-state-management`, `vue-complex-modal-forms-autosave`, `adonisjs-transmit-sse`, `vue-adonis-transmit-sse`, `adonisjs-auth-remember-me`, `adonisjs-ally-oauth` (todas confirmadas aderentes ao contrato).