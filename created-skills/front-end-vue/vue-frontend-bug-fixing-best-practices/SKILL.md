---
name: vue-frontend-bug-fixing-best-practices
description: Use when diagnosing and fixing front-end bugs in the EngeApp project built with Vue 3 + TypeScript + MaxPinia (@maxvue/max-pinia) + UnoCSS + MaxComponentsUi + MaxUse — visual glitches, reactivity issues, TS type errors, broken MaxPinia stores (cache/auto-save), MaxComponentsUi/MaxUse component or composable failures, Vite/HMR breakage, or routing problems.
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
| Vue | 3.6.0-beta.17 | Composition API + `<script setup lang="ts">` — SEMPRE |
| TypeScript | Strict mode | Tipagem obrigatória em todo front-end |
| **@maxvue/max-pinia** | **local** | **State management — camada de cache + auto-save (debounced). TODO GET/save de dados de página passa por stores MaxPinia (sobre Pinia 3). Não usar Pinia puro nem GET/POST manual para dados de página.** |
| Vue Router | 4 | SPA pura (Adonis serve catch-all HTML) — rotas de API resolvidas por helpers do `@maxvue/max-use` para caminhos string `/api/...` (sem Ziggy) |
| PrimeVue | — | Componentes base para UI (base da MaxComponentsUi) |
| UnoCSS | 66 | Estilização utilitária (sem Tailwind) |
| Vite | 8 | Bundler + HMR |
| Unplugin Auto Import | — | Auto-importação de composables e helpers |
| Unplugin Vue Components | — | Auto-importação de componentes |
| **@maxvue/max-components-ui** | **local** | **Biblioteca própria de componentes UI (58 componentes + componentes do PrimeVue inclusos)** |
| **@maxvue/max-use** | **local** | **Biblioteca própria de composables, helpers, rotas e utilitários** |
| @adonisjs/transmit-client | 1 | Realtime via SSE (AdonisJS Transmit) |
| @vue-flow/core | 1 | Diagramas de fluxo |
| @tanstack/vue-virtual | 3 | Virtualização de listas |
| floating-vue | 5 | Tooltips e popovers |
| lucide-vue-next | 1 | Ícones |
| Vitest | 4 | Testes unitários front-end |

### Bibliotecas Próprias — Contexto Obrigatório

#### `@maxvue/max-components-ui` (link local: `file:../MaxComponentsUi`)

Biblioteca de **componentes UI** construída sobre PrimeVue com estilos e comportamentos customizados.
Código-fonte em: `/home/johnattas/GitHub/MaxComponentsUi/src/`

**Componentes principais (58 total):**
- **Inputs:** `MaxInputText`, `MaxInputNumber`, `MaxInputSelect`, `MaxInputAutoComplete`, `MaxInputAutoCompleteApi`, `MaxInputCep`, `MaxInputCpfCnpj`, `MaxInputDatePicker`, `MaxInputCheckbox`, `MaxInputRadio`, `MaxInputSwitch`, `MaxInputToggle`, `MaxInputTextArea`, `MaxInputSearch`, `MaxInputPhoneMail`, `MaxInputCoordinateDecimalLat/Lng`
- **Upload:** `MaxInputFile`, `MaxInputFileUpload`, `MaxInputFileUploadBig`, `MaxInputFileUploadButton`, `MaxInputFileProject`
- **Botões:** `MaxButton` (aliases: `Button`, `Botao`), `MaxIconButton`, `MaxIconConfirm`
- **Layout:** `MaxGrid`, `MaxGridCols`, `MaxTable`, `MaxTableColumn`, `MaxModal`, `MaxPopover`, `MaxPopoverConfirm`, `MaxTogglePopover`
- **Feedback:** `MaxLoader`, `MaxLoaderAi`, `MaxLoaderIcon`, `MaxDoneIcon`, `MaxErrorIcon`, `MaxWaitIcon`, `MaxBadgeComponent`, `MaxMsgLabels`, `MaxEmptyDiv`
- **Navegação:** `MaxLink`, `MaxLogo`, `MaxUserAvatar`
- **Mídia:** `MaxIcon` (Iconify), `MaxPdfView`, `MaxMaps`
- **Animação:** `MaxAnimateFade`, `TransitionFade`, `MaxTransitionFadeLight`, `MaxTransitionUp`
- **Títulos:** `MaxTitle1`, `MaxTitle2`
- **Base:** `InputBase` (wrapper de todos os inputs — gerencia labels, erros, ícones)

**Stores internas da lib:**
- `useConfirm.Store` — diálogos de confirmação
- `usePopover.Store` — controle de popovers

**Temas e estilos:**
- `src/themes/` — temas PrimeVue customizados
- `src/styles/` — estilos base da biblioteca
- `src/prime/` — configurações PrimeVue
- `src/presetMaxUno.ts` — preset UnoCSS da biblioteca

#### `@maxvue/max-use` (link local: `file:../MaxUse`)

Biblioteca de **composables, helpers e utilitários** que unifica helpers próprios, VueUse e Lodash.
Código-fonte em: `/home/johnattas/GitHub/MaxUse/src/`

**Composables próprios:**
- `useDefaultReset` — reset de estado para valores padrão
- `useRefCached` — ref com cache em localStorage
- `useRefCachedApi` — ref com cache + sincronização com API
- `useTimeAgo` — formatação de tempo relativo

**Módulos de Helpers (namespace `_`):**
- `Browser` — utilitários do navegador
- `Dates` — manipulação de datas (inclui `now()`)
- `Iterables` — operações em iteráveis
- `Math` — cálculos matemáticos
- `Objects` — manipulação de objetos (inclui `get()`, `set()`)
- `Strings` — manipulação de strings
- `Types` — verificação de tipos (inclui `isObject()`)
- `Validations` — validações de dados
- `Electrical` — cálculos elétricos fotovoltaicos
- `Format` — formatação de valores

**Sistema de Rotas (helpers do `@maxvue/max-use`, caminhos `/api/...` — sem Ziggy):**
- `apiGetRoute` — GET requests
- `apiPostRoute` — POST requests
- `apiPutRoute` — PUT requests
- `apiDeleteRoute` — DELETE requests
- `apiUploadRoute` — upload de arquivos
- `apiRoute` — rota genérica
- `getRoute` — obter URL de rota nomeada
- `goToRoute` — navegar para rota

**Objeto utilitário `_` (underscore):**
A biblioteca exporta `_` como um objeto centralizado que unifica helpers próprios + VueUse + Lodash, com prioridade para os próprios (sem duplicatas). Usar `_.nomeFuncao()` para acessar qualquer utilitário.

**Re-exportações do VueUse:**
Todas as funções do `@vueuse/core` são re-exportadas e disponíveis via auto-import.

## Estrutura de Pastas do Front-End

```
resources/
├── Vue/
│   ├── Components/    # Componentes reutilizáveis do projeto
│   ├── Layouts/       # Layouts de página
│   ├── Pages/         # Páginas/views
│   ├── Sections/      # Seções de funcionalidades (subpastas por domínio)
│   └── Structure/     # Componentes estruturais
├── Stores/            # Stores @maxvue/max-pinia (organizados por domínio)
│   ├── Client/
│   ├── Component/
│   ├── Concessionaire/
│   ├── Equipments/
│   ├── List/
│   ├── Location/
│   ├── Planner/
│   ├── Project/
│   ├── Setting/
│   ├── Support/
│   ├── UserStores/
│   ├── _Plugins/      # Plugins do MaxPinia/Pinia
│   └── calendar/
├── Types/             # Tipos TypeScript / DTOs (gerados do backend)
│   ├── generated.d.ts # DTOs gerados automaticamente — NÃO EDITAR MANUALMENTE
│   ├── Global.d.ts
│   ├── Electrical.d.ts
│   ├── Menu.d.ts
│   └── Settings.d.ts
├── Functions/         # Composables e funções do projeto (2 arquivos)
├── Helpers/           # Helpers do projeto (34 arquivos + subpastas)
│   ├── Composables/   # Composables específicos do projeto
│   ├── Chat/          # Helpers de chat
│   └── Locales/       # i18n / localização
├── App.vue            # Componente raiz (NÃO MODIFICAR sem aprovação)
├── app.ts             # Entry point (NÃO MODIFICAR sem aprovação)
└── env.d.ts           # Declarações de tipos globais
```

### Bibliotecas Próprias (código-fonte fora do projeto)

```
/home/johnattas/GitHub/MaxComponentsUi/   # @maxvue/max-components-ui
/home/johnattas/GitHub/MaxUse/            # @maxvue/max-use
```

> **IMPORTANTE:** Bugs podem se originar nestas bibliotecas. Se o stack trace apontar para `node_modules/@maxvue/`, investigar o código-fonte nos caminhos acima.

### Pastas a Ignorar na Investigação

- `resources/Brain/`
- `resources/Theme/`
- `resources/Views/`
- `resources/Js/`

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

