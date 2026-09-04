---
name: vue-max-stack-frontend-best-practices
description: "Use when developing Vue 3 Single File Components (<script setup lang='ts'>) in Engeapp. Covers template structure, UnoCSS styling, MaxComponentsUi elements, MaxUse composables, MaxPinia cached stores, forms, tables, and Ziggy named routes."
author: Johnattas Conrady Gomes Santana
---
# Front-end Vue do Ecossistema Max (EngeApp — Laravel 13)

## Objetivo

Padronizar o desenvolvimento front-end em **Vue 3 (Composition API) + Vue Router + UnoCSS/SCSS** integrado com o backend **Laravel 13** / PHP 8.4 e com as bibliotecas locais `@maxvue/max-components-ui`, `@maxvue/max-use` e `@maxvue/max-pinia`.

## Instruções

### 1. Estrutura Canônica do SFC

O projeto segue estritamente regras ESLint (`@stylistic` + `vue/*`):

- **Ordem dos Blocos:** `<template>` → `<script setup lang="ts">` → `<style lang="scss" scoped>`.
- **Atributos Sempre Inline:** Todos os atributos/props de qualquer tag devem permanecer em uma única linha no template.
- **Inputs e Botões Max:** Nunca use `<input>`, `<button>`, `<select>` crus — use sempre componentes `Max*` (`MaxInputText`, `MaxInputCpfCnpj`, `MaxInputCep`, `MaxInputSelect`, `MaxButton`, `MaxIconButton`).
- **Títulos e Estrutura:** Use `MaxTitle1` (props `h1` e `h2`) ou `MaxTitle2` em vez de `<h1>`–`<h4>`. Agrupe com `<div>`, nunca `<section>`.
- **Formulários:** Use sempre `<MaxGrid>` (não `MaxGridCols`), dimensionando campos via atributos UnoCSS (`s-100`, `s-50`, `s-30`, `w-max-400`).
- **Auto-Imports:** `ref`, `computed`, `watch`, `defineStore`, stores e componentes `Max*` são auto-importados. Importe manualmente apenas `useRoute`/`useRouter` e `storeToRefs`.

```vue
<template>
    <div class="entidade-page" s100 flex flex-col>
        <MaxLoader v-if="!status.server.get.is_success" label="Carregando..." />
        <MaxGrid v-else>
            <MaxInputText v-model="data.nome" label="Nome" s-70 w-max-400 />
            <MaxButton label="Salvar" icon="mdi:content-save" @click="salvar" />
        </MaxGrid>
    </div>
</template>

<script setup lang="ts">
    import { storeToRefs } from 'pinia';

    const store = useEntidadesStore();
    const { data, status } = storeToRefs(store);

    async function salvar(): Promise<void> {
        await store.save();
    }
</script>

<style lang="scss" scoped>
.entidade-page {
    height: 100%;
}
</style>
```

---

### 2. Utilitários e Formatação: `@maxvue/max-use`

- **Validação e Formatação BR:** Use utilitários do MaxUse (`isCpf`, `isCnpj`, `cepIsValid`, `formatCurrency`, `formatCpf`, `formatPhone`), nunca regex ad-hoc.
- **Composables Úteis:** `useRefCached` (cache local), `useDefaultReset` (reset de formulário), `useTimeAgo` (tempo relativo pt-BR).
- **Sem Libs Cruas:** Nunca importe `lodash` ou `@vueuse/core` diretamente no código de aplicação — use `@maxvue/max-use`.

---

### 3. Gerenciamento de Estado: `@maxvue/max-pinia`

- **Stores em Sintaxe Setup:** Localizadas em `resources/Stores/{Domínio}/use{Nome}.Store.ts`.
- **Todo GET passa por MaxPinia:** Declare `isCached = ref(true)` e a computed `options`:
  ```typescript
  export const useClientStore = defineStore('project.client', () => {
      const isCached = ref(true);
      const data = ref<Client | null>(null);
      const options = computed(() => ({
          get: { route: 'client.data', data: { id: clientId.value } },
          save: 'client.save',
          key: 'project.client'
      }));

      return { data, isCached, options };
  });
  ```
- **Mutações HTTP:** Use `apiPostRoute('rota.nome', payload)` ou `apiPutRoute`/`apiDeleteRoute` do `@maxvue/max-use`.

---

### 4. Integração de Rotas com Backend Laravel 13

- **Rotas são NOMES Ziggy Pontilhados:** Helpers recebem o nome da rota (ex: `apiGetRoute('project.data', { id })`) e resolvem internamente via Ziggy. Nunca monte paths `/api/...` à mão.
- **Sem Camada `services/` no Front:** Ações de API vivem dentro das stores ou no `script setup`.
- **Autenticação por Cookie:** O `@maxvue/max-use` gerencia `withCredentials: true` para sessão web.

---

### 5. Estilização: UnoCSS + SCSS

- **Layout e Espaçamento:** Resolva via utilitários UnoCSS (`flex`, `items-center`, `gap-4`, `w-full`, `s100`, `s50`, `s33`, `s25`).
- **Cores do Tema:** Use variáveis CSS (`var(--background-0)`, `var(--background-100)`, `var(--primary)`).
- **Toast:** Use sempre `Toast.show({ title, severity })` do `@maxvue/max-components-ui` (`MaxToast` montado no `App.vue`).

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR).
- **NÃO** use Options API em arquivos `.vue`.
- **NÃO** importe `@vueuse/core`, `lodash` ou `primevue` diretamente.
- **NÃO** quebre atributos de tags em múltiplas linhas no template.
- **NÃO** chame `axios.get` direto nem crie camada `services/` no front-end.
