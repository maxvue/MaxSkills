# Exemplo de Teste de Store MaxPinia (Vitest)

Este exemplo demonstra como testar uma store MaxPinia (`@maxvue/max-pinia`) que carrega dados de página via auto-GET (`options.get.route`). O foco é testar o estado carregado em `store.data`, o opt-in de cache (`isCached`) e o recarregamento via `reload()`. Como o MaxPinia executa o GET/save **dentro do plugin** (não dentro de actions), o plugin é registrado com uma instância de `axios` mockada, que é o ponto de isolamento correto.

### Store Alvo: `useUserStore.ts`
```typescript
import { defineStore } from 'pinia';

interface User {
  id: number;
  name: string;
  email: string;
}

// Setup store no padrão MaxPinia: o GET dos dados de página é declarado
// em options.get.route e executado automaticamente pela camada MaxPinia.
// O opt-in `isCached: true` ativa o plugin de cache para esta store.
export const useUserStore = defineStore('user', () => {
  // O MaxPinia SEMPRE escreve a resposta do GET em `store.data`.
  // Não existe `options.get.target`; a rota é lida de `options.get.route`.
  const data = ref<User[]>([]);
  const isCached = true;

  const options = {
    get: {
      // route é um NOME de rota Ziggy pontilhado (resolvido pelo MaxPinia),
      // NÃO um caminho '/api/...'. Nas stores reais do engeapp: 'user.data',
      // 'client.data', 'stats.data', etc.
      route: 'user.data',
    },
  };

  function clearUsers() {
    data.value = [];
  }

  return { data, isCached, options, clearUsers };
});
```

---

### Arquivo de Teste: `useUserStore.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { createMaxPinia } from '@maxvue/max-pinia';
import { flushPromises } from '@vue/test-utils';
import { useUserStore } from './useUserStore';

// Instância de axios mockada injetada no plugin MaxPinia.
// O GET/save do MaxPinia acontece dentro do plugin (via axios), não em actions.
const mockedAxios = {
  get: vi.fn(),
  post: vi.fn(),
};

describe('useUserStore (MaxPinia)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Registra o plugin MaxPinia com o axios mockado ANTES de ativar o Pinia,
    // para que o comportamento de auto-GET/cache exista nas stores.
    const pinia = createPinia();
    pinia.use(createMaxPinia({ axios: mockedAxios }));
    setActivePinia(pinia);
  });

  it('inicia com o estado padrão vazio', () => {
    const store = useUserStore();

    expect(store.data).toEqual([]);
    // O auto-GET ainda não trouxe dados; o estado de sucesso é falso.
    expect(store.status.server.get.is_success).toBe(false);
  });

  it('carrega usuários via reload() (auto-GET MaxPinia) e marca sucesso', async () => {
    const mockUsers = [
      { id: 1, name: 'João Silva', email: 'joao@engeapp.com' },
      { id: 2, name: 'Maria Souza', email: 'maria@engeapp.com' },
    ];

    // A camada MaxPinia resolve o nome Ziggy de options.get.route ('user.data') e chama axios.get.
    mockedAxios.get.mockResolvedValue({ data: mockUsers });

    const store = useUserStore();

    // reload() força o refetch pelo auto-GET declarado em options.get.route.
    // ATENÇÃO: internamente o MaxPinia dispara `axios.get(...).then(...)` SEM
    // aguardar essa promise (o `.then` que escreve em `store.data` e marca
    // `is_success` roda num microtask não aguardado). Logo, `await store.reload()`
    // pode resolver ANTES de os dados chegarem. Esvazie as promises pendentes
    // com `flushPromises()` antes de assertar, senão o teste fica flaky.
    await store.reload();
    await flushPromises();

    // Os dados sempre chegam em `store.data`; o carregamento é rastreado
    // por `status.server.get.is_success` (ou `store.is_done`).
    expect(store.data).toEqual(mockUsers);
    expect(store.status.server.get.is_success).toBe(true);
    expect(store.is_done).toBe(true);
  });

  it('limpa os usuários da lista através da action clearUsers', () => {
    const store = useUserStore();

    // Define estado inicial sujo diretamente em store.data.
    store.data = [{ id: 1, name: 'João Silva', email: 'joao@engeapp.com' }];

    store.clearUsers();

    expect(store.data).toEqual([]);
  });
});
```

> **Nota:** O teste valida o comportamento da store pelo estado carregado em `store.data`, pelos flags de status do MaxPinia (`status.server.get.is_success` / `store.is_done`) e pelo `reload()`. O isolamento é feito injetando uma instância de `axios` mockada em `createMaxPinia({ axios })`, pois o GET/save do MaxPinia é executado dentro do plugin — não em actions da store. `isCached: true` é um flag de **entrada** (opt-in) que a store declara para ativar o plugin de cache; não é uma flag de saída que indica "dados carregados". Como o plugin dispara o `axios.get(...).then(...)` sem aguardar a promise interna, sempre chame `flushPromises()` (ou `vi.waitFor(...)`) após `await store.reload()` antes de assertar sobre `store.data`/status — do contrário o teste pode ser flaky.