#### 1.2 Verificar Erros do Backend

Verificar os logs do servidor AdonisJS (saída do `node ace serve --watch` / logger do Adonis) para identificar se o bug tem origem no backend (erro 500, validação 422, exceção de controller/serviço).

#### 1.3 Verificar Terminal do Vite

Verificar se o `npm run dev` está reportando erros:
- Erros de compilação TypeScript
- Erros de importação/resolução de módulos
- Warnings do Vite sobre dependências

#### 1.4 Reproduzir o Problema

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
| **MaxUse/Rotas** | `apiGetRoute`/`apiPostRoute` falhando, caminho `/api/...` incorreto, upload com erro |
| **PrimeVue** | Componente PrimeVue puro (não Max*) quebrado, tema incorreto |
| **CSS/Layout** | Estilos não aplicados, UnoCSS não gerando classes, SCSS com erros, preset Max não carregado |
| **Roteamento** | Navegação falhando, parâmetros incorretos, guards com problema |
| **Build/HMR** | Vite não recarrega, erros de importação, módulos não resolvidos, lib local não atualizada |
| **Async/API** | Dados não carregando, race conditions, tratamento de erro ausente |
| **Auto-Import** | Composable/componente não reconhecido pelo TS, tipos faltando em `auto-imports.d.ts` |

### Fase 3: Diagnóstico Guiado

#### Para bugs de Reatividade

Checklist:
- [ ] Acessando `.value` corretamente em `ref()` dentro do `<script>`?
- [ ] Usando `reactive()` sem desestruturar? (desestruturação quebra reatividade)
- [ ] `computed()` retornando valor derivado sem side effects?
- [ ] `watch` usando getter function para propriedades de objetos reativos?
- [ ] `watchEffect` não tem `await` antes das dependências rastreadas?
- [ ] Usando `toRef()` / `toRefs()` ao passar props para composables?
- [ ] Usando `shallowRef` quando deveria usar `ref` (ou vice-versa)?
- [ ] Objetos não-reativos sendo marcados com `markRaw()` quando necessário?

#### Para bugs de TypeScript

Checklist:
- [ ] Tipo `Ref<T>` vs `T` — atribuindo valor a `.value` corretamente?
- [ ] `defineProps` com tipos importados suportados? (limitações de tipos complexos)
- [ ] `withDefaults` usando factory function para valores mutáveis?
- [ ] Template refs tipados com `ref<InstanceType<typeof Component> | null>(null)`?
- [ ] Eventos tipados com `defineEmits<{...}>()`?
- [ ] Verificar se o auto-import gerou os tipos no `auto-imports.d.ts`?

#### Para bugs de Template/Renderização

Checklist:
- [ ] `v-for` tem `:key` único e estável?
- [ ] `v-if` e `v-for` não estão no mesmo elemento?
- [ ] `v-if` verifica nulidade antes de acessar propriedades?
- [ ] Componentes filhos em `v-for` recebem props corretamente?
- [ ] `v-model` está no elemento correto (não em `<template>`)?
- [ ] Slots nomeados sendo usados com `v-slot:nome` ou `#nome`?

#### Para bugs de MaxPinia/Store (`@maxvue/max-pinia`)

Checklist:
- [ ] Dados de página estão vindo de uma store `@maxvue/max-pinia` (não de `apiGetRoute` manual no componente)?
- [ ] Auto-save (debounced) do MaxPinia disparando ao alterar o estado? Verificar se a alteração é feita no estado da store (não em cópia local)
- [ ] Camada de cache do MaxPinia retornando dado obsoleto? Verificar invalidação/refetch
- [ ] Store usando `storeToRefs()` ao desestruturar estado/getters?
- [ ] Actions são chamadas como métodos (sem desestruturar)?
- [ ] Estado reativo não sendo substituído por reatribuição direta?
- [ ] Verificar se o store está registrado corretamente no MaxPinia?

#### Para bugs de MaxComponents (`@maxvue/max-components-ui`)

Checklist:
- [ ] Componente Max* está sendo auto-importado? Verificar `components.d.ts`
- [ ] Props do componente Max* correspondem à API definida no source (`MaxComponentsUi/src/components/`)?
- [ ] `InputBase` está recebendo as props de erro/validação corretamente?
- [ ] `v-model` funciona com o componente? Verificar se o componente usa `defineModel()` ou `emit('update:modelValue')`
- [ ] Stores internas da lib (`useConfirm.Store`, `useModal.Store`, `usePopover.Store`) estão funcionando?
- [ ] Eventos customizados do componente estão com a assinatura correta?
- [ ] O bug é no componente Max* ou no PrimeVue subjacente? Verificar se o problema persiste usando o PrimeVue puro

