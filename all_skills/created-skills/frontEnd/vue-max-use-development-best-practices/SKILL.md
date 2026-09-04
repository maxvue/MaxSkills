---
name: vue-max-use-development-best-practices
description: "Use when developing, extending, or optimizing helpers and composables in the `@maxvue/max-use` library. Triggers on adding new utility functions, creating custom Vue composables, writing Vitest unit tests for helpers, or refactoring TypeScript types in `@maxvue/max-use`."
author: Johnattas Conrady Gomes Santana
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
   - Coloque os novos helpers dentro de suas respectivas pastas temáticas em `src/Helpers` (ex: `src/Helpers/Format`, `src/Helpers/Dates`), novos composables em `src/Composables`, e novos helpers de rota em `src/Routes` (área de topo com `apiGetRoute`/`apiPostRoute`/`getRoute`/`goToRoute` e `setRouteResolver` em `src/Routes/config.ts`).
   - Para um novo helper/composable individual, basta exportá-lo no `index.ts` da sua categoria — nada precisa ser adicionado manualmente em `src/Helpers/maxUseItems.ts`.
   - Para criar uma nova CATEGORIA de módulo, registre-a nos três pontos de agregação: `src/index.ts`, `src/Helpers/maxUseItems.ts` e `src/scripts/buildAutoImport.ts`, seguindo a convenção de cada `Helpers/<Categoria>/index.ts` reexportar tanto de forma flat (`export *`) quanto montar um objeto namespace (ex: `export const format = {...}`, `export const validate = {...}`).
   - Em caso de colisão de nomes entre categorias, adicione uma reexportação explícita de desambiguação em `src/index.ts` (ex: `now`, `get`/`set`, `isObject`).
   - O objeto centralizado `_` (estilo lodash) mescla `ownHelpers`, o VueUse filtrado (que não sobrescreve helpers próprios) e o lodash-es, nessa ordem de merge — como lodash-es não é filtrado, ele pode sobrescrever `ownHelpers` dentro de `_`. Módulos novos exportados por `src/index.ts` entram automaticamente em `ownHelpers`.
   - Garanta suporte a tree-shaking evitando efeitos colaterais (side effects) nas exportações.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO ignore o uso de `toValue()` ao lidar com parâmetros `MaybeRefOrGetter`.
- NÃO edite `src/Helpers/autoImportData.json` à mão; esse arquivo é GERADO pelo prebuild `npx tsx src/scripts/buildAutoImport.ts` e apenas consumido por `src/Helpers/maxUseItems.ts`.
- NÃO teste composables com watchers reativos fora de um `effectScope()`.
- NÃO use `any` não justificado onde a tipagem forte puder ser inferida ou especificada (a exceção documentada é `Record<string, any>` na montagem do objeto `_` em `src/index.ts`). `unknown` é a alternativa type-safe e não é proibido.
