---
name: vue-frontend-bug-fixing-best-practices
description: "Use when diagnosing and fixing front-end bugs in Engeapp (Vue 3 + TS + MaxPinia + UnoCSS + MaxComponentsUi + MaxUse): reactivity issues, TS errors, store cache/auto-save, HMR, and routing. Covers objectives, project stack, and frontend bug fixing."
---
# Correção de Bugs do Front-End Vue — Melhores Práticas

Skill especializada para diagnosticar e corrigir bugs do front-end no projeto EngeApp.
Segue um processo estruturado: **evidência → classificação → diagnóstico → correção → validação**.

## Objetivo

Diagnosticar e corrigir bugs do front-end em projetos Vue 3 + TypeScript + MaxPinia (@maxvue/max-pinia) + UnoCSS + MaxComponentsUi + MaxUse, atacando a causa raiz em vez de mascarar o sintoma, respeitando as convenções do projeto e suas próprias bibliotecas de componentes/composables.

Usar esta skill quando:

- O usuário reportar um bug visual ou comportamental no front-end
- Erros de TypeScript aparecerem em arquivos `.vue` ou `.ts` do front-end
- Ocorrerem problemas de reatividade (estado não atualiza, `watch` não dispara, `computed` incorreto)
- Aparecerem erros no console do navegador (runtime errors, warnings do Vue)
- Ocorrerem problemas com MaxPinia (stores não sincronizando, estado perdido, auto-save/cache falhando)
- Ocorrerem problemas com MaxComponentsUi (componentes não renderizando, props incorretas)
- Aparecerem erros de build do Vite ou HMR quebrado
- O layout/CSS estiver quebrado (UnoCSS, SCSS)
- Ocorrerem erros de roteamento (Vue Router)

## Stack do Projeto

| Tecnologia | Versão | Notas |
|------------|--------|-------|
| Vue | `^3.6.0-rc.2` | Composition API + `<script setup lang="ts">` — SEMPRE |
| TypeScript | Strict mode | Tipagem obrigatória em todo front-end |
| **@maxvue/max-pinia** | **local** | **State management — camada de cache + auto-save (debounced). TODO GET/save de dados de página passa por stores MaxPinia (sobre Pinia 3). Não usar Pinia puro nem GET/POST manual para dados de página.** |
| Vue Router | 5 | SPA pura (Laravel serve catch-all HTML) — Ziggy (`ziggy-js`) está configurado e é usado; as rotas de API são passadas como **nome (Ziggy)** — ex.: `'client.data'` — e os helpers do `@maxvue/max-use` (`apiGetRoute`) resolvem o nome internamente (via `route()`) para a URL `/api/...` |
| PrimeVue | — | Componentes base para UI (base da MaxComponentsUi) |
| UnoCSS | 66 | Estilização utilitária (sem Tailwind) |
| Vite | 8 (`^8.0.14`) | Bundler + HMR |
| Unplugin Auto Import | — | Auto-importação de composables e helpers |
| Unplugin Vue Components | — | Auto-importação de componentes |
| **@maxvue/max-components-ui** | **local** | **Biblioteca própria de componentes UI (~70 componentes `Max*`/`InputBase`; **não reexporta componentes do PrimeVue** — só registra `app.use(PrimeVue)` e a diretiva `v-tooltip`)** |
| **@maxvue/max-use** | **local** | **Biblioteca própria de composables, helpers, rotas e utilitários** |
| laravel-echo / @laravel/echo-vue | dependência | Realtime via WebSockets (Laravel Reverb) — bootstrap com `import { configureEcho } from '@laravel/echo-vue'` (`resources/Js/configureReverbEcho.js`) e consumo via `useEcho`. Não há `import Echo from 'laravel-echo'` em `resources/`; `laravel-echo` está em `devDependencies` e `@laravel/echo-vue` em `dependencies` |
| @vue-flow/core | `^1.48.2` | Diagramas de fluxo — **dependência direta** do app (`dependencies` do `package.json`) |
| @tanstack/vue-virtual | `^3.13.26` | Virtualização de listas — **dependência direta** do app |
| floating-vue | `^5.2.2` | Consta no `package.json` mas é **DEPENDÊNCIA MORTA** — nunca importada em `resources/` nem nas libs Max*. Tooltips do projeto usam a diretiva `v-tooltip` do PrimeVue registrada pela MaxComponentsUi (`app.directive('tooltip', Tooltip)`); popovers usam `MaxPopover`/`MaxPopoverMenu`. Não diagnosticar tooltips via floating-vue. |
| lucide-vue-next / lucide | `^1.0.0` / `^1.17.0` | Ícones — **dependências diretas** do app (além de `@iconify/vue`, `@kalimahapps/vue-icons`) |
| Vitest | `^4.1.7` (devDep) | Há `vitest.config.ts` na raiz do engeapp cobrindo `tests/Js/**/*.{test,spec}.ts` (specs reais de VOIP e TRT), além das suítes das libs Max*. Testes de backend usam **Pest** (`php artisan test`). |

### Bibliotecas Próprias — Contexto Obrigatório

#### `@maxvue/max-components-ui` (link local: `file:./storage/libs/MaxComponentsUi`)

Biblioteca de **componentes UI** construída sobre PrimeVue com estilos e comportamentos customizados.
Código-fonte em: `storage/libs/MaxComponentsUi/src/` (dentro do próprio projeto engeapp)

Agrupamentos-chave (para bug fixing, basta saber onde procurar — a lista completa e as props ao vivo estão no source e na skill dedicada, não replique nomes aqui):
- **Inputs** (todos envolvem `InputBase`, que gerencia label/erro/ícone), **Upload**, **Botões** (`MaxButton`/aliases `Button`,`Botao`), **Layout** (`MaxTable`, `MaxModal`, `MaxPopover`…), **Feedback/Loaders**, **Navegação**, **Mídia** (`MaxIcon`/Iconify, `MaxPdfView`, `MaxMaps`), **Animação**, **Títulos**.
- **Stores internas da lib:** `useConfirmStore`, `useModalStore`, `usePopoverStore`.
- **Temas/estilos:** `src/themes/`, `src/styles/`, `src/prime/`, `src/presetMaxUno.ts`.

> Para a lista granular de componentes/props, consulte o **source** (`storage/libs/MaxComponentsUi/src/components/`) ou a skill **`vue-max-ecosystem-api-reference`** — não confie numa lista transcrita aqui (desatualiza).

#### `@maxvue/max-use` (link local: `file:./storage/libs/MaxUse`)

Biblioteca de **composables, helpers e utilitários** que unifica helpers próprios, VueUse e Lodash.
Código-fonte em: `storage/libs/MaxUse/src/` (dentro do próprio projeto engeapp)

> **Obs.:** o MaxPinia também é link local (`file:./storage/libs/MaxPinia`), com código-fonte em `storage/libs/MaxPinia/src/`.

Para bug fixing, os agrupamentos relevantes (nomes exatos e assinaturas: consulte o **source** `storage/libs/MaxUse/src/` ou a skill **`vue-max-ecosystem-api-reference`**):
- **Composables próprios:** `useDefaultReset`, `useRefCached` (cache em localStorage), `useRefCachedApi` (cache + sincronização com API), `useTimeAgo`.
- **Módulos de Helpers (namespace `_`):** `Browser`, `Dates`, `Iterables`, `Math`, `Objects`, `Strings`, `Types`, `Validations`, `Electrical` (fotovoltaica), `Format`.
- **Sistema de Rotas** — `apiGetRoute`/`apiPostRoute`/`apiPutRoute`/`apiDeleteRoute`/`apiUploadRoute`/`apiRoute` + `getRoute`/`goToRoute`. **Todos recebem o nome da rota (Ziggy)** — ex.: `'client.data'` — e resolvem internamente (via `route()`) para a URL `/api/...`.

**Objeto utilitário `_` (underscore):** objeto centralizado que unifica helpers próprios + VueUse + Lodash, com prioridade para os próprios (sem duplicatas). Usar `_.nomeFuncao()`. Todas as funções do `@vueuse/core` também são re-exportadas via auto-import.

## Estrutura de Pastas do Front-End

> Confira a árvore real com `ls resources/` antes de assumir caminhos; a lista abaixo reflete o estado atual.

```
resources/
├── Vue/
│   ├── Components/    # Componentes reutilizáveis do projeto
│   ├── Layouts/       # Layouts de página
│   ├── Pages/         # Páginas/views
│   ├── Sections/      # Seções de funcionalidades (subpastas por domínio)
│   ├── Site/          # Área/páginas do site
│   └── Structure/     # Componentes estruturais
├── Stores/            # Stores @maxvue/max-pinia (organizados por domínio) — dir de auto-import
│   ├── calendar/
│   ├── Client/
│   ├── Component/
│   ├── Concessionaire/
│   ├── Equipments/
│   ├── Finance/
│   ├── Integrador/
│   ├── List/
│   ├── Location/
│   ├── Planner/
│   ├── Project/
│   ├── Promotion/
│   ├── Setting/
│   ├── Solar_company/
│   ├── Statistics/
│   ├── Support/
│   ├── UserStores/
│   └── Voip/
├── Functions/         # Funções de domínio (ex.: trt.ts) — dir de auto-import
├── Types/             # Tipos TypeScript / DTOs (gerados do backend)
│   ├── generated.d.ts # DTOs gerados automaticamente — NÃO EDITAR MANUALMENTE
│   ├── Global.d.ts
│   ├── Electrical.d.ts
│   ├── Menu.d.ts
│   └── Settings.d.ts
├── Helpers/           # Helpers do projeto (arquivos .ts + subpastas Chat/ e Locales/)
│   ├── Chat/          # Helpers de chat
│   └── Locales/       # i18n / localização
├── Js/                # Infra do SPA consumida por app.ts: router.ts (Vue Router),
│                      # ziggy.js + ziggy.d.ts (rotas Ziggy geradas),
│                      # configureReverbEcho.js (Echo/Reverb), inactivityWatcher.ts,
│                      # Composables/, Locales/ — fonte legítima de investigação
├── Theme/             # (ver "Pastas a Ignorar")
├── Views/ e views/    # (ver "Pastas a Ignorar")
├── App.vue            # Componente raiz (NÃO MODIFICAR sem aprovação)
├── app.ts             # Entry point (NÃO MODIFICAR sem aprovação)
└── env.d.ts           # Declarações de tipos globais
```

### Bibliotecas Próprias (código-fonte dentro do projeto, via link local)

As libs Max* são linkadas via `file:` a partir de `storage/libs/` do próprio engeapp:

```
storage/libs/MaxComponentsUi/   # @maxvue/max-components-ui
storage/libs/MaxUse/            # @maxvue/max-use
storage/libs/MaxPinia/          # @maxvue/max-pinia
```

> **IMPORTANTE:** Bugs podem se originar nestas bibliotecas. Se o stack trace apontar para `node_modules/@maxvue/`, investigar o código-fonte em `storage/libs/<Lib>/src/`.

### Pastas a Ignorar na Investigação

- `resources/Theme/`
- `resources/Views/` e `resources/views/`

> **Não ignorar `resources/Js/`:** é onde vivem `router.ts` (Vue Router), `ziggy.js`/`ziggy.d.ts`
> (rotas Ziggy geradas), `configureReverbEcho.js` (Echo/Reverb), `inactivityWatcher.ts`,
> `Composables/` e `Locales/` — todos importados pelo entry point `resources/app.ts`.
> Para bugs de **Roteamento**, **Ziggy/rotas** ou **Echo/realtime**, investigue ali.

## Instruções

### Fase 1: Coleta de Evidências

**OBRIGATÓRIO antes de qualquer tentativa de correção.**

#### 1.1 Verificar Logs do Navegador

Capturar erros recentes no console do navegador (DevTools → Console).

