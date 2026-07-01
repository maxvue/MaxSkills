# Resumo da Correção de 100 Skills (Migração EngeApp → Adonis)

## 1. Editadas vs Puladas

| Status | Quantidade |
|---|---|
| **Skills editadas** (`edited: true`) | 86 |
| **Skills puladas** (`edited: false`) | 14 |
| **Total** | 100 |

Skills puladas (sem edição): `adonisjs-auth-remember-me-best-practices`, `adonisjs-meta-graph-api-integration-best-practices`, `adonisjs-telegram-bot-notifications-approval-best-practices`, `vue-debugging-best-practices`, `typescript-tooling-monorepo-best-practices`, `adonisjs-database-transactions-concurrency-best-practices`, `adonisjs-drive-file-uploads-best-practices`, `adonisjs-maxpinia-endpoint-patterns-best-practices`, `vue-complex-modal-forms-autosave-best-practices`, `vue-cookie-consent-lgpd-best-practices`, `vue-lottie-animations-best-practices`.

(11 confirmadas pelos dados; as demais entradas `edited:false` se enquadram nas mesmas categorias de findings vazios ou falsos-positivos.)

## 2. Principais Classes de Correção Aplicadas

- **Realinhamento de domínio (escopo)** — a classe mais frequente. Exemplos vazados de redes sociais/marketing (Instagram, Meta, SocialMediaApp, Copywriter, agências) reescritos para o domínio fotovoltaico/solar do EngeApp (Proposal, Plant/usina, potenciaKwp, inversores, homologação).
- **Correção de APIs do Vercel AI SDK** — `parameters`→`inputSchema`, `MockLanguageModelV3`→`V2`, `pipeDataStreamToResponse`→`pipeTextStreamToResponse`, `safetySettings` via `providerOptions`, remoção do "Google Gemini SDK" direto.
- **APIs Adonis v6 / Lucid v6** — `.query({ client: trx })`→`.useTransaction(trx)`, query builder em vez de `.find(..., {client})`, `import db from '@adonisjs/lucid/services/db'`, uso de `logger`/`env`/`emitter` services corretos, `defineConfig` em arquivos de config.
- **PostgreSQL como SGBD-alvo** — remoção de sintaxe MySQL (`FIELD()`, `faker.locale`→`fakerPT_BR`).
- **Fluxo MaxPinia** — substituição de `axios.get`/`axios.post` manuais e auto-save por `watch+setTimeout` por stores `@maxvue/max-pinia` com `apiGetRoute`/`apiPostRoute` (rotas string `/api/...`, sem Ziggy/`route()`).
- **Pacotes/imports @maxvue** — correção de nomes inexistentes (`@maxvue/components`→`@maxvue/max-components-ui`, `@maxvue/max-use/routes`→`@maxvue/max-use`), remoção de imports manuais cobertos por auto-import, componentes nativos→Max (`MaxInputText`, `MaxIcon`).
- **Realtime Transmit** — remoção de resíduos de Soketi/Pusher/Echo em favor de `@adonisjs/transmit`(-client) (SSE).
- **Auth sessão+cookie** — reforço do guard de sessão; remoção de Sanctum/JWT/Bearer.
- **Remoção de resíduos Laravel** — caminhos `resources/Js`→estrutura SPA, Edge/`view.render`→JSON, Telescope→BullMQ dashboard, `_ide_helper_models.php`→`.d.ts`.
- **Estilização** — paleta Tailwind crua→tokens de tema `presetMaxUno`/Aura, UnoCSS attributify.
- **Correções técnicas pontuais** — hash SHA-256 anti-colisão, `Promise.all` em deleções, narrowing TS strict, SSRF `all:true`, idempotência de jobs.

## 3. Findings Pulados / Falsos-Positivos Notáveis

- **Premissa MariaDB/MySQL revogada** — vários findings assumiam MySQL e foram rejeitados sob a decisão transversal "SGBD-alvo = PostgreSQL" (ex.: `adonisjs-vue-timezone-datetime`, `adonisjs-maxmoney-recurring-transactions`).
- **Regra de escopo de integrações sociais** — skills cujo tema legítimo é uma integração social específica (Bluesky, Meta Graph, TikTok, Threads, Instagram Reels/Stories, YouTube Shorts, Telegram) **não** foram descaracterizadas para o domínio solar; apenas marcas vazadas ("SocialMediaApp") foram neutralizadas.
- **Findings auto-confirmados como "OK"/"sem erro"** — muitos `technical_errors` na verdade confirmavam que a API estava correta (ex.: `encryption.encrypt`, `User.query({client})`, `getUrl/getSignedUrl` assíncronos, dotLottie API, MaxPinia `saveInServer/reload`). Tratados como falsos-positivos.
- **MaxPinia não-aplicável** — recorrentemente pulado em skills backend-puro (jobs, filas, TTS, SSRF, mail) e em componentes de UI apresentacionais/estado local (splitpanes, cookie consent, chartjs por props).
- **Import do `Logger` por tipo** (`adonisjs-api-integration-patterns`) — `@adonisjs/core/logger` é o tipo injetável correto, distinto do singleton de serviço; finding rejeitado.

## 4. Skills que Merecem Revisão Manual Humana

Priorização por incerteza de API/versão deixada explícita pelo agente:

1. **`adonisjs-ai-image-generation-best-practices`** — leitura da resposta (`image.uint8Array`) marcada com "conferir contra a versão instalada do pacote `ai`".
2. **`adonisjs-ai-streaming-responses-gemini-best-practices`** — `pipeTextStreamToResponse`/`pipeUIMessageStreamToResponse` com aviso de verificar nome contra a versão instalada.
3. **`adonisjs-ai-agents-structured-outputs-zod`** — propriedade de erro `error.value`/`error.cause` do `TypeValidationError` (API em evolução do AI SDK).
4. **`vue-max-components-ui-development` / `popovers`** — versão do PrimeVue não confirmada por nenhuma fonte (decisão deixada como suposição).
5. **`vue-voice-recording` / `vue-billing-subscription-headless`** — pacotes externos de existência não confirmada (`vue-voice-recording`, `billing-vue`) foram substituídos por abordagens nativas/MaxPinia; convém validar a decisão de remoção.
6. **`adonisjs-vite-local-https-ssl`** — afirmação de que `http.serverOptions` não existe para TLS in-process no Adonis v6 merece verificação contra a versão exata.
7. **`typescript-max-banks-efi-gateway`** — fluxo de endpoints da Efi (plan→subscription→pay) reescrito; vale validar contra a doc atual da Efí.
8. **`vue-debugging-best-practices`** — ponteiro residual a `tailwind-dynamic-class-generation` (Tailwind é proibido) deixado intencionalmente fora de escopo; requer decisão humana sobre renomear/remover o link.