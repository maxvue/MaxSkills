# Auditoria Profunda — `created-skills/`

**Data:** 2026-06-30
**Método:** inventário estrutural determinístico + leitura profunda de 266 SKILL.md por 18 subagentes paralelos + deduplicação cruzada.
**Escopo acordado:** manter Adonis, Laravel e Vue (sem julgar escolha de stack). Foco em problemas internos reais, duplicatas e qualidade.

## Sumário

- **266 skills** auditadas (87 adonisjs, 77 laravel, 64 vue, 4 typescript, 2 python, 6 caveman/cavecrew, + suporte). 17 estão em `_archived/`.
- **94 problemas de conteúdo**: 17 médios, 77 baixos. Nenhum crítico/alto.
- **6 grupos de redundância real** (mesmo stack + mesmo tópico) + ~50 sobreposições parciais (em sua maioria legítimas, paralelas entre camadas).
- **5 problemas estruturais** confirmados (dirs aninhados + duplicata física).

---

## P0 — Correções seguras e óbvias (recomendo aplicar já)

### A. Artefato de geração vazado (frontmatter/conteúdo corrompido)
- **`adonisjs-ai-financial-insights-gemini-best-practices`** — o arquivo termina com tags `</content>` e `</invoke>` (linhas 79-80), restos do scaffolding de tool-call que vazaram para dentro da skill. **Verificado.** Remover essas 2 linhas.

### B. Diretórios aninhados que quebram a estrutura plana
Todas as outras skills vivem na raiz de `created-skills/`. Estas estão indevidamente aninhadas:
- `backend-node/` → 3 skills (`adonisjs-canva-api-integration`, `adonisjs-database-replicas-connection-pooling`, `adonisjs-editorial-calendar-event-workflow`)
- `front-end-vue/` → 1 skill (`vue-3-dynamic-components-and-keep-alive-caching`)
- `python/` → 1 skill (duplicata — ver C)

**Ação:** mover para a raiz e remover os diretórios-contêiner vazios.

### C. Duplicata física real
- **`python-concessionarias-automation-best-practices`** existe na **raiz** E em **`python/`**, e os arquivos **diferem**. Precisa decidir qual versão é a boa, manter uma na raiz e apagar a outra.

### D. `name` ≠ nome do diretório
- **`prompt-generator-1.0.0/`** tem `name: prompt-generator`. Padronizar (renomear o dir ou o campo) — divergência atrapalha o carregamento/referência.

---

## P1 — Erros técnicos que ensinam algo incorreto (médios, verificados)

Estes fazem a skill ensinar uma API inexistente, versão inventada ou código que quebra. Correções pontuais:

| Skill | Problema | Correção |
|---|---|---|
| `laravel-gemini-php-sdk-best-practices` | model id `gemini-3.1-flash-lite` **não existe** (verificado, linha 15) | usar id real (`gemini-2.5-flash-lite`) |
| `vue-eslint-stylelint-quality-standards` | "ESLint 10 e Stylelint 17" **não existem** (verificado, linha 9) | ESLint 9 / Stylelint 16 |
| `laravel-migrations-seeders-factories-best-practices` | `SET FOREIGN_KEY_CHECKS` é MySQL; projeto-alvo é **PostgreSQL** (verificado, linha 60) | `Schema::withoutForeignKeyConstraints()` |
| `backend-node/adonisjs-canva-api-integration` | importa `@adonisjs/core/services/http` (não existe em Adonis v6) e usa `this.httpClient` nunca definido | usar cliente HTTP real (ex.: `@adonisjs/ally` axios / `node-fetch`) |
| `backend-node/adonisjs-database-replicas-connection-pooling` | shape de réplicas Lucid errado (`read.replicas` em vez de `read.connection`) | corrigir para `read: { connection: [...] }` |
| `adonisjs-ai-sdk-google-gemini-best-practices` | `maxSteps`/`maxCalls` não são params do Vercel AI SDK v5 | usar `stopWhen`/`stepCountIs` (já importado, sem uso) |
| `laravel-security-hardening-best-practices` | `DB::raw('... ?', [$id])` **não** parametriza (skill de segurança ensinando SQL injection) | `DB::select(...)` / `whereRaw` |
| `laravel-livekit-server-sdk-best-practices` | controller chama `$liveKit->getWsUrl()`, método nunca definido → fatal error | adicionar o método ou usar a propriedade |
| `laravel-slack-notifications-integration` | mistura API legada (`->attachment()`) com config Block Kit v3 | alinhar para a API Block Kit moderna |
| `laravel-vue-inertia-best-practices` | ensina `Inertia::lazy()` (deprecado → `Inertia::optional()` no Inertia v2) | atualizar nome |
| `vue-axios-api-integration-best-practices` | envolve `apiPostRoute()` em `axios.post()` — contradiz `vue-auth-session-state` (apiPostRoute já faz a request) | remover o wrapper |
| `vue-tenant-client-context-best-practices` | usa API MaxPinia incompatível com a skill canônica `vue-pinia-state-management` (`defineStore` de `@maxvue/max-pinia` + `store.get()` vs contrato `isCached`/options) | alinhar ao contrato canônico |
| `adonisjs-drive-file-uploads-best-practices` | coluna `avatarUrl` armazena uma *key* de storage, não URL — risco de passar URL para `drive.delete()` | renomear para `avatarKey` ou documentar |
| `adonisjs-lucid-soft-deletes-cascade-best-practices` | mixin depende de flags setadas em scope que podem rodar **depois** do hook `@beforeFetch` → `withTrashed` pode não funcionar | revisar contra ordem de execução hook/scope do Lucid |

---

## P2 — Redundância real (mesmo stack + mesmo tópico) — candidatos a consolidar/arquivar

1. **Realtime Adonis duplicado:** `adonisjs-broadcasting-websockets` **e** `adonisjs-transmit-sse-realtime` cobrem ambos Transmit/SSE. → Fundir numa só (a memória do projeto confirma Transmit como padrão). `vue-adonis-transmit-sse` é o cliente Vue (manter).
2. **Puppeteer Adonis:** `adonisjs-puppeteer-rendering` (ativa) já supersede as 2 arquivadas (`_archived/...puppeteer-image-generation`, `_archived/...reporting-pdf-excel`). → Confirmar arquivamento; remover de qualquer índice ativo.
3. **Simuladores de preview social:** `vue-social-post-preview-simulator` (ativa) generaliza ~8 skills arquivadas (facebook, gbp, instagram feed/reels/stories, threads, tiktok, youtube). → Consolidação já feita via `_archived/`; OK.
4. **Max Components UI:** `vue-max-components-ui-development` + `...popovers-confirmations` + `...wizard-stepper-forms` + `vue-floating-vue-tooltips-popovers` se sobrepõem (popovers aparece 2x). → Avaliar fundir os dois de popovers.
5. **Max-stack overview:** `vue-max-stack-frontend` supersede `_archived/vue-max-ecosystem`. → OK (arquivada).
6. **Python concessionárias:** duplicata física (ver P0-C).

### Sobreposições parciais que valem revisão (mesmo stack)
- `laravel-frankenphp-octane` vs `laravel-octane-compatibility` — fortemente sobrepostas; candidatas a merge.
- `laravel-services` vs `laravel-action-classes` vs `laravel-service-providers-dependency-injection` — padrões de lógica de negócio/DI sobrepostos.
- `vue-debugging` vs `vue-frontend-bug-fixing` — troubleshooting Vue redundante.
- `adonisjs-lucid-orm` absorve parcialmente `adonisjs-lucid-soft-deletes-cascade` e `adonisjs-api-serialization`.

> **Nota:** ~35 grupos "cross-stack-parallel" (ex.: `laravel-X` vs `adonisjs-X` vs `vue-X`) são **intencionais e corretos** dado que você decidiu manter os três stacks. Não recomendo mexer neles.

---

## P3 — Higiene (baixo, opcional)
- `_archived/adonisjs-reporting-pdf-excel` embute paths absolutos da máquina (`/home/johnattas/GitHub/socialmedia-node/...`) como links `file://` — ruído. (arquivada, baixa prioridade)
- Vários exemplos de simuladores arquivados hardcodam cores hex contradizendo a própria regra "não duplique cores CSS" (gbp, instagram-feed). (arquivados)
- `_archived/typescript-documentation` referencia 7 arquivos `references/*.md` cuja existência não foi verificada; menciona Compodoc/Angular fora de escopo.

---

## Recomendação de execução
Aplicar **P0 (A–D)** e **P1** como correções seguras em lotes (cada uma é pontual e de baixo risco). **P2** exige sua decisão de produto (o que fundir vs. manter). **P3** é opcional.

---

## ✅ Ações aplicadas (2026-06-30)

Decisões do usuário: manter Adonis/Laravel/Vue; aplicar P0, P1 e fundir redundâncias claras do P2.

### P0 — estrutural (tudo aplicado)
- **Artefato vazado**: removidas as tags `</content></invoke>` de `adonisjs-ai-financial-insights-gemini-best-practices`.
- **Dirs aninhados achatados para a raiz**: `backend-node/` (continha **7** skills, não 3 — 4 foram criadas durante a auditoria: encryption-sensitive-data, environment-variables-validation, gemini-file-api-media-integration, image-optimization-sharp), `front-end-vue/` (1), `python/` (1). Diretórios-contêiner removidos.
- **Duplicata python**: mantida a versão de `python/` (superior — descrição mais rica, nota de escopo, PT) movida para a raiz; versão antiga em inglês descartada.
- **`prompt-generator-1.0.0`** → renomeado para `prompt-generator` (casa com o campo `name`).

### P1 — técnico (14 + 6 aplicadas)
14 correções pontuais: canva HTTP client (fetch nativo), db-replicas (`read.connection`), ai-sdk-gemini (`stopWhen`/`stepCountIs` + frontmatter), laravel-security (`DB::select` parametrizado), livekit (`getWsUrl()`), laravel-slack (Block Kit v3), inertia (`optional()`), vue-axios (apiPostRoute sem wrapper), vue-tenant (contrato MaxPinia canônico), drive (`avatarKey`), lucid soft-delete (flag antes do fetch), gemini model id (1), eslint/stylelint (9/16), FOREIGN_KEY_CHECKS (Postgres).
- **Model id inventado `gemini-3.1-*`**: corrigido em **6 skills no total** (→ `gemini-2.5-*`). O audit por lotes só pegou 1; varredura global pegou as outras 5.

### P2 — fusões de redundância
- **Transmit/SSE Adonis**: conteúdo único de `broadcasting-websockets` incorporado em `transmit-sse-realtime` (canônica); redundante **removida**.
- **Octane Laravel**: conteúdo único de `octane-compatibility` incorporado em `frankenphp-octane` (canônica); redundante **removida**.
- **Popovers Vue**: **não fundidas** — são bibliotecas distintas (MaxComponentsUI interna vs floating-vue de terceiros). Descriptions afiadas com fronteira clara ("qual skill usar?") para eliminar competição de trigger.

### Resultado
- **269 → 267 skills** (2 redundantes fundidas/removidas; +4 que estavam escondidas em `backend-node/`).
- Verificado: 0 artefatos vazados, 0 model ids falsos, 0 dirs-contêiner órfãos (exceto `_archived/`), estrutura plana restaurada.

### Pendente para sua decisão
- **Sobreposições parciais P2** ainda não tocadas (services vs action-classes vs service-providers; debugging Vue; lucid-orm absorvendo subconjuntos) — exigem julgamento caso a caso.
- **P3 (higiene)** — opcional, em sua maioria nas skills já arquivadas.

---

## ✅ 2ª verificação (segunda passada) — 2026-06-30

Re-auditoria profunda das **267 skills** já corrigidas (18 verificadores paralelos), focada em confirmar as correções e caçar problemas novos.

**Resultado da verificação:** todas as 20 correções P0/P1 e as 2 fusões P2 **seguraram** — nenhum reaparecimento, zero referências pendentes às skills fundidas. Mas a segunda passada (mais minuciosa em APIs de biblioteca) encontrou **18 problemas NOVOS** que o primeiro audit não pegou (1 alto, 5 médios, 12 baixos). **Todos corrigidos** nesta rodada:

| Sev | Skill | Problema → Correção |
|---|---|---|
| **HIGH** | `laravel-qrcode-generation` | Ensinava API v5 (`Builder::create()`) com dep declarada v6 → migrado p/ `new Builder(...)` named args + `logoPunchoutBackground` (verificado contra README oficial v6) |
| MED | `laravel-database-eloquent` | `pruning(): Builder` trocado com `prunable()` → corrigido p/ a API real da trait `Prunable` |
| MED | `adonisjs-ai-agent-cost-analytics...` | Tabela de preços com `gemini-2.5-flash-lite` duplicado (efeito colateral da correção P1 anterior) → linha duplicada removida |
| MED | `adonisjs-gemini-file-api...` | Misturava classes do SDK novo no exemplo do SDK legado → `GoogleGenerativeAI` + `GoogleAIFileManager` (de `/server`) |
| MED | `laravel-sentry-integration` | `new Breadcrumb(title:...)` — arg inválido + `$type` omitido → assinatura correta com `type:`/`message:` |
| MED | `_archived/vue-instagram-feed-grid...` | Ref cruzada para `front-end-vue/` (dir inexistente) → path corrigido |
| LOW ×12 | vários | "Laravel v13" inexistente em **8 skills** → "Laravel 12"; refs cruzadas com nome/path errado (`maxpinia-...`, `backend-laravel/` em socialite **e** pulse); cores hardcoded contradizendo restrições (chartjs, gbp); aspect-ratios Instagram em skill solar; billing store fora do contrato MaxPinia; cipher AES-256-GCM→CBC; contagem de filas (4→5); typo "le callback"→"o callback" |

**Verificação final:** 267 skills, 0 artefatos vazados, 0 frontmatter inválido, 0 refs pendentes, 0 ids/versões inventadas remanescentes. Biblioteca consistente.

> Nota: a 2ª passada confirma o valor de verificar — pegou erros de API que só aparecem em leitura minuciosa, e detectou que uma correção P1 minha havia introduzido uma duplicata (já sanada).

---

## ✅ 3ª passada — alinhamento ao escopo confirmado (2026-06-30)

Decisões do usuário nesta rodada (resolvem conflitos do escopo): **Laravel 13 + MariaDB + Ziggy** (Laravel MANTÉM Ziggy); **Inertia proibido e removido em tudo**; auth segue **Maxdmin** (MaxAuthCard + social). Reverte correções da 1ª/2ª passada que tinham assumido Laravel 12 + PostgreSQL.

### Inertia (proibido) — removido
- `laravel-vue-inertia-best-practices` → **arquivada** em `_archived/`.
- Inertia removido e substituído pelo padrão SPA (`/api` + stores `@maxvue/max-pinia`, Ziggy/Vue Router) em **6 skills**: `laravel-authorization-policies-gates`, `laravel-pennant-feature-flags`, `laravel-user-impersonation`, `laravel-code-generators` (incl. `vuex`→MaxPinia), `laravel-sanctum-api-authentication`, `laravel-socialite-oauth-integration`.
- Verificado: **0 skills ativas** instruem Inertia; as 8 menções restantes são todas negativas ("NÃO use Inertia").