Procurar por:
- `[Vue warn]` — avisos do Vue (reatividade, props, template)
- `TypeError` / `ReferenceError` — erros de runtime JS/TS
- `Uncaught (in promise)` — promises rejeitadas
- `Failed to resolve component` — componentes não registrados
- Erros de rede (API calls falhando)

Na aba **Network** do DevTools, inspecionar as requisições `/api/...` (status, payload, resposta)
para separar falha de front de falha de backend.

#### 1.2 Verificar Erros do Backend

Verificar os logs do servidor Laravel (`storage/logs/laravel.log` / saída do `php artisan serve`) para identificar se o bug tem origem no backend (erro 500, validação 422, exceção de controller/serviço).

#### 1.3 Verificar Terminal do Vite

Verificar se o `npm run dev` está reportando erros:
- Erros de compilação TypeScript
- Erros de importação/resolução de módulos
- Warnings do Vite sobre dependências

#### 1.4 Verificar os Dados no Banco

Quando o bug parecer de dados (campo vazio, valor divergente), conferir direto no MySQL
(cliente SQL ou `php artisan tinker`) antes de acusar o front.

#### 1.5 Reproduzir o Problema

- Identificar os passos exatos para reprodução
- Verificar se o erro é consistente ou intermitente
- Anotar em qual componente/página ocorre

### Fase 2: Classificação do Bug

Classificar o bug em uma das categorias abaixo para direcionar o diagnóstico:

| Categoria | Sinais Típicos |
|-----------|----------------|
| **Reatividade** | Estado não atualiza, UI desatualizada, `.value` ausente, `watch` não dispara |
| **Tipagem TypeScript** | Erros TS2322, TS2345, TS2339, tipos incompatíveis, `Ref` vs valor primitivo |
| **Template/Renderização** | `v-if`/`v-for` incorretos, componentes não renderizando, key ausente |
| **MaxPinia/Store** | Estado global não sincroniza, store não reativo, ações falhando, auto-save não dispara, cache desatualizado |
| **MaxComponents** | Componente Max* com props/eventos incorretos, InputBase não valida, MaxTable quebrada |
| **MaxUse/Helpers** | `_` retornando undefined, composable com estado incorreto, `useRefCached` não persistindo |
| **MaxUse/Rotas** | `apiGetRoute`/`apiPostRoute` falhando, nome de rota (Ziggy) incorreto, upload com erro |
| **PrimeVue** | Componente PrimeVue puro (não Max*) quebrado, tema incorreto |
| **CSS/Layout** | Estilos não aplicados, UnoCSS não gerando classes, SCSS com erros, preset Max não carregado |
| **Roteamento** | Navegação falhando, parâmetros incorretos, guards com problema |
| **Build/HMR** | Vite não recarrega, erros de importação, módulos não resolvidos, lib local não atualizada |
| **Async/API** | Dados não carregando, race conditions, tratamento de erro ausente |
| **Auto-Import** | Composable/componente não reconhecido pelo TS, tipos faltando em `auto-import.d.ts` |

### Fase 3: Diagnóstico Guiado

#### Para bugs de Reatividade, TypeScript e Template/Renderização

Para causas genéricas de Vue 3/TS (`ref`/`.value`, `reactive` desestruturado, `computed` com side
effects, `watch`/`watchEffect`, `v-if` + `v-for` no mesmo elemento, `withDefaults`, `defineEmits`,
template refs) consulte as skills `vue-debugging-best-practices` (um guia por sintoma em
`reference/`), `vue` e `vue-typescript-best-practices`.

#### Para bugs de MaxPinia/Store (`@maxvue/max-pinia`)

