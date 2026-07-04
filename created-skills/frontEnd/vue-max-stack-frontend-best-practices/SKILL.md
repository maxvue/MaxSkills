---
name: vue-max-stack-frontend-best-practices
description: "Use when developing the Vue 3 front-end of EngeApp (Laravel 13 backend) with Vue Router, MaxComponentsUi, MaxUse and MaxPinia. Triggers on creating or editing components, pages, Pinia stores, composables or routes; building forms, tables, modals, grids; API calls via axios + MaxPinia /api string paths (no Ziggy); Max* components or @maxvue/* imports — even if the user never says \"Max\"."
---

# Front-end Vue do Ecossistema Max (EngeApp — Laravel 13)

## Objetivo

Produzir código front-end consistente, idiomático e alinhado para o projeto **EngeApp** (backend **Laravel 13** / PHP 8.4 / MySQL). Stack de UI: **Vue 3 (Composition API) + Vue Router + UnoCSS/SCSS** sobre as bibliotecas locais **MaxComponentsUi**, **MaxUse** e **MaxPinia**.

Esta skill é autocontida: ela traz os padrões reais do stack de front-end sobre o backend Laravel 13.

## Por que essas convenções importam

O ecossistema Max depende fortemente de **auto-import** (`unplugin-auto-import`) e **auto-resolução de componentes** (`unplugin-vue-components`). Isso significa que `ref`, `computed`, `watch`, `defineStore`, `axios`, as stores e os componentes `Max*` ficam disponíveis **sem import manual**. Seguir o padrão não é estética: import duplicado, ordem de blocos errada ou SCSS que reimplementa o que o UnoCSS já resolve quebram o lint, incham o bundle e divergem do que o resto da base espera. Quando você escreve no mesmo idioma da base, o código "desaparece" — que é o objetivo.

## 1. Estrutura do SFC (regra rígida — vem do ESLint)

Ambos os projetos compartilham o mesmo `eslint.config.js` (regras `@stylistic` + `vue/*`). Siga exatamente:

- **Ordem dos blocos**: `<template>` → `<script setup lang="ts">` → `<style lang="scss" scoped>`. (`vue/block-order`)
- **Sempre Composition API** com `<script setup lang="ts">`. Options API é proibida.
- **Indentação**: 4 espaços, em `.ts`, `.js` e dentro de `<script>` e `<template>`.
- **Aspas simples** (`'texto'`), nunca duplas no JS/TS.
- **Ponto e vírgula** obrigatório ao fim de cada instrução.
- **Sem vírgula pendente** (`comma-dangle: never`).
- **Arrow parens sempre**: `(x) => x`, nunca `x => x`.
- **Atributos sempre inline (regra absoluta)**: mantenha **todos** os props/atributos de uma tag — componente, `div` ou qualquer elemento — em **uma única linha**, por mais atributos que tenha. **Nunca** quebre atributos em múltiplas linhas no `<template>`.

  ❌ Errado — atributos quebrados em várias linhas:
  ```vue
  <MaxModal
      ref="cardModal"
      no-button
      class="card-modal"
  >
  ```

  ✅ Certo — tudo na mesma linha:
  ```vue
  <MaxModal ref="cardModal" no-button class="card-modal">
  ```
- **Nunca use `<section>`**: use sempre `<div>` no lugar de `<section>` (e de outras tags seccionais como `<article>`/`<aside>`) para agrupar conteúdo.
- **Nunca use inputs/botões nativos em código de aplicação**: nada de `<input>`, `<button>`, `<select>`, `<textarea>`, `<checkbox>` crus. Use **sempre** os componentes da biblioteca **MaxComponentsUi**. Mapeamento:
  - `<input type="text">` → `<MaxInputText>` · número → `<MaxInputNumber>` · CPF/CNPJ → `<MaxInputCpfCnpj>` · CEP → `<MaxInputCep>` · telefone/e-mail → `<MaxInputPhoneMail>`
  - `<textarea>` → `<MaxInputTextArea>` · `<select>` → `<MaxInputSelect>` · `<input type="checkbox">` → `<MaxInputCheckbox>` · `<input type="file">` → `<MaxInputFileUpload>`/`<MaxInputFileUploadButton>`
  - `<button>` → `<MaxButton>` (ou `<MaxIconButton>` para botão só-ícone)

  ❌ `<button @click="salvar">Salvar</button>`  →  ✅ `<MaxButton label="Salvar" icon="mdi:content-save" @click="salvar" />`

  (Exceção: **dentro** da própria biblioteca MaxComponentsUi — ao construir os wrappers via `InputBase` — o elemento nativo é a primitiva e é permitido.)
- **Nunca use headings nativos como título**: nada de `<h1>`/`<h2>` (nem `<h3>`/`<h4>`). Use `<MaxTitle1 h1="Título" h2="Subtítulo" />` para o título principal e `<MaxTitle2 h1="Título da seção" />` para títulos de seção.
- **Formulários usam `MaxGrid` (nunca `MaxGridCols`)**: dimensione os campos internos com atributos UnoCSS — `s-[porcentagem]` (ex.: `s-30` = 30% da largura do formulário) e `[w|h]-[max|min]-[valor]` (px sem unidade, ou `rem`: `w-max-300`, `h-min-50`, `w-min-10rem`). Não monte grids/larguras manuais com CSS.
- **Nunca importe `@vueuse/core` nem `lodash` diretamente**: use os composables e utilitários do **MaxUse** (`@maxvue/max-use`) — o objeto `_` (estilo lodash) para helpers e os composables do MaxUse para reatividade. Se o composable/helper necessário ainda não existir no MaxUse, adicione-o lá (encapsulando o VueUse), em vez de importar `@vueuse/core`/`lodash` no código de aplicação.
- **Comentários sempre em pt-BR.**

Esqueleto canônico:

```vue
<template>
    <div class="entidade-page" s100 flex flex-col>
        <MaxLoader v-if="loading" label="Carregando..." />
        <MaxGrid v-else>
            <MaxButton label="Novo" icon="mdi:plus" @click="abrirCriacao" />
        </MaxGrid>
    </div>
</template>

<script setup lang="ts">
    // vue, vue-router, defineStore e stores são auto-importados — não reimporte.
    const route = useRoute();
    // Todo GET de dados de página passa por uma store @maxvue/max-pinia (cache + auto-save).
    // Não faça axios.get direto no componente — consuma a store cacheada.
    const store = useEntidadesStore();
    // MaxPinia popula o GET cacheado em store.data (não em um ref de nome arbitrário).
    const { data, loading } = storeToRefs(store);

    // O GET é automático ao montar a store (MaxPinia). Para revalidar, use store.reload().
</script>

<style lang="scss" scoped>
.entidade-page {
    display: flex;
    flex-direction: column;
    height: 100%;
}
</style>
```

> **Auto-import**: confira `vite.config.ts` e `auto-imports.d.ts` do projeto antes de adicionar um import manual de `vue`/`vue-router`/`pinia`/`axios` — quase sempre já está disponível. Importe manualmente apenas o que não está coberto (tipos, libs de terceiros, componentes específicos de `@maxvue/max-components-ui` quando precisar do tipo).

## 2. Componentes: MaxComponentsUi (PrimeVue por baixo)

Prefira sempre o componente `Max*` a um elemento HTML cru. Eles já trazem tema, acessibilidade e integração com o restante da UI. **Escolha o componente mais específico que existir** — há um input dedicado para cada tipo de dado (CPF, CEP, telefone, data). Usar o wrapper genérico `MaxInputText` onde existe um dedicado obriga você a reimplementar máscara e validação que o componente já entrega de graça.

### Use o input dedicado (não reinvente máscara/validação)

| Dado | Componente | Em vez de |
|------|------------|-----------|
| CPF/CNPJ | `MaxInputCpfCnpj` (prop `cpf` ou `cnpj`) | `MaxInputText` + regex |
| CEP | `MaxInputCep` | `MaxInputText` + máscara |
| Telefone | `MaxPhoneField` / `MaxInputPhoneMail` | `MaxInputText` + `formatPhone` |
| Data | `MaxInputDatePicker` | `MaxInputText` |
| Endereço | `MaxInputTypeAddress` | vários `MaxInputText` |
| Número | `MaxInputNumber` | `MaxInputText` + parse |
| Seleção | `MaxInputSelect`, `MaxInputSelectTag`, `MaxInputAutoCompleteApi` | — |
| Texto longo | `MaxInputTextArea`, `MaxInputMarkdown` | — |
| Lista de texto | `MaxInputTextList` | — |
| Switch/checkbox/radio | `MaxInputSwitch`, `MaxInputCheckbox`, `MaxInputRadio` | — |
| Upload | `MaxInputFileUpload`, `MaxInputFileUploadButton` | `<input type=file>` |

Todos herdam layout e estado de erro do `InputBase`: controle com `:done="isValid"`, `:error="mensagemErro"`, `:caution="aviso"` e `v-model` para o valor.

### Componentes estruturais (nomes reais)

- **Botões**: `MaxButton`, `MaxIconButton`.
- **Layout/grid**: `MaxGrid` (wrapper flexbox) ou `MaxGridCols` (24 colunas). **Ao montar formulários, use sempre `MaxGrid` — nunca `MaxGridCols`.** Os elementos internos (inputs, etc.) recebem o dimensionamento por props/atributos UnoCSS diretamente:
  - **Largura percentual do formulário**: `s-[porcentagem]` → `s-30` ocupa 30% da largura do formulário, `s-50` = 50%, `s-100` = 100%. (Os atalhos discretos `s100`/`s50`/`s33`/`s25` continuam válidos como equivalentes de 100/50/33/25%.)
  - **Limites de largura/altura**: `[w|h]-[max|min]-[valor]`. Sem unidade = px; com `rem` = rem. Exemplos: `w-max-300` (largura máxima de 300px), `h-min-50` (altura mínima de 50px), `w-min-10rem` (largura mínima de 10rem).

  Ex.: `<MaxInputText v-model="form.nome" label="Nome" s-70 w-max-400 />` · `<MaxInputCep v-model="form.cep" label="CEP" s-30 w-min-8rem />` dentro de um `<MaxGrid>`.
- **Tabelas**: `MaxTable` (leitura, cabeçalho fixo) e `MaxTableFields` (+ `MaxTableColumn`, editável).
- **Modais/popovers**: `MaxModal` (métodos `toggle()`/`show()`/`hide()` ou store `useModalStore`), `MaxPopover`, `MaxPopoverConfirm`, `MaxPopoverMenu`, `MaxIconConfirm`.
- **Feedback**: `MaxLoader`, `MaxBadgeComponent`, `MaxToast` (montar uma vez na raiz). Disparo: `Toast.show({ severity: 'success' | 'error' | 'warn', title, message })` (importado de `@maxvue/max-components-ui`).
- **Títulos/cards**: `MaxTitle1` (título principal — props `h1="Título"` e `h2="Subtítulo"`), `MaxTitle2` (título de seção), `MaxAuthCard`. **Nunca use headings nativos** (`<h1>`, `<h2>`, `<h3>`, `<h4>`) como título — use `MaxTitle1`/`MaxTitle2`.
- **Ícones**: `MaxIcon` ou prop `icon` por string Iconify — MDI no EngeApp (`icon="mdi:plus"`). Não importe SVGs avulsos quando há ícone no set.

> Se o componente que você imagina não está nesta lista, confira o catálogo do projeto (`resources/components-catalog.md` / `components-catalog`) **antes** de varrer o código-fonte da MaxComponentsUi — a lista acima já cobre os casos comuns e evita exploração desnecessária (e lenta).

## 3. Utilitários e composables: MaxUse

`@maxvue/max-use` evita reinventar lógica comum (datas, validação BR, cache, rotas). Vários composables são auto-importados via `maxUseAutoImport`; confira a config do projeto.

- **Import modular** (melhor tree-shaking) quando importar manualmente:
  ```ts
  import { isCpf, isCnpj, cepIsValid } from '@maxvue/max-use/validations';
  import { formatCurrency, formatCpf, formatPhone, maskSensitive } from '@maxvue/max-use/format';
  import { useTimeAgo, useRefCached, useDefaultReset } from '@maxvue/max-use/composables';
  import { apiGetRoute, apiPostRoute, goToRoute } from '@maxvue/max-use/routes';
  ```
  Para múltiplos utilitários, também é possível acessar a interface fundida via `import { _ } from '@maxvue/max-use'` — mas prefira os imports modulares acima para melhor tree-shaking.
- **Reatividade**: os utilitários aceitam `Ref` ou getter `() => T` e usam `toValue()` internamente — passe a fonte reativa diretamente, não desembrulhe com `unref()` antes.
- **Validação/formatação BR**: nunca escreva regex próprio para CPF/CNPJ/CEP/telefone. Use `isCpf()`, `isCnpj()`, `isCpfCnpj()`, `cepIsValid()`, `phone()`, `formatCurrency()`, `formatCpf()`, `formatCnpj()`, `formatPhone()`, `maskSensitive()`.
- **Composables úteis**: `useRefCached(key, initial)` (sincroniza Ref com `localStorage`), `useDefaultReset(initial)` (Ref zerável com ULID e data automáticos), `useTimeAgo()` (tempo relativo pt-BR, formatos `br`/`abbrev`/`action`/`limit`), `useCachedApi`/`useRefCachedApi` (estado de API cacheado — para dados de página prefira a store `@maxvue/max-pinia`), `watchTrue`.

## 4. Estado: MaxPinia (`defineStore` em sintaxe setup)

Stores usam **sintaxe de setup** (função), nunca a sintaxe de objeto. Nome do export em camelCase com sufixo `Store` (`useProjectStore`, `useUserStore`, `useUsinasStore`).

Padrão CRUD típico: a store é cacheada via `@maxvue/max-pinia` (o GET de carga vem da camada de cache, não de um `axios.get` manual). Exponha `isCached` + `options.get.route` para o GET; use os helpers `apiPostRoute`/`apiPutRoute`/`apiDeleteRoute` do `@maxvue/max-use` para as mutações (lembre que o MaxPinia também faz auto-save dos dados editados):

```ts
export const useEntidadesStore = defineStore('entidades', () => {
    // O MaxPinia sempre grava o payload do GET cacheado em `data` — use exatamente esse
    // nome de ref (nunca um nome arbitrário como `itens`, senão o GET automático popula
    // `store.data` e o seu ref fica vazio).
    const data = ref<Entidade[]>([]);
    const isCached = ref(true);
    // GET roteado pela camada de cache do @maxvue/max-pinia — sem axios.get manual.
    // NÃO passe `key`: o plugin ignora `options.key`. A chave de cache é derivada de
    // `store.$id` (+ `store.id`/`store.options.id` opcionais) via getKey(). Ver skill
    // vue-pinia-state-management-best-practices.
    const options = computed(() => ({ get: { route: '/api/entidades' } }));

    // GET automático ao montar; para revalidar use o reload() injetado pelo MaxPinia
    // (params dinâmicos vão via options.get.data reativo). Não invente um load() próprio.

    async function create(payload: Partial<Entidade>): Promise<Entidade> {
        // apiPostRoute executa a requisição e retorna o payload DIRETAMENTE (não { data }).
        const novo = await apiPostRoute('/api/entidades', payload);
        data.value.push(novo);
        return novo;
    }

    return { data, isCached, options, create };
});
```

### Integração com `@maxvue/max-pinia`

Toda store de dados de página usa o plugin `@maxvue/max-pinia` (anteriormente `piniaWithCache`, hoje `@maxvue/max-pinia`) para cache + auto-save. Exponha `isCached` e a computed `options` (apenas a rota string `/api/...`; **não** passe `key` — o plugin ignora `options.key` e deriva a chave de `store.$id` + `store.id`/`store.options.id` via `getKey()`). O contrato do MaxPinia injeta `status.server.get` na store; o flag `is_requested` (GET finalizado, sucesso ou erro) é usado para aguardar a carga. Em stores de autenticação, exponha `waitRequest` para que guards de rota aguardem os dados do usuário antes de redirecionar:

```ts
export const useUserStore = defineStore('user', () => {
    const data = ref<User | null>(null);
    const isCached = ref(true);
    // Rota string /api/... resolvida pela camada de cache (sem Ziggy/route()).
    // Sem `key`: o plugin ignora options.key e deriva a chave de store.$id.
    const options = computed(() => ({ get: { route: '/api/user/data' } }));

    // Aguarda a carga via contrato MaxPinia: status.server.get.is_requested.
    function waitRequest(this: any): Promise<void> {
        return new Promise((resolve) => {
            if (this?.status?.server?.get?.is_requested) return resolve();
            const unwatch = watch(
                () => this?.status?.server?.get?.is_requested,
                (isRequested) => {
                    if (isRequested) {
                        unwatch();
                        resolve();
                    }
                }
            );
        });
    }

    return { data, options, isCached, waitRequest };
});
```

