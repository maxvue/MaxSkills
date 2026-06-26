---
name: adonisjs-vite8-full-config-best-practices
description: Use when configuring, updating, or debugging the Vite 8 build setup in an AdonisJS v6 project. This project uses Vite 8 (NOT older versions) with @adonisjs/vite, unplugin-auto-import, unplugin-vue-components, UnoCSS, Vue 3.6, and the MaxComponentsUi resolver. Triggers on vite.config.ts changes, plugin configuration, auto-import setup, path aliases, HMR issues, build optimization, or upgrading from an older Vite version.
---

# Configuração Completa do Vite 8 com AdonisJS

## Objetivo
Documentar a configuração padrão do Vite 8 no ecossistema Engeapp com AdonisJS v6. O Vite 8 traz melhorias significativas no Environment API, performance de HMR, e suporte a módulos ESM. **Sempre especifique a versão 8 do Vite** — nunca faça downgrade ou use configurações de versões anteriores.

---

## Dependências (`package.json`)

```json
{
  "devDependencies": {
    "vite": "^8.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "@adonisjs/vite": "^3.0.0",
    "unplugin-auto-import": "^0.18.0",
    "unplugin-vue-components": "^0.27.0",
    "unocss": "^66.0.0"
  }
}
```

---

## Configuração Completa (`vite.config.ts`)

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import adonisjs from '@adonisjs/vite/client'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import UnoCSS from 'unocss/vite'
import { maxUseAutoImport } from '@maxvue/max-use'
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    // Plugin AdonisJS — integração com asset bundling e HMR
    adonisjs({
      entrypoints: ['resources/app.ts'],
      reloadServer: false,
    }),

    // Vue 3.6 com suporte completo a SFC
    vue(),

    // UnoCSS com presetMaxUno do MaxComponentsUi
    UnoCSS(),

    // Auto-import: Vue, Pinia, MaxUse, Axios e composables locais
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        maxUseAutoImport(),
        {
          axios: [['default', 'axios']],
        },
      ],
      dirs: [
        './resources/Functions/**',
        './resources/Helpers/**',
        './resources/Stores/**',
      ],
      dts: './resources/Types/auto-imports.d.ts',
      vueTemplate: true,
    }),

    // Auto-resolução de componentes: MaxComponentsUi + componentes locais
    Components({
      dirs: ['./resources/Vue'],
      extensions: ['vue', 'ts'],
      resolvers: [MaxComponentsUiResolver()],
      dts: './resources/Types/components.d.ts',
    }),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./resources', import.meta.url)),
      '@stores': fileURLToPath(new URL('./resources/Stores', import.meta.url)),
      '@components': fileURLToPath(new URL('./resources/Vue/Components', import.meta.url)),
      '@pages': fileURLToPath(new URL('./resources/Vue/Pages', import.meta.url)),
      '@sections': fileURLToPath(new URL('./resources/Vue/Sections', import.meta.url)),
      '@layouts': fileURLToPath(new URL('./resources/Vue/Layouts', import.meta.url)),
      '@functions': fileURLToPath(new URL('./resources/Functions', import.meta.url)),
      '@theme': fileURLToPath(new URL('./resources/Theme', import.meta.url)),
    },
  },

  build: {
    chunkSizeWarningLimit: 4000,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-primevue': ['primevue'],
          'vendor-charts': ['chart.js'],
        },
      },
    },
  },
})
```

---

## Configuração UnoCSS (`uno.config.ts`)

```typescript
import { defineConfig } from 'unocss'
import { presetMaxUno } from '@maxvue/max-components-ui'
import presetAttributify from '@unocss/preset-attributify'

export default defineConfig({
  presets: [
    presetMaxUno(), // preset personalizado do MaxComponentsUi — inclui shortcuts, rules e preflights
    presetAttributify(),
  ],
})
```

---

## Configuração `adonisrc.ts` (Vite 8)

```typescript
import { defineConfig } from '@adonisjs/core/build/config'

export default defineConfig({
  vite: {
    config: 'vite.config.ts',
  },
})
```

---

## Configuração HMR em Desenvolvimento Local

Para HMR funcionando com domínio local e HTTPS, veja a skill `adonisjs-vite-local-https-ssl-best-practices`.

Para desenvolvimento sem HTTPS:
```typescript
// vite.config.ts — adição para HMR em localhost
server: {
  host: 'localhost',
  port: 5173,
  hmr: {
    host: 'localhost',
  },
},
```

---

## TypeScript (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "jsxImportSource": "vue",
    "paths": {
      "@/*": ["./resources/*"],
      "@stores/*": ["./resources/Stores/*"],
      "@components/*": ["./resources/Vue/Components/*"],
      "@pages/*": ["./resources/Vue/Pages/*"],
      "@sections/*": ["./resources/Vue/Sections/*"],
      "@layouts/*": ["./resources/Vue/Layouts/*"],
      "@functions/*": ["./resources/Functions/*"],
      "@theme/*": ["./resources/Theme/*"]
    },
    "types": ["vite/client", "pinia"]
  },
  "include": [
    "./resources/**/*.{vue,ts,tsx}",
    "./resources/Types/**/*.d.ts",
    "./*.config.ts"
  ]
}
```

---

## Restrições
- **Sempre use Vite 8** — não faça downgrade para versões anteriores. Verifique `"vite": "^8.0.0"` no `package.json`.
- **`unplugin-auto-import` e `unplugin-vue-components` são obrigatórios** — não importe Vue, Pinia, MaxUse ou componentes Max manualmente nos `.vue` files.
- **UnoCSS é o sistema de estilos** — não use Tailwind CSS. O preset `presetMaxUno` do MaxComponentsUi é obrigatório.
- **Não use Inertia.js** — esta é uma SPA pura com Vue Router. O AdonisJS serve o HTML via catch-all e o Vue Router cuida da navegação.
- **Code splitting**: sempre use `() => import(...)` para rotas Vue Router — nunca imports estáticos nas rotas.
- **Alias `@`** aponta para `./resources/` — use-o consistentemente em vez de caminhos relativos.
