---
name: vue-auto-import-components-best-practices
description: "Use ao configurar, modificar ou depurar o auto-import do front do engeapp (Vue 3) via unplugin-auto-import e unplugin-vue-components no vite.config.ts, corrigir declarações de tipo geradas (auto-import.d.ts, auto-import-components.d.ts) registradas no tsconfig.json, ou depurar erros 'Cannot find name ref' e componentes Max* não resolvidos pelo MaxComponentsUiResolver."
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

### 2. Integração com TypeScript (`tsconfig.json`)
Os arquivos autogerados de declaração de tipos (`auto-import.d.ts` e `auto-import-components.d.ts`) precisam estar registrados no `include` do `tsconfig.json` (é o `tsconfig` do front no engeapp — não existe `tsconfig.frontend.json`) para que a IDE resolva as variáveis e componentes globais. No projeto real ambos já constam do `include`:

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
2.  **Verificar os Caminhos no Include**: Confirme se o `tsconfig.json` inclui `./auto-import.d.ts` e `./auto-import-components.d.ts` na seção `include`.
3.  **Verificar os `dirs` de varredura**: Confirme que os `dirs` do auto-import apontam para `./resources/...` (e não `./src/...`); caso contrário Helpers, Stores e Types não serão importados.
4.  **Verificar o Registro do Resolver**: Certifique-se de que o resolver `MaxComponentsUiResolver` está listado no array `resolvers` do plugin `Components`.

## Examples

### Utilização Prática de APIs e Componentes Auto-importados
Em componentes Single-File do Vue (SFCs), escreva tags `<script setup>` limpas sem a necessidade de importar APIs reativas ou helpers conhecidos:

```vue
<template>
  <div class="user-dashboard">
    <!-- MaxTitle1 e MaxButton são importados automaticamente pelo MaxComponentsUiResolver -->
    <MaxTitle1>Painel de Controle</MaxTitle1>
    
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
  return formatDate(rawDate.value, 'dd/MM/yyyy');
});

function increment(): void {
  count.value++;
}
</script>

<style scoped lang="scss">
.user-dashboard {
  padding: 1.5rem;
  
  .card {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid var(--border-base);
  }
}
</style>
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
*   **Não Escreva Imports Manuais**: Jamais importe manualmente funções do núcleo do Vue (`ref`, `computed`, `watch`, `onMounted`, etc.) ou funções auxiliares do `@maxvue/max-use` que já estejam mapeadas no auto-import.
*   **Não Desative a Geração de DTS**: Nunca defina `dts: false` na configuração dos plugins. Isso quebra o autocompletar da IDE e a validação estática.
*   **Mantenha Arquivos Gerados fora do Git (Opcional)**: Se preferir, garanta que os arquivos `auto-import.d.ts` e `auto-import-components.d.ts` estejam no `.gitignore` caso o pipeline de build os gere em tempo de execução (mas garanta que estejam disponíveis no desenvolvimento local para DX).
*   **Atributos de Componente Inline**: Ao usar componentes auto-importados do Vue no `<template>`, mantenha todos os atributos em uma única linha, de acordo com as regras de formatação do projeto (ex: `<MaxButton param1="..." param2="..." />`).