### Versão/DB Laravel — revertido para o escopo correto
- `Laravel 12` → **`Laravel 13`** em 6 skills (activity-log, code-generators, php-code-quality, rate-limiting, sanctum, task-scheduling). Convenções `bootstrap/app.php`/`routes/console.php`/`Schedule` permanecem válidas em 13.
- `laravel-migrations-seeders-factories`: rationale do FK-check corrigido de PostgreSQL para **MariaDB** (helper `withoutForeignKeyConstraints` mantido como best-practice portável; `SET FOREIGN_KEY_CHECKS` volta a ser válido como forma raw).
- Ziggy **preservado** em todas as skills Laravel.

### Erros técnicos novos (model ids inventados)
- `gemini-3.5-flash` (**id inexistente**) → `gemini-2.5-flash` em `adonisjs-ai-agent-cost-analytics-and-budget-control` e `adonisjs-ai-agents-domain-catalog` (5 ocorrências).
- `gemini-2.5-pro-preview` (id não-estável) e linhas duplicadas na tabela de custo/cadeia de fallback **removidas** — tabela agora só com ids reais (flash-lite/flash/pro).
- Verificado AI SDK por stack: **Laravel** usa Laravel AI SDK (`laravel/ai`; `gemini-php-sdk` é skill especializada à parte); **Adonis** usa Vercel AI SDK (`ai`/`@ai-sdk/google`, `stopWhen`/`stepCountIs`). Sem SDK concorrente fora de lugar.

### Auth / Maxdmin
- **Backend alinhado** (verificado): `adonisjs-ally-oauth` (session guard, Google/Facebook, find-or-create, 30 dias), `adonisjs-access-tokens` (escopo MCP, não é o login da SPA), `adonisjs-auth-remember-me` (sessão 30 dias).
- **MaxAuthCard + login social** já presente como exemplo canônico em `vue-auth-session-state` (`<MaxAuthCard :providers @submit @provider>`). Requisito do escopo já atendido.
- **2FA**: tela de desafio agora instrui reutilizar **MaxAuthCard** (consistência com o login) em vez de `MaxCard` genérico.
- **Hardening Ally**: adicionada checagem `email_verified` antes de vincular login social a conta local existente (fecha vetor de account-hijacking por email não verificado) + redirect `/login?error=email_not_verified`.

> Nota: a recomendação do verificador de marcar `laravel-sanctum`/`laravel-socialite` como "apenas origem da migração" foi **descartada** — o novo escopo trata Laravel 13 como stack-alvo legítimo (dual-stack Laravel+Adonis), não como origem a depreciar.

---

## ✅ 4ª passada — auditoria front-end Vue (2026-07-01)

Auditoria das **71 skills front-end** (branch `skills/frontend-house-rules`) por 7 agentes paralelos + verificação contra a fonte-verdade `vue-max-ecosystem-api-reference` (referências derivadas do código-fonte de MaxComponentsUi/MaxUse/MaxPinia). Todas as correções abaixo foram aplicadas e verificadas (grep residual limpo).

### 🔴 Bug sistêmico do contrato de rota MaxPinia (raiz na skill canônica)
A referência derivada do fonte (`maxpinia.md`) confirma: `options.get.route`/`options.save` são **string de path plano** (`'/api/user'`); a store chama `apiGetRoute`/`apiPostRoute` **internamente**. `apiGetRoute`/`apiPostRoute` **executam a request e retornam `response.data`** — logo, embrulhá-los na config (`route: apiGetRoute(...)`) dispara request espúria no boot e guarda uma `Promise` como rota.
- Corrigido em: **`vue-pinia-state-management` (canônica)**, `vue-billing-subscription-headless`, `vue-brand-positioning-character-management`, `vue-tenant-client-context` → config vira string plana.
- `{ data } = await apiGetRoute/apiPostRoute` (payload vem direto): `vue-meta-api-oauth`, `vue-max-stack-frontend`.
- Uso indevido como URL de lib 3rd-party: `vue-uppy-file-upload` (`endpoint`) → string/`apiRoute().routeURL`.
- Método de store inventado `load()`/`save(payload,route)`/`flush()` → `reload()`/`saveInServer()`: `vue-max-stack-frontend`, `vue-meta-api-oauth`, `vue-rss-news-moderation-dashboard` (reescrita de Options→Setup store), `vue-zod-schema-validation`, `vue-max-components-ui-wizard-stepper-forms`, `vue-floating-vue-tooltips-popovers`.