Checklist:
- [ ] Dados de página estão vindo de uma store `@maxvue/max-pinia` (não de `apiGetRoute` manual no componente)?
- [ ] Auto-save (debounced) do MaxPinia disparando ao alterar o estado? Verificar se a alteração é feita no estado da store (não em cópia local)
- [ ] Camada de cache do MaxPinia (LocalForage) retornando dado obsoleto? A chave é formada por `getKey() = store.$id + '.' + (store.id ?? store.options.id ?? 'global')` (`storage/libs/MaxPinia/src/plugin.ts`). Ao diagnosticar cache cruzado/obsoleto, confira qual `id` a store está usando: sem `id`/`options.id`, a chave cai em `'.global'` e pode colidir entre instâncias. `options.key` **não** entra na chave de cache. Verificar invalidação/refetch
- [ ] Store usando `storeToRefs()` ao desestruturar estado/getters?
- [ ] Actions são chamadas como métodos (sem desestruturar)?
- [ ] Estado reativo não sendo substituído por reatribuição direta?
- [ ] Verificar se o store está registrado corretamente no MaxPinia?

#### Para bugs de MaxComponents (`@maxvue/max-components-ui`)

Checklist:
- [ ] Componente Max* está sendo auto-importado? Verificar `auto-import-components.d.ts`
- [ ] Props do componente Max* correspondem à API definida no source (`MaxComponentsUi/src/components/`)?
- [ ] `InputBase` está recebendo as props de erro/validação corretamente?
- [ ] `v-model` funciona com o componente? Verificar se o componente usa `defineModel()` ou `emit('update:modelValue')`
- [ ] Stores internas da lib (`useConfirmStore`, `useModalStore`, `usePopoverStore`) estão funcionando?
- [ ] Eventos customizados do componente estão com a assinatura correta?
- [ ] O bug é no componente Max* ou no PrimeVue subjacente? Verificar se o problema persiste usando o PrimeVue puro

> **Regra:** Se o bug está no source da lib, corrija em `storage/libs/MaxComponentsUi/src/` e siga o **"Fluxo de Atualização das Bibliotecas Locais"** (rebuild + restart) descrito adiante.

#### Para bugs de MaxUse — Helpers e Composables (`@maxvue/max-use`)

Checklist:
- [ ] Função/composable é própria da MaxUse ou re-exportação do VueUse/Lodash?
- [ ] Se é do namespace `_` — verificar prioridade de resolução (próprio > VueUse > Lodash)
- [ ] `useRefCached` — localStorage está acessível? Chave de cache correta?
- [ ] `useRefCachedApi` — endpoint da API respondendo? Fallback para cache funcionando?
- [ ] `useDefaultReset` — estado padrão está correto? Reset não está quebrando reatividade?
- [ ] `useTimeAgo` — locale configurado corretamente?
- [ ] Helpers de `Electrical` — fórmulas fotovoltaicas retornando valores corretos?
- [ ] Helpers de `Validations` — regras de CPF/CNPJ/CEP validando corretamente?
- [ ] Helpers de `Format` — formatação de moeda/número/data correta?

> **Regra:** Se o bug está no source da lib, corrija em `storage/libs/MaxUse/src/` e siga o **"Fluxo de Atualização das Bibliotecas Locais"** (rebuild + restart) descrito adiante.

#### Para bugs de MaxUse — Sistema de Rotas

Checklist:
- [ ] Nome de rota (Ziggy) existe no backend? Verificar com `php artisan route:list` (coluna Name) — é o nome que o helper resolve para a URL `/api/...`
- [ ] Parâmetros da rota sendo passados corretamente (`apiGetRoute('recurso.data', { id: 1 })` — passa-se o **nome** da rota; o helper do MaxUse resolve via Ziggy para o caminho `/api/...`)
- [ ] `apiPostRoute` — corpo da requisição com dados corretos?
- [ ] `apiUploadRoute` — arquivo sendo enviado como `FormData`?
- [ ] Erros de CORS ou autenticação? A auth do engeapp é por **guard `web`** (padrão em `config/auth.php`: `AUTH_GUARD=web`) — login via `AuthenticatedSessionController` + `Auth::attempt`, **sessão em banco + cookie**. O MaxUse já aplica `withCredentials=true`, então o cookie de sessão vai junto; não há bootstrap clássico de `/sanctum/csrf-cookie` no front (nenhuma **chamada** a essa rota em `resources/`; a ocorrência de `sanctum.csrf-cookie` em `Js/ziggy.js`/`Js/ziggy.d.ts` é apenas a tabela de rotas gerada). Não procurar Bearer/token nem fluxo Sanctum SPA
- [ ] Resposta HTTP sendo tratada (status 200 vs 422 vs 500)?

