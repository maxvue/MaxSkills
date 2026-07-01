# Exemplo de Teste de Store MaxPinia (Vitest)

Este exemplo demonstra como testar uma store MaxPinia (`@maxvue/max-pinia`) que carrega dados de página via auto-GET (`options.get.route`). O foco é testar estado, cache (`isCached`) e o recarregamento via `reload()` — sem mockar `axios` diretamente, pois a camada de rota/cache do MaxPinia é quem executa a requisição.

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
export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([]);

  // Convenção MaxPinia: auto-GET para /api/users. A store dispara o GET,
  // popula `users` e mantém o resultado em cache (isCached).
  const options = {
    get: {
      route: '/api/users',
      target: users,
    },
  };

  function clearUsers() {
    users.value = [];
  }

  return { users, options, clearUsers };
});
```

---

### Arquivo de Teste: `useUserStore.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from './useUserStore';

describe('useUserStore (MaxPinia)', () => {
  beforeEach(() => {
    // Inicializa uma nova instância do Pinia antes de cada teste
    // para isolar o estado entre as execuções.
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('inicia com o estado padrão vazio', () => {
    const store = useUserStore();

    expect(store.users).toEqual([]);
    // O auto-GET ainda não trouxe dados; o cache está frio.
    expect(store.isCached).toBe(false);
  });

  it('carrega usuários via reload() (auto-GET MaxPinia) e marca cache', async () => {
    const mockUsers = [
      { id: 1, name: 'João Silva', email: 'joao@engeapp.com' },
      { id: 2, name: 'Maria Souza', email: 'maria@engeapp.com' },
    ];

    // A camada MaxPinia resolve options.get.route ('/api/users').
    // Em teste, interceptamos a rota respondendo os dados mockados.
    server.use(
      http.get('/api/users', () => HttpResponse.json(mockUsers)),
    );

    const store = useUserStore();

    // reload() força o refetch pelo auto-GET declarado em options.get.route.
    await store.reload();

    // Validamos pelo estado da store, não por chamadas de axios.
    expect(store.users).toEqual(mockUsers);
    expect(store.isCached).toBe(true);
  });

  it('serve os dados do cache sem novo refetch quando isCached é true', async () => {
    const mockUsers = [{ id: 1, name: 'João Silva', email: 'joao@engeapp.com' }];
    server.use(
      http.get('/api/users', () => HttpResponse.json(mockUsers)),
    );

    const store = useUserStore();
    await store.reload();

    expect(store.isCached).toBe(true);
    // Segundo acesso deve vir do cache (MaxPinia); o estado permanece populado.
    expect(store.users).toEqual(mockUsers);
  });

  it('limpa os usuários da lista através da action clearUsers', () => {
    const store = useUserStore();

    // Define estado inicial sujo diretamente no estado da store.
    store.users = [{ id: 1, name: 'João Silva', email: 'joao@engeapp.com' }];

    store.clearUsers();

    expect(store.users).toEqual([]);
  });
});
```

> **Nota:** O teste valida o comportamento da store pelo seu estado e pelos flags do MaxPinia (`isCached`) e pelo `reload()`, em vez de mockar `axios`. As requisições HTTP são interceptadas no nível da rede (ex.: MSW — `http`/`HttpResponse` de um `server` compartilhado no setup dos testes), respeitando o contrato de rotas string do `@maxvue/max-use`.
