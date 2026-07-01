// resources/Stores/UserStores/useUser.Store.ts
//
// Store do usuário atual ("me"). Diferente da store de login, o usuário ATUAL é
// estado de página -> store MaxPinia, configurada por NOME de rota Ziggy.
// O MaxPinia faz o GET automaticamente (get.route) e auto-save ao alterar `data`
// (save). É essa store que o guard do router lê para decidir autenticação.

interface User {
  id: string;
  name: string;
  email: string;
  phone_number?: string;
  // ... demais campos do seu User
}

export const useUserStore = defineStore('user', () => {
  const data = ref<User | null>(null);
  const isCached = ref(true);

  // MaxPinia: GET por nome de rota + auto-save. 'user.data'/'user.save' são as
  // rotas nomeadas do app (não as de auth.php).
  const options = computed(() => ({
    get: { route: 'user.data' }, // nome Ziggy; MaxPinia dispara o GET
    save: 'user.save', // auto-save ao alterar `data`
    key: 'user',
  }));

  // Resolve quando a 1ª busca de sessão concluir. Evita race condition no guard
  // logo após o reload pós-login (o guard espera por isto antes de checar o id).
  function waitRequest(this: any): Promise<void> {
    return new Promise((resolve) => {
      if (this?.status?.server?.get?.is_requested) return resolve();
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
