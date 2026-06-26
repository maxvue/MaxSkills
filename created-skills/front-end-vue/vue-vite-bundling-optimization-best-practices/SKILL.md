---
name: vue-vite-bundling-optimization-best-practices
description: Use when configuring, analyzing, or optimizing the Vite 8 bundler, Rollup build options, code splitting, dynamic imports, or plugins (unplugin-auto-import, unplugin-vue-components, visualizer) in a Vue 3 and AdonisJS application. Triggers on build performance issues, huge bundle size warnings, Vite 8 config changes, and lazy loading strategies.
---

# Melhores Práticas de Otimização de Bundling com Vue & Vite

## Objetivo
Fornecer diretrizes sólidas e padrões arquiteturais para a otimização do processo de build, redução do tamanho do bundle final e melhoria da performance de carregamento no frontend utilizando o Vite no ecossistema Engeapp.

## Instruções

### 1. Roteamento Dinâmico & Code Splitting (Divisão de Código)
- Sempre carregue as views de rota dinamicamente usando `() => import(...)`. Não importe componentes de rota estaticamente no topo do arquivo de configuração do roteador.
- Exemplo:
  ```typescript
  // Recomendado: Permite a divisão de código (code splitting) para esta página
  const Dashboard = () => import('@/Vue/Pages/Dashboard.vue');
  
  // Evitar: Aumenta o tamanho do bundle inicial desnecessariamente
  import Dashboard from '@/Vue/Pages/Dashboard.vue';
  ```

### 2. Carregamento Tardio (Lazy Loading) de Componentes Pesados
- Para bibliotecas ou componentes pesados que não são necessários durante o carregamento inicial da página (ex: Gráficos, Leitores de PDF, LiveKit, Uppy), carregue-os de forma assíncrona utilizando `defineAsyncComponent` do Vue.
- Exemplo:
  ```typescript
  import { defineAsyncComponent } from 'vue';

  const HeavyChart = defineAsyncComponent(() =>
    import('@/Vue/Components/HeavyChart.vue')
  );
  ```

### 3. Configuração de Manual Chunking (Opções do Rollup)
- Agrupe dependências de terceiros (vendor) em chunks separados e cacheados no `vite.config.ts` utilizando `rollupOptions.output.manualChunks`. Isso evita a criação de um único arquivo `vendor.js` massivo.
- Defina chunks separados para módulos pesados específicos:
  ```typescript
  // vite.config.ts
  export default defineConfig({
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              if (id.includes('pdfjs-dist')) return 'vendor-pdfjs';
              if (id.includes('chart.js')) return 'vendor-charts';
              if (id.includes('livekit')) return 'vendor-livekit';
              if (id.includes('uppy')) return 'vendor-uppy';
              return 'vendor-core'; // Fallback para outros pacotes
            }
          }
        }
      }
    }
  });
  ```

### 4. Otimização de Auto-Imports & Componentes
- Certifique-se de que os plugins `unplugin-auto-import` e `unplugin-vue-components` estão configurados para varrer apenas os diretórios necessários (ex: `./resources/Functions/**`, `./resources/Helpers/**`).
- Utilize a opção `dts` para gerar arquivos de declaração TypeScript (`auto-import.d.ts` e `auto-import-components.d.ts`) para manter a verificação de tipos rápida e precisa.
- Sempre inclua os resolvers nativos ou de bibliotecas (como o `MaxComponentsUiResolver` para os componentes de UI do Engeapp) para permitir que o bundler faça o tree-shaking correto de componentes não utilizados.

### 5. Otimização de Dependências em Desenvolvimento (`optimizeDeps`)
- Exclua bibliotecas locais do workspace que sejam muito grandes (como `@maxvue/max-components-ui` e `@maxvue/max-use`) do pré-bundling utilizando `optimizeDeps.exclude` ao trabalhar com links simbólicos ou recarregamento rápido (HMR), garantindo que sejam resolvidas corretamente através dos aliases em `resolve.alias`.

### 6. Análise do Tamanho do Bundle
- Utilize o plugin `rollup-plugin-visualizer` para gerar um mapa visual do bundle de produção. Execute um build de produção para verificar o relatório HTML gerado.
- Instalação e configuração:
  ```typescript
  // vite.config.ts
  import { visualizer } from 'rollup-plugin-visualizer';

  export default defineConfig({
    plugins: [
      // Inclui o visualizador apenas no modo de build de produção
      visualizer({
        filename: 'public/build/stats.html',
        open: false,
        gzipSize: true,
        brotliSize: true
      })
    ]
  });
  ```

## Restrições
- **Não aumente o valor de `chunkSizeWarningLimit`** apenas para mascarar problemas de empacotamento. O limite deve refletir metas reais de performance (o padrão do Vite é 500KB; evite alterá-lo para valores extremos como `4000` sem antes tentar otimizar com chunks manuais).
- **Não importe estilos CSS globalmente** se eles forem utilizados por apenas um componente. Utilize `<style scoped lang="scss">` para que o compilador possa otimizar os estilos e remover CSS não utilizado.
- **Não desative a divisão de código (code splitting)** ou force todo o empacotamento em um único arquivo, a menos que seja explicitamente necessário para assets independentes.
- **Não importe dependências pesadas de forma estática** dentro de arquivos de layout geral (como `AppLayout.vue`). Mantenha os layouts o mais leves possível para que a renderização inicial da página seja rápida.
- **Não utilize a Options API** ou componentes tradicionais fora do padrão `<script setup>` ao implementar componentes sob demanda; siga estritamente o padrão da Composition API.
