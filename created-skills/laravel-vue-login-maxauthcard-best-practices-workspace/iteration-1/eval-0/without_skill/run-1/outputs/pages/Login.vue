<script setup lang="ts">
// pages/Login.vue
//
// Tela de login do Maxdmin usando o MaxAuthCard (@maxvue/max-components-ui).
// Liga o componente na store de autenticação (MaxPinia) e dispara a action de login.

import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { MaxAuthCard } from '@maxvue/max-components-ui'
import { useToggle } from '@maxvue/max-use'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

// useToggle do MaxUse para o estado do "lembrar-me".
const [remember, toggleRemember] = useToggle(false)

const form = reactive({
  login: '', // aceita e-mail OU telefone
  password: '',
})

async function handleSubmit() {
  try {
    await auth.login({
      login: form.login,
      password: form.password,
      remember: remember.value,
    })
    // Sessão criada no Laravel; segue para o destino pós-login.
    router.push({ name: 'dashboard' })
  } catch {
    // Erros já populados em auth.errors e renderizados pelo MaxAuthCard.
  }
}

function handleSocial(provider: 'google' | 'facebook') {
  auth.loginWith(provider)
}
</script>

<template>
  <div class="login-page">
    <MaxAuthCard
      title="Entrar no Maxdmin"
      subtitle="Use seu e-mail ou telefone"
      :loading="auth.loading"
      :errors="auth.errors"
      @submit="handleSubmit"
    >
      <!-- Campo único: e-mail ou telefone -->
      <MaxAuthCard.Field
        v-model="form.login"
        name="login"
        label="E-mail ou telefone"
        type="text"
        autocomplete="username"
        :error="auth.errors.login"
        required
      />

      <MaxAuthCard.Field
        v-model="form.password"
        name="password"
        label="Senha"
        type="password"
        autocomplete="current-password"
        :error="auth.errors.password"
        required
      />

      <MaxAuthCard.Checkbox
        :model-value="remember"
        name="remember"
        label="Lembrar-me"
        @update:model-value="toggleRemember"
      />

      <template #actions>
        <MaxAuthCard.SubmitButton :loading="auth.loading">
          Entrar
        </MaxAuthCard.SubmitButton>
      </template>

      <!-- Login social -->
      <template #social>
        <MaxAuthCard.SocialButton
          provider="google"
          @click="handleSocial('google')"
        >
          Entrar com Google
        </MaxAuthCard.SocialButton>

        <MaxAuthCard.SocialButton
          provider="facebook"
          @click="handleSocial('facebook')"
        >
          Entrar com Facebook
        </MaxAuthCard.SocialButton>
      </template>
    </MaxAuthCard>
  </div>
</template>

<style scoped>
.login-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
}
</style>