> **Regra:** Se o bug está no código-fonte da biblioteca, corrigir em `/home/johnattas/GitHub/MaxComponentsUi/src/`. Depois rodar `npm run build` na lib e reiniciar `npm run dev` no EngeApp.

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

> **Regra:** Se o bug está no código-fonte da biblioteca, corrigir em `/home/johnattas/GitHub/MaxUse/src/`. Depois rodar `npm run build` na lib e reiniciar `npm run dev` no EngeApp.

#### Para bugs de MaxUse — Sistema de Rotas

Checklist:
- [ ] Caminho/rota `/api/...` existe no backend? Verificar na lista de rotas do Adonis
- [ ] Parâmetros da rota sendo passados corretamente (`apiGetRoute('nome.rota', { id: 1 })`)
- [ ] `apiPostRoute` — corpo da requisição com dados corretos?
- [ ] `apiUploadRoute` — arquivo sendo enviado como `FormData`?
- [ ] Erros de CORS ou autenticação? Auth é sessão + cookie (guard web) — verificar se o cookie de sessão está sendo enviado (`withCredentials`), não procurar Bearer/token
- [ ] Resposta HTTP sendo tratada (status 200 vs 422 vs 500)?

#### Para bugs de PrimeVue (componentes puros, não Max*)

Checklist:
- [ ] Componente está sendo auto-importado corretamente?
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
- [ ] **Bibliotecas locais desatualizadas?** Rodar `npm run build` em MaxComponentsUi/MaxUse e reiniciar `npm run dev`
- [ ] Auto-import falhou — rodar `npm run dev` novamente para regenerar tipos?
- [ ] Cache do Vite corrompido — limpar `node_modules/.vite`?
- [ ] `auto-imports.d.ts` ou `components.d.ts` não gerados? Verificar configuração do Vite

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
- [ ] Composable/componente aparece no `auto-imports.d.ts` ou `components.d.ts`?
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
- [ ] Nenhum erro TypeScript novo (`npm run build` ou verificar IDE)
- [ ] Componentes relacionados continuam funcionando
- [ ] HMR recarregou corretamente (ou reiniciar `npm run dev` se necessário)
- [ ] Executar lint do ESLint se aplicável

### Skills Relacionadas

Ativar conforme necessário durante o diagnóstico (usar apenas skills que existam de fato neste ambiente):

| Skill | Quando Ativar |
|-------|---------------|
| `superpowers:systematic-debugging` | Bugs difíceis que necessitam investigação sistemática em fases |
| `superpowers:test-driven-development` | Reproduzir o bug com um teste (Vitest) antes de corrigir |

> Para regras específicas de Vue 3 / TypeScript / MaxPinia / MaxComponentsUi / MaxUse, este documento já consolida os checklists; não dependa de skills `@...` que possam não existir no repositório.

### Fontes de Diagnóstico Disponíveis

| Fonte | Uso |
|-------|-----|
| Console do navegador (DevTools) | Logs/erros do front-end (`[Vue warn]`, runtime errors) |
| Logs do servidor AdonisJS | Último erro/exceção do backend (controller/serviço/validação) |
| Aba Network (DevTools) | Inspecionar requisições `/api/...` (status, payload, resposta) |
| PostgreSQL (psql / cliente) | Verificar dados no banco quando o bug parecer de dados |
| Terminal do Vite | Erros de compilação/HMR |

### Fluxo de Atualização das Bibliotecas Locais

Quando o bug for corrigido no código-fonte de uma biblioteca própria:

```bash
# 1. Corrigir o código-fonte na lib
# Em MaxComponentsUi/src/ ou MaxUse/src/

# 2. Rebuildar a lib
cd /home/johnattas/GitHub/MaxComponentsUi && npm run build
# ou
cd /home/johnattas/GitHub/MaxUse && npm run build

# 3. Reiniciar o dev server do EngeApp
# (parar e reiniciar npm run dev no engeapp)
```

## Restrições

- Esta skill é focada em bugs do **front-end**.
- Não modificar `App.vue`, `app.ts` ou `env.d.ts` sem aprovação explícita.
- Não modificar `resources/Types/generated.d.ts` manualmente — é gerado pelo backend.
- Sempre apresentar plano de correção antes de implementar.
- Não substituir esta skill por validação manual, testes ou revisão humana.
