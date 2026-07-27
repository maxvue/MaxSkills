---
name: typescript-advanced-types-best-practices
description: "Use when designing type-safe TypeScript architectures or solving advanced type problems — generics, conditional types, mapped types, template literal types, utility types, branded types, strict compiler configuration, type inference, and type testing. Triggers on type-level programming, shared type contracts, and hardening type safety for production systems."
---

# Tipos Avançados e Boas Práticas em TypeScript

## Objetivo

Fornecer orientação especializada para sistemas de tipos avançados em TypeScript e design de tipos para produção: modelar arquiteturas type-safe, resolver problemas complexos de generics/inferência/tipos avançados, construir bibliotecas type-safe e fortalecer a segurança de tipos para sistemas em produção.

## Instruções

Siga esta abordagem ao projetar ou fortalecer tipos em TypeScript:

1. Defina os alvos de runtime e os requisitos de rigor (strictness).
2. Modele tipos e contratos para as superfícies críticas.
3. Implemente com salvaguardas de compilador e linting.
4. Valide o desempenho de build e a ergonomia para o desenvolvedor.
5. Prefira a inferência de tipos a anotações explícitas quando estiver claro.

### Generics

Função genérica básica:

```typescript
function identity<T>(value: T): T {
  return value;
}
```

Restrições de generics:

```typescript
interface HasLength { length: number; }

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}
```

Múltiplos parâmetros de tipo:

```typescript
function merge<T, U>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}
```

### Tipos Condicionais

```typescript
type IsString<T> = T extends string ? true : false;

// Extraindo tipos de retorno (renomeado para não colidir com o built-in `ReturnType`)
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Tipos condicionais distributivos
type ToArray<T> = T extends any ? T[] : never;
type StrOrNumArray = ToArray<string | number>; // string[] | number[]

// Manipulação recursiva de tipos (cuidado: limite a recursão ~10 níveis)
type DeepReadonly<T> = T extends (...args: any[]) => any
  ? T
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;

// Recursão limitada para evitar "excessive stack depth"
type NestedArray<T, D extends number = 5> =
  D extends 0 ? T : T | NestedArray<T, [-1, 0, 1, 2, 3, 4][D]>[];
```

### Tipos Mapeados

```typescript
// Tornar todas as propriedades opcionais (renomeado para não colidir com o built-in `Partial`)
type MyPartial<T> = { [P in keyof T]?: T[P]; };

// Remapeamento de chaves
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

// Filtrar propriedades por tipo
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};
```

### Tipos de Template Literal

```typescript
type EventName = "click" | "focus" | "blur";
type EventHandler = `on${Capitalize<EventName>}`;
// "onClick" | "onFocus" | "onBlur"

// Construção de caminhos (paths)
type Path<T> = T extends object
  ? { [K in keyof T]: K extends string ? `${K}` | `${K}.${Path<T[K]>}` : never; }[keyof T]
  : never;

// Sistemas de eventos type-safe
type PropEventSource<Type> = {
  on<Key extends string & keyof Type>(
    eventName: `${Key}Changed`,
    callback: (newValue: Type[Key]) => void
  ): void;
};
```

### Inferência de Tipos

```typescript
// 'satisfies' valida restrições preservando os tipos literais (TS 4.9+)
const config = {
  api: "https://api.example.com",
  timeout: 5000
} satisfies Record<string, string | number>;

// const assertions para inferência máxima de literais
const routes = ['/home', '/about', '/contact'] as const;
type Route = typeof routes[number]; // '/home' | '/about' | '/contact'
```

### Utility Types

Utilitários nativos do TS (`Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Exclude`, `Extract`, `NonNullable`, `Record`, `ReturnType`, etc.) — ver [documentação oficial](https://www.typescriptlang.org/docs/handbook/utility-types.html). Cuidado ao redeclarar tipos com esses mesmos nomes (ver `MyReturnType`/`MyPartial` acima, renomeados para não colidir com os built-ins).

### Branded Types (Tipos Marcados)

```typescript
type Brand<K, T> = K & { __brand: T };
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function processOrder(orderId: OrderId, userId: UserId) { }
```

Use para: primitivos de domínio críticos, fronteiras de API, moeda/unidades. Recurso: https://egghead.io/blog/using-branded-types-in-typescript

### Configuração Estrita

O baseline real dos 4 projetos (engeapp, MaxUse, MaxPinia, MaxComponentsUi) é `strict: true` + `skipLibCheck: true`. As flags abaixo são adicionais/aspiracionais — nenhuma delas está ativa hoje em nenhum tsconfig.json real; avalie caso a caso antes de propô-las.

```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    // Flags opcionais/aspiracionais — ainda não adotadas nos projetos reais
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

### Teste de Tipos

Valide tipos no nível do compilador com um helper de asserção — não exige runner nem execução em runtime, apenas `tsc`:

```typescript
type AssertEqual<T, U> = [T] extends [U] ? ([U] extends [T] ? true : false) : false;

// Erro de compilação se o tipo divergir do esperado
const _check: AssertEqual<UserId, Brand<string, 'UserId'>> = true;
```

O Vitest está disponível nos projetos Max*/engeapp (é o runner de testes), mas o helper `expectTypeOf` NÃO é usado hoje em nenhuma fonte própria. Se optar por testes de tipo com Vitest, ele é a via oficial (`import { expectTypeOf } from 'vitest'`); caso contrário, prefira o helper `AssertEqual` acima, que já cobre a validação em build.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.

## Boas práticas

1. Use `unknown` em vez de `any` — force a verificação de tipos nas fronteiras.
2. Prefira `interface` para formatos de objetos (melhores mensagens de erro).
3. Use `type` para uniões, interseções e transformações complexas.
4. Use `satisfies` para validação de restrições preservando os tipos literais.
5. Use `const assertions` para preservar tipos literais: `as const`.
6. Use type guards e predicados em vez de asserções de tipo (`as`).
7. Documente tipos complexos com JSDoc.
8. Ative o modo `strict` em todos os projetos TypeScript.
9. Evite referências de tipo circulares.
10. Teste definições de tipo com um helper `AssertEqual` validado por `tsc` (ou `expectTypeOf` do Vitest, se adotar testes de tipo no projeto).

## Armadilhas comuns a evitar

1. Uso excessivo de `any` — anula o propósito do TypeScript.
2. Ignorar as verificações estritas de null — leva a erros em runtime.
3. Tipos condicionais aninhados profundamente demais — tornam a compilação lenta.
4. Não usar uniões discriminadas — perde o estreitamento (narrowing) de tipos.
5. Esquecer `readonly` em estruturas imutáveis.

## Limitações de escopo

- Use esta skill apenas quando a tarefa corresponder claramente ao design de tipos avançados.
- Não trate a saída como substituto para validação ou testes específicos do ambiente.
- Para geração de documentação (TypeDoc, JSDoc), use a skill de documentação.
- Para ferramental (Biome vs ESLint), desempenho do compilador tsc, monorepo (Nx/Turborepo/project references), migração JS→TS, module resolution e ESM/CJS, veja a skill typescript-tooling-monorepo-best-practices.
