# Build Tooling & Vite

---

## Vite Configuration for Vue

### Basic Configuration

O EngeApp mantém o código-fonte em `resources/` (não `src/`). Aliases reais:

```typescript
// vite.config.ts (trecho real — resolve.alias)
import path from 'path'

export default defineConfig(() => ({
  resolve: {
    dedupe: ['pinia', 'vue', 'vue-router'],
    alias: {
      '@': path.resolve(__dirname, './resources'),
      '@stores': path.resolve(__dirname, './resources/Stores'),
      '@components': path.resolve(__dirname, './resources/Vue/Components'),
      '@pages': path.resolve(__dirname, './resources/Vue/Pages'),
      '@sections': path.resolve(__dirname, './resources/Vue/Sections'),
      '@layouts': path.resolve(__dirname, './resources/Vue/Layouts'),
      '@functions': path.resolve(__dirname, './resources/Functions'),
      '@theme': path.resolve(__dirname, './resources/Theme')
    }
  }
}))
```

### Essential Plugins

```typescript
// vite.config.ts (trecho real — simplificado)
import laravel from 'laravel-vite-plugin'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { defineConfig } from 'vite'
import { maxUseAutoImport } from '@maxvue/max-use'
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver'

export default defineConfig(() => ({
  plugins: [
    // Integração Laravel + Vite (mesma origem; entradas em resources/).
    laravel({ input: ['@/Theme/All.scss', '@/app.ts'], refresh: true }),

    // UnoCSS (presetMaxUno + attributify) — ver uno.config.ts
    UnoCSS(),

    vue(),

    // Auto-import de Vue APIs + composables/helpers do MaxUse + defineStore do pinia.
    AutoImport({
      imports: ['vue', ...(Array.isArray(maxUseAutoImport) ? maxUseAutoImport : [maxUseAutoImport]),
        { pinia: ['defineStore'] }, { '@maxvue/max-pinia': ['useAsyncStatus'] }, { axios: [['default', 'axios']] }],
      dts: './auto-import.d.ts',
      vueTemplate: true,
      dirs: ['./resources/Functions/**', './resources/Helpers/**', './resources/Types/**', './resources/Stores/**']
    }),

    // Auto-import de componentes — os Max* são resolvidos por MaxComponentsUiResolver.
    Components({
      dirs: ['./resources/Vue', './resources/components'],
      extensions: ['vue', 'js', 'ts', 'store.ts'],
      deep: true,
      dts: './auto-import-components.d.ts',
      resolvers: [MaxComponentsUiResolver() as any]
    })
  ]
}))
```

> UnoCSS usa `presetMaxUno()` (de `@maxvue/max-components-ui/preset`), `presetWind3()`,
> `presetAttributify()` e `presetIcons()` no `uno.config.ts`. Ver a skill
> `vue-unocss-styling-best-practices` para os tokens de tema e o attributify.

### Environment Variables

O EngeApp é um SPA Vue **servido pelo Laravel na mesma origem** (via `laravel-vite-plugin`). Não há
backend Node nem proxy `/api` → `localhost:3000`: a API vive na própria origem e as chamadas usam **nomes
de rota (Ziggy)** resolvidos pelos helpers do `@maxvue/max-use` — não existe `VITE_API_URL`.

```typescript
// Variáveis realmente usadas (definidas no vite.config.ts / .env)
VITE_HOST=dev.engeapp.com.br   // host de dev com HTTPS local

// Injetadas via `define` no vite.config.ts a partir do package.json:
import.meta.env.VITE_APP_VERSION   // versão do app
import.meta.env.VITE_APP_SANDBOX   // true quando host === dev.engeapp.com.br
```

```typescript
// Uso em código
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
const version = import.meta.env.VITE_APP_VERSION
```

### Dev Server (Laravel + HTTPS local)

O dev server roda sob o host customizado com TLS local; sem proxy `/api` (mesma origem do Laravel).

```typescript
// vite.config.ts (trecho real — simplificado)
const customHost = process.env.VITE_HOST || 'dev.engeapp.com.br'

export default defineConfig(() => ({
  server: {
    host: customHost,
    allowedHosts: true,
    cors: { origin: `https://${customHost}` },
    hmr: { host: customHost },
    https: fs.existsSync('dev.engeapp.com.br.key') ? {
      key: fs.readFileSync('dev.engeapp.com.br.key'),
      cert: fs.readFileSync('dev.engeapp.com.br.crt')
    } : undefined
  }
}))
```

---

## Sourcemaps Configuration

### Development Sourcemaps

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // Full sourcemaps for development
    sourcemap: true
  }
})
```

### Production Sourcemaps

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // Options: true | 'inline' | 'hidden' | false
    sourcemap: process.env.NODE_ENV === 'production' ? 'hidden' : true
  }
})
```

| Mode | Value | Use Case |
|------|-------|----------|
| Full | `true` | Development, staging |
| Hidden | `'hidden'` | Production with error tracking |
| Inline | `'inline'` | Single-file debugging |
| None | `false` | Production without debugging |

### VS Code Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Debug Vue App",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "sourceMapPathOverrides": {
        "webpack:///./src/*": "${webRoot}/*"
      }
    }
  ]
}
```

### Sentry Error Tracking

