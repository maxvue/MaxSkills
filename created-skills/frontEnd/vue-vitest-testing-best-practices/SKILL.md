---
name: vue-vitest-testing-best-practices
description: "Use when writing or updating front-end unit/integration tests with Vitest and Vue Test Utils for Vue 3 components, MaxPinia stores, and composables in tests/Js/, including API mocking. Covers objectives and core workflows."
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
- **Ambiente:** O ambiente padrão do `vitest.config.ts` do engeapp é `node` (sem DOM), e o `include` cobre apenas `tests/Js/**/*.{test,spec}.ts`. Testes que precisam de DOM devem declarar a diretiva no topo do próprio arquivo, como fazem os testes reais em `tests/Js/`:
  ```typescript
  // @vitest-environment jsdom
  ```
  ```typescript
  /**
   * @vitest-environment happy-dom
   */
  ```
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
- **Vínculos de Formulários (Form Bindings):** O projeto não usa inputs nativos — os campos são componentes `MaxInput*` de `@maxvue/max-components-ui`. Preencha o valor pelo stub registrado (que emite `update:modelValue`) ou emitindo o evento diretamente no componente encontrado:
  ```typescript
  // Emita o evento no componente: o stub padrão do VTU não renderiza um <input>,
  // então `setValue` falharia (só funciona em input/select/textarea).
  await wrapper.findComponent({ name: 'MaxInputText' }).vm.$emit('update:modelValue', 'Novo Valor');
  // Se registrar um stub próprio com <input> interno, aí sim vale:
  // await wrapper.find('input').setValue('Novo Valor');
  ```

### 3. Testes de Store MaxPinia
- **Pinia Ativo + plugin MaxPinia registrado:** `@maxvue/max-pinia` é um **plugin do Pinia** instalado via `createMaxPinia()` (`pinia.use(...)`). Suas propriedades injetadas (`reload`, `status`, cache, e a escrita dos dados do GET em `store.data`) só existem quando o plugin está ativo **e** a store faz opt-in (`isCached: true`). Um teste baseado em `createPinia()` puro **não** terá comportamento MaxPinia — `store.reload()` seria `undefined`. Sempre registre o plugin no `beforeEach`:
  ```typescript
  import { createPinia, setActivePinia } from 'pinia';
  import { createMaxPinia } from '@maxvue/max-pinia';

  // axios mockado: o GET/save do MaxPinia roda DENTRO do plugin, via axios.
  const mockedAxios = { get: vi.fn(), post: vi.fn() };

  beforeEach(() => {
      const pinia = createPinia();
      pinia.use(createMaxPinia({ axios: mockedAxios }));
      setActivePinia(pinia);
  });
  ```
  `createMaxPinia` e `useAsyncStatus` são os únicos exports de **valor** de `@maxvue/max-pinia` (o pacote também exporta tipos: `MaxPiniaConfig`, `LoadingAdapter`, `LoadingOptions`, `Status`, `OperationStatus`).
- **Isolamento de rede — injete o axios mockado, não `createTestingPinia`:** O MaxPinia executa o GET (auto-GET) e o save **dentro do plugin** (via `axios`, disparado por watchers), e **não** dentro de actions da store. Portanto, `createTestingPinia({ stubActions: true })` do `@pinia/testing` **não** intercepta essas requisições — as chamadas reais aconteceriam mesmo assim. Prefira injetar uma instância de `axios` mockada em `createMaxPinia({ axios })` (como acima) ou interceptar no nível da rede (MSW). Só use `@pinia/testing` após adicioná-lo como devDependency do projeto (ele não é dependência do projeto-alvo).
- **Opt-in de cache e estado de carga:** `isCached`/`is_cached` é um flag de **entrada** que a store declara para ativar o plugin de cache (o plugin faz `if (!store.isCached && !store.is_cached) return {};`), **não** um flag de saída de "dados carregados". Para saber se os dados chegaram, use `store.status.server.get.is_success` ou `store.is_done`.
- **`reload()` não aguarda o GET interno — esvazie as promises:** após `await store.reload()`, chame sempre `flushPromises()` (de `@vue/test-utils`) ou `vi.waitFor(...)` antes de assertar, senão o teste fica flaky. Explicação detalhada em [Exemplo de Teste de Store](examples/store-test-example.md).
- **Testes Isolados:** Teste as ações da store invocando-as diretamente e inspecionando o estado mutado:
  ```typescript
  const store = useMyStore();
  store.increment();
  expect(store.count).toBe(1);
  ```

