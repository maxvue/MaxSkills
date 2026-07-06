---
name: vue-axios-api-integration-best-practices
description: "Use ao integrar o front Vue 3 do EngeApp com a API Laravel via HTTP. Sem Axios direto: o transporte passa pelos helpers apiGetRoute/apiPostRoute/apiPutRoute/apiDeleteRoute do @maxvue/max-use, que recebem NOMES de rota Ziggy pontilhados e já aplicam headers e withCredentials. GET sempre via store MaxPinia. Sucesso retorna data; erro HTTP retorna null; nome de rota inexistente LANÇA exceção."
---

# Boas Práticas de Integração de API HTTP no Vue 3 (EngeApp)

## Objetivo
Padronizar como o front Vue 3 do EngeApp conversa com a API Laravel. **Neste projeto não existe uma camada de configuração global de Axios** (sem `axios.defaults`, sem interceptadores, sem `baseURL`, sem fluxo de `/sanctum/csrf-cookie`). Todo o transporte HTTP passa pelos helpers do `@maxvue/max-use`, que já encapsulam Axios com headers e credenciais corretos. O papel desta skill é ensinar a usar esses helpers e o contrato de retorno deles — não a reconfigurar Axios.

## Regras fundamentais

### 1. Todo GET ao backend passa por uma store MaxPinia
Nunca faça `axios.get` (ou `apiGetRoute`) direto em um componente. GETs de leitura vão para uma store MaxPinia com `isCached = true` e `options.get.route` apontando para o NOME da rota Ziggy. A store cuida de cache, deduplicação e `status.server.get.is_requested/is_success`. Isso evita requisições repetidas e mantém o estado consistente entre telas.

### 2. Mutações (POST/PUT/DELETE) usam os helpers do @maxvue/max-use
Para enviar formulários e alterar estado no backend, use `apiPostRoute`, `apiPutRoute` ou `apiDeleteRoute`. Eles executam o Axios internamente e retornam `response.data` em sucesso. Não instancie Axios nem chame `axios.post` cru — você perderia os headers e o `withCredentials` que os helpers já injetam.

### 3. Rotas são NOMES Ziggy pontilhados, nunca strings de path
O primeiro argumento dos helpers é o **nome** da rota (ex.: `'login'`, `'social.providers'`, `'profile.update'`, `'planner.card.add.task'`), não um path como `'/api/login'`. O resolvedor é configurado uma única vez em `resources/app.ts` via `setRouteResolver((name, params) => { try { return route(name, params); } catch { return null; } })` (Ziggy). Se você passar um nome que não existe, o resolver Ziggy lança, o wrapper acima devolve `null` e, internamente, `resolveRoute` faz `throw new Error('Rota "…" não encontrada pelo resolver.')`. **Esse throw NÃO é engolido**: em `apiRoute` a resolução acontece fora do `try/catch` do helper, então a exceção **propaga para o seu código** (veja a Regra 4). Ou seja, nome inexistente é um erro de programação que estoura, não um `false` silencioso.

### 4. Contrato de retorno dos helpers — e quando eles LANÇAM
Contrato real de `apiPostRoute`/`apiPutRoute`/`apiDeleteRoute`, em `@maxvue/max-use`:
- **Sucesso** → retorna `response.data`.
- **`RouteName` vazio/`null`** → retorna `false` **antes** de qualquer requisição (a guarda `if (!system_options) return false`, que só dispara quando o nome é falsy). Não confunda: isso é "nome ausente", não "nome inexistente".
- **Nome truthy, mas inexistente no Ziggy** → o helper **lança exceção** (o `throw` de `resolveRoute` propaga, pois a resolução ocorre fora do `try/catch` interno). Se o nome puder vir errado, **envolva a chamada em `try/catch`**.
- **Erro HTTP (401/403/422/500) ou de rede** → o helper faz `console.error` e retorna `null`.

Atenção: `apiGetRoute` **não tem** a guarda de `false` — nome falsy nele cai no `catch` e vira `null`; nome inexistente também lança. Como GET no projeto vai sempre via store MaxPinia (Regra 1), isso raramente aparece no seu código.

Portanto, para as mutações: **ramifique pelo valor de retorno** (`response.data` = ok; `null`/`false` = falha, mostre mensagem ao usuário) **e** proteja-se do `throw` de rota inexistente com `try/catch` quando o nome não for uma constante confiável. Não há interceptador global de resposta. Erros de validação 422 detalhados (`{ message, errors }`) **não** chegam ao chamador — o helper os engole no `null`. Se um formulário precisar do corpo do 422, esse endpoint teria de usar `axios.post` direto (exceção pontual, hoje não usada no projeto).

### 5. Headers e credenciais já são responsabilidade dos helpers
Não configure `Accept`, `Content-Type`, `X-Requested-With` nem `withCredentials` manualmente para chamadas normais. `apiPostRoute` já envia esses headers, mescla `getConfiguredHeaders()` e usa `withCredentials` (padrão `true`, definido em `@maxvue/max-use`). A autenticação é por sessão + cookie; não anexe `Authorization: Bearer` para chamadas de API comuns.

### 6. CSRF manual só para widgets de upload de terceiros
O único lugar onde um token CSRF é anexado à mão é a configuração de bibliotecas externas de upload (ex.: VueFinder), onde se passa `'XSRF-TOKEN': system.token` / `'X-CSRF-TOKEN': system.token` e `baseUrl: system.base_url`, lendo do store `useSystemStore` (`token`, `base_url`). Isso é exceção para libs que fazem seu próprio HTTP — **não** é o fluxo das chamadas de API do app.

## Exemplo real — login (POST de mutação)

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

    // 'login' é um nome de rota constante e válido, então aqui basta ramificar pelo retorno:
    // sucesso = response.data (truthy); erro HTTP/rede = null; nome vazio = false.
    // (Se o nome pudesse vir errado/inexistente, seria preciso try/catch — o helper LANÇA nesse caso.)
    if (result_api) location.reload();
    else {
        showToast('Não foi possível realizar o login. <br>Verifique os dados e tente novamente.', 'error');
        error.value = 'Usuário ou senha inválidos.';
    }

    loading.value = false;
};
```

## Restrições
- **Idioma:** comunique-se com o usuário humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
- **GET ao backend NUNCA via Axios direto** em componentes ou serviços — sempre store MaxPinia com `isCached = true` e `options.get`.
- **NÃO** configure `axios.defaults`, `baseURL`, interceptadores globais nem fluxo `/sanctum/csrf-cookie`: nada disso existe neste projeto e não deve ser introduzido para chamadas de API.
- **NÃO** passe strings de path (`'/api/...'`) para os helpers — apenas NOMES de rota Ziggy pontilhados.
- **Ramifique o fluxo pelo retorno** (`response.data` = ok; `null`/`false` = falha), **mas** lembre que um nome de rota inexistente **LANÇA** exceção (o `throw` de `resolveRoute` propaga); envolva em `try/catch` quando o nome não for uma constante confiável.
- **NÃO** anexe headers de auth/CSRF manualmente em chamadas de API comuns — só para widgets de upload de terceiros, lendo de `useSystemStore`.
- **NÃO** exponha erros brutos do backend ao usuário final; exiba mensagens limpas via `showToast` / `Toast.show` do `@maxvue/max-components-ui`.
