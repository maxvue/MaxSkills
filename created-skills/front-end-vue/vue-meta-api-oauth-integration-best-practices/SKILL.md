---
name: vue-meta-api-oauth-integration-best-practices
description: Use when building, refactoring, or debugging client-side social media OAuth integration flows in Vue 3 (Facebook, Instagram, WhatsApp), handling connection popups, listener events via postMessage, or managing social connection state. Triggers on window.open for OAuth, window.addEventListener('message'), and social account authorization UI.
---

## Objetivo
Estabelecer padrões claros, seguros e robustos de implementação para fluxos de integração OAuth de mídias sociais no lado do cliente (especificamente o Login da Meta) usando popups centralizados, callbacks baseados em eventos com `window.postMessage` e sincronização de estado adequada no Vue 3.

## Instruções

1. **Criação da Janela Popup e Prevenção de Bloqueios**
   - Os navegadores modernos bloqueiam o `window.open` a menos que ele seja executado dentro de um ciclo de evento de interação direta do usuário (como um manipulador `@click`).
   - Se a URL de autorização OAuth precisar ser recuperada de forma assíncrona a partir da API do backend, NÃO faça a requisição da API primeiro. Em vez disso, abra um popup temporário em branco (`window.open('about:blank', ...)`) dentro do manipulador de clique imediatamente. Depois, atribua a URL de autorização obtida ao `popup.location.href` assim que a resposta da API retornar.
   - Sempre centralize o popup na tela ativa do usuário. Use a largura da tela, a altura da tela, o zoom do sistema e os deslocamentos de monitores duplos para calcular as coordenadas precisas.

2. **Segurança nos Listeners de postMessage (Prevenindo XSS)**
   - Registre o manipulador de callback usando `window.addEventListener('message', handleCallback)`.
   - **Validação Crucial**: Sempre verifique se o `event.origin` corresponde estritamente ao domínio de backend da API confiável ou à origem da aplicação (`import.meta.env.VITE_API_URL` ou similar). Nunca confie em comunicações de origens arbitrárias (`*`).
   - Valide a estrutura do payload da mensagem (`event.data`) antes de executar mutações ou atualizações na store. Um payload de evento padrão deve ter um formato reconhecível: `{ type: 'META_OAUTH_RESPONSE', status: 'success' | 'error', data: any }`.
   - Remova o listener (`window.removeEventListener('message', handleCallback)`) imediatamente após o sucesso da autenticação, falha ou quando o componente Vue for desmontado (`onUnmounted`).

3. **Monitoramento do Ciclo de Vida e Fechamento Manual**
   - Implemente um temporizador de verificação com `setInterval` monitorando o `popup.closed` a cada 500ms.
   - Se o usuário fechar o popup manualmente sem concluir a autorização, resolva o estado graciosamente, limpe o listener e exiba uma notificação amigável para o usuário.

4. **Integração com Stores (MaxPinia)**
   - Todo GET de dados de página (incluindo a auth-url e as credenciais sociais) deve passar por uma store `@maxvue/max-pinia`, não por `axios.get` manual no componente. Use `apiGetRoute('/api/...')` do `@maxvue/max-use` para resolver os caminhos string da API.
   - O callback do OAuth deve disparar uma atualização de estado na store de credenciais sociais (recarregando via store MaxPinia), refletindo o auto-save/cache da camada `@maxvue/max-pinia`.
   - Nunca armazene credenciais brutas ou tokens de acesso confidenciais dentro de stores do lado do cliente ou no LocalStorage. Dependa de sessões do backend (guard web, sessão+cookie) e represente o estado de autorização com flags abstratas como `has_token: boolean`.

## Restrições
- NÃO busque URLs de autorização na API antes de abrir a janela popup, caso contrário, os bloqueadores de popup do navegador serão ativados.
- NÃO aceite mensagens de origens curinga (`*`) nos listeners de `postMessage`.
- NÃO armazene ou exponha credenciais brutas ou tokens de autorização confidenciais no estado do lado do cliente.
- NÃO deixe listeners ou intervalos ativos quando o componente for desmontado.

# Exemplos

```vue
<template>
  <div class="oauth-integration">
    <!-- Componentes de botão formatados em uma única linha, mantendo atributos inline -->
    <MaxButton id="btn-meta-connect" icon="mdi:facebook" label="Conectar Página do Facebook" :action="connectAccount" :loading="loading" />
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { Toast } from '@maxvue/max-components-ui';
import { apiGetRoute } from '@maxvue/max-use';

// Store MaxPinia auto-importada (definida em stores/)
const credentialsStore = useSocialMediaCredentialsStore();
const loading = ref(false);

let popupWindow: Window | null = null;
let pollTimer: number | null = null;

// Origem confiável para validação de segurança do postMessage
const TRUSTED_ORIGIN = import.meta.env.VITE_API_URL || window.location.origin;

/**
 * Calcula a posição e abre a janela popup centralizada na tela ativa.
 */
const openCenteredPopup = (url: string, title: string, w = 600, h = 650): Window | null => {
  const dualScreenLeft = window.screenLeft !== undefined ? window.screenLeft : window.screenX;
  const dualScreenTop = window.screenTop !== undefined ? window.screenTop : window.screenY;

  const width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
  const height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

  const systemZoom = width / window.screen.width;
  const left = (width - w) / 2 / systemZoom + dualScreenLeft;
  const top = (height - h) / 2 / systemZoom + dualScreenTop;

  const newWindow = window.open(
    url,
    title,
    `scrollbars=yes,width=${w / systemZoom},height=${h / systemZoom},top=${top},left=${left}`
  );

  if (window.focus && newWindow) newWindow.focus();
  return newWindow;
};

/**
 * Limpa todos os recursos de escuta e monitoramento.
 */
const cleanup = (): void => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
  window.removeEventListener('message', handleMessage);
  loading.value = false;
  popupWindow = null;
};

/**
 * Trata as mensagens recebidas via postMessage a partir da janela filha.
 */
const handleMessage = async (event: MessageEvent): Promise<void> => {
  // Validação estrita de segurança da origem da mensagem (evita ataques XSS)
  if (event.origin !== TRUSTED_ORIGIN) {
    return;
  }

  const { type, status, data } = event.data || {};
  if (type !== 'META_OAUTH_RESPONSE') return;

  cleanup();

  if (status === 'success') {
    try {
      // Recarrega as credenciais de mídias sociais via store MaxPinia (cache/auto-save)
      await credentialsStore.load();
      Toast.show({ severity: 'success', title: 'Sucesso', message: 'Conta conectada com sucesso!' });
    } catch {
      Toast.show({ severity: 'error', title: 'Erro', message: 'Erro ao carregar credenciais atualizadas.' });
    }
  } else {
    Toast.show({ severity: 'error', title: 'Erro de Autenticação', message: data?.error || 'A autorização falhou.' });
  }
};

/**
 * Inicia o fluxo de autenticação Meta Login.
 */
const connectAccount = async (): Promise<void> => {
  loading.value = true;

  // Abre janela popup em branco imediatamente para evitar bloqueador de popups do navegador
  popupWindow = openCenteredPopup('about:blank', 'auth-popup');

  if (!popupWindow) {
    loading.value = false;
    Toast.show({ severity: 'warn', title: 'Popup Bloqueado', message: 'Por favor, habilite a exibição de popups para este site.' });
    return;
  }

  try {
    // Obtém do AdonisJS a URL de redirecionamento de autorização da Meta
    // via apiGetRoute (resolve para o caminho string /api/...), nunca axios.get manual
    const { data } = await apiGetRoute('/api/social_media/facebook/auth-url');

    // Redireciona o popup em branco para a URL oficial
    popupWindow.location.href = data.url;

    // Inicia a escuta de mensagens do popup de callback
    window.addEventListener('message', handleMessage);

    // Verifica se a janela foi fechada manualmente pelo usuário
    pollTimer = window.setInterval(() => {
      if (popupWindow && popupWindow.closed) {
        cleanup();
        Toast.show({ severity: 'warn', title: 'Cancelado', message: 'A conexão com a conta foi cancelada pelo usuário.' });
      }
    }, 500);

  } catch (error) {
    if (popupWindow) popupWindow.close();
    cleanup();
    Toast.show({ severity: 'error', title: 'Erro', message: 'Não foi possível iniciar o login da Meta.' });
  }
};

onUnmounted(() => {
  cleanup();
});
</script>
```