### 4. Mockando Chamadas de API e Dependências
- **Prefira mockar a store MaxPinia:** Como TODO GET/save de dados de página passa por uma store `@maxvue/max-pinia`, o ponto de isolamento natural é a instância de `axios` injetada em `createMaxPinia({ axios })` (como na seção 3) — não o cliente HTTP importado diretamente. Sobrescreva diretamente o estado/ações expostas quando quiser deixar o componente alheio ao transporte:
  ```typescript
  const store = useMyStore();
  store.data = [{ id: 1, nome: 'Usina Solar 01' }]; // estado já carregado, sem fetch real
  ```
- **Axios fora da store (raro):** `axios` também é um global auto-importado (`vite.config.ts`: `{ axios: [['default', 'axios']] }`), então nenhum SFC/store o importa e `vi.mock('axios')` **não intercepta** nada. Se o código sob teste chamar `axios` fora da store, stube o global: `vi.stubGlobal('axios', { post: vi.fn() })` (padrão real de `tests/Js/voip.test.ts`).
- **Helpers de rota são GLOBAIS — use `vi.stubGlobal`, não `vi.mock`:** As rotas do front são NOMES Ziggy pontilhados (ex.: `'user.data'`, `'client.save'`) passados a `apiGetRoute`/`apiPostRoute` de `@maxvue/max-use`. No engeapp esses helpers são injetados como globais pelo `unplugin-auto-import` (`maxUseAutoImport` no `vite.config.ts`, declarados em `auto-import.d.ts`) e **nunca são importados nos arquivos** — por isso `vi.mock('@maxvue/max-use')` é inerte. Pior: o `vitest.config.ts` registra auto-import apenas de `vue`, `{ pinia: ['defineStore'] }` e das stores em `dirs: ['./resources/Stores/**']`, ou seja, sob teste esses globais do max-use **nem existem**. Declare-os você mesmo:
  ```typescript
  // apiGetRoute/apiPostRoute recebem NOMES Ziggy pontilhados (ex.: 'user.data')
  // e resolvem para o CORPO da resposta (`return response.data`), não para `{ data }`.
  vi.stubGlobal('apiGetRoute', vi.fn().mockResolvedValue([]));
  vi.stubGlobal('apiPostRoute', vi.fn().mockResolvedValue({}));
  // Se o código sob teste chamar route() do Ziggy diretamente:
  vi.stubGlobal('route', vi.fn((name: string) => name));
  ```
  Lembre de restaurar com `vi.unstubAllGlobals()` no `afterEach` quando o stub for local ao bloco.

### 5. Idioma do Código e Comentários
- **Regra Crucial:** Todos os comentários dentro dos arquivos de teste DEVEM ser escritos em **Português do Brasil (pt-BR)** para alinhar com os padrões do projeto Engeapp.

## Exemplos
Consulte o diretório `examples/` para ver implementações detalhadas:
- [Exemplo de Teste de Componente](examples/component-test-example.md) — Demonstra testes em um componente Vue 3 com props, emissões e stubs.
- [Exemplo de Teste de Store](examples/store-test-example.md) — Demonstra testes em uma store Pinia com simulação de ações e estado.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** permita que os testes realizem operações de rede reais.
- **NUNCA** deixe de chamar `vi.clearAllMocks()` ou `setActivePinia` ao testar componentes ou stores que possuem estado mutável ou que rastreiam históricos de mocks.
- **NUNCA** teste detalhes internos de implementação; verifique apenas a API pública (props, eventos emitidos, interações do usuário e saídas visuais).
