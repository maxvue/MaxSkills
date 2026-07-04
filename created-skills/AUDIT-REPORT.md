# Auditoria created-skills — Relatório Consolidado

Data: 2026-07-04 · 175 skills analisadas por 9 subagentes, comparando cada SKILL.md com o
código real dos projetos de referência (`engeapp` = Laravel 13.7 / PHP 8.4 / MySQL + Vue 3;
libs `MaxComponentsUi`, `MaxUse`, `MaxPinia`, `MaxBanks`).

## Placar geral
- **OK (sem correção): ~111**
- **Com ISSUES: ~54**
- **IRRELEVANT (mover): 10** (+3 ai-media condicionais)
- Duplicatas: 2 pares

## P0 — ADONIS (regra 5): 31 skills mencionam AdonisJS
Herança da migração Adonis abandonada. O texto da camada de backend foi escrito para Node/Adonis
(Transmit, Lucid, VineJS, Shield, Ally, Bouncer, "não use Sanctum/Echo"). O frontend Vue/Max em si
costuma estar correto — o problema é a camada backend descrita.

Equivalências Laravel 13 a aplicar:
- Adonis Transmit (SSE) → **Laravel Reverb + `@laravel/echo-vue`** (ambos no package.json real)
- Adonis Shield/guard web → **Sanctum SPA** (csrf-cookie) — várias skills negam Sanctum invertido
- Adonis Bouncer → **`spatie/laravel-permission`**
- VineJS → **FormRequest / validação Laravel** (+ corrigir shape 422 `{message, errors:{campo:[...]}}`)
- Lucid → **Eloquent**; Ally → **Socialite**; `node ace`/Japa → **`php artisan`/Pest**; PostgreSQL → **MySQL**

Arquivos (31):
- Críticas (skill inteira sobre Adonis): `frontEnd/vue-adonis-transmit-sse`, `frontEnd/vue-bouncer-roles-permissions`, `frontEnd/vue-frontend-bug-fixing`
- Backend/TS/docs: `backend_laravel/laravel-vue-login-maxauthcard`, `dev-practices/technical-documentation` (HIGH), `typescript/typescript-best-practices`, `typescript/typescript-billing-core-architecture`
- Frontend: vue-ai-agent-playground, vue-auth-session-state, vue-axios-api-integration, vue-billing-subscription-headless, vue-code-generators, vue-dayjs-date-manipulation, vue-draggable-next, vue-expert, vue-i18n-localization, vue-image-cropping-resizing, vue-inputs-masks-validation, vue-instagram-comments-moderation-inbox, vue-instagram-stories-sticker-editor, vue-livekit-client-integration, vue-max-stack-frontend, vue-meta-api-oauth-integration, vue-playwright-e2e-testing, vue-social-post-preview-simulator, vue-solar-roi-calculator-dashboard, vue-typescript, vue-uppy-file-upload, vue-vite-bundling-optimization, vue-voice-recording, vue-zod-schema-validation

**Tensão a decidir:** `@maxvue/max-banks` REAL (/home/johnattas/GitHub/MaxBanks) TEM camada `src/adonis/`
(`@adonisjs/core ^7.3.0`). As skills billing/efi descrevem o pacote corretamente. Aplicar "zero Adonis"
mesmo assim exige reescrever para Laravel/genérico.

## P0 — IRRELEVANT (regra 4): mover para created-skills/_irrelevant
- `caveman-suite/*` (7): caveman, cavecrew, caveman-help, caveman-stats, caveman-commit, caveman-review, caveman-compress — estilo meme; cavecrew referencia subagentes inexistentes; caveman-stats depende de hooks não instalados; conflita com diretriz pt-BR.
- `agent-tooling/*` (3): prompt-generator (inteiro em coreano, exemplos Spring Boot/Java), find-skills (meta-tooling npx), agent-browser (CLI genérico, hidden:true stub).
- `ai-media/*` (3) — **DECISÃO**: RunComfy/inference.sh (provedores pagos, ausentes) vs `google-gemini-php/laravel ^2` já instalado. Se o módulo social usa Gemini → mover/reescrever; senão são as únicas defensáveis.

