# TSConfig e Declarações de Módulo (ferramental)

> Escopo desta referência: apenas o **ferramental** (tsconfig e declarações de módulo/ambient).
> Programação em nível de tipos — generics, tipos condicionais/mapeados/template literal,
> branded types, discriminated unions, type guards e utility types — pertence à skill
> **typescript-advanced-types-best-practices**; não está duplicada aqui.

## Module Declarations

```typescript
// Declarar módulo para pacote sem tipos
declare module 'untyped-package' {
  export function doSomething(): void
  export const value: string
}

// Aumentar um módulo existente
declare module 'express' {
  interface Request {
    user?: { id: string }
  }
}

// Declarar global
declare global {
  interface Window {
    myGlobal: string
  }
}
```

## TSConfig Essentials

```json
{
  "compilerOptions": {
    // Strictness
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    // Modules
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,

    // Output
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],

    // Performance
    "skipLibCheck": true,
    "incremental": true,

    // Paths (sem baseUrl: os projetos usam TypeScript 6.x, que emite
    // TS5101 para `baseUrl`; os padrões de `paths` já são relativos
    // ao diretório do próprio tsconfig.json)
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

> Para os valores canônicos de `strict` e o racional de cada flag, veja a seção
> "Configuração Estrita" da skill **typescript-advanced-types-best-practices**.
