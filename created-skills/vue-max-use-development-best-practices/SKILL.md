---
name: vue-max-use-development-best-practices
description: Use when developing, extending, or optimizing helpers and composables in the `@maxvue/max-use` library. Triggers on adding new utility functions, creating custom Vue composables, writing Vitest unit tests for helpers, or refactoring TypeScript types in `@maxvue/max-use`.
---

## Objetivo
Fornecer diretrizes rígidas e padrões para criação, extensão e manutenção de composables reativos e funções auxiliares (helpers) puras dentro da biblioteca de utilitários `@maxvue/max-use`, garantindo o tratamento correto de reatividade, tipagem TypeScript e cobertura de testes com Vitest.

## Instruções
1. **Padrões de Reatividade**:
   - Para funções utilitárias puras que precisam suportar argumentos reativos, sempre use `MaybeRefOrGetter<T>` do `vue`.
   - Resolva os valores brutos internamente usando `toValue(arg)` do `vue`. Não use `unref` se precisar dar suporte a funções getter.
   - Exemplo:
     ```typescript
     import { toValue, type MaybeRefOrGetter } from 'vue';

     export function myHelper(value: MaybeRefOrGetter<string>): string {
       const rawValue = toValue(value);
       // ... lógica
     }
     ```

2. **Tipagem TypeScript**:
   - Forneça tipos explícitos para parâmetros e retornos de todas as funções.
   - Use generics onde apropriado para preservar tipos precisos (ex: em helpers de coleções/iteráveis).
   - Garanta interfaces limpas para objetos de configuração.

3. **Testes Unitários com Vitest**:
   - Crie um arquivo `.test.ts` correspondente lado a lado com a implementação.
   - Teste tanto valores estáticos quanto wrappers reativos (`ref` ou funções getter).
   - Para testar composables com estado reativo ou watchers, envolva os testes em um `effectScope()` do Vue para evitar vazamentos de memória e gerenciar corretamente os eventos de ciclo de vida:
     ```typescript
     import { describe, it, expect, beforeEach, afterEach } from 'vitest';
     import { effectScope } from 'vue';
     import { useCustomComposable } from './useCustomComposable';

     describe('useCustomComposable', () => {
       let scope: ReturnType<typeof effectScope>;

       beforeEach(() => {
         scope = effectScope();
       });

       afterEach(() => {
         scope.stop();
       });

       it('deve atualizar o estado reativo', () => {
         scope.run(() => {
           const { state } = useCustomComposable();
           expect(state.value).toBe(defaultValue);
         });
       });
     });
     ```

4. **Organização e Exportação**:
   - Coloque os novos helpers dentro de suas respectivas pastas temáticas em `src/Helpers` (ex: `src/Helpers/Format`, `src/Helpers/Dates`).
   - Coloque os novos composables em `src/Composables`.
   - Atualize o arquivo `index.ts` correspondente dentro do subdiretório para exportar o novo módulo.
   - Atualize `src/index.ts` para exportar todos os novos módulos. Garanta que eles também sejam mesclados no objeto centralizado `_` (estilo lodash) exportado.
   - Garanta suporte a tree-shaking evitando efeitos colaterais (side effects) nas exportações.

## Restrições
- NÃO ignore o uso de `toValue()` ao lidar com parâmetros `MaybeRefOrGetter`.
- NÃO registre imports automáticos (auto-imports) manualmente nos projetos consumidores; garanta que eles sejam devidamente adicionados no arquivo `src/Helpers/maxUseItems.ts` ou arquivos correspondentes, se necessário.
- NÃO teste composables com watchers reativos fora de um `effectScope()`.
- NÃO use tipos genéricos inseguros (`any` ou `unknown`) onde a tipagem forte puder ser inferida ou especificada.