## P1 — Violações de biblioteca (regra 1) — reais em código de app
- `frontEnd/vue-solar-roi-calculator-dashboard`: usa `<Column ...>` (PrimeVue DataTable) → **`<MaxTableColumn>`** (MaxTable existe). + `<h3>` título → MaxTitle2.
- `frontEnd/vueuse`: exemplos importam `@vueuse/core` direto (linhas 104/139/146) → rotear via **MaxUse**; contém conteúdo Nuxt irrelevante.
- (Demais menções a "PrimeVue" são factuais/permitidas: descrevem que MaxComponentsUi é construída SOBRE PrimeVue — não são violação.)

## P1 — Incorreções factuais / DB / versão
- `backend_laravel/laravel-migrations-seeders-factories`: "MariaDB (SGBD alvo)" 2x → **MySQL** (engeapp usa mysql).
- `dev-practices/technical-documentation`: DB PostgreSQL → MySQL; badge AdonisJS-6 → Laravel-13.
- `backend_laravel/laravel-frankenphp-octane`: diz Octane padrão = RoadRunner; real `.env` usa `OCTANE_SERVER=frankenphp` → inverter (FrankenPHP primário).
- `frontEnd/vue-dayjs-date-manipulation`: afirma "dayjs não é dependência" — FALSO (`dayjs ^1.11.21` existe). Corrigir banner.
- `frontEnd/vue-zod-schema-validation`: shape do erro 422 errado → `{ message, errors: { campo: [msgs] } }`.
- `backend_laravel/laravel-telescope-debugging`: oferece `app/Console/Kernel.php` (não existe no L13). Remover.
- `frontEnd/vue-typescript`: afirma não haver `_ide_helper_models.php` — engeapp tem `laravel/ide-helper`.
- `typescript/typescript-billing-core`: sugere BullMQ (não existe no MaxBanks real; usar fila Laravel/Horizon).
- `backend_laravel/laravel-brazilian-payments`: `config('bank.inter_webhook_token')` não existe; Asaas apresentado como real sem confirmação — rebaixar a aspiracional.

## P2 — Cross-refs quebradas / pasta errada
- `backend_laravel/laravel-socialite`: cross-ref L48 aponta caminho pré-reorganização (`created-skills/laravel-code-generators...` → `backend_laravel/...`).
- `backend_laravel/laravel-solar-irradiance-cresesb-nasa`: cross-ref `laravel-base-api-integration-patterns` → `laravel-api-integration-patterns`.
- `backend_laravel/laravel-gemini-file-api`: cross-ref com caminho absoluto `file:///home/johnattas/...` → relativo.
- `backend_laravel/laravel-pulse-custom-recorders`: links de exemplos faltam segmento `backend_laravel/`.
- `general/laravel-meta-graph-api-integration`: skill Laravel na pasta `general/` → mover para `backend_laravel/`.
- `frontEnd/vue-router`: declara supersedir `vue-router-routing-layouts`/`-navigation` (não existem mais) — limpar referência.

## P2 — Duplicatas
- `frontEnd/vue-expert` ↔ `frontEnd/vue-code-generators` — mesmo escopo (convenções de componente/store/serviço). Avaliar merge.
- `ai-media/nano-banana-2` ⊂ `ai-media/ai-image-generation` — subconjunto. Merge.

## P3 — Estilo front-end (memória de house-rules)
- Headings/inputs nativos → MaxTitle1/2, MaxComponents: vue-3-dynamic-components (`<h2>/<h3>`), vue-draggable-next (`<h2>`), vue-splitpanes (`<h1>/<h3>`), vue-solar-roi (`<h3>`).
- Hex hardcoded / mandatos "SCSS-only / PROIBIDO Tailwind" → UnoCSS attributify + CSS vars do tema: vue-floating-vue, vue-image-cropping, vue-jsbarcode, vue-fullcalendar, vue-auto-import (1 hex), vue-3-dynamic-forms.
- vue-ai-agent-playground: sugere `MaxGridCols` em formulário (usar `MaxGrid`).

## P3 — Cosméticos
- laravel-electrical-calculations & laravel-hashids: dois cabeçalhos "Restrições".
- laravel-context-metadata: falta heading `#` de título.
- laravel-prompts: labels de exemplo em inglês → pt-BR.
- laravel-multitenancy: "facade Context do Laravel 11" → "(Laravel 11+)".
- php-best-practices: "51 rules" vs 53 arquivos em rules/.
- laravel-finance-coupons: exemplo usa float round() contra diretriz BCMath.
- laravel-digital-signatures: Clicksign não instalado → marcar opcional.
