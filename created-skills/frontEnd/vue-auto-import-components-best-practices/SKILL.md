---
name: vue-auto-import-components-best-practices
description: "Use when configuring or debugging Vue 3 auto-imports via unplugin-auto-import and unplugin-vue-components in vite.config.ts, tsconfig.json integration, auto-import.d.ts, and MaxComponentsUiResolver."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Importação Automática e Resolvers de Componentes no Vue 3

## Objetivo
Manter a configuração de `unplugin-auto-import` e `unplugin-vue-components` no front do engeapp (Vue 3 sobre Laravel), garantindo geração correta dos tipos TypeScript (`auto-import.d.ts` e `auto-import-components.d.ts`) e suporte às bibliotecas `@maxvue/max-use` e `@maxvue/max-components-ui`. No engeapp o código-fonte do front vive em `./resources/` (não em `src/`), e as globais são resolvidas por declarações `.d.ts` registradas no `tsconfig.json` — o projeto NÃO usa o bloco `eslintrc` do auto-import.

## Instruções

### 1. Configuração do Vite (`vite.config.ts`)
Configure os plugins de importação automática no seu arquivo do Vite usando os resolvers e diretórios de varredura corretos:

*   **unplugin-auto-import**: importa as APIs padrão do Vue, `defineStore` do Pinia, `useAsyncStatus` de `@maxvue/max-pinia`, o `default` do `axios` como `axios` e o array de import-sources de `@maxvue/max-use` (via spread de `maxUseAutoImport`). Varre `./resources/Functions/**`, `./resources/Helpers/**`, `./resources/Types/**` e `./resources/Stores/**`.
*   **unplugin-vue-components**: escaneia recursivamente `./resources/Vue` e `./resources/components` e usa o resolver customizado `MaxComponentsUiResolver` para os componentes `Max*` da biblioteca de UI.

Bloco real usado no engeapp (fiel ao `vite.config.ts` do projeto):

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { maxUseAutoImport } from '@maxvue/max-use';
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver';

export default defineConfig(() => ({
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        // maxUseAutoImport é um ARRAY de import-sources: faça spread dele nos imports
        ...(Array.isArray(maxUseAutoImport) ? maxUseAutoImport : [maxUseAutoImport]),
        { pinia: ['defineStore'] },
        { 'ziggy-js': ['route'] },
        { '@maxvue/max-pinia': ['useAsyncStatus'] },
        { axios: [['default', 'axios']] }
      ],
      ignore: ['toRef', 'toRefs'],
      dts: './auto-import.d.ts',
      vueTemplate: true,
      viteOptimizeDeps: true,
      defaultExportByFilename: false,
      injectAtEnd: true,
      dirsScanOptions: {
        types: true
      },
      dirs: ['./resources/Functions/**', './resources/Helpers/**', './resources/Types/**', './resources/Stores/**']
    }),
    Components({
      dirs: ['./resources/Vue', './resources/components'],
      extensions: ['vue', 'js', 'ts', 'store.ts'],
      directoryAsNamespace: false,
      deep: true,
      dts: './auto-import-components.d.ts',
      syncMode: 'overwrite',
      directives: true,
      resolvers: [MaxComponentsUiResolver() as any]
    })
  ]
}));
```

> As globais NÃO são geradas via bloco `eslintrc` do auto-import. O engeapp não possui `.eslintrc-auto-import.json`; a resolução das globais acontece pelos `.d.ts` registrados no `tsconfig.json` (ver Seção 2). Não adicione o bloco `eslintrc` ao copiar esta config.

> **Alias obrigatório `ziggy-js`**: como o auto-import de `route` (via `{ 'ziggy-js': ['route'] }`) injeta o import em qualquer arquivo processado — inclusive em libs linkadas fora da raiz do projeto —, o `vite.config.ts` também precisa do alias `'ziggy-js': path.resolve(__dirname, './node_modules/ziggy-js')` na seção `resolve.alias`, para que essas libs consigam resolver o módulo.

### 2. Integração com TypeScript (`tsconfig.json`)
Os arquivos autogerados de declaração de tipos (`auto-import.d.ts` e `auto-import-components.d.ts`) precisam estar registrados no `include` do `tsconfig.json` (é o `tsconfig` do front no engeapp — não existe `tsconfig.frontend.json`) para que a IDE resolva as variáveis e componentes globais. No projeto real ambos já constam do `include` (recorte ilustrativo — o `include` real tem mais entradas, ex.: `./resources/Stores/**/*.ts`, `./resources/Functions/**/*.ts`):

```json
{
  "include": [
    "./resources/**/*.vue",
    "./resources/**/*.ts",
    "./resources/**/*.tsx",
    "./resources/Types/**/*.d.ts",
    "./auto-import.d.ts",
    "./auto-import-components.d.ts",
    "./*.config.ts"
  ]
}
```

### 3. Resolução de Problemas Comuns (Troubleshooting)
Se a IDE apresentar erros como "Cannot find name 'ref'" ou se os componentes customizados não renderizarem:
1.  **Regenerar as Declarações**: Execute o dev server do Vite (ou force um rebuild) para atualizar os arquivos `auto-import.d.ts` e `auto-import-components.d.ts`.
2.  **Se persistir**: revise a configuração das Seções 1 e 2 (dirs de varredura, include do tsconfig, resolver registrado).

## Examples

### Utilização Prática de APIs e Componentes Auto-importados
Em componentes Single-File do Vue (SFCs), escreva tags `<script setup>` limpas sem a necessidade de importar APIs reativas ou helpers conhecidos:

```vue
<template>
  <div class="user-dashboard">
    <!-- MaxTitle1 e MaxButton são importados automaticamente pelo MaxComponentsUiResolver -->
    <MaxTitle1 h1="Painel de Controle" />
    
    <div class="card">
      <p>Contagem Atual: {{ count }}</p>
      <p>Data Formatada: {{ formattedDate }}</p>
      
      <!-- MaxButton utiliza atributos em uma única linha para formatação padrão -->
      <MaxButton @click="increment" label="Incrementar" />
    </div>
  </div>
</template>

<script setup lang="ts">
// APIs do Vue (ref, computed) e helpers do MaxUse (formatDate) são importados automaticamente.
// Nenhuma declaração de import é necessária aqui!

const count = ref<number>(0);
const rawDate = ref<Date>(new Date());

const formattedDate = computed<string>(() => {
  return formatDate(rawDate.value, 'DD/MM/YYYY');
});

function increment(): void {
  count.value++;
}
</script>
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
*   **Não Escreva Imports Manuais**: Jamais importe manualmente funções do núcleo do Vue (`ref`, `computed`, `watch`, `onMounted`, etc.) ou funções auxiliares do `@maxvue/max-use` que já estejam mapeadas no auto-import.
*   **Não Desative a Geração de DTS**: Nunca defina `dts: false` na configuração dos plugins. Isso quebra o autocompletar da IDE e a validação estática.
*   **Arquivos Gerados fora do Git**: No engeapp, `auto-import.d.ts` e `auto-import-components.d.ts` JÁ estão no `.gitignore` (gerados em tempo de dev/build); não os versione.
*   **Atributos de Componente Inline**: Ao usar componentes auto-importados do Vue no `<template>`, mantenha todos os atributos em uma única linha, de acordo com as regras de formatação do projeto (ex: `<MaxButton param1="..." param2="..." />`).
