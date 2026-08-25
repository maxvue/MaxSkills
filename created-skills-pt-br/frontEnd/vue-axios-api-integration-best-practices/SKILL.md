---
name: vue-axios-api-integration-best-practices
description: "Use when integrating Vue 3 front-end with Laravel API via apiGetRoute/apiPostRoute/apiPutRoute/apiDeleteRoute from @maxvue/max-use, Ziggy named routes with credentials, and MaxPinia stores."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Integração de API HTTP no Vue 3 (EngeApp)

## Objetivo
Padronizar como o front Vue 3 do EngeApp conversa com a API Laravel. **Neste projeto não existe uma camada de configuração global de Axios** (sem `axios.defaults`, sem interceptadores, sem `baseURL`, sem fluxo de `/sanctum/csrf-cookie`). Todo o transporte HTTP passa pelos helpers do `@maxvue/max-use`, que já encapsulam Axios com headers e credenciais corretos. O papel desta skill é ensinar a usar esses helpers e o contrato de retorno deles — não a reconfigurar Axios.

## Instruções

### Regras fundamentais

### 1. Todo GET ao backend passa por uma store MaxPinia
Nunca faça `axios.get` (ou `apiGetRoute`) direto em um componente. GETs de leitura vão para uma store MaxPinia com `isCached = true` e `options.get.route` apontando para o NOME da rota Ziggy. A store cuida de cache, deduplicação e `status.server.get.is_requested/is_success`. Isso evita requisições repetidas e mantém o estado consistente entre telas.

### 2. Mutações (POST/PUT/DELETE) usam os helpers do @maxvue/max-use
Para enviar formulários e alterar estado no backend, use `apiPostRoute`, `apiPutRoute` ou `apiDeleteRoute`. Eles executam o Axios internamente e retornam `response.data` em sucesso. Não instancie Axios nem chame `axios.post` cru — você perderia os headers e o `withCredentials` que os helpers já injetam.

### 3. Rotas são NOMES Ziggy pontilhados, nunca strings de path
O primeiro argumento dos helpers é o **nome** da rota (ex.: `'login'`, `'social.providers'`, `'profile.update'`, `'planner.card.add.task'`), não um path como `'/api/login'`. O resolvedor é configurado uma única vez em `resources/app.ts`:

```typescript
setRouteResolver((name: string, params?: any) => {
    try {
        const url: string = route(name, params);

        // O Ziggy devolve URL absoluta. O goToRoute() do MaxUse repassa esse valor
        // ao router.push(), que trata string como path relativo e duplica o domínio
        // (ex.: /https://dominio/settings). Reduz para path quando for a mesma origem.
        const origin = typeof window !== 'undefined' ? window.location.origin : '';
        return origin && url.startsWith(origin) ? (url.slice(origin.length) || '/') : url;
    } catch {
        return null;
    }
});
```

Não simplifique esse resolvedor: sem a normalização de origem, `goToRoute()` receberia a URL absoluta do Ziggy e a duplicaria ao repassá-la para `router.push()`. Nome inexistente continua caindo no `catch` → `null`, do ponto de vista do resolver — o comportamento para o chamador dos helpers está detalhado na Regra 4.

### 4. Contrato de retorno dos helpers — e quando eles LANÇAM
Contrato real dos helpers de mutação (ver Regra 2), em `@maxvue/max-use`:
- **Sucesso** → retorna `response.data`.
- **`RouteName` vazio/`null`** → retorna `false` **antes** de qualquer requisição (a guarda `if (!system_options) return false`, que só dispara quando o nome é falsy). Isso é "nome ausente", não "nome inexistente".
- **Nome truthy, mas inexistente no Ziggy** → o resolver Ziggy lança e, internamente, `resolveRoute` faz `throw new Error('Rota "…" não encontrada pelo resolver.')`. Esse throw **NÃO é engolido**: em `apiRoute` a resolução acontece fora do `try/catch` do helper, então a exceção **propaga para o seu código**. Ou seja, nome inexistente é um erro de programação que estoura, não um `false` silencioso. Se o nome puder vir errado, **envolva a chamada em `try/catch`**.
- **Erro HTTP (401/403/422/500) ou de rede** → o helper faz `console.error` e retorna `null`.

Atenção: `apiGetRoute` **não tem** a guarda de `false` — nome falsy nele faz `apiRoute` retornar `null`, e no caminho default (sem `options.error === false`) o `catch` interno desreferencia esse `null` de novo ao montar a mensagem de erro (`system_options.routeURL`), produzindo um segundo `TypeError` **não capturado** que propaga para o chamador. Só quando o chamador passa `options.error === false` esse segundo throw é evitado e a função retorna `null` de fato. Nome inexistente também lança. Como GET no projeto vai sempre via store MaxPinia (Regra 1), isso raramente aparece no seu código.

Portanto, para as mutações: **ramifique pelo valor de retorno** (`response.data` = ok; `null`/`false` = falha, mostre mensagem ao usuário) **e** proteja-se do `throw` de rota inexistente com `try/catch` quando o nome não for uma constante confiável. Não há interceptador global de resposta. Erros de validação 422 detalhados (`{ message, errors }`) **não** chegam ao chamador — o helper os engole no `null`. Se um formulário precisar do corpo do 422, esse endpoint teria de usar `axios.post` direto. Isso não é apenas teórico: `axios.get`/`axios.post` direto aparecem hoje dezenas de vezes no código do engeapp (ex.: `ArtisanPage.vue`, `PublicationsPage.vue`, `PromotionsPage.vue`), inclusive com paths crus `'/api/...'`. A regra desta skill é a convenção-alvo a seguir em código novo — não presuma que o código existente já está isolado disso.

### 5. Headers e credenciais já são responsabilidade dos helpers
Não configure `Accept`, `Content-Type`, `X-Requested-With` nem `withCredentials` manualmente para chamadas normais. `apiPostRoute` já envia esses headers, mescla `getConfiguredHeaders()` e usa `withCredentials` (padrão `true`, definido em `@maxvue/max-use`). A autenticação é por sessão + cookie; não anexe `Authorization: Bearer` para chamadas de API comuns.

### 6. CSRF manual só para widgets de upload de terceiros
O único lugar onde um token CSRF é anexado à mão é a configuração de bibliotecas externas de upload (ex.: VueFinder), onde se passa `'XSRF-TOKEN': system.token` / `'X-CSRF-TOKEN': system.token` e `baseUrl: system.base_url + '/normas/files'` (subpath concatenado, não o `base_url` puro), lendo do store `useSystemStore` (`token`, `base_url`). Isso é exceção para libs que fazem seu próprio HTTP — **não** é o fluxo das chamadas de API do app.

### Exemplo real — login (POST de mutação)

Trecho fiel a `resources/Stores/UserStores/useLogin.Store.ts`. O login é um POST via `apiPostRoute` usando o nome de rota `'login'`; em sucesso a página é recarregada (`location.reload()`), em falha exibe-se um toast. Note: sem `csrf-cookie`, sem `router.push`, sem `axios`.

```typescript
// Submete o formulário de login.
const submit = async () => {
    loading.value = true;
    error.value = '';

    // NOME de rota Ziggy 'login' (não um path '/api/login').
    const result_api = await apiPostRoute('login', {
        method: method.value,
        email: email.value,
        password: password.value,
        remember: remember.value,
        phone_number: phone_number.value
    });

    // 'login' é um nome de rota constante e válido, então aqui basta ramificar pelo retorno (ver Regra 4).
    if (result_api) location.reload();
    else {
        toast('Não foi possível realizar o login. <br>Verifique os dados e tente novamente.', { type: 'error', dangerouslyHTMLString: true });
        error.value = 'Usuário ou senha inválidos.';
    }

    loading.value = false;
};
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** comunique-se com o usuário humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
- **NÃO** configure `axios.defaults`, `baseURL`, interceptadores globais nem fluxo `/sanctum/csrf-cookie`: nada disso existe neste projeto e não deve ser introduzido para chamadas de API.
- **NÃO** exponha erros brutos do backend ao usuário final; exiba mensagens limpas via `Toast.show({ title, message, severity: 'error' })` do `@maxvue/max-components-ui` (padrão MaxToast — ver skill `vue-toast-notifications-toastify-best-practices`). O `vue3-toastify` que aparece no trecho de `useLogin.Store.ts` acima é código legado; não replique em código novo.
