---
name: shadcn-ui
description: "Implement accessible UI components using Radix UI primitives, Tailwind CSS, and the shadcn/ui component registry. Use when scaffolding design systems, configuring components.json, or customizing unstyled Accessible primitives."
risk: safe
source: curated-youtube
---
# shadcn/ui Architecture & Implementation

## When to Use
- Scaffolding new accessible UI components into React/Next.js projects via `@shadcn/ui`.
- Composing Radix UI primitives with Tailwind CSS utility classes and `cn()` helper (`clsx` + `tailwind-merge`).
- Customizing component theme variables in `globals.css`.

## Core Setup & Usage

```bash
# Inicializar configuração de componentes no projeto
npx shadcn@latest init

# Adicionar componentes específicos à pasta /components/ui
npx shadcn@latest add button dialog dropdown-menu form
```

### Exemplo de Componente Tipado
```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```