#### Para bugs de PrimeVue (componentes puros, não Max*)

Checklist:
- [ ] Componente foi importado **explicitamente**? Componentes PrimeVue puros **não** são auto-importados (o `unplugin-vue-components` usa só o `MaxComponentsUiResolver`, que resolve apenas nomes `Max*`/aliases do manifest). Use `import Dialog from 'primevue/dialog'` — como em `resources/Vue/Sections/Project/Files/OnlyOfficeEditor.vue`
- [ ] Props seguem a API da versão instalada?
- [ ] Eventos seguem a convenção do PrimeVue (camelCase)?
- [ ] Slots estão usando a sintaxe correta?
- [ ] Tema/estilo do PrimeVue está carregado? (verificar `src/prime/` na MaxComponentsUi)

#### Para bugs de CSS/Layout

Checklist:
- [ ] Classes UnoCSS estão sendo geradas? (verificar no DevTools)
- [ ] Preset `presetMaxUno` da MaxComponentsUi está ativo no `uno.config.ts`?
- [ ] `<style lang="scss" scoped>` — `scoped` impede estilizar filhos?
- [ ] Deep selector `:deep()` usado quando necessário para estilizar filhos?
- [ ] Variáveis CSS estão definidas e acessíveis no escopo?
- [ ] Conflitos de especificidade entre UnoCSS e estilos customizados?
- [ ] Estilos da MaxComponentsUi (`src/styles/`) conflitando com estilos locais?

#### Para bugs de Build/HMR

Checklist:
- [ ] Importações circulares?
- [ ] Módulo não encontrado — verificar `tsconfig.json` paths e `vite.config.ts` aliases?
- [ ] **Bibliotecas locais desatualizadas?** Seguir o **"Fluxo de Atualização das Bibliotecas Locais"** (rebuild da lib + restart do dev)
- [ ] Auto-import falhou — rodar `npm run dev` novamente para regenerar tipos?
- [ ] Cache do Vite corrompido — limpar `node_modules/.vite`?
- [ ] `auto-import.d.ts` ou `auto-import-components.d.ts` não gerados? Verificar configuração do Vite

#### Para bugs Async/API

Checklist:
- [ ] `await` sendo usado corretamente em chamadas async?
- [ ] Usando `apiGetRoute`/`apiPostRoute` da MaxUse (não `fetch` ou `axios` direto)?
- [ ] Tratamento de erro com `try/catch` ou `.catch()`?
- [ ] Loading state sendo gerenciado durante operações async?
- [ ] Race conditions — última resposta sobrescrevendo com `watchEffect` cleanup?
- [ ] Dados nulos/undefined sendo tratados antes do uso no template?

#### Para bugs de Auto-Import

Checklist:
- [ ] Composable/componente aparece no `auto-import.d.ts` ou `auto-import-components.d.ts`?
- [ ] `maxUseAutoImport` está configurado no `vite.config.ts`?
- [ ] Após adicionar novo export na MaxUse/MaxComponents, rodou `npm run build` na lib?
- [ ] TypeScript reconhece o tipo mas o runtime não encontra? Verificar se o export existe no `index.ts` da lib
- [ ] Conflito de nomes entre exports da MaxUse e VueUse? Verificar resolução de ambiguidade no `index.ts` da MaxUse

### Fase 4: Correção

#### Regras de Correção

1. **Corrigir a causa raiz, NÃO o sintoma**
   - ❌ `user?.profile?.name || 'N/A'` (esconde o problema)
   - ✅ Garantir que `user.profile` é carregado antes de renderizar

2. **Uma correção por vez** — não misturar refatorações com bug fixes

