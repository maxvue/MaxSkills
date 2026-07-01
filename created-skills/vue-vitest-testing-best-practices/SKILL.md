---
name: vue-vitest-testing-best-practices
description: >-
  Use when writing, debugging, or updating front-end unit and integration tests using Vitest and Vue Test Utils for Vue 3 components, @maxvue/max-pinia stores, and composables in Engeapp. Triggers on creating test files, configuring Vitest, mocking MaxPinia stores, Axios, or @maxvue/max-use route helpers, and verifying component rendering, user interactions, or store states.
---

# Melhores Práticas de Testes com Vitest no Vue

## Objetivo
Estabelecer padrões de teste limpos, consistentes e confiáveis para o front-end do Engeapp utilizando Vitest e Vue Test Utils. Garantir o isolamento adequado de componentes, stores e composables por meio de estratégias corretas de mock.

## Instruções

### 1. Configuração e Ambiente de Testes
- **Framework Vitest:** Utilize o Vitest para testes unitários e de integração. Sempre importe as funções de teste de forma explícita:
  ```typescript
  import { describe, it, expect, beforeEach, vi } from 'vitest';
  ```
- **Ambiente:** Certifique-se de que o ambiente está configurado como `happy-dom` ou `jsdom` (geralmente definido em `vitest.config.ts`).
- **Estado Limpo:** Sempre limpe os mocks e estados locais antes de cada execução de teste:
  ```typescript
  beforeEach(() => {
      vi.clearAllMocks();
  });
  ```

### 2. Testes de Componente com Vue Test Utils
- **Mount vs. ShallowMount:** Prefira `mount` para testes de integração completos. Se os componentes filhos forem pesados ou fizerem chamadas de API, faça o stub deles na configuração global ou simule suas importações.
- **Stubs Globais:** Use `global.stubs` para mockar componentes pesados ou de terceiros (como ícones de bibliotecas de UI, modais ou botões externos) para que eles não quebrem a árvore de renderização do componente:
  ```typescript
  const wrapper = mount(MyComponent, {
      global: {
          stubs: {
              MaxIcon: true,
              MaxButton: { template: '<button><slot /></button>' }
          }
      }
  });
  ```
- **Testando Props e Renderização:** Verifique se o componente exibe as propriedades corretamente e vincula classes/estilos conforme o esperado:
  ```typescript
  expect(wrapper.text()).toContain('Texto Esperado');
  expect(wrapper.classes()).toContain('is-active');
  ```
- **Interações do Usuário:** Simule cliques, pressionamentos de teclas ou alterações em campos de entrada. Sempre utilize `await` nas interações para garantir que o DOM seja atualizado (ciclo de reatividade do Vue) antes de fazer asserções:
  ```typescript
  const button = wrapper.find('button');
  await button.trigger('click');
  expect(wrapper.emitted('submit')).toBeTruthy();
  ```
- **Vínculos de Formulários (Form Bindings):** Para componentes que utilizam utilitários de formulário (como `useForm`), defina os valores usando `setValue` e valide o estado correspondente:
  ```typescript
  const input = wrapper.find('input[type="text"]');
  await input.setValue('Novo Valor');
  ```

### 3. Testes de Store MaxPinia
- **Pinia Ativo:** Sempre inicialize e configure a instância ativa do Pinia no gancho `beforeEach` para evitar a poluição de estado entre os testes:
  ```typescript
  import { setActivePinia, createPinia } from 'pinia';
  
  beforeEach(() => {
      setActivePinia(createPinia());
  });
  ```
- **Stores `@maxvue/max-pinia`:** As stores do projeto usam `@maxvue/max-pinia` (camada de cache + auto-save/debounced sobre rotas string `/api/...`). Ao montar componentes que consomem essas stores, prefira `createTestingPinia` do `@pinia/testing` para interceptar as ações de fetch/save e evitar requisições reais:
  ```typescript
  import { createTestingPinia } from '@pinia/testing';

  const wrapper = mount(MyComponent, {
      global: {
          plugins: [createTestingPinia({ createSpy: vi.fn })]
      }
  });
  ```
  Com `createTestingPinia`, as ações da store (incluindo o fetch via `apiGetRoute` e o auto-save via `apiPostRoute`) ficam stubadas por padrão — defina `stubActions: false` apenas quando precisar exercitar a lógica real da action.
- **Testes Isolados:** Teste as ações da store invocando-as diretamente e inspecionando o estado mutado:
  ```typescript
  const store = useMyStore();
  store.increment();
  expect(store.count).toBe(1);
  ```

### 4. Mockando Chamadas de API e Dependências
- **Prefira mockar a store MaxPinia:** Como TODO GET/save de dados de página passa por uma store `@maxvue/max-pinia`, o ponto de isolamento natural é a própria store — não o cliente HTTP. Mocke a store (via `createTestingPinia`, como na seção 3) ou sobrescreva diretamente o estado/ações expostas, deixando o componente alheio ao transporte:
  ```typescript
  const store = useMyStore();
  store.items = [{ id: 1, nome: 'Usina Solar 01' }]; // estado já carregado, sem fetch real
  ```
- **Mock do Axios (apenas casos de baixo nível):** Quando o código sob teste fizer uma chamada HTTP fora da store (raro neste projeto), evite requisições reais mockando o Axios com `vi.mock`. Não use isto como atalho para contornar o fluxo MaxPinia:
  ```typescript
  import axios from 'axios';
  
  vi.mock('axios', () => ({
      default: {
          get: vi.fn(),
          post: vi.fn()
      }
  }));
  ```
- **Mock dos helpers de rota:** Mocke as importações de `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`) quando as rotas forem necessárias (não existe Ziggy/`route` global neste projeto):
  ```typescript
  import * as maxUse from '@maxvue/max-use';
  
  vi.mock('@maxvue/max-use', async (importOriginal) => {
      const actual = await importOriginal();
      return {
          ...(actual as object),
          goToRoute: vi.fn()
      };
  });
  ```

### 5. Idioma do Código e Comentários
- **Regra Crucial:** Todos os comentários dentro dos arquivos de teste DEVEM ser escritos em **Português do Brasil (pt-BR)** para alinhar com os padrões do projeto Engeapp.

## Examples
Consulte o diretório `examples/` para ver implementações detalhadas:
- [Exemplo de Teste de Componente](examples/component-test-example.md) — Demonstra testes em um componente Vue 3 com props, emissões e stubs.
- [Exemplo de Teste de Store](examples/store-test-example.md) — Demonstra testes em uma store Pinia com simulação de ações e estado.

## Restrições
- **NUNCA** permita que os testes realizem operações de rede reais.
- **NUNCA** escreva comentários em inglês; sempre utilize português (pt-BR) dentro do código do teste.
- **NUNCA** deixe de chamar `vi.clearAllMocks()` ou `setActivePinia` ao testar componentes ou stores que possuem estado mutável ou que rastreiam históricos de mocks.
- **NUNCA** teste detalhes internos de implementação; verifique apenas a API pública (props, eventos emitidos, interações do usuário e saídas visuais).
