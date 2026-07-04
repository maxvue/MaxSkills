---
name: vue-axios-api-integration-best-practices
description: Use when configuring Axios instances, setting up CSRF cookies, handling global API errors (401, 403, 422, 500), managing request interception, or connecting Vue 3 Pinia stores with the backend API.
---

# Boas Práticas de Integração de API com Axios no Vue 3

## Objetivo
Estabelecer a configuração padrão e resiliente do cliente HTTP Axios no Vue 3. O Axios é usado para: configuração global (CSRF, interceptadores, baseURL), requisições POST/PUT/DELETE de formulários, e como transporte interno do `@maxvue/max-pinia`. **Requisições GET ao backend NUNCA devem ser feitas com Axios diretamente em componentes ou serviços — sempre use uma store MaxPinia com `isCached = true` e `options.get`.**

## Instruções

### 1. Configuração Global do Axios
Configure a instância global do Axios no ponto de entrada principal da aplicação (ex: `resources/app.ts` or `resources/Js/bootstrap.ts`).
Para sessões baseadas em SPA, você deve habilitar o envio automático de credenciais e tokens CSRF:
- `axios.defaults.withCredentials = true;`
- `axios.defaults.withXSRFToken = true;`
- Defina `axios.defaults.baseURL` apontando para a API do backend.

### 2. Proteção CSRF (AdonisJS Shield)
A autenticação é baseada em **sessão + cookie (guard `web`)**. O AdonisJS Shield emite automaticamente o cookie `XSRF-TOKEN` em respostas; não existe (e não deve existir) um endpoint dedicado de "csrf-cookie" — esse fluxo é do Sanctum/Laravel e está fora do escopo.
- Habilite `axios.defaults.withXSRFToken = true;` e `axios.defaults.withCredentials = true;` para que o Axios leia o cookie `XSRF-TOKEN` e o reenvie no header `X-XSRF-TOKEN` automaticamente.
- Como o Adonis serve um catch-all HTML na carga inicial da SPA, o cookie `XSRF-TOKEN` já estará presente; não é necessário nenhum GET prévio para "buscar" o token.

### 3. Configuração de Interceptadores Globais
Defina interceptadores globais de requisição e resposta para gerenciar tokens de autenticação, logs e estados de erro HTTP comuns.

#### Interceptador de Requisição
- A autenticação é por **sessão + cookie** (guard `web`); não anexe header `Authorization`/Bearer nem tokens manualmente — as credenciais viajam via cookie de sessão (`withCredentials`) e o CSRF via `withXSRFToken`.
- Configure os cabeçalhos padrão como `Accept: application/json` e `Content-Type: application/json`.

#### Interceptador de Resposta (Tratamento de Erros)
Trate os códigos de erro HTTP comuns de forma global para evitar a repetição de try/catch redundantes em cada store:
- **401 Unauthorized (Não Autorizado)**: Redirecione o usuário para a tela de login (usando a instância do Vue Router) e limpe todas as sessões e stores ativas do Pinia.
- **403 Forbidden (Proibido)**: Exiba um toast/notificação de aviso utilizando o helper da biblioteca de UI local (`Toast.show` do `@maxvue/max-components-ui`) informando que o acesso foi negado.
- **422 Unprocessable Entity (Entidade Não Processável)**: Formate os erros de validação (comumente retornados por validadores como o VineJS) e rejeite a Promise com os erros estruturados. **Atenção:** o `apiPostRoute` do `@maxvue/max-use` embrulha o `axios.post` em seu próprio `try/catch` e **engole qualquer erro, retornando `null`** (e `false` para rota inválida) — ou seja, o valor rejeitado pelo interceptador (os erros 422 estruturados) **NÃO** chega a quem chamou `apiPostRoute`. Para receber os erros de validação estruturados em um formulário, inspecione o retorno `null` e leia os erros por outra via, ou use `axios.post` diretamente nesse endpoint específico (não `apiPostRoute`).
- **500 Internal Server Error (Erro Interno do Servidor)**: Exiba uma mensagem amigável e genérica via notificação toast (ex: "Erro no servidor. Tente novamente mais tarde.") e registre os detalhes técnicos no console ou sistema de telemetria (nunca exponha stack traces aos usuários em produção).

### 4. Integração com Pinia Stores
Ao fazer requisições HTTP dentro das ações do Pinia, siga estas diretrizes:
- Mantenha variáveis de estado reativo para `loading` (booleano) e opcionalmente `error` (string ou objeto).
- Defina `loading.value = true` antes de iniciar a requisição e resete-o no bloco `finally`.
- Para erros padrão tratados pelo interceptador global, não é necessário usar blocos try-catch manuais nas ações do Pinia, a menos que você precise de um comportamento customizado específico.

---

## Examples

### Bootstrap do Axios e Interceptadores (`resources/Js/bootstrap.ts`)
```typescript
import axios from 'axios';
import router from '@/Js/router';
import { Toast } from '@maxvue/max-components-ui';

// Habilita o compartilhamento de cookies e a vinculação automática do header XSRF
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;
axios.defaults.baseURL = import.meta.env.VITE_API_URL || '/';
axios.defaults.headers.common['Accept'] = 'application/json';

// Interceptador de resposta
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        const { response } = error;

        if (response) {
            const status = response.status;
            const data = response.data;

            switch (status) {
                case 401:
                    // Não autorizado: Redireciona para o login e limpa o estado
                    router.push({ name: 'login' });
                    break;
                case 403:
                    // Proibido: Exibe toast de aviso
                    Toast.show({
                        title: 'Acesso Negado',
                        message: 'Você não tem permissão para realizar esta ação.',
                        severity: 'warning'
                    });
                    break;
                case 422:
                    // Erro de validação: Retorna os erros formatados para o componente
                    return Promise.reject(data.errors || data);
                case 500:
                    // Erro no servidor: Exibe toast amigável de erro
                    Toast.show({
                        title: 'Erro de Servidor',
                        message: 'Ocorreu um erro no servidor. Tente novamente mais tarde.',
                        severity: 'error'
                    });
                    break;
                default:
                    Toast.show({
                        title: 'Erro na Requisição',
                        message: data?.message || 'Algo deu errado. Verifique sua conexão.',
                        severity: 'error'
                    });
            }
        } else {
            // Erro de rede ou CORS
            Toast.show({
                title: 'Erro de Rede',
                message: 'Não foi possível conectar ao servidor. Verifique sua conexão.',
                severity: 'error'
            });
        }

        return Promise.reject(error);
    }
);

export default axios;
```

### Login Reativo na Store do Pinia (POST de formulário)
O `login` é um POST de mutação de estado e usa `apiPostRoute` do `@maxvue/max-use`, que **já executa o POST e retorna `response.data`** (não embrulhe em `axios.post`). O Axios global continua sendo o transporte interno (cookies/CSRF/interceptadores). O cookie `XSRF-TOKEN` do Shield já está presente, então **não há GET prévio de "csrf-cookie"**. Os **dados do usuário autenticado (`/api/user/data`) NÃO são buscados aqui** — eles vêm de uma store MaxPinia (`isCached`/`options.get`), conforme a skill de auth-session.
```typescript
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiPostRoute } from '@maxvue/max-use';
import router from '@/Js/router';

export const useAuthStore = defineStore('auth', () => {
    const loading = ref(false);

    async function login(credentials: { email: string; password: string }) {
        loading.value = true;
        try {
            // POST de autenticação (sessão + cookie via guard web do Adonis).
            // O Shield já emitiu o cookie XSRF-TOKEN; withXSRFToken o reenvia.
            // apiPostRoute já executa o POST e retorna response.data (não embrulhe em axios.post).
            const data = await apiPostRoute('/api/login', credentials);

            // IMPORTANTE: apiPostRoute NUNCA lança — em falha (401/422) ele retorna
            // null (ou false para rota inválida). Portanto NÃO confie em catch:
            // guarde o redirecionamento no valor de retorno.
            if (!data) {
                // exiba o erro de login / interrompa o fluxo
                return;
            }

            // Os dados do usuário são carregados pela store MaxPinia correspondente,
            // não por axios.get manual aqui.
            router.push({ name: 'dashboard' });
        } finally {
            loading.value = false;
        }
    }

    return { loading, login };
});
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **GETs ao backend NUNCA via Axios direto em componentes ou serviços** — sempre use uma store MaxPinia com `isCached = true` e `options.get`. O `@maxvue/max-pinia` usa Axios internamente para esses GETs.
- **NÃO** instancie novos clientes Axios dentro de componentes ou stores do Pinia. Utilize sempre a instância globalmente configurada do Axios.
- **NÃO** ignore o fluxo de redirecionamento do erro 401. Qualquer resposta 401 deve obrigatoriamente invalidar a sessão do usuário e redirecionar para a tela de login.
- **NÃO** exiba erros brutos do banco de dados ou detalhes internos do backend para o usuário final. Mapeie sempre erros 500 para mensagens limpas e seguras.
- **NÃO** insira credenciais, chaves de API ou segredos diretamente nos arquivos de configuração do frontend. Utilize variáveis de ambiente via `import.meta.env`.
- **NÃO** escreva blocos try/catch individuais em todas as stores apenas para exibir mensagens de erro genéricas; confie no interceptador global centralizado para esta finalidade.