3. **Respeitar as convenções do projeto:**
   - Composition API com `<script setup lang="ts">` — SEMPRE
   - Ordem nos SFCs: `<template>` → `<script setup>` → `<style lang="scss">`
   - Nomes descritivos para variáveis e métodos
   - Comentários em pt-BR
   - Usar componentes Max* em vez de PrimeVue puro quando disponível
   - Usar `apiGetRoute`/`apiPostRoute` da MaxUse para chamadas HTTP (não `fetch`/`axios` direto)
   - Usar helpers do `_` (MaxUse) antes de implementar lógica utilitária customizada

4. **Verificar componentes irmãos** antes de criar algo novo

5. **Verificar se o bug é do projeto ou da lib** — se for da lib, corrigir no source da lib

6. **Apresentar plano de correção** para aprovação antes de implementar

#### Template do Plano de Correção

```markdown
## Bug: [Descrição curta]

**Sintoma:** [O que o usuário vê/experimenta]

**Causa Raiz:** [O que realmente está errado no código]

**Arquivo(s) Afetado(s):**
- `path/to/file.vue` (linha X)

**Correção Proposta:**
- [Descrever a mudança]

**Impacto:**
- [Outros componentes afetados, se houver]
```

### Fase 5: Validação Pós-Correção

- [ ] Bug original não reproduz mais
- [ ] Nenhum novo warning do Vue no console
- [ ] Nenhum erro TypeScript novo — rodar `npm run typecheck:tsgo` (= `tsgo --noEmit`); NÃO usar `npm run build` (que é só `vite build`, sem type-check dedicado). Alternativamente, verificar a IDE. Lint: `npm run lint` (= `eslint resources/ --fix`)
- [ ] Componentes relacionados continuam funcionando
- [ ] HMR recarregou corretamente (ou reiniciar `npm run dev` se necessário)
- [ ] Executar lint do ESLint se aplicável

### Skills Relacionadas

Ativar conforme necessário durante o diagnóstico (usar apenas skills que existam de fato neste ambiente):

| Skill | Quando Ativar |
|-------|---------------|
| `superpowers:systematic-debugging` | Bugs difíceis que necessitam investigação sistemática em fases |
| `superpowers:test-driven-development` | Reproduzir o bug com um teste antes de corrigir — no front, adicionar um spec em `tests/Js/` (Vitest, via `vitest.config.ts` da raiz) quando aplicável; no backend, Pest (`php artisan test`) |

> Para regras específicas de Vue 3 / TypeScript / MaxPinia / MaxComponentsUi / MaxUse, este documento já consolida os checklists; não dependa de skills `@...` que possam não existir no repositório.

### Fluxo de Atualização das Bibliotecas Locais

Quando o bug for corrigido no código-fonte de uma biblioteca própria:

```bash
# 1. Corrigir o código-fonte na lib
# Em storage/libs/MaxComponentsUi/src/, storage/libs/MaxUse/src/ ou storage/libs/MaxPinia/src/

# 2. Rebuildar a lib (a partir da raiz do engeapp)
cd storage/libs/MaxComponentsUi && npm run build
# ou
cd storage/libs/MaxUse && npm run build
# ou
cd storage/libs/MaxPinia && npm run build

# 3. Reiniciar o dev server do EngeApp
# (parar e reiniciar npm run dev no engeapp)
```

> **Atenção:** `storage/libs/MaxComponentsUi`, `storage/libs/MaxUse` e `storage/libs/MaxPinia` são
> **symlinks** para os repositórios irmãos (`/home/johnattas/GitHub/MaxComponentsUi`, `.../MaxUse`,
> `.../MaxPinia`). Editar/rebuildar ali altera o repositório externo, não uma cópia local do engeapp.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Esta skill é focada em bugs do **front-end**.
- Não modificar `App.vue`, `app.ts` ou `env.d.ts` sem aprovação explícita.
- Não modificar `resources/Types/generated.d.ts` manualmente — é gerado pelo backend.
- Sempre apresentar plano de correção antes de implementar.
- Não substituir esta skill por validação manual, testes ou revisão humana.
