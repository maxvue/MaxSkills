# Exemplo de Teste de Pinia Store (Vitest)

Este exemplo demonstra como testar uma Pinia Store que realiza requisições HTTP via Axios. O foco é testar mutações de estado, ações assíncronas e garantir que o Axios seja mockado de forma robusta.

### Store Alvo: `useUserStore.ts`
```typescript
import { defineStore } from 'pinia';
import axios from 'axios';

interface User {
  id: number;
  name: string;
  email: string;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [] as User[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchUsers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/users');
        this.users = response.data;
      } catch (err: any) {
        this.error = err.message || 'Erro ao carregar usuários';
      } finally {
        this.isLoading = false;
      }
    },

    clearUsers() {
      this.users = [];
    }
  }
});
```

---

### Arquivo de Teste: `useUserStore.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from './useUserStore';
import axios from 'axios';

// Mock do Axios global no arquivo de teste
vi.mock('axios', () => {
    return {
        default: {
            get: vi.fn()
        }
    };
});

describe('useUserStore', () => {
    beforeEach(() => {
        // Inicializa uma nova instância do Pinia antes de cada teste
        // para isolar o estado entre as execuções de testes
        setActivePinia(createPinia());
        vi.clearAllMocks();
    });

    it('inicia com o estado padrão vazio e isLoading falso', () => {
        const store = useUserStore();
        
        expect(store.users).toEqual([]);
        expect(store.isLoading).toBe(false);
        expect(store.error).toBeNull();
    });

    it('carrega usuários com sucesso através da action fetchUsers', async () => {
        const mockUsers = [
            { id: 1, name: 'João Silva', email: 'joao@engeapp.com' },
            { id: 2, name: 'Maria Souza', email: 'maria@engeapp.com' }
        ];

        // Configura o mock do Axios para retornar sucesso com os dados mockados
        vi.mocked(axios.get).mockResolvedValueOnce({ data: mockUsers });

        const store = useUserStore();
        
        // Dispara a chamada assíncrona
        const fetchPromise = store.fetchUsers();
        
        // Verifica se o estado de loading é ativado imediatamente
        expect(store.isLoading).toBe(true);
        
        await fetchPromise;

        // Validações pós-resolução
        expect(store.isLoading).toBe(false);
        expect(store.users).toEqual(mockUsers);
        expect(store.error).toBeNull();
        expect(axios.get).toHaveBeenCalledWith('/api/users');
    });

    it('trata erro na requisição da API de forma resiliente', async () => {
        // Configura o mock do Axios para simular uma falha de conexão
        vi.mocked(axios.get).mockRejectedValueOnce(new Error('Falha na rede'));

        const store = useUserStore();
        
        await store.fetchUsers();

        // Validações de erro
        expect(store.isLoading).toBe(false);
        expect(store.users).toEqual([]);
        expect(store.error).toBe('Falha na rede');
    });

    it('limpa os usuários da lista através da action clearUsers', () => {
        const store = useUserStore();
        
        // Define estado inicial sujo
        store.users = [{ id: 1, name: 'João Silva', email: 'joao@engeapp.com' }];
        
        store.clearUsers();
        
        expect(store.users).toEqual([]);
    });
});
```
