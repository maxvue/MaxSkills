---
name: vue-max-use-usecachedapi-state-cache-best-practices
description: "Use when implementing or debugging Vue 3 code with useRefCachedApi (or useCachedApi, useSharedCacheApi, useInCacheApi) from @maxvue/max-use to cache GET requests in localStorage with background revalidation. Covers objectives, composable signatures, and cached state management."
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Otimizar o gerenciamento de estado do frontend Vue 3 utilizando o `useRefCachedApi` (e seus aliases `useCachedApi`, `useSharedCacheApi`, `useInCacheApi`) da biblioteca `@maxvue/max-use` para armazenar e carregar dados de requisições GET do `localStorage` de forma síncrona na montagem, e de forma transparente buscar dados atualizados da API em segundo plano.

## Instruções

### 1. Assinatura do Composable & Opções
O composable é importado de `@maxvue/max-use` e possui a seguinte assinatura real:
```typescript
export type ToRefCachedApi<T> = T extends Ref ? T : Ref<T>;

export function useCachedApi<T>(
  route_name: string,
  options: {
    data_get?: any;
    data?: any;
    key?: string | null;
    defaultValue?: T;
    sync?: boolean;
    watch?: boolean;
  } = {}
): ToRefCachedApi<T>
```
> O retorno é `ToRefCachedApi<T>`, que resolve para `Ref<T>` quando `T` não é uma `Ref` (e mantém o próprio tipo quando `T` já é uma `Ref`). Na prática você usa como uma `Ref<T>` comum. Os parâmetros da rota podem ser passados em `options.data` ou no alias `options.data_get`.
* **`route_name`**: O **nome** da rota Ziggy (pontilhado — ex.: `'clients.data'`). O nome é resolvido por `resolveRoute()` do `@maxvue/max-use`, que delega ao resolvedor injetado pela aplicação via `setRouteResolver()` (em `engeapp/resources/app.ts`, implementado com `route()` do Ziggy, que ainda remove o origin da URL absoluta). Se `setRouteResolver()` não tiver sido chamado, `resolveRoute()` lança um `Error` explícito, que vira uma Promise rejeitada não tratada — a falha NÃO é silenciosa. Passe sempre o **nome** da rota, nunca um caminho `/api/...`. Lembre-se: para GET de dados de página, prefira uma store `@maxvue/max-pinia` (todo GET deve passar por store); use `useRefCachedApi` apenas em casos pontuais.
* **`options.defaultValue`**: Crucial para evitar erros de renderização inicial (ex: `defaultValue: []` para listas). Sempre forneça um valor padrão compatível com o tipo.
* **`options.key`**: Chave personalizada do `localStorage` (padrão: `route_name`). Necessária ao fazer cache de dados para diferentes escopos de contexto (como tenants ou clientes).
* **`options.sync`**: Padrão é `true`. Se definido como `false`, não executará a requisição GET da API em segundo plano automaticamente na criação.
* **`options.watch`**: Padrão é `true`. Se `true`, qualquer alteração no `Ref` retornado será monitorada e persistida automaticamente de volta no `localStorage`.

### 2. Boas Práticas para Vue 3 SFC & TypeScript
Ao utilizar `useRefCachedApi` em um arquivo `.vue` ou store do Pinia, você deve aderir às seguintes regras:
* **Sempre Forneça `defaultValue`**: Omitir ou definir como array/objeto vazio evita erros de referência nula (`null`) no render do template antes que o cache ou a API retornem dados:
  ```typescript
  const clients = useRefCachedApi<Client[]>('clients.data', { defaultValue: [] });
  ```
* **Tipos do TypeScript**: Defina explicitamente o parâmetro genérico `<T>` para que os templates Vue e as propriedades computadas tenham verificação de tipo precisa.

### 3. Chaves de Cache Dinâmicas e Isolamento (Multi-tenant/Cliente)
Como o `useRefCachedApi` avalia a opção `key` apenas uma vez no momento da criação (não reativamente), se o tenant ou cliente ativo mudar, você deve gerenciar manualmente o carregamento e a atualização do cache dentro de um `watch`:
* **Incorreto (Avaliação estática de valor dinâmico)**:
  ```typescript
  // RUIM: options.key é avaliado apenas uma vez; se selectedClient.id mudar, a chave e o cache NÃO são atualizados.
  const list = useRefCachedApi<Data[]>('reports.data', { 
    key: `data::${selectedClient.id}`,
    defaultValue: [] 
  });
  ```
* **Correto (Troca de cache manual via Watch)**: use `sync: false` para desativar a sincronização automática, e um `watch({ immediate: true })` no id do tenant/cliente para: carregar do `localStorage` com a chave `data::${newId}` (fallback `[]`), depois buscar em segundo plano via `apiGetRoute` e regravar o `localStorage` com o resultado. A chave (`key` avaliada uma única vez na criação, ver Restrições) é reconstruída manualmente a cada mudança de `newId`.

### 4. Invalidação de Cache e Atualizações Pós-Mutação
Ao realizar modificações por meio de requisições POST/PUT/DELETE (mutações), o cache local torna-se obsoleto.

> **Mutações pertencem ao MaxPinia.** Criar/editar/excluir dados de página é responsabilidade de uma store `@maxvue/max-pinia`, que faz o auto-save (debounced) e revalida o estado. O `useRefCachedApi` cobre apenas leituras pontuais (GET com cache) fora do fluxo de store.

* **Atualizações automáticas via watch**: Se `watch: true` (padrão), modificar diretamente o `list.value` irá salvá-lo de volta no `localStorage` — útil apenas para o cache local de leitura.
* **Quando precisar revalidar**: deixe a store MaxPinia disparar a mutação e a releitura. O padrão abaixo (POST manual) só se justifica em integrações fora do domínio de página gerenciado pela store:
  ```typescript
  const addClient = async (newClient: ClientInput) => {
    const freshClient = await apiPostRoute('clients.save', newClient);
    if (freshClient) {
      clients.value = [...clients.value, freshClient];
    }
  };
  ```

### 5. Serialização Segura
Se os dados contiverem objetos complexos, garanta que sejam serializáveis antes de colocá-los no ref (sem referências circulares, métodos ou objetos Vue Raw). Use `JSON.parse(JSON.stringify(value))` se for necessário limpar, embora o composable faça isso internamente na resposta da API.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use a Options API em arquivos `.vue`. Use `<script setup lang="ts">`; a estilização deve usar UnoCSS attributify (`presetMaxUno`) com tokens de tema — sem Tailwind cru e sem SCSS ad-hoc.
- **NÃO** assuma que `options.key` mudará reativamente os escopos de cache se passar um wrapper reativo diretamente. Use o padrão de `watch` manual para caches dependentes de contexto/tenant.
- **NÃO** omita o `defaultValue` a menos que a interface de usuário seja completamente ocultada durante o carregamento e a assinatura de tipo contemple `null`.
- **NÃO** quebre os atributos do template Vue em várias linhas. Mantenha as tags declaradas em linha única (inline).
- Comentários dentro de arquivos Vue e stores do Pinia devem ser escritos em **Português do Brasil (pt-BR)**.
