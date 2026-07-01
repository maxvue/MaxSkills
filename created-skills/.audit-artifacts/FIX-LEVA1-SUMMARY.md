# Resumo da Correção de 66 Skills (Migração EngeApp → Adonis)

## 1. Editadas vs Puladas

- **Skills editadas:** 66 de 66 (todas tiveram `edited: true`).
- **Skills puladas integralmente:** 0.
- O termo "pulado" aqui refere-se a *findings* individuais descartados dentro de skills editadas (ver seção 3).

## 2. Principais Classes de Correção Aplicadas

**Realtime (Pusher/Soketi/Reverb → AdonisJS Transmit/SSE)**
Substituição sistemática de WebSockets/laravel-echo por `@adonisjs/transmit` (backend) e `@adonisjs/transmit-client` (frontend). Afetou broadcasting, events-listeners, ai-agents, reporting, ai-cost-analytics, instagram-comments, frontend-bug-fixing, ai-agents-domain-catalog.

**MaxPinia (axios manual → store @maxvue/max-pinia)**
GET/save de dados de página roteados via store com cache + auto-save debounced; rotas como strings `/api/...` via `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`. Afetou axios-integration, zod, draggable, uppy, s3-presigned, billing, dynamic-forms, instagram-feed/comments, tenant-client, livekit, rss-news, solar-roi, max-stack-frontend, pinia, usecachedapi, meta-oauth, auth-session.

**Ziggy/route() → strings `/api/...`**
Eliminação de nomes de rota Laravel em pinia, usecachedapi, instagram-feed.

**Auth (Bearer/JWT/Sanctum → sessão+cookie guard web)**
Remoção de `/sanctum/csrf-cookie`, headers Authorization/Bearer, X-CSRF-TOKEN manual; adoção do cookie XSRF-TOKEN do Shield. Afetou axios-integration, openapi, mcp-server, whatsapp-passwordless, uppy, tenant-client, technical-docs, typescript-docs.

**IA (SDKs diretos → Vercel AI SDK)**
`openai`/`@google/genai` → `ai` + `@ai-sdk/*`; correção de modelos Gemini inexistentes e APIs (`generateObject`, `tc.input`/`tr.output`). Afetou audio-transcription, ai-sdk-gemini, ai-agents-observability, rss-news.

**APIs Lucid v6 / AdonisJS v6 incorretas (estilo Eloquent/Laravel)**
Correções de `addGlobalScope`/`boot()` → query hooks; `whereJson*` inexistentes → `whereJsonSuperset/Subset`; `Model.db.raw` → `db` service; `@afterSave` frágil → `@afterCreate`/`@afterUpdate`; `Env.schema` → `Env.create`; emitter v6; `result.error.errors` → `.issues` (Zod 4); imports de Drive/logger/scope. Afetou multitenancy, postgresql-jsonb, rag-vector, activity-log, soft-deletes, lucid-brazilian, vinejs, vite8, exception-handling, media-ffmpeg, puppeteer, asaas.

**Vazamento de domínio (SocialMediaApp → fotovoltaico/EngeApp)**
Renomeação de modelos/colunas (MarketingAgency→SolarCompany, SocialMediaCredential→domínio específico) e exemplos. Afetada a maioria das skills de backend.

**UI (Tailwind → UnoCSS attributify + MaxComponentsUi, auto-import)**
Conversão de classes Tailwind, remoção de imports manuais de componentes Max/composables, `<button>`/`<h*>` → MaxButton/MaxTitle. Afetou facebook/google-business/instagram-preview, dynamic-forms, stories-editor, wizard-stepper.

## 3. Findings Pulados / Falsos-Positivos Notáveis

- **MariaDB vs PostgreSQL (recorrente):** múltiplas skills (activity-log, rag-vector, postgresql-jsonb, ai-cost-analytics) tiveram findings que assumiam MariaDB; **falso-positivo** — o escopo define PostgreSQL, e JSONB/GIN/pgvector/HNSW/`<=>` estão corretos.
- **`#models/...` tratado como FQCN Laravel:** falso-positivo — é a sintaxe oficial de subpath imports do AdonisJS v6 (ai-agents-multi-agent).
- **Temas sociais específicos preservados deliberadamente:** TikTok, Instagram (comments/stories/feed), Google Business, Meta OAuth, media-ffmpeg (Reels), WhatsApp — integrações sociais legítimas, **não** descaracterizadas para fotovoltaico conforme regra de escopo.
- **`limiter.groupKey` (bullmq):** corrigido por ser exclusivo do BullMQ Pro, não OSS.
- **MaxPinia não aplicável a skills backend-only:** vários `maxpinia_gaps` vazios corretamente ignorados (jobs/serviços sem GET/save de página).
- **`loginAs`, `BaseEvent.dispatch`, `manualChunks`, `@beforeCreate`:** findings auto-classificados como corretos no v6 — nenhuma alteração.

## 4. Skills que Merecem Revisão Manual Humana

- **adonisjs-brazilian-payments-asaas-integration** — contradição de gateway (EFI/Inter vs Asaas) não resolvida; verificar se Asaas é realmente o gateway-alvo do projeto.
- **adonisjs-ai-agents-domain-catalog** — manteve domínio social-media inteiro (calendário editorial, reels) sob premissa de que é o lado de gestão de mídia do produto solar; confirmar se essa premissa de negócio é verdadeira.
- **typescript-documentation** — arquivos em `references/` (ex. framework-patterns.md) podem reter vazamentos NestJS/React não editados; só o SKILL.md foi corrigido.
- **vue-instagram-feed-grid-simulator** — store apontada para nome genérico (`useCalendarEventStore`) por não existir path canônico no escopo; confirmar a store real.
- **adonisjs-reporting-pdf-excel** — sobreposição/merge potencial com puppeteer-image-generation e pdf-coordinate-editing; avaliar consolidação (fora do escopo da edição cirúrgica).
- **vue-max-use-usecachedapi** — inconsistência cross-skill sobre `apiGetRoute` retornar Promise vs resolver URL deixada como está; alinhar contrato entre skills.
- **Skills com integrações sociais preservadas** (TikTok, Instagram x4, Meta, GBP, WhatsApp) — confirmar se permanecem no escopo do produto fotovoltaico ou se devem ser removidas/arquivadas.