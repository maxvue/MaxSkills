// resources/Stores/UserStores/useUser.Store.ts
//
// Store MaxPinia do usuário atual ("me").
//
// O "me" é ESTADO DE PÁGINA -> ele DEVE vir de uma store MaxPinia configurada
// por NOME de rota Ziggy (`user.data`), nunca de um `axios.get` solto. Assim o
// MaxPinia cuida do cache, do auto-save e — o ponto crítico aqui — expõe o status
// da 1ª requisição de sessão para o guard do router.
//
// O bug clássico ("recarreguei a página e o guard achou que não estava logado")
// acontece quando o guard lê `user.data?.id` ANTES do GET de `user.data` terminar.
// No primeiro paint a store ainda está vazia, então o guard conclui "não logado"
// e chuta o usuário para /login. A solução é `waitRequest()`: o guard espera a
// 1ª busca concluir antes de decidir. Veja o guard em router.ts.

import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

export interface User {
  id: string;
  name: string;
  email: string;
  phone_number?: string | null;
  // ... demais campos do usuário
}

export const useUserStore = defineStore('user', () => {
  // Estado da sessão. Começa null; o MaxPinia preenche após o GET de `user.data`.
  const data = ref<User | null>(null);

  // Mantém o cache entre navegações (não refaz o GET a cada rota).
  const isCached = ref(true);

  // Contrato MaxPinia: GET por nome de rota Ziggy + auto-save ao alterar `data`.
  // `key` é o identificador do cache local.
  const options = computed(() => ({
    get: { route: 'user.data' }, // nome Ziggy; MaxPinia executa o GET
    save: 'user.save', // auto-save quando `data` muda
    key: 'user',
  }));

  /**
   * Resolve quando a 1ª busca de sessão concluir.
   *
   * É a peça que elimina a race condition no reload da página: o guard chama
   * `await user.waitRequest()` e só então lê `user.data?.id`. Sem isto, num F5
   * o guard avaliaria a store ainda vazia e redirecionaria para /login mesmo
   * com o usuário autenticado no backend.
   *
   * `status` é injetado pelo MaxPinia na instância da store. Por isso lemos
   * SEMPRE via `this` aqui dentro (o método é chamado como `user.waitRequest()`),
   * e nunca via `this` fora dos métodos da store.
   */
  function waitRequest(this: any): Promise<void> {
    return new Promise((resolve) => {
      // Já buscou? Resolve imediatamente (navegações seguintes não esperam de novo).
      if (this?.status?.server?.get?.is_requested) return resolve();

      // Ainda não buscou: observa o flag e resolve assim que virar true.
      const stop = watch(
        () => this?.status?.server?.get?.is_requested,
        (done) => {
          if (done) {
            stop();
            resolve();
          }
        },
      );
    });
  }

  return { data, isCached, options, waitRequest };
});
