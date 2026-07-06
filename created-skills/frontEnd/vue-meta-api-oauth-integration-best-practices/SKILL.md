---
name: vue-meta-api-oauth-integration-best-practices
description: Use ao construir, refatorar ou depurar a UI de credenciais das APIs oficiais da Meta (Instagram e Página do Facebook) no front-end Vue 3 do engeapp (SocialMedia/TabCredentials.vue). Cobre entrada MANUAL de external_account_id e token via MaxInputText/MaxButton, salvamento pela store Pinia comum useSocialMediaCredentials (load/save via axios + route Ziggy) e o indicador has_token.
---

## Objetivo
Padronizar a tela de **credenciais de redes sociais** do engeapp: o gestor **digita manualmente** o identificador da conta (Page ID do Facebook ou Instagram User ID) e **cola o token de acesso** obtido no painel da Meta, salvando via botão. Não existe fluxo OAuth de popup/redirect no front-end — a autorização é feita fora da aplicação e apenas as credenciais resultantes são armazenadas pelo backend.

Arquivos reais que esta skill descreve:
- `resources/Vue/Sections/SocialMedia/TabCredentials.vue` — a tela.
- `resources/Stores/calendar/useSocialMediaCredentials.Store.ts` — a store.

## Instruções

1. **Modelo mental: entrada manual, não OAuth client-side**
   - NÃO implemente `window.open`, `about:blank`, `window.postMessage`, `addEventListener('message')` nem polling de `popup.closed`. Nenhum desses padrões existe na seção SocialMedia e não há rota de `auth_url`.
   - Cada API do catálogo (Facebook, Instagram) é representada por um `SocialMediaCredentialItem` com `external_account_id` (o ID da conta) e `has_token` (flag). O gestor edita esses valores num formulário e clica em Salvar.

2. **Store: Pinia de composição comum (NÃO MaxPinia)**
   - A credencial é gerida por `useSocialMediaCredentialsStore` — uma store `defineStore` de composição comum que usa `axios` diretamente com o helper Ziggy `route()`. Ela **não** é `@maxvue/max-pinia`: não tem `isCached`, `options.get.route/save`, `status.server` nem `reload()`.
   - Ela expõe exatamente `items`, `loading`, `load()` e `save(payload)`:
     - `load()` → `axios.get(route('social_media.credentials.data'))`, preenche `items` com `data.items`.
     - `save(payload)` → `axios.post(route('social_media.credentials.save'), payload)` e atualiza o item local (`external_account_id`, `is_active`, e liga `has_token` quando um novo `access_token` foi enviado).
   - Para recarregar dados, chame `load()`, não `reload()` (que não existe). Os nomes de rota são `social_media.credentials.data` (GET) e `social_media.credentials.save` (POST) — nomes Ziggy pontilhados resolvidos por `route()`.

3. **Segurança do token: nunca trafegue de volta ao cliente**
   - O backend nunca devolve o token salvo. A store só conhece `has_token: boolean` para indicar se já há um token configurado.
   - No formulário, o campo de token começa **vazio** a cada carregamento. Envie `access_token` somente quando o gestor digitar um novo valor; caso contrário mande `null` para preservar o token existente no backend.
   - Nunca persista o token em LocalStorage nem em estado global. Após salvar, limpe o campo local (`access_token = ''`).

4. **UI: apenas componentes Max, atributos inline**
   - Use `MaxInputText` para o ID da conta e para o token (`type="password"`), `MaxInputSwitch` para `is_active` e `MaxButton` com `:action` + `:loading` para salvar. Nada de `<input>`/`<button>` nativos nem PrimeVue cru.
   - Feedback via `Toast.show({ severity, title, message })` de `@maxvue/max-components-ui`.
   - O rótulo/placeholder do identificador muda conforme a plataforma (Page ID para Facebook, Instagram User ID para Instagram). Comentários de código em pt-BR.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), sem exceção.
- NÃO invente fluxo OAuth de popup/redirect no front-end (`window.open`, `postMessage`, `auth_url`): ele não existe neste projeto.
- NÃO trate a store de credenciais como MaxPinia; use `load()`/`save()` (axios + `route()`).
- NÃO exponha nem armazene o token de acesso no cliente; dependa de `has_token` e da sessão do backend.
- NÃO use inputs/botões nativos ou PrimeVue cru; use `MaxInputText`, `MaxInputSwitch`, `MaxButton`, `Toast`.

# Exemplo

Formulário fiel a `TabCredentials.vue`: carrega via store, edita manualmente, salva enviando o token só quando preenchido.

```vue
<template>
    <div class="social-credentials">
        <template v-for="form in forms" :key="form.event_api_id">
            <MaxTitle2 :icon="form.icon" :title="form.api_name" :subtitle="form.has_token ? 'Conta conectada.' : 'Nenhuma credencial configurada ainda.'" />

            <MaxGrid p0>
                <MaxInputText s50 :id="`cred-account-${form.event_api_id}`" :label="accountLabel(form.api_name)" v-model="form.external_account_id" no-message />
                <MaxInputText s50 :id="`cred-token-${form.event_api_id}`" type="password" label="Token de Acesso" v-model="form.access_token" :placeholder="form.has_token ? 'Token já configurado — deixe em branco para manter' : 'Cole o token de acesso da Meta'" no-message />
                <MaxInputSwitch s50 :id="`cred-active-${form.event_api_id}`" v-model="form.is_active" :question="`Canal ${form.is_active ? 'ativado' : 'desativado'}`" />

                <div s50 style="text-align: right;">
                    <MaxButton :id="`btn-save-cred-${form.event_api_id}`" icon="mdi:content-save-outline" label="Salvar" :action="() => saveForm(form)" :loading="form.saving" />
                </div>
            </MaxGrid>
        </template>
    </div>
</template>

<script setup lang="ts">
    import { Toast } from '@maxvue/max-components-ui';
    import type { SocialMediaCredentialItem } from '@/Stores/calendar/useSocialMediaCredentials.Store';

    interface CredentialForm extends SocialMediaCredentialItem {
        access_token: string;
        saving: boolean;
    }

    // Store Pinia comum auto-importada (axios + route Ziggy), NÃO MaxPinia
    const credentials = useSocialMediaCredentialsStore();
    const forms = ref<CredentialForm[]>([]);

    /** Estado editável local a partir dos itens carregados (token sempre vazio). */
    const buildForms = (): void => {
        forms.value = credentials.items.map(item => ({ ...item, access_token: '', saving: false }));
    };

    /** Rótulo do identificador da conta conforme a plataforma. */
    const accountLabel = (apiName: string): string => {
        return apiName.toLowerCase() === 'facebook' ? 'ID da Página (Page ID)' : 'ID da Conta (Instagram User ID)';
    };

    /** Salva a credencial; envia o token só quando o gestor digitou um novo valor. */
    const saveForm = async (form: CredentialForm): Promise<void> => {
        form.saving = true;
        try {
            await credentials.save({
                event_api_id:        form.event_api_id,
                external_account_id: form.external_account_id,
                access_token:        form.access_token || null,
                is_active:           form.is_active
            });
            form.access_token = '';                        // nunca mantém o token no cliente
            if ( ! form.has_token) form.has_token = true;
            Toast.show({ severity: 'success', title: 'Salvo!', message: `Credencial do ${form.api_name} atualizada.` });
        } catch {
            Toast.show({ severity: 'error', title: 'Erro', message: 'Não foi possível salvar a credencial.' });
        } finally {
            form.saving = false;
        }
    };

    onMounted(async () => {
        await credentials.load();                          // recarrega via load(), não reload()
        buildForms();
    });
</script>
```