## 5. Vue Router

- Rotas montadas a partir do diretório de páginas via `import.meta.glob(...)` das `Pages/`.
- Integre o roteador ao MaxUse com `setLibraryRouter(router as any)`.
- Use `beforeEach`/`afterEach` para o loading global (`useLoadingStore().start()` / `.end()`) e para aguardar o usuário autenticado: `await user.waitRequest()` antes de decidir o redirecionamento.
- Use `meta.layout` (ou equivalente) para diferenciar áreas `guest` e `auth`. A raiz (`App.vue`) decide o layout/shell.
- Rotas devem ser lazy quando fizer sentido para o bundle.

## 6. Integração com o backend (Laravel 13)

- **Todo GET ao backend passa por uma store `@maxvue/max-pinia`** (cache + auto-save). Não busque dados com `axios.get` direto em componentes/serviços — defina uma store cacheada (`isCached` + `options.get.route`).
- Rotas de API são caminhos string com prefixo `/api`: `'/api/projects/${id}'`. Os helpers `apiGetRoute`/`apiPostRoute`/`apiPutRoute`/`apiDeleteRoute`/`apiUploadRoute` do `@maxvue/max-use` resolvem para esses caminhos `/api/...`; `goToRoute` para navegação SPA. O Ziggy (`ziggy-js`) existe no projeto Laravel, mas as chamadas de API dos stores usam esses caminhos string diretamente — não o helper `route()`.
- O axios é configurado para sessão por cookie + XSRF (em `app.ts`):
  ```ts
  axios.defaults.withCredentials = true;
  axios.defaults.withXSRFToken = true;
  ```
- Há interceptor global: `401` → redireciona para `/login`.
- Não use Inertia — é um SPA Vue puro servido pelo Laravel (rota catch-all).

## 7. Estilização: UnoCSS + SCSS

- **Layout e espaçamento são responsabilidade do UnoCSS**, não do SCSS. Use utilitários: `flex`, `items-center`, `justify-center`, `gap`, `w-full`, `h-max-200`, `flex-grow`, e os atalhos de tamanho `s100`/`s50`/`s33`/`s25`. Presets em uso: `presetMaxUno()`, `presetWind3()`, `presetAttributify()`, `presetIcons()`.
- **Não reescreva em SCSS** o que o UnoCSS já resolve (width, height, padding, margin, flex). Reserve o `<style scoped>` para estrutura específica do componente e composições que os utilitários não cobrem.
- **Cores via CSS vars** do tema, não hex cru: `var(--background-0)`, `var(--background-100)`, `var(--background-200)`.
- **Attributify** é válido: `<div s100 flex items-center>` funciona como classe.
- Estilos globais/tema ficam em `resources/.../Theme/All.scss` (fonte, vars). Não duplique tema dentro de componentes.

## 8. Estrutura de pastas (EngeApp — `resources/`)

```
Pages/  Layouts/  stores/  Theme/  App.vue  app.ts  router.ts
```
Stores ficam em `stores/` (auto-importadas). Não há pasta `components/` local — usa-se MaxComponentsUi.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use Options API.
- **NÃO** quebre atributos de componentes em múltiplas linhas no `<template>`.
- **NÃO** reimporte o que é auto-importado (`ref`, `computed`, `watch`, `axios`, `defineStore`, stores, componentes `Max*`).
- **NÃO** escreva regex próprio para CPF/CNPJ/CEP/telefone — use MaxUse.
- **NÃO** reimplemente layout/espaçamento em SCSS quando o UnoCSS resolve.
- **NÃO** use `route()`/Ziggy — não existem neste projeto. Use os helpers do `@maxvue/max-use` (que resolvem para `/api/...`) e, para GETs, stores `@maxvue/max-pinia`.
- **NÃO** omita `withCredentials`/`withXSRFToken` na configuração do axios do EngeApp.
- **NÃO** escreva comentários fora do pt-BR.
