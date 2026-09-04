---
name: tailwind-css
description: "Utility-first CSS styling using Tailwind CSS v4, theme tokens, responsive modifiers, and container queries. Use when building modern web layouts, configuring design tokens in @theme, or optimizing CSS bundle output."
risk: safe
source: curated-youtube
---
# Tailwind CSS v4 Engineering Standards

## When to Use
- Developing modern, responsive layouts with utility classes and CSS variables.
- Configuring custom design tokens using modern `@theme` directives in CSS.
- Applying responsive (`sm:`, `md:`, `lg:`), state (`hover:`, `focus-visible:`), and dark mode modifiers.

## Core CSS Configuration (Tailwind v4)
```css
@import "tailwindcss";

@theme {
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --font-display: "Inter", sans-serif;
  --radius-card: 0.75rem;
}
```

## Responsive Layout Pattern
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 max-w-7xl mx-auto">
  <div class="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
    <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Título do Card</h3>
    <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">Conteúdo do layout responsivo.</p>
  </div>
</div>
```
