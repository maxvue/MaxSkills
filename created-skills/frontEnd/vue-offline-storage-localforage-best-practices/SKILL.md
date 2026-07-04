---
name: vue-offline-storage-localforage-best-practices
description: Use when implementing or debugging offline storage, persistent client-state, or local caching using localforage or idb-keyval in Vue 3 — para dados que NÃO são dados de página (esses passam por @maxvue/max-pinia, que já usa LocalForage internamente para cache/auto-save). Triggers on indexedDB access, localForage configuration, state synchronization, and offline-first client architecture.
---

# Boas Práticas para Armazenamento Offline e LocalForage no Vue

## Objetivo
Estabelecer diretrizes sólidas, seguras e consistentes para armazenamento local no cliente, cache de dados e persistência de estado offline em aplicações Vue 3 utilizando `localforage`.

## Caminho padrão: MaxPinia primeiro
> **CRÍTICO:** Para **dados de página** (qualquer coisa que o front busca do backend via GET ou salva via POST), o caminho correto é uma store `@maxvue/max-pinia`. O MaxPinia **já usa LocalForage internamente** para cache e salvamento automático (auto-save/debounced). Não reimplemente manualmente o que ele faz: não crie sincronização manual store↔storage nem flags do tipo `is_save_in_pause` para dados de página — isso duplica o comportamento do MaxPinia e gera divergência de estado.
>
> Use `localforage` diretamente **apenas** para estado que fica **fora do fluxo de dados de página**, por exemplo:
> - preferências/UI puramente locais (tema, layout, rascunhos offline);
> - cache de assets/listas estáticas que não pertencem a uma store de domínio;
> - filas offline-first que serão reconciliadas depois.
>
> Se o dado pertence a uma página/domínio e precisa ir ao backend, prefira a store MaxPinia (rotas string `/api/...` via `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`) em vez das técnicas manuais abaixo.

## Instruções

### 1. Configuração e Inicialização
* Sempre customize a configuração do `localforage` antes de usar para evitar colisões de banco de dados com outras funcionalidades ou aplicações.
* Defina um `name` distinto (normalmente o namespace da aplicação) e um `storeName` (representando o domínio específico).
* Evite modificar a configuração global repetidamente. Se precisar de múltiplas stores ou bancos de dados independentes, inicialize-os usando `localforage.createInstance()` em vez de configurar a instância padrão.

```typescript
import localforage from 'localforage';

// Para funcionalidades distintas, prefira usar createInstance
const cityCacheStore = localforage.createInstance({
    name: 'lists',
    storeName: 'city-ufs'
});
```

### 2. Operações Assíncronas e Integração com TypeScript
* Todos os métodos do `localforage` são assíncronos e retornam Promises. Sempre use `async/await` para melhor legibilidade.
* Defina explicitamente tipos ou interfaces TypeScript para as estruturas armazenadas e realize o cast dos itens recuperados.
* Envolva todas as chamadas de acesso ao armazenamento em blocos `try/catch` para tratar exceções (como bloqueios do modo de navegação privada, limites de cota de armazenamento do navegador ou bancos de dados corrompidos).

```typescript
interface CachedCityList {
    uf: string;
    cities: string[];
    updatedAt: number;
}

async function getCachedCities(uf: string): Promise<CachedCityList | null> {
    try {
        const key = `cities-ufs:${uf}`;
        const cached = await cityCacheStore.getItem<CachedCityList>(key);
        return cached;
    } catch (error) {
        console.error(`[Cache] Erro ao ler a chave cities-ufs:${uf}:`, error);
        return null;
    }
}
```

### 3. Sanitização de Dados e Serialização
* Garanta que todos os objetos armazenados sejam totalmente serializáveis em JSON. Proxies reativos do Vue ou objetos contendo métodos não podem ser salvos diretamente.
* Use `JSON.parse(JSON.stringify(data))` para sanitizar os objetos e remover elementos não clonáveis (como funções, getters ou Symbols) antes de salvá-los no IndexedDB.

```typescript
async function cacheData(key: string, rawData: any): Promise<void> {
    try {
        const cleanData = JSON.parse(JSON.stringify(rawData));
        await cityCacheStore.setItem(key, cleanData);
    } catch (error) {
        console.error(`[Cache] Falha ao serializar ou salvar dados para a chave ${key}:`, error);
    }
}
```

### 4. Sincronização e Gerenciamento de Estado
* **Dados de página → use MaxPinia, não sincronize manualmente.** O cache offline e o auto-save de dados de domínio são responsabilidade do `@maxvue/max-pinia`. Não recrie o ciclo store↔storage à mão (com flags de bloqueio como `is_save_in_pause`) para esses dados — isso é exatamente o que o MaxPinia já resolve e duplicá-lo causa loops e divergência de estado.
* **Apenas para estado fora do fluxo de dados de página** (preferências locais, rascunhos, filas offline) você pode sincronizar `localforage` manualmente. Nesse caso, gerencie o fluxo com cuidado para evitar loops infinitos de leitura/escrita e use um padrão de bloqueio ao carregar o estado para evitar que watchers reativos disparem uma escrita de volta com valores iniciais ou parciais.
* Implemente políticas de expiração de cache. Adicione um campo de metadados com timestamp `updatedAt` dentro da estrutura cacheada e invalide/atualize o cache quando ele exceder o limite de expiração.

```typescript
// Exemplo APENAS para estado fora do fluxo de dados de página
// (para dados de domínio, use uma store @maxvue/max-pinia em vez disto)

// Instância dedicada: NUNCA use o localforage padrão — ele é compartilhado com o
// cache do @maxvue/max-pinia (storeName 'max-pinia-cache'), e o clearAll() dele
// chama localforage.clear(), apagando qualquer chave local guardada no DB padrão.
const localStateStore = localforage.createInstance({ name: 'app-local-state', storeName: 'ui-state' });

let isSavingPaused = false;

async function loadStoreState() {
    isSavingPaused = true;
    try {
        const savedState = await localStateStore.getItem('my-store-key');
        if (savedState) {
            store.data = savedState;
        }
    } finally {
        isSavingPaused = false; // Retoma com segurança os salvamentos após a carga concluir
    }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Sem Acesso Síncrono:** Não tente usar modelos de armazenamento síncronos. Não bloqueie a thread principal.
* **Sem Dados Sensíveis:** Nunca armazene informações confidenciais do usuário não criptografadas (como credenciais, tokens em texto limpo ou dados de identificação pessoal) no localforage.
* **Sem Reatividade no Banco:** Não passe refs reativas ou proxies Vue diretamente para `localforage.setItem`. Sempre faça a sanitização antes.
* **Trate Falhas:** Não assuma que as escritas no armazenamento sempre terão sucesso. Sempre capture erros para evitar falhas na aplicação quando a cota do IndexedDB for excedida ou permissões de armazenamento forem bloqueadas.