```typescript
// vite.config.ts
import { sentryVitePlugin } from '@sentry/vite-plugin'

export default defineConfig({
  build: {
    sourcemap: true
  },
  plugins: [
    sentryVitePlugin({
      org: 'your-org',
      project: 'your-project',
      authToken: process.env.SENTRY_AUTH_TOKEN,
      sourcemaps: {
        assets: './dist/**',
        filesToDeleteAfterUpload: './dist/**/*.map'
      }
    })
  ]
})
```

---

## Build Optimization

### Tree Shaking Best Practices

No EngeApp não se importa `date-fns` nem `@vueuse/core`/`lodash` crus: datas usam `dayjs` **via**
`@maxvue/max-use` (`useDateFormat`, `useTimeAgo`) e utilitários vêm do próprio MaxUse. Imports nomeados
ainda ajudam o tree-shaking nas libs que você de fato usar.

```typescript
// Bom: imports nomeados permitem tree shaking (MaxUse é auto-importado no projeto)
import { useDateFormat, useTimeAgo } from '@maxvue/max-use'

// Ruim: imports de namespace trazem tudo
import * as maxUse from '@maxvue/max-use'
```

```typescript
// Ensure package.json has sideEffects for proper tree shaking
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "*.vue"
  ]
}
```

### Code Splitting & Lazy Loading

```typescript
// Route-based code splitting
const routes = [
  {
    path: '/dashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/settings',
    component: () => import('./views/Settings.vue')
  }
]

// Component-level lazy loading
const HeavyChart = defineAsyncComponent(() =>
  import('./components/HeavyChart.vue')
)

// With loading/error states
const AsyncModal = defineAsyncComponent({
  loader: () => import('./components/Modal.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 10000
})
```

### Manual Chunks Configuration

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk for core dependencies
          'vendor': ['vue', 'vue-router', 'pinia'],

          // Ecossistema Max (UI + composables + stores cacheadas)
          'max': ['@maxvue/max-components-ui', '@maxvue/max-use', '@maxvue/max-pinia'],

          // Utility libraries realmente usadas no projeto (datas via dayjs; HTTP via axios)
          'utils': ['dayjs', 'axios']
        }
      }
    }
  }
})
```

```typescript
// Dynamic chunking by package
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Split each package into its own chunk
            const packageName = id.split('node_modules/')[1].split('/')[0]
            return `vendor-${packageName}`
          }
        }
      }
    }
  }
})
```

### Chunk Size Optimization

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // Warn if chunk exceeds 500KB
    chunkSizeWarningLimit: 500,

    rollupOptions: {
      output: {
        // Ensure CSS is extracted
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js'
      }
    }
  }
})
```

### Compression Plugins

```typescript
// vite.config.ts
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    // Gzip compression
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 1024
    }),

    // Brotli compression (better ratio)
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024
    })
  ]
})
```

### Image Optimization

```typescript
// vite.config.ts
import viteImagemin from 'vite-plugin-imagemin'

export default defineConfig({
  plugins: [
    viteImagemin({
      gifsicle: { optimizationLevel: 3 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      svgo: {
        plugins: [
          { name: 'removeViewBox', active: false },
          { name: 'removeEmptyAttrs', active: true }
        ]
      },
      webp: { quality: 80 }
    })
  ]
})
```

---

## Performance Analysis

### Bundle Analyzer

```typescript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    visualizer({
      filename: 'stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
      template: 'treemap' // or 'sunburst', 'network'
    })
  ]
})
```

```bash
# Generate analysis report
npm run build
# Opens stats.html automatically
```

### Build Performance

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // Faster builds with esbuild minification
    minify: 'esbuild',

    // Target modern browsers only
    target: 'esnext',

    // Disable CSS code splitting for faster builds
    cssCodeSplit: false
  },

  // Optimize dependency pre-bundling.
  // No EngeApp as libs Max locais são EXCLUÍDAS do pre-bundle (resolvidas por alias para o source):
  optimizeDeps: {
    exclude: ['@maxvue/max-components-ui', '@maxvue/max-use']
  }
})
```

### Web Vitals Monitoring

```typescript
// src/utils/vitals.ts
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

type VitalMetric = {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
}

function sendToAnalytics(metric: VitalMetric) {
  // Send to your analytics endpoint
  console.log(metric)
}

export function initVitals() {
  onCLS(sendToAnalytics)
  onFID(sendToAnalytics)
  onLCP(sendToAnalytics)
  onFCP(sendToAnalytics)
  onTTFB(sendToAnalytics)
}
```

```typescript
// main.ts
import { initVitals } from './utils/vitals'

if (import.meta.env.PROD) {
  initVitals()
}
```

---

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `@vitejs/plugin-vue` | Vue 3 SFC support |
| `unplugin-vue-components` | Auto-import components |
| `unplugin-auto-import` | Auto-import Vue APIs |
| `manualChunks` | Vendor code splitting |
| `sourcemap: 'hidden'` | Production error tracking |
| `vite-plugin-compression` | Gzip/Brotli compression |
| `rollup-plugin-visualizer` | Bundle size analysis |
| `import.meta.env.VITE_*` | Environment variables |
| `defineAsyncComponent` | Component lazy loading |
| `web-vitals` | Core Web Vitals monitoring |
