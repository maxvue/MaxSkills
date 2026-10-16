# UnoCSS Dynamic Class Generation

## Rule

Never construct UnoCSS utilities dynamically using string concatenation or template literals. UnoCSS scans your source statically at build time, so a class assembled at runtime (e.g. `bg-${color}-500`) is never generated and the style is silently missing in production. This project uses UnoCSS with `presetMaxUno` + `presetAttributify` (attributify + theme tokens) — never raw Tailwind and there is no `tailwind.config.js`.

## Why This Matters

- UnoCSS uses static analysis at build time to determine which utilities to generate
- Dynamically constructed utilities (e.g., `bg-${color}-500`) are invisible to the scanner
- Utilities may appear in dev (on-demand) but fail silently in production builds
- This is a common source of "it works locally but not in production" bugs

## Bad Code

```vue
<script setup>
const props = defineProps({
  color: String, // 'primary', 'danger', 'success'
  size: String   // 'sm', 'md', 'lg'
})
</script>

<template>
  <!-- WRONG: UnoCSS cannot detect these attributify/utility names -->
  <div :bg="`${color}-500`" :text="`${size}`">Content</div>

  <!-- WRONG: String concatenation -->
  <div :class="'p-' + padding">Content</div>

  <!-- WRONG: Template literal in array -->
  <div :class="[`gap-x-${spacing}`]">Content</div>
</template>
```

## Good Code

```vue
<script setup>
const props = defineProps({
  color: String,
  size: String
})

// Use a mapping object with complete utilities (theme tokens, not raw hex)
const colorClasses = {
  primary: 'bg-primary-500',
  danger: 'bg-red-500',
  success: 'bg-green-500'
}

const sizeClasses = {
  sm: 'text-sm p-2',
  md: 'text-base p-4',
  lg: 'text-lg p-6'
}
</script>

<template>
  <!-- CORRECT: full utility strings that UnoCSS can detect statically -->
  <div :class="[colorClasses[color], sizeClasses[size]]">Content</div>
</template>
```

## Using Conditional Objects

```vue
<script setup>
const props = defineProps({
  variant: String // 'primary', 'secondary', 'danger'
})
</script>

<template>
  <!-- CORRECT: all utilities are complete strings -->
  <button :class="{ 'bg-primary-500 hover:bg-primary-600': variant === 'primary', 'bg-gray-500 hover:bg-gray-600': variant === 'secondary', 'bg-red-500 hover:bg-red-600': variant === 'danger' }">Click me</button>
</template>
```

## Safelist for Truly Dynamic Classes

If you must generate utilities dynamically, add them to the UnoCSS `safelist` in `uno.config.ts` (this project already uses one for `Splitpanes`/`Pane`):

```typescript
// uno.config.ts
import { defineConfig } from '@unocss/vite'
import { presetMaxUno } from '@maxvue/max-components-ui/preset'
import presetAttributify from '@unocss/preset-attributify'

export default defineConfig({
  presets: [presetMaxUno(), presetAttributify()],
  // Enumerate the utilities that are built at runtime, or generate them programmatically
  safelist: [
    'bg-primary-500',
    'bg-red-500',
    'bg-green-500',
    ...['primary', 'red', 'green'].flatMap((c) => [100, 500, 900].map((s) => `bg-${c}-${s}`))
  ]
})
```

## Alternative: CSS Custom Properties

For truly dynamic values (arbitrary colors), use CSS custom properties instead of generating utilities:

```vue
<script setup>
const props = defineProps({
  customColor: String // Any hex color
})
</script>

<template>
  <!-- Use a CSS variable for truly dynamic values -->
  <div class="dynamic-bg" :style="{ '--dynamic-color': customColor }">Content</div>
</template>

<style lang="scss">
.dynamic-bg {
  background-color: var(--dynamic-color);
}
</style>
```

## Caso Específico: Família `sN` do presetMaxUno e MaxGrid

A família de dimensionamento fluido `sN`/`s-N` (ex.: `s12-full`, `s8-full`, `s3-10-start`) opera pelo scanner estático do UnoCSS. Nunca monte tokens `sN` em tempo de execução concatenando números ou sufixos (ex.: `'s' + colunas` ou `` `s-${tamanho}` ``):

```vue
<!-- INCORRETO: UnoCSS não detecta o token em tempo de build -->
<MaxInputText :class="'s' + tamanho" label="Campo" />

<!-- CORRETO: mapeamento com literais completos estáticos -->
<script setup lang="ts">
// Mapeamento explícito com strings literais completas
const tamanhoClasses = {
  compacto: 's8-full',
  medio: 's12-full',
  amplo: 's16-full'
};
</script>

<template>
  <MaxGrid>
    <!-- Literal estático completo detectado pelo UnoCSS -->
    <MaxInputText :class="tamanhoClasses[tipo]" label="Campo Dinâmico" />
  </MaxGrid>
</template>
```

**Atenção aos limites do organizador:**
- Lembre-se de que `sN` define limites em pixels (`min-width: N×20px`, `max-width: N×24px` ou `M×20px`), e não porcentagens.
- O organizador `GridSlotRows` do `MaxGrid` coordena quebras de linha apenas para `start` e `end` sem dispositivo, e `end-mobile`/`mobile-end` em telas mobile. Marcadores como `start-mobile`, tablet ou desktop geram CSS no preset mas não coordenam linhas no grid.
- Para detalhes e regras completas, consulte [max-grid-sizing.md](../../vue-unocss-styling-best-practices/references/max-grid-sizing.md).

## References

- [UnoCSS: Extracting / content](https://unocss.dev/guide/extracting)
- [UnoCSS: safelist](https://unocss.dev/config/#safelist)
