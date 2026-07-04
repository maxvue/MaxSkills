---
name: vue-auto-import-components-best-practices
description: "Use when configuring, modifying, or debugging Vue 3 auto-import setups (unplugin-auto-import, unplugin-vue-components), fixing missing global type declarations (auto-import.d.ts, components.d.ts), or improving IDE support for auto-imported APIs and library components (MaxComponentsUi, MaxUse). Triggers on vite.config.ts auto-import config and lint errors about undeclared globals."
---

# Boas Práticas de Importação Automática e Resolvers de Componentes no Vue 3

## Objetivo
Estabelecer configurações limpas e otimizadas para `unplugin-auto-import` e `unplugin-vue-components` em aplicações Vue 3, garantindo geração fluida de tipos TypeScript, integração com ESLint e suporte robusto para as bibliotecas do monorepo `MaxUse` e `MaxComponentsUi`.

## Instruções

### 1. Configuração do Vite (`vite.config.ts`)
Configure os plugins de importação automática no seu arquivo do Vite usando os resolvers e diretórios de varredura corretos:

*   **unplugin-auto-import**: Configurado para importar APIs padrão do Vue, `defineStore` do Pinia, Axios e as funções customizadas de `@maxvue/max-use`.
*   **unplugin-vue-components**: Configurado para escanear recursivamente as pastas de componentes e usar o resolver customizado `MaxComponentsUiResolver` para a biblioteca de UI.

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { maxUseAutoImport } from '@maxvue/max-use';
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver';

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        // maxUseAutoImport é um ARRAY de import-sources: faça spread dele nos imports
        ...(Array.isArray(maxUseAutoImport) ? maxUseAutoImport : [maxUseAutoImport]),
        { pinia: ['defineStore'] }
      ],
      ignore: ['toRef', 'toRefs'],
      dts: './auto-import.d.ts',
      vueTemplate: true,
      viteOptimizeDeps: true,
      dirs: [
        './src/Functions/**',
        './src/Helpers/**',
        './src/Types/**',
        './src/Stores/**'
      ],
      // Gera arquivo de variáveis globais para o ESLint evitar erros de validação
      eslintrc: {
        enabled: true,
        filepath: './.eslintrc-auto-import.json',
        globalsPropValue: true
      }
    }),
    Components({
      dirs: ['./src/Vue', './src/components'],
      extensions: ['vue', 'js', 'ts'],
      deep: true,
      dts: './auto-import-components.d.ts',
      syncMode: 'overwrite',
      directives: true,
      resolvers: [
        MaxComponentsUiResolver() as any
      ]
    })
  ]
});
```

### 2. Integração com TypeScript (`tsconfig.frontend.json`)
Certifique-se de que os arquivos autogerados de declaração de tipos (`auto-import.d.ts` e `auto-import-components.d.ts`) estejam registrados na configuração do TypeScript para que a IDE consiga resolver as variáveis e componentes globais:

```json
{
  "compilerOptions": {
    // ... outras configurações do compilador
  },
  "include": [
    "./src/**/*.vue",
    "./src/**/*.ts",
    "./auto-import.d.ts",
    "./auto-import-components.d.ts"
  ]
}
```

### 3. Integração com ESLint (Flat Config: `eslint.config.js`)
Para evitar erros de variáveis indefinidas (ex: "ref is not defined") nos arquivos examinados pelo ESLint, importe as configurações globais autogeradas de `.eslintrc-auto-import.json`:

```javascript
import fs from 'fs';
import path from 'path';

// Carrega as variáveis globais do auto-import se o arquivo existir
const autoImportGlobals = fs.existsSync('./.eslintrc-auto-import.json')
  ? JSON.parse(fs.readFileSync('./.eslintrc-auto-import.json', 'utf-8'))
  : { globals: {} };

export default [
  {
    languageOptions: {
      globals: {
        ...autoImportGlobals.globals
      }
    }
    // ... restante das configurações do ESLint
  }
];
```

### 4. Resolução de Problemas Comuns (Troubleshooting)
Se a IDE apresentar erros como "Cannot find name 'ref'" ou se os componentes customizados não renderizarem:
1.  **Regenerar as Declarações**: Execute `npm run dev` ou force um rebuild do Vite para atualizar os arquivos `auto-import.d.ts` e `auto-import-components.d.ts`.
2.  **Verificar os Caminhos no Include**: Confirme se `tsconfig.frontend.json` inclui os arquivos `.d.ts` na seção `include`.
3.  **Verificar o Registro do Resolver**: Certifique-se de que o resolver `MaxComponentsUiResolver` está listado no array `resolvers` do plugin `Components`.

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
