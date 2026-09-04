# Exemplo de Teste de Store MaxPinia (Vitest)

Este exemplo demonstra como testar uma store MaxPinia (`@maxvue/max-pinia`) que carrega dados de página via auto-GET (`options.get.route`). O foco é testar o estado carregado em `store.data`, o opt-in de cache (`isCached`) e o recarregamento via `reload()`. Como o MaxPinia executa o GET/save **dentro do plugin** (não dentro de actions), o plugin é registrado com uma instância de `axios` mockada, que é o ponto de isolamento correto.

### Store Alvo: `resources/Stores/User/useUser.Store.ts`
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
  const isCached: Ref = ref(true);

  const options = {
    get: {
      // route é um NOME de rota Ziggy pontilhado, NÃO um caminho '/api/...'.
      // Quem resolve o nome é o `resolveRoute` que o app injeta em
      // createMaxPinia (resources/app.ts: `(name, params) => route(name, params)`);
      // o MaxPinia apenas chama cfg.resolveRoute(route_name, data).
      // Nas stores reais do engeapp: 'user.data', 'client.data', 'stats.data', etc.
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

### Arquivo de Teste: `tests/Js/useUserStore.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { createMaxPinia } from '@maxvue/max-pinia';
import { flushPromises } from '@vue/test-utils';

// O vitest.config.ts só inclui tests/Js/**; importe o alvo por caminho relativo profundo.
import { useUserStore } from '../../resources/Stores/User/useUser.Store';

// O plugin MaxPinia importa `localforage` incondicionalmente e já o usa na criação
// da store (localforage.config + loadInCache no watch immediate). Sem este mock o
// teste toca IndexedDB/localStorage — que nem existem no environment 'node'.
vi.mock('localforage', () => ({
  default: {
    config: vi.fn(),
    getItem: vi.fn().mockResolvedValue(null),
    setItem: vi.fn().mockResolvedValue(null),
    removeItem: vi.fn().mockResolvedValue(null),
    clear: vi.fn().mockResolvedValue(null),
  },
}));

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
    // `resolveRoute` é obrigatório aqui: em produção o app injeta o route() do Ziggy;
    // sem ele o MaxPinia cai no buildUrl padrão e trata o NOME como URL literal.
    const pinia = createPinia();
    pinia.use(createMaxPinia({
      axios: mockedAxios,
      resolveRoute: (name: string) => name,
    }));
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

    // O MaxPinia passa o nome de options.get.route ('user.data') ao resolveRoute injetado
    // e usa o resultado como URL do axios.get.
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

> **Nota:** O isolamento é feito injetando uma instância de `axios` mockada em `createMaxPinia({ axios })` (mais o mock de `localforage` e um `resolveRoute` de teste), pois o GET/save do MaxPinia é executado dentro do plugin — não em actions da store (ver SKILL.md seção 3 para os detalhes de `isCached`).
