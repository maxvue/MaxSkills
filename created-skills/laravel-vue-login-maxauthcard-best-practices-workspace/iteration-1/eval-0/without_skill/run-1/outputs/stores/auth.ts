// stores/auth.ts
//
// Store de autenticação para o Maxdmin.
// Stack: Laravel 13 (backend) + Vue + MaxPinia (@maxvue/max-pinia) + Ziggy, sem Inertia.
//
// O MaxPinia usa rotas como STRINGS resolvidas via Ziggy (route()), faz GET automático
// no setup do store e auto-save (debounced) das mutações. Para fluxos imperativos como
// o login, usamos as actions explícitas do store (post) em cima das rotas Ziggy.

import { defineStore } from '@maxvue/max-pinia'
import { ref } from 'vue'
import { route } from 'ziggy-js'

export interface LoginCredentials {
  /** O usuário pode entrar com e-mail OU telefone neste mesmo campo. */
  login: string
  password: string
  remember: boolean
}

export interface AuthUser {
  id: number
  name: string
  email: string | null
  phone: string | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  // Erros por campo, no formato que o MaxAuthCard espera para exibir mensagens inline.
  const errors = ref<Record<string, string>>({})

  /**
   * Login com e-mail/telefone + senha.
   * Aponta para a rota nomeada do Laravel `login` (POST /login), resolvida via Ziggy.
   */
  async function login(credentials: LoginCredentials) {
    loading.value = true
    errors.value = {}

    try {
      // O store do MaxPinia expõe `.post(url, payload)` que já cuida de:
      //  - header X-Requested-With / Accept: application/json
      //  - cookie CSRF (XSRF-TOKEN) do Laravel
      //  - credentials: 'include' para a sessão
      const { data } = await this.post(route('login'), {
        login: credentials.login,
        password: credentials.password,
        remember: credentials.remember,
      })

      user.value = data.user
      return data
    } catch (err: any) {
      // Laravel devolve 422 com { message, errors: { campo: [msg] } }
      if (err?.status === 422 && err.body?.errors) {
        errors.value = Object.fromEntries(
          Object.entries(err.body.errors).map(([k, v]) => [k, (v as string[])[0]]),
        )
      } else {
        errors.value = { login: err?.body?.message ?? 'Não foi possível entrar.' }
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Login social. Como o OAuth exige um round-trip de browser (redirect),
   * navegamos para a rota de redirect do provider (Laravel Socialite).
   * Não é uma chamada AJAX.
   */
  function loginWith(provider: 'google' | 'facebook') {
    window.location.href = route('oauth.redirect', { provider })
  }

  async function logout() {
    await this.post(route('logout'))
    user.value = null
  }

  return { user, loading, errors, login, loginWith, logout }
})
