---
name: adonisjs-vite8-full-config-best-practices
description: Use when configuring, updating, or debugging the Vite build setup in an AdonisJS v6 project. This project uses Vite 7 (vite@^7.3.3) with @adonisjs/vite@^5, @vitejs/plugin-vue@^6, unplugin-auto-import, unplugin-vue-components, UnoCSS, Vue 3.6, and the MaxComponentsUi resolver. Triggers on vite.config.ts changes, plugin configuration, auto-import setup, path aliases, HMR issues, or build optimization.
---

# Configuração Completa do Vite com AdonisJS

## Objetivo
Documentar a configuração padrão do Vite no ecossistema Engeapp com AdonisJS v6.

> **Versões instaladas no projeto:** `vite@^7.3.3`, `@vitejs/plugin-vue@^6.0.7`, `@adonisjs/vite@^5.1.1`. Use exatamente estas versões — não faça upgrade para Vite 8 sem validar a compatibilidade com `@adonisjs/vite`.

---

## Dependências (`package.json`)

```json
{
  "devDependencies": {
    "vite": "^7.3.3",
    "@vitejs/plugin-vue": "^6.0.7",
    "@adonisjs/vite": "^5.1.1",
    "unplugin-auto-import": "^21.0.0",
    "unplugin-vue-components": "^32.1.0",
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
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver'
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
        // maxUseAutoImport é um ARRAY (JSON), não uma função — faça spread, não chame
        ...(Array.isArray(maxUseAutoImport) ? maxUseAutoImport : [maxUseAutoImport]),
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
import { presetMaxUno } from '@maxvue/max-components-ui/preset'
import presetAttributify from '@unocss/preset-attributify'

export default defineConfig({
  presets: [
    presetMaxUno(), // preset personalizado do MaxComponentsUi — inclui shortcuts, rules e preflights
    presetAttributify(),
  ],
})
```

---

## Configuração `adonisrc.ts` (Adonis v6)

No Adonis v6 **não existe** uma chave `vite` em `adonisrc.ts`. A integração com o Vite é feita por:
1. o plugin `adonisjs()` no `vite.config.ts` (já configurado acima), e
2. o provider `@adonisjs/vite/vite_provider` registrado em `adonisrc.ts`.

O `defineConfig` é importado de `@adonisjs/core/app`:

```typescript
import { defineConfig } from '@adonisjs/core/app'

export default defineConfig({
  // ...
  providers: [
    () => import('@adonisjs/core/providers/app_provider'),
    () => import('@adonisjs/core/providers/hash_provider'),
    () => import('@adonisjs/core/providers/edge_provider'),
    () => import('@adonisjs/vite/vite_provider'),
    // ...
  ],
  // ...
})
```

> O bundling e o HMR são controlados pelo plugin `adonisjs()` (entrypoints, `reloadServer`) no `vite.config.ts`. Não há `adonisrc.vite.config`.

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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Use `vite@^7.3.3`** com `@vitejs/plugin-vue@^6.0.7` e `@adonisjs/vite@^5.1.1` — versões instaladas no projeto. Não faça upgrade para Vite 8 sem validar `@adonisjs/vite` compatível.
- **`unplugin-auto-import` e `unplugin-vue-components` são obrigatórios** — não importe Vue, Pinia, MaxUse ou componentes Max manualmente nos `.vue` files.
- **UnoCSS é o sistema de estilos** — não use Tailwind CSS. O preset `presetMaxUno` do MaxComponentsUi é obrigatório.
- **Não use Inertia.js** — esta é uma SPA pura com Vue Router. O AdonisJS serve o HTML via catch-all e o Vue Router cuida da navegação.
- **Code splitting**: sempre use `() => import(...)` para rotas Vue Router — nunca imports estáticos nas rotas.
- **Alias `@`** aponta para `./resources/` — use-o consistentemente em vez de caminhos relativos.
