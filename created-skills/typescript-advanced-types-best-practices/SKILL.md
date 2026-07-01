---
name: typescript-advanced-types-best-practices
description: Use when designing type-safe TypeScript architectures or solving advanced type problems — generics, conditional types, mapped types, template literal types, utility types, branded types, strict compiler configuration, type inference, and type testing. Triggers on type-level programming, shared type contracts, and hardening type safety for production systems.
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
6. Projete interfaces e classes abstratas robustas.
7. Implemente fronteiras de erro adequadas com exceções tipadas.
8. Otimize os tempos de build com compilação incremental.

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
```

### Utility Types

```typescript
Partial<T>          // Todas as propriedades opcionais
Required<T>         // Todas as propriedades obrigatórias
Readonly<T>         // Todas as propriedades somente leitura
Pick<T, K>          // Selecionar propriedades específicas
Omit<T, K>          // Remover propriedades específicas
Exclude<T, U>       // Excluir tipos de uma união
Extract<T, U>       // Extrair tipos de uma união
NonNullable<T>      // Excluir null e undefined
Record<K, T>        // Criar tipo objeto com chaves K e valores T
ReturnType<F>       // Tipo de retorno de uma função
```

### Branded Types (Tipos Marcados)

```typescript
type Brand<K, T> = K & { __brand: T };
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function processOrder(orderId: OrderId, userId: UserId) { }
```

### Configuração Estrita

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

### Teste de Tipos

```typescript
type AssertEqual<T, U> = [T] extends [U] ? ([U] extends [T] ? true : false) : false;

// Com Vitest
import { expectTypeOf } from 'vitest';
expectTypeOf<UserId>().toEqualTypeOf<Brand<string, 'UserId'>>();
```

## Restrições

Boas práticas:

1. Use `unknown` em vez de `any` — force a verificação de tipos nas fronteiras.
2. Prefira `interface` para formatos de objetos (melhores mensagens de erro).
3. Use `type` para uniões, interseções e transformações complexas.
4. Use `satisfies` para validação de restrições preservando os tipos literais.
5. Use `const assertions` para preservar tipos literais: `as const`.
6. Use type guards e predicados em vez de asserções de tipo (`as`).
7. Documente tipos complexos com JSDoc.
8. Ative o modo `strict` em todos os projetos TypeScript.
9. Evite referências de tipo circulares e tipos condicionais profundamente aninhados.
10. Use `expectTypeOf` do Vitest para testar definições de tipo.

Armadilhas comuns a evitar:

1. Uso excessivo de `any` — anula o propósito do TypeScript.
2. Ignorar as verificações estritas de null — leva a erros em runtime.
3. Tipos condicionais aninhados profundamente demais — tornam a compilação lenta.
4. Não usar uniões discriminadas — perde o estreitamento (narrowing) de tipos.
5. Esquecer `readonly` em estruturas imutáveis.
6. Faltar `await` em funções assíncronas — retorna `Promise<T>`, não `T`.

Limitações de escopo:

- Use esta skill apenas quando a tarefa corresponder claramente ao design de tipos avançados.
- Não trate a saída como substituto para validação ou testes específicos do ambiente.
- Para geração de documentação (TypeDoc, JSDoc), use a skill de documentação.
- Para ferramental, migração, monorepo e resolução de problemas avançados, use a skill de ferramental/monorepo.
