---
name: vue-typescript-best-practices
description: "Use when writing, reviewing, or debugging Vue 3 components, composables, Pinia stores, or utility functions in TypeScript: SFC structure, defineProps/defineEmits typing, tsconfig.json, and module declarations. Covers objectives, SFC structure, and TypeScript declarations."
---
## Objetivo
Garantir a segurança de tipos, estrutura limpa de código e total conformidade com o compilador do TypeScript no desenvolvimento com Vue 3 no ecossistema Engeapp, utilizando componentes tipados, composables, stores do Pinia e DTOs integrados ao backend.

## Instruções

Siga as convenções abaixo ao escrever Vue 3 + TypeScript no ecossistema Engeapp. Cada item traz o padrão e o porquê; aplique-os na ordem em que aparecem.

### 1. Estrutura do Componente Single File (SFC)
Sempre estruture os componentes SFC do Vue na seguinte ordem de blocos:
1. `<template>`: Estrutura HTML.
2. `<script setup lang="ts">`: Lógica da Composition API em TypeScript.
3. `<style scoped lang="scss">` ou `<style lang="scss">`: Estilização escrita em SCSS.

As demais convenções de front-end do ecossistema Engeapp já são cobertas por `vue-max-stack-frontend-best-practices` e `vue-pinia-state-management-best-practices` — esta skill foca exclusivamente em tipagem TypeScript e não repete essas regras.

### 2. Tipagem de defineProps e defineEmits
- **defineProps:** Use declarações baseadas em tipo (`defineProps<{ ... }>()`) em vez de arrays ou objetos em tempo de execução. Utilize `withDefaults` para definir valores padrão para as propriedades.
  ```typescript
  interface Props {
      clientId: string;
      isActive?: boolean;
      role?: 'admin' | 'user';
  }

  const props = withDefaults(defineProps<Props>(), {
      isActive: true,
      role: 'user',
  });
  ```
- **defineEmits:** Use emissões tipadas para garantir a validação estrita dos eventos.
  ```typescript
  const emit = defineEmits<{
      (e: 'update', id: string): void;
      (e: 'close'): void;
  }>();
  ```

### 3. Estado Reativo e Referências de Template
> `ref`, `computed`, `watch`, `defineStore` e os tipos `Ref`/`ComputedRef`/`PropType` são globais via `unplugin-auto-import` neste projeto (ver `auto-import.d.ts`) — não importe de `'vue'`/`'pinia'` nos exemplos abaixo, seguindo o padrão real do projeto (ex.: `useClient.Store.ts`).
- **Refs e Propriedades Computadas:** Defina explicitamente o tipo de refs quando o valor inicial for null ou complexo.
  ```typescript
  const clientData: Ref<Client | null> = ref<Client | null>(null);
  const isLoaded = ref<boolean>(false);

  const formattedName: ComputedRef<string> = computed<string>(() => {
      return clientData.value ? `${clientData.value.name}` : '';
  });
  ```
- **Template Refs:** Especifique o elemento DOM ou o tipo do componente alvo.
  ```typescript
  const modalContainer = ref<HTMLDivElement | null>(null);
  ```

### 4. Consumo de Tipos Gerados pelo Backend
- O backend Laravel 13 usa DTOs com **`spatie/laravel-data`** (classes `App\Data\*Data`) e gera as definições TypeScript correspondentes via **`spatie/laravel-typescript-transformer`** (ex.: `Brand`, `Client`, `User`, `Project`) em um arquivo `.d.ts` gerado. Prefira os tipos vindos dos DTOs (`Data`) por serem o contrato explícito do payload da API — mais estável que inferir a partir do model Eloquent.
- Acesse estes tipos globalmente em toda a aplicação frontend. **Não escreva imports manuais** para esses tipos gerados.
- Evite o uso do tipo `any`. Consulte o arquivo de tipos gerado (`.d.ts`) para identificar os tipos corretos das tabelas e relacionamentos. Para auxiliar a tipagem no lado PHP/Eloquent, o projeto TEM `barryvdh/laravel-ide-helper` instalado — os artefatos `_ide_helper.php`/`_ide_helper_models.php` são gerados por `php artisan ide-helper:generate` e `ide-helper:models`, refletindo colunas e relacionamentos dos models.
- Os relacionamentos já vêm como propriedades opcionais nos próprios tipos gerados (ex.: `Client.projects?: Project[]`) — não é necessário criar interseções manuais para tipá-los.

### 5. Stores do Pinia (Setup Stores)
- **Dados de página vindos do backend (GET) e salvamento (save) DEVEM passar por uma store `@maxvue/max-pinia`**, que é a camada padrão de cache + auto-save (debounced) do projeto. Não faça `axios.get`/`axios.post` manuais nem salvamento por submit manual para dados de página; o próprio MaxPinia faz o GET e o save usando a instância axios que ele injeta internamente, contra um **nome de rota (Ziggy)** configurado nas `options` da store — que ele resolve, via Ziggy, para a URI real registrada em `routes/web/*` (ex.: `'client.data'` → `client/data`), sem prefixo `api/`. Reserve `apiGetRoute`/`apiPostRoute` para chamadas pontuais fora do fluxo da store cacheada. Tipifique explicitamente o estado da store.
  ```typescript
  export const useClienteStore = defineStore('cliente', () => {
      // Contrato da store cacheada: `data` guarda o estado do servidor, `isCached` ativa
      // a camada MaxPinia e `options` fornece as rotas string. Com isso o plugin faz o GET
      // (cache-first) e o auto-save (debounce 300ms sobre `data`) automaticamente.
      const data = ref<Client | null>(null);
      const isCached = ref(true);

      const options = computed(() => ({
          get:  { route: 'client.data' }, // nome de rota (Ziggy); resolve para a URI 'client/data'
          save: 'client.save',            // opcional: POST com auto-save debounced
          id:   'cliente',                 // alimenta a chave de cache do localforage
      }));

      const possuiProjetos = computed<boolean>(() => (data.value?.projects?.length ?? 0) > 0);

      return { data, isCached, options, possuiProjetos };
  });
  ```
- Para estado puramente local de UI (sem origem no backend), uma Setup Store Pinia comum (`defineStore` de `pinia`) é aceitável. Tipifique explicitamente refs de estado, getters e retornos de actions.
  ```typescript
  export const useActiveUserStore = defineStore('activeUser', () => {
      const currentUser = ref<User | null>(null);
      const isAuthenticated = computed<boolean>(() => currentUser.value !== null);

      function setCurrentUser(user: User | null): void {
          currentUser.value = user;
      }

      return { currentUser, isAuthenticated, setCurrentUser };
  });
  ```

### 6. Resolução de Rotas com TypeScript
- O projeto tem `ziggy-js` configurado e em uso (é o stack Laravel). O fluxo padrão do Max passa o **nome da rota (Ziggy)** — ex.: `'client.data'` — para os helpers `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`, que resolvem o nome internamente (via `route()`) para a URI real registrada no backend (sem prefixo `api/`). Prefira `apiGetRoute`/`apiPostRoute` a chamar `route()` diretamente — o projeto usa `route()` direto em alguns pontos de código de app, mas o padrão recomendado por esta skill é passar pelos helpers do Max.
- Respeite as assinaturas de parâmetros esperadas pelo backend. Evite passar objetos não tipados para endpoints que esperam parâmetros específicos.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), e escreva comentários no código estritamente em pt-BR, independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **SCSS é obrigatório:** Não utilize CSS padrão, Less ou utilitários (como Tailwind) a menos que utilize as classes utilitárias do UnoCSS.
