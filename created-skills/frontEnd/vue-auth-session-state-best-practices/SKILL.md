---
name: vue-auth-session-state-best-practices
description: "Use ao implementar, refatorar, revisar ou depurar autenticação por sessão + cookie no engeapp (Vue 3 + Vue Router): login por e-mail OU telefone na store useLogin (apiPostRoute), usuário atual na store useUser (@maxvue/max-pinia), login social por redirect Ziggy, guard de rotas com user.waitRequest e logout full-page em /logout. Triggers em stores de sessão, guard do router e view de Login."
---

## Objetivo
Padronizar o fluxo de autenticação por sessão (cookie) no frontend do engeapp: login via `apiPostRoute`, logout por navegação full-page, recuperação do usuário atual por store MaxPinia, login social por redirecionamento OAuth e guard de rotas no Vue Router. O backend é autenticação **por sessão + cookie**; não é token/Bearer. A sessão dura 30 dias quando `remember` estiver marcado.

## Endpoints reais (nome Ziggy → URI de backend)
As rotas deste projeto **não** têm prefixo `/api`. Use sempre o nome Ziggy, nunca a URI fixa.
- `login` (POST `/login_request`) — cria a sessão. Body real: `{ method, email, password, remember, phone_number }` (login por e-mail **ou** telefone — ver Seção 1).
- `user.data` (GET `/user/data`) — usuário atual ("me"), protegido por `auth`. Consumido pela store `useUser`.
- `user.save` (POST `/user/save`) — save da store `useUser`.
- `logout` (POST `/logout`) e `logout.post` (GET `/logout`) — encerram a sessão. **Na prática o app faz logout por navegação full-page** (`window.location.href = '/logout'`, GET), não por `apiPostRoute` — ver Seção 4.
- `social.providers` (GET `/auth/providers`) — retorna um **array de strings** (ids de provedor, ex.: `['google']`).
- `social.redirect` (GET `/auth/{provider}/redirect`) — inicia o login social; é uma navegação full-page do navegador.
- `social.callback` (GET `/auth/{provider}/callback`) — callback do provedor; ao autenticar, o backend faz `redirect('/')` (raiz = rota `board`), **não** para `/projects`.

> Os helpers `apiGetRoute` / `apiPostRoute` (`@maxvue/max-use`) recebem o **nome** Ziggy pontilhado (ex.: `apiGetRoute('social.providers')`, `apiPostRoute('login', payload)`) e **já executam** a requisição (retornam `response.data`, ou valor falsy em falha) — não os embrulhe em `axios`. Para links/navegação de página use rota nomeada do Vue Router; para gerar a **URL** de um redirect OAuth full-page use `route('social.redirect', { provider })` do Ziggy diretamente (Ziggy ESTÁ configurado). Autenticação é por **sessão + cookie** — não invente token/Bearer.

## Instruções

## 1. Store de login (`useLogin.Store.ts`)
A view de login não contém lógica: toda ela vive numa store MaxPinia dedicada. Faça a view apenas instanciar a store (`const login = useLoginStore()`) e delegar via `v-model`/eventos.
- O login é por **e-mail OU telefone**. Mantenha `value` (entrada única) e derive `email`/`phone_number` por computeds, detectando `method` num `watch(value)`: contém `@` → `email`; contém dígitos → `phone`; vazio → `''`. Quando `method === 'email'`, `phone_number` é `''`; quando é `'phone'`, `email` cai para um placeholder (`'undefined@enge.tec.br'`).
- `submit()` faz `apiPostRoute('login', { method, email, password, remember, phone_number })`. `apiPostRoute` retorna valor falsy em falha (não lança) — ramifique pelo retorno: em sucesso, `location.reload()` (recarrega para reidratar a sessão); em falha, exiba toast e mensagem de erro.
- Os provedores voltam do backend como **array de strings**. Mapeie-os por um `PROVIDER_MAP` local (`{ google: { label, icon, class }, facebook: {...} }`), filtrando os ids conhecidos: `ids.filter(id => PROVIDER_MAP[id]).map(id => ({ id, ...PROVIDER_MAP[id] }))`.
- `social(provider)` inicia o OAuth com navegação real: `window.location.href = route('social.redirect', { provider })`.
- `loadUrlError()` lê `?error=` da URL (o redirect social devolve códigos como `invalid_provider`, `oauth_failed`, `no_email`) e mostra a mensagem correspondente no card.

## 2. Store de sessão (`useUser.Store.ts`)
- O estado do usuário atual DEVE vir de uma store `@maxvue/max-pinia`, nunca de `axios.get` solto pelas views.
- Declare com Composition API e configure `options` com o nome de rota: `const options = computed(() => ({ get: { route: 'user.data' }, save: 'user.save', key: 'user' }))`. `isCached` habilita cache offline. Atenção: `options.key` é um campo herdado e **não** define a chave de cache do MaxPinia — a chave real é `getKey()` = `$id + '.' + (id ?? options.id ?? 'global')`. Mantenha o campo como está no código real, mas não confie nele como chave de cache.
- O MaxPinia injeta `status`, `reload()` e `clearAll()` na instância. Dentro da setup store, os métodos que precisam ler `status` usam `this` (a store é chamada como `user.waitRequest()`), pois `status` é injetado na instância, não é uma variável do closure.
- Exponha `waitRequest()` como **método da store** (retornado no `return`) que resolve quando a primeira requisição de sessão **concluir com sucesso** — observe `this?.status?.server?.get?.is_success` (é o sinal de "dados carregados"; `is_requested` resolveria antes de haver dados). Isso evita race conditions no guard do router ao recarregar a página.

## 3. CSRF e headers
- Este projeto **não** tem camada global de Axios (`axios.defaults`, interceptadores, `baseURL`) nem fluxo de `/sanctum/csrf-cookie`. Todo transporte HTTP das chamadas de app passa pelos helpers do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`), que já injetam headers e `withCredentials` — ver skill **`vue-axios-api-integration-best-practices`**. Não faça GET em `/sanctum/csrf-cookie` nem configure `withXSRFToken`: nada disso existe aqui.
- O token CSRF vem da meta tag `csrf-token` renderizada no blade (`resources/Views/site.blade.php`). Para chamadas normais de API, **não** anexe o header CSRF à mão — os helpers cuidam disso.
- O único lugar onde um token CSRF é anexado manualmente é a configuração de bibliotecas externas de upload (ex.: VueFinder), passando `'X-CSRF-TOKEN': system.token` e `withCredentials: true`, lendo de `useSystemStore` (`token`, `base_url`). É exceção para libs que fazem HTTP próprio — não é o fluxo do login nem das chamadas de API do app.

## 4. Encerramento de sessão (logout) e 401
- **Não existem interceptadores de Axios neste projeto** (não há handler global de `401/403/422/500`). Não invente um. A validação de sessão e o redirecionamento para o login são feitos pelo **guard do Vue Router** (Seção 5), que aguarda `user.waitRequest()` e redireciona quando `!user.data?.id`.
- **Logout real:** é uma **navegação full-page** para `/logout` (GET), disparada no menu do usuário (`resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue`): `window.location.href = '/logout'`. O backend encerra a sessão e redireciona. Não há `apiPostRoute('logout')` + `router.push` + `clearAll()` no código real; a navegação full-page já reidrata o estado ao recarregar a aplicação na tela de login.
- Orientação genérica (não é código existente no projeto): se algum dia for preciso reagir a um `401` de forma programática, prefira centralizar no guard/na store e limpar cache com `clearAll()` antes de redirecionar por rota nomeada, evitando loop na própria tela de login.

## 5. Proteção de Rotas com Vue Router Guard
- O guard real usa `router.beforeEach` e decide por `to.meta` (`public`, `requiresAuth`, com default `true`).
- Aguarde a validação inicial da sessão com `await user.waitRequest()` antes de decidir.
- Avalie autenticação pelos dados da store: `const isAuthenticated = !!user.data?.id`.
- Redirecione para `{ name: 'login' }` quando a rota exigir auth e o usuário não estiver autenticado; e usuários autenticados que caírem em `login` vão para `{ name: 'board' }` (a rota `board` é a raiz `/` — **não existe** rota `projects`).
- Guards de permissão de UX (ex.: rotas `integrador_*`, `menu_roles`, `menus_admin`) leem `user.data?.permissions` e redirecionam para `{ name: 'board' }` quando falta permissão. A segurança real fica no backend.

## 6. Estrutura da View de Login
- A view (`resources/Vue/Sections/Auth/Login.vue`) usa `<MaxAuthCard>` de `@maxvue/max-components-ui` com `identifier`, `v-model:email`/`:password`/`:remember`, `:providers`, `:forgot-to`/`:register-to` (objetos de rota/query) e eventos `@submit`/`@social` ligados aos métodos da store. Nada de `<input>`/`<button>` nativos.
- `onMounted` só dispara `login.loadProviders()` e `login.loadUrlError()`.
- Componentes chamados de forma linear (inline) no `<template>`; toda lógica em `<script setup lang="ts">`; estilos em `<style scoped lang="scss">`. Comentários em pt-BR.

## Restrições
- **Idioma:** comunique-se com o humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
- NUNCA use a Options API. Use `<script setup lang="ts">`.
- Não hardcode URIs `/api/...` nem caminhos fixos para navegação: use nomes Ziggy (`route()`, `apiGetRoute`/`apiPostRoute`) e rotas nomeadas do router (`router.push({ name: 'login' })`).
- Não consuma `/user/data` com `axios.get` solto — sempre pela store `useUser`.
- Não introduza token/Bearer; o modelo é sessão + cookie. Não configure `axios.defaults`, interceptadores nem fluxo `/sanctum/csrf-cookie` — nada disso existe no projeto.
- Não anexe headers de CSRF manualmente em chamadas normais de API (só em widgets de upload de terceiros, lendo de `useSystemStore`).
- Logout é navegação full-page para `/logout`; não o reescreva como POST via `apiPostRoute`.
- Sem camada `services/` no front; sem `vueuse`/`lodash`/PrimeVue crus (use `@maxvue/max-use` e `Max*`).

# Examples

### Exemplo 1: Store de sessão (`useUser.Store.ts`)
```typescript
// `status`, `reload()` e `clearAll()` são injetados pelo plugin MaxPinia na instância da store.
export const useUserStore = defineStore('user', () => {
    // Dados do usuário autenticado, vindos de GET user.data via MaxPinia
    const data: Ref<User | null> = ref(null);
    const isCached: Ref = ref(true);
    // route é o NOME Ziggy (não caminho); a store executa a requisição internamente.
    const options = computed(() => ({ get: { route: 'user.data' }, save: 'user.save', key: 'user' }));

    /**
     * Aguarda a primeira requisição de sessão concluir COM SUCESSO.
     * Evita race condition no guard do Vue Router ao recarregar a página.
     * Usa `this` porque `status` é injetado na instância pelo MaxPinia.
     */
    function waitRequest(this: any): Promise<void> {
        return new Promise((resolve) => {
            if (this?.status?.server?.get?.is_success) return resolve();

            const unwatch = watch(
                () => this?.status?.server?.get?.is_success,
                (isSuccess) => {
                    if (isSuccess) {
                        unwatch();
                        resolve();
                    }
                }
            );
        });
    }

    return { data, options, isCached, waitRequest };
});
```

### Exemplo 2: Store de login (`useLogin.Store.ts`)
```typescript
export const useLoginStore = defineStore('login', () => {
    const loading: Ref<boolean> = ref(false);
    const value: Ref<string> = ref('');   // entrada única: e-mail ou telefone
    const method: Ref<string> = ref('');
    const password: Ref<string> = ref('');
    const remember: Ref<boolean> = ref(true);
    const error: Ref<string> = ref('');

    // Provedores voltam do backend como array de strings; mapeados para o card.
    const PROVIDER_MAP: Record<string, { label: string; icon: string; class: string }> = {
        google:   { label: 'Google',   icon: 'mdi:google',   class: 'btn-google' },
        facebook: { label: 'Facebook', icon: 'mdi:facebook', class: 'btn-facebook' }
    };
    const providers: Ref<Array<{ id: string; label: string; icon: string; class: string }>> = ref([]);

    // Deriva e-mail/telefone a partir da entrada única
    const email = computed(() => (method.value === 'email' ? value.value : 'undefined@enge.tec.br'));
    const phone_number = computed(() => (method.value === 'phone' ? value.value : ''));

    // Detecta o método pela forma da entrada
    watch(value, () => {
        const current = value.value ?? '';
        if (current.includes('@')) method.value = 'email';
        else if (/[0-9]/.test(current)) method.value = 'phone';
        else if (current.length === 0) method.value = '';
    });

    // apiPostRoute executa o POST e retorna falsy em falha (não lança).
    const submit = async () => {
        loading.value = true;
        error.value = '';
        const result = await apiPostRoute('login', {
            method: method.value,
            email: email.value,
            password: password.value,
            remember: remember.value,
            phone_number: phone_number.value
        });

        if (result) location.reload();
        else {
            showToast('Não foi possível realizar o login. <br>Verifique os dados e tente novamente.', 'error');
            error.value = 'Usuário ou senha inválidos.';
        }
        loading.value = false;
    };

    const loadProviders = async () => {
        const ids = await apiGetRoute('social.providers'); // array de strings
        providers.value = (ids ?? [])
            .filter((id: string) => PROVIDER_MAP[id])
            .map((id: string) => ({ id, ...PROVIDER_MAP[id] }));
    };

    // Login social: navegação full-page; URL gerada pelo Ziggy.
    const social = (provider: string) => {
        window.location.href = route('social.redirect', { provider });
    };

    const SOCIAL_ERROR_MESSAGES: Record<string, string> = {
        invalid_provider: 'Provedor de login inválido.',
        oauth_failed: 'Não foi possível autenticar com o provedor. Tente novamente.',
        no_email: 'Sua conta social não forneceu um e-mail. Use e-mail e senha.'
    };
    const loadUrlError = () => {
        const code = new URLSearchParams(window.location.search).get('error');
        if (code && SOCIAL_ERROR_MESSAGES[code]) error.value = SOCIAL_ERROR_MESSAGES[code];
    };

    return { email, value, phone_number, method, password, remember, loading, error, submit, providers, loadProviders, social, loadUrlError };
});
```

### Exemplo 3: View de login (`Login.vue`)
```vue
<template>
    <div class="container-div-center-main-div">
        <MaxAuthCard identifier="email-phone" :loading="login.loading" :error="login.error" v-model:email="login.value" v-model:password="login.password" v-model:remember="login.remember" :providers="login.providers" :forgot-to="{ query: { sub_page: 'forgot-password' } }" :register-to="{ query: { sub_page: 'register' } }" @submit="login.submit" @social="login.social">
            <template #header>
                <div flex justify-center s100><Logo p /></div>
            </template>
        </MaxAuthCard>
    </div>
</template>

<script setup lang="ts">
    // A view não tem lógica: instancia a store e delega tudo.
    const login = useLoginStore();

    onMounted(() => {
        login.loadProviders();
        login.loadUrlError();
    });
</script>
```

### Exemplo 4: Guard do router e logout
```typescript
// Guard: aguarda a sessão e decide pela store MaxPinia.
router.beforeEach(async (to, from, next) => {
    const user = useUserStore();
    const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);
    await user.waitRequest();
    const isAuthenticated = !!user.data?.id;

    if (requiresAuth && !isAuthenticated) return next({ name: 'login' });
    if (to.name === 'login' && isAuthenticated) return next({ name: 'board' }); // raiz '/', não 'projects'
    next();
});

// Logout real (menu do usuário): navegação full-page, o backend encerra a sessão.
// Não há apiPostRoute('logout') nem router.push no código real.
function logout() {
    window.location.href = '/logout';
}
```
