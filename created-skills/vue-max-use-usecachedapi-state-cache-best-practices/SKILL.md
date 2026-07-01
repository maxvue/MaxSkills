---
name: vue-max-use-usecachedapi-state-cache-best-practices
description: Use when implementing, reviewing, or debugging Vue 3 frontend code utilizing the useRefCachedApi (or useCachedApi, useSharedCacheApi, useInCacheApi) composable from @maxvue/max-use to cache API GET requests in localStorage and synchronize them in the background. Triggers on files containing these composables, managing stale-while-revalidate states, dynamic cache keys, loading indicators, type definitions, and cache invalidation.
---

## Objetivo
Otimizar o gerenciamento de estado do frontend Vue 3 utilizando o `useRefCachedApi` (e seus aliases `useCachedApi`, `useSharedCacheApi`, `useInCacheApi`) da biblioteca `@maxvue/max-use` para armazenar e carregar dados de requisições GET do `localStorage` de forma síncrona na montagem, e de forma transparente buscar dados atualizados da API em segundo plano.

## Instruções

## 1. Assinatura do Composable & Opções
O composable é importado de `@maxvue/max-use` e possui a seguinte assinatura:
```typescript
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
): Ref<T>
```
* **`route_name`**: O caminho do endpoint, sempre como string `/api/...` (ex.: `'/api/clients'`), resolvido pelos helpers do `@maxvue/max-use`. **Não existe Ziggy / `route()`** — use exclusivamente caminhos string. Lembre-se: para GET de dados de página, prefira uma store `@maxvue/max-pinia` (todo GET deve passar por store); use `useRefCachedApi` apenas em casos pontuais.
* **`options.defaultValue`**: Crucial para evitar erros de renderização inicial (ex: `defaultValue: []` para listas). Sempre forneça um valor padrão compatível com o tipo.
* **`options.key`**: Chave personalizada do `localStorage` (padrão: `route_name`). Necessária ao fazer cache de dados para diferentes escopos de contexto (como tenants ou clientes).
* **`options.sync`**: Padrão é `true`. Se definido como `false`, não executará a requisição GET da API em segundo plano automaticamente na criação.
* **`options.watch`**: Padrão é `true`. Se `true`, qualquer alteração no `Ref` retornado será monitorada e persistida automaticamente de volta no `localStorage`.

## 2. Boas Práticas para Vue 3 SFC & TypeScript
Ao utilizar `useRefCachedApi` em um arquivo `.vue` ou store do Pinia, você deve aderir às seguintes regras:
* **Sempre Forneça `defaultValue`**: Omitir ou definir como array/objeto vazio evita erros de referência nula (`null`) no render do template antes que o cache ou a API retornem dados:
  ```typescript
  const clients = useRefCachedApi<Client[]>('/api/clients', { defaultValue: [] });
  ```
* **Tipos do TypeScript**: Defina explicitamente o parâmetro genérico `<T>` para que os templates Vue e as propriedades computadas tenham verificação de tipo precisa.
* **Composition API**: Deve-se utilizar `<script setup lang="ts">`. O uso de Options API é estritamente proibido.
* **Atributos de Elementos HTML em Linha Única**: No bloco `<template>`, formate os elementos em linha (mantenha todos os atributos na mesma linha, sem quebras de linha múltiplas).

## 3. Chaves de Cache Dinâmicas e Isolamento (Multi-tenant/Cliente)
Como o `useRefCachedApi` avalia a opção `key` apenas uma vez no momento da criação (não reativamente), se o tenant ou cliente ativo mudar, você deve gerenciar manualmente o carregamento e a atualização do cache dentro de um `watch`:
* **Incorreto (Avaliação estática de valor dinâmico)**:
  ```typescript
  // RUIM: options.key é avaliado apenas uma vez; se selectedClient.id mudar, a chave e o cache NÃO são atualizados.
  const list = useRefCachedApi<Data[]>('/api/data', { 
    key: `data::${selectedClient.id}`,
    defaultValue: [] 
  });
  ```
* **Correto (Troca de cache manual via Watch)**:
  ```typescript
  const list = useRefCachedApi<Data[]>('/api/data', { 
    defaultValue: [],
    sync: false // Desativa a sincronização automática na criação
  });

  watch(
    () => selectedClient.id,
    (newId) => {
      if (!newId) {
        list.value = [];
        return;
      }
      const cacheKey = `data::${newId}`;
      const localData = localStorage.getItem(cacheKey);
      
      // 1. Carrega instantaneamente do cache, se disponível
      list.value = localData ? JSON.parse(localData) : [];

      // 2. Busca dados novos da API em segundo plano e atualiza o cache
      apiGetRoute('/api/data', { client_id: newId }).then((data) => {
        if (data) {
          list.value = data;
          localStorage.setItem(cacheKey, JSON.stringify(data));
        }
      });
    },
    { immediate: true }
  );
  ```

## 4. Invalidação de Cache e Atualizações Pós-Mutação
Ao realizar modificações por meio de requisições POST/PUT/DELETE (mutações), o cache local torna-se obsoleto.

> **Mutações pertencem ao MaxPinia.** Criar/editar/excluir dados de página é responsabilidade de uma store `@maxvue/max-pinia`, que faz o auto-save (debounced) e revalida o estado. NÃO escreva `apiPostRoute`/`apiPutRoute` manuais nem manipule `localStorage` à mão para persistir mutações. Altere o estado da store e o salvamento ocorre automaticamente. O `useRefCachedApi` cobre apenas leituras pontuais (GET com cache) fora do fluxo de store.

* **Atualizações automáticas via watch**: Se `watch: true` (padrão), modificar diretamente o `list.value` irá salvá-lo de volta no `localStorage` — útil apenas para o cache local de leitura.
* **Quando precisar revalidar**: deixe a store MaxPinia disparar a mutação e a releitura. O padrão abaixo (POST manual) é desencorajado e só se justifica em integrações fora do domínio de página gerenciado pela store:
  ```typescript
  // Evite: prefira mutar a store @maxvue/max-pinia, que salva automaticamente.
  const addClient = async (newClient: ClientInput) => {
    const freshClient = await apiPostRoute('/api/clients', newClient);
    if (freshClient) {
      clients.value = [...clients.value, freshClient];
    }
  };
  ```

## 5. Serialização Segura
Se os dados contiverem objetos complexos, garanta que sejam serializáveis antes de colocá-los no ref (sem referências circulares, métodos ou objetos Vue Raw). Use `JSON.parse(JSON.stringify(value))` se for necessário limpar, embora o composable faça isso internamente na resposta da API.

## Restrições
- **NÃO** use a Options API em arquivos `.vue`. Use `<script setup lang="ts">` e SCSS para estilização.
- **NÃO** assuma que `options.key` mudará reativamente os escopos de cache se passar um wrapper reativo diretamente. Use o padrão de `watch` manual para caches dependentes de contexto/tenant.
- **NÃO** omita o `defaultValue` a menos que a interface de usuário seja completamente ocultada durante o carregamento e a assinatura de tipo contemple `null`.
- **NÃO** quebre os atributos do template Vue em várias linhas. Mantenha as tags declaradas em linha única (inline).
- Comentários dentro de arquivos Vue e stores do Pinia devem ser escritos em **Português do Brasil (pt-BR)**.
