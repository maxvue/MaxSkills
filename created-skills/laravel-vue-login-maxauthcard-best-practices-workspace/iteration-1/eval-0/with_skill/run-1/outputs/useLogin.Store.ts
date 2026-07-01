// resources/Stores/UserStores/useLogin.Store.ts
//
// Store de LOGIN. O login é a exceção deliberada ao padrão MaxPinia: não é
// "estado de página", é uma transição de autenticação (um POST pontual). Por
// isso usa apiPostRoute do MaxUse com NOME de rota Ziggy ('login'), e NÃO uma
// store MaxPinia com get/save. Depois do login, o usuário atual (user.data)
// passa a ser estado de página e vem da store MaxPinia useUserStore.
//
// apiPostRoute / apiGetRoute / route / defineStore / ref / computed / watch
// são auto-importados (unplugin-auto-import). Sem auto-import, importe:
//   import { defineStore } from 'pinia';
//   import { ref, computed, watch } from 'vue';
//   import { apiPostRoute, apiGetRoute } from '@maxvue/max-use';
//   import { route } from 'ziggy-js';

interface ProviderBtn {
  id: string;
  label: string;
  icon: string;
  class?: string;
}

// Mapa visual dos provedores suportados. O backend devolve só os ids
// habilitados (com credenciais); aqui transformamos em botões para o card.
const PROVIDER_MAP: Record<string, Omit<ProviderBtn, 'id'>> = {
  google: { label: 'Google', icon: 'mdi:google', class: 'btn-google' },
  facebook: { label: 'Facebook', icon: 'mdi:facebook', class: 'btn-facebook' },
};

export const useLoginStore = defineStore('login', () => {
  const loading = ref(false);
  const value = ref(''); // campo único do card: e-mail OU telefone
  const method = ref<'email' | 'phone'>('email');
  const password = ref('');
  const remember = ref(true); // "lembrar-me" ligado por padrão
  const error = ref('');
  const providers = ref<ProviderBtn[]>([]);

  // Detecta e-mail vs telefone pelo conteúdo do campo único.
  // Se tiver '@' -> e-mail; se só restarem dígitos/símbolos de telefone -> phone.
  watch(value, (v) => {
    const semDigitos = v.replace(/[0-9()\-\s+]/g, '');
    if (v.includes('@') && semDigitos.length > 0) method.value = 'email';
    else if (semDigitos.length === 0 && v.length > 0) method.value = 'phone';
  });

  // Deriva os dois campos que o backend (LoginRequest) espera. Quando o método
  // for telefone, manda um e-mail-sentinela para não falhar a validação 'email'.
  const email = computed(() =>
    method.value === 'email' ? value.value : 'undefined@enge.tec.br',
  );
  const phone_number = computed(() =>
    method.value === 'phone' ? value.value : '',
  );

  // AÇÃO DE LOGIN — POST pontual via MaxUse com nome de rota Ziggy.
  // apiPostRoute resolve o nome 'login' via route() do Ziggy e JÁ executa a
  // requisição (não embrulhar em axios; não passar URL crua).
  const submit = async () => {
    if (loading.value) return;
    loading.value = true;
    error.value = '';

    const result = await apiPostRoute('login', {
      method: method.value,
      email: email.value,
      phone_number: phone_number.value,
      password: password.value,
      remember: remember.value,
    });

    if (result) {
      // Sucesso: recarrega a página. O boot reidrata a store MaxPinia useUser
      // e o guard do router faz o redirecionamento para a área autenticada.
      location.reload();
    } else {
      error.value = 'Usuário ou senha inválidos.';
      setTimeout(() => (error.value = ''), 4000);
    }
    loading.value = false;
  };

  // LOGIN SOCIAL — navegação total do navegador (NÃO é XHR). O OAuth precisa de
  // um redirect real; resolvemos a rota Laravel pelo nome Ziggy 'social.redirect'.
  const social = (provider: string) => {
    window.location.href = route('social.redirect', { provider });
  };

  // Carrega os provedores habilitados no backend e monta os botões do card.
  const loadProviders = async () => {
    const ids: string[] | null = await apiGetRoute('social.providers');
    providers.value = (ids ?? [])
      .filter((id) => PROVIDER_MAP[id])
      .map((id) => ({ id, ...PROVIDER_MAP[id] }));
  };

  return {
    loading,
    value,
    password,
    remember,
    error,
    providers,
    submit,
    social,
    loadProviders,
  };
});