### 🔴 APIs inexistentes / código que quebra
- `useToast` de `@maxvue/max-use` não existe → `Toast` de `@maxvue/max-components-ui` (`vue-social-post-preview-simulator`).
- `definePiniaStore` não existe → `defineStore` de `pinia` (`vue-typescript-best-practices`).
- `MaxCard` genérico não existe → `<div>`+SCSS (`vue-instagram-comments-moderation-inbox`, `vue-social-post-preview-simulator`).
- `dotLottie.is_playing()` → getter `.isPlaying` (`vue-lottie-animations`).
- `Stepper/Step/...` importados do entry errado → subpath `@maxvue/max-components-ui/prime` (`vue-max-components-ui-wizard-stepper-forms`).
- `http` (axios) não é export de MaxUse → `setApiRequestConfig` (`vue-sentry-error-tracking`).
- Bugs em reference files de `vue-debugging`: `reactivity-same-tick-batching.md` (`Object.defineProperty` em ref + `.call` em número → substituído por watch `flush:'sync'`), `use-template-ref-vue35.md` (`x?.prop = v` SyntaxError → guard).

### 🟡 Contradições / incorreções
- `new Transmit()` direto → `useTransmitClient()` (`vue-ai-agent-playground`).
- Versões inventadas: "Vue 3.6 / Vue Router 5" → Vue 3 / Vue Router 4 (`vue-auth-session-state`); metadata "Vue v18" removida (`vue-best-practices`); pin "3.6" removido do Vapor experimental (`vue-vapor-mode`).
- Ordem de blocos SFC → template-first (`vue-best-practices`); guardas de rota `next()` → return-based (`vue-router`).
- Helper "E.164" falso → `libphonenumber-js` (`vue-inputs-masks-validation`).
- `axios` manual/interceptor global para salvar página → store MaxPinia (`vue-toast-notifications`, `vue-tenant-client-context`).
- Classes de paleta cru → tokens semânticos (`vue-unocss-styling`).
- `KeepAlive include` não casava com wrapper async + SCSS morto → wrapper nomeado + `:deep(.max-button)` (`vue-3-dynamic-components`).
- `messageIcon` default `null` (`vue-max-components-ui-popovers-confirmations`).
- `defineModel` deep-mutation emite em 3.4+ e `undefined` em dynamic-arg avisa (não "remove") → reference `vue-debugging` corrigidas.
- Exemplo de store do `vue-vitest` (Options+axios) reescrito para MaxPinia setup store.

### 🟡 Versões ESLint/Stylelint
- `vue-eslint-stylelint-quality-standards`: "ESLint 9 / Stylelint 16" → **"ESLint 10 / Stylelint 17"** (decisão do usuário: projeto real usa esses majors; reverte a suposição da 1ª passada).

### ⚪ Higiene
- H1/import faltando (`vue-cookie-consent-lgpd`), contagem de componentes 58→~70 e nomes de export de store (`useConfirmStore` etc.) em `vue-frontend-bug-fixing`, `html2canvas allowTaint` removido, input nativo→`MaxInputText` (`vue-keyboard-shortcuts`), cor hex fixa→CSS var (`vue-solar-roi`), `resolveComponent` top-level anotado (`vue-3-dynamic-forms`), registro local de `draggable` (`vue-social-post-preview-simulator`).

**Verificação final:** 0 route-wraps residuais, 0 `{data}` destructuring de route-helpers, 0 `definePiniaStore`/`useToast`/`is_playing()`/`MaxCard` ativos, 0 versões inventadas remanescentes. `vue-debugging` tem ~139 reference files; 136 auditados nesta passada (3 restantes não verificados).
