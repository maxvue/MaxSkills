<template>
  <!--
    MaxAuthCard é puramente VISUAL: só renderiza inputs/botões e emite eventos.
    Nenhuma lógica de HTTP/store vive aqui — tudo fica na store useLoginStore.

    - v-model:email   -> campo único (e-mail OU telefone). A store detecta o método.
    - v-model:password / v-model:remember -> credenciais e "lembrar-me".
    - :providers      -> array de botões sociais; vazio = seção social oculta.
    - :loading/:error -> estado do botão de submit e mensagem de erro.
    - @submit         -> dispara o POST de login (store.submit).
    - @social         -> redireciona o navegador para o OAuth (store.social).
  -->
  <MaxAuthCard
    title="Maxdmin"
    subtitle="Acesse sua conta"
    icon="mdi:shield-account-outline"
    :loading="login.loading"
    :error="login.error"
    v-model:email="login.value"
    v-model:password="login.password"
    v-model:remember="login.remember"
    :providers="login.providers"
    :register-to="{ name: 'register' }"
    :forgot-to="{ name: 'password.request' }"
    @submit="login.submit"
    @social="login.social"
  />
</template>

<script setup lang="ts">
  // useLoginStore é auto-importado (unplugin-auto-import); MaxAuthCard é
  // auto-registrado (unplugin-vue-components). Se o seu setup não usar
  // auto-import, adicione:
  //   import { onMounted } from 'vue';
  //   import { useLoginStore } from '@/Stores/UserStores/useLogin.Store';
  //   import MaxAuthCard from '@maxvue/max-components-ui';
  const login = useLoginStore();

  // Carrega a lista de provedores sociais habilitados no backend e monta
  // os botões (Google/Facebook) só para os que têm credenciais configuradas.
  onMounted(login.loadProviders);
</script>
