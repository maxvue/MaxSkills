---
name: typescript-tooling-monorepo-best-practices
description: "Use when solving TypeScript tooling issues: compiler performance (tsc/vue-tsc), per-package composite references, module resolution errors, ESM/CJS interop, ESLint/typescript-eslint configuration, and build speed in Engeapp/Max* packages."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Ferramental, Monorepo e Migração em TypeScript

## Objetivo

Fornecer diretrizes e soluções práticas para tooling, compilação e qualidade em TypeScript (^6.0.3) e Vue 3 (`vue-tsc` ^3.3.2) no ecossistema Engeapp e pacotes `@maxvue/*` (`MaxUse`, `MaxPinia`, `MaxComponentsUi`).

## Instruções

### 1. Realidade do Ferramental dos Projetos

- **Pacotes Independentes:** Os pacotes (`MaxUse`, `MaxPinia`, `MaxComponentsUi`) são pacotes npm separados, com `composite: true` por pacote no próprio `tsconfig.json`. O app `engeapp` usa `moduleResolution: "bundler"` sem `composite`.
- **Sem `baseUrl`:** O TypeScript 6 emite TS5101 para `baseUrl` — use exclusivamente `paths` para aliases.
- **Validação com SFCs:** Nunca valide tipos com `tsc --noEmit` puro em projetos Vue. Use `npm run type-check` (`vue-tsc --noEmit`) ou `npm run typecheck:tsgo` (`tsgo --noEmit`).
- **Lint & Testes:** ESLint + `typescript-eslint` em `engeapp`, `MaxUse`, `MaxComponentsUi`; Vitest em `MaxUse`, `MaxPinia`, `MaxComponentsUi`.

```bash
# Scripts de validação padrão:
npm run type-check       # vue-tsc --noEmit (checa .vue + .ts)
npm run typecheck:tsgo   # tsgo --noEmit (compilador nativo rápido)
npm run test             # vitest run
npm run lint             # eslint .
```

---

### 2. Otimização de Desempenho do Compilador

Para diagnosticar e corrigir lentidão no compilador:

```bash
# Diagnóstico de tempo de compilação
npx tsc --extendedDiagnostics --incremental false | grep -E "Check time|Files:|Lines:"
```

- **Substituir Interseções por Interfaces:** `interface B extends A` é muito mais rápida para o compilador do que `type B = A & { ... }`.
- **SkipLibCheck:** Mantenha `"skipLibCheck": true` no `tsconfig.json` para ignorar `.d.ts` de terceiros em `node_modules`.
- **Cache Incremental:** Use `"incremental": true` com `.tsbuildinfo` em bibliotecas.

---

### 3. Resolução de Módulos e ESM

- **Configuração Bundler:** Use `"moduleResolution": "bundler"` e `"module": "ESNext"`.
- **Interoperabilidade CJS/ESM:** Use dynamic import com tipagem explícita para bibliotecas legadas CommonJS:
  ```typescript
  const pkg = (await import('cjs-package')).default;
  ```
- **Declarações Ambient (`.d.ts`):** Para pacotes sem tipagem nativa, crie declaração em `types/`:
  ```typescript
  declare module 'untyped-package' {
    const value: unknown;
    export default value;
  }
  ```

---

### 4. Project References e Configuração de `composite`

Em pacotes compartilhados (`MaxUse`, `MaxComponentsUi`):

```jsonc
// tsconfig.json do pacote
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true,
    "moduleResolution": "bundler",
    "strict": true
  },
  "include": ["src/**/*"]
}
```

---

### 5. Árvore de Decisão Rápida

| Cenário | Ferramenta / Abordagem Recomendada |
|---|---|
| Checagem de tipos em SFC Vue 3 | `npm run type-check` (`vue-tsc --noEmit`) |
| Checagem rápida de tipos (CLI) | `npm run typecheck:tsgo` (`tsgo`) |
| Linting estático e regras de estilo | ESLint com `typescript-eslint` e `@stylistic` |
| Testes unitários e de integração | Vitest (`vitest run`) |
| Tipo inferido excessivamente profundo | Trocar `&` por `interface`, simplificar recursão |

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR).
- **Sem `tsc` puro para Vue:** Nunca execute `tsc --noEmit` direto onde há arquivos `.vue` — use `vue-tsc`.
- **Sem `baseUrl`:** Não adicione `baseUrl` ao `tsconfig.json` (causa TS5101 no TS 6+).
- **Escopo Estrito:** Para lógica pura de types avançados (generics/mapped types/conditional types), utilize `typescript-advanced-types-best-practices`.
