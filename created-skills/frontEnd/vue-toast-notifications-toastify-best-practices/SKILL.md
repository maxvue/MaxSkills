---
name: vue-toast-notifications-toastify-best-practices
description: Use ao disparar notificações toast em componentes Vue 3 do engeapp com vue3-toastify (auto-mount, opções passadas por chamada; sem registro global). Prefira o Toast/MaxToast nativo do @maxvue/max-components-ui e use toastify só para extras (HTML, loading dinâmico). Cobre toasts de sucesso/erro/aviso e resolução do save MaxPinia via status reativo.
---

# Boas Práticas para Notificações Toast com vue3-toastify no Vue 3

## Objetivo
Estabelecer um padrão robusto e consistente para implementar, configurar e disparar notificações toast assíncronas e dinâmicas utilizando `vue3-toastify` no frontend Vue 3, alinhado com o design system do Engeapp.

## Instruções

> **Escopo (toast nativo do ecossistema Max):** O `@maxvue/max-components-ui` já fornece um sistema de toast de primeira parte — o helper global `Toast` (`Toast.show({ title, severity })`, `Toast.add(payload)`, `Toast.hide(id)`, `Toast.clear()`), o componente `MaxToast.vue` e a `useToast.Store`. Pela house rule "usar componentes/composables Max* em vez de equivalentes de terceiros", **prefira o `Toast` nativo do Max** e reserve `vue3-toastify` para recursos que ele não cobre (ex.: `toast.promise`/estados de loading dinâmicos, HTML arbitrário) — nunca registre um segundo container de toast concorrente com o `<MaxToast />`. Exemplo nativo:
> ```typescript
> import { Toast } from '@maxvue/max-components-ui';
> Toast.show({ title: 'Projeto salvo com sucesso!', severity: 'success' });
> ```

### 1. Montagem: `<MaxToast />` global + auto-mount do toastify
No engeapp, o container de toast do app é o `<MaxToast />` (do `@maxvue/max-components-ui`), renderizado uma vez no `App.vue`. O `resources/app.ts` **não** registra `app.use(Vue3Toastify, …)` nem monta `<ToastContainer />` — ele registra `ZiggyVue`, `vaporInteropPlugin`, `pinia`, `MaxComponentsUi` e o `router` (VueFinder NÃO é registrado globalmente — o `FileManager.vue` provê `VueFinderOptions` localmente).

Quando você usa `vue3-toastify`, importe `{ toast }` e chame-o direto no componente. A lib faz **auto-mount preguiçoso**: na primeira chamada `toast(...)` ela injeta seu próprio container no DOM, sem precisar de `app.use`. É assim que os consumidores reais do projeto chamam o toast (ver `CheckoutBoleto.vue`, `CheckoutPix.vue`, `TrtPaymentScheduleModal.vue`) — sempre passando as opções por chamada. Nenhum desses consumidores importa hoje o CSS do toastify; a importação abaixo é uma boa prática recomendada por esta skill, não um padrão já existente no projeto:

```typescript
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css'; // importe o CSS uma vez, junto do toast

toast('Ação realizada!', {
  theme: 'auto',
  type: 'success',
  autoClose: 1700,
  closeOnClick: false,
});
```
> Como não há configuração global, **as opções (theme, type, autoClose, position…) devem ir em cada chamada**. Mantenha esses valores consistentes entre componentes para não divergir o visual.

### 2. Disparos Padrão de Toasts
Importe `{ toast }` de `vue3-toastify` para disparar notificações. Sempre especifique o tipo e utilize mensagens descritivas em português do Brasil (pt-BR).

- **Toast de Sucesso:** Usado para ações concluídas com sucesso (ex: salvar formulários, cálculos concluídos).
  ```typescript
  import { toast } from 'vue3-toastify';

  toast.success('Cálculo concluído com sucesso!');
  ```

- **Toast de Erro:** Usado para falhas. Prefira exibir mensagens amigáveis em vez de strings brutas de erros do sistema.
  ```typescript
  toast.error('Falha ao salvar o projeto. Por favor, verifique sua conexão.');
  ```

- **Toasts de Alerta / Informação:**
  ```typescript
  toast.warning('Este projeto possui pendências de homologação.');
  toast.info('Exportando dados. Você será notificado ao finalizar.');
  ```

### 3. Toasts Assíncronos para o Save da Store MaxPinia
**Atenção:** `saveInServer()` da store `@maxvue/max-pinia` **não** retorna uma promise que resolve/rejeita conforme o resultado HTTP. Ela é `async`, mas nunca retorna a cadeia `axios.post(...)` e captura todos os erros internamente — a promise resolve para `undefined` quase imediatamente, independentemente do sucesso/falha real. Por isso **NÃO use** `toast.promise(store.saveInServer(), ...)`: o `success` dispararia na hora (mesmo em falha) e o ramo `error.render({ data })` nunca executaria.

Em vez disso, dispare o save e observe o estado reativo de save da store (`status.server.save.is_success` / `is_error`) para acionar os toasts corretos:

```typescript
import { watch } from 'vue';
import { toast } from 'vue3-toastify';

// `projectStore` é uma store @maxvue/max-pinia; saveInServer() persiste o estado da página.
const pendingId = toast.loading('Salvando dados do projeto...', { position: 'top-right' });

projectStore.saveInServer(); // dispara o save (não é awaitable de forma confiável)

// Observa o resultado real via status reativo do MaxPinia e resolve o toast.
const stop = watch(
  () => [
    projectStore.status.server.save.is_success,
    projectStore.status.server.save.is_error,
  ],
  ([isSuccess, isError]) => {
    if (isSuccess) {
      toast.update(pendingId, { render: 'Projeto salvo com sucesso! 👌', type: 'success', isLoading: false, autoClose: 3000 });
      stop();
    } else if (isError) {
      const message = projectStore.status.server.save.error?.response?.data?.message || 'Falha ao salvar o projeto.';
      toast.update(pendingId, { render: message, type: 'error', isLoading: false, autoClose: 3000 });
      stop();
    }
  }
);
```
> Se preferir promises reais, exponha/aguarde uma variante de `saveInServer` que efetivamente retorne e rejeite a promise do `axios.post` — não confie na promise atual para resolução de sucesso/erro.

### 4. Estilização Personalizada (Alinhamento com o Tema Aura/Max)
Você pode aplicar estilos inline personalizados ou classes para alinhar os toasts com o design system Aura/Max:
```typescript
toast('Ação realizada!', {
  theme: 'auto',
  type: 'success',
  autoClose: 2000,
  closeOnClick: false,
  dangerouslyHTMLString: true,
  style: {
    fontSize: '0.85rem',
    borderRadius: '10px',
  }
});
```

### 5. Tratamento de Erros HTTP → Toast
Hoje **não existe** nenhum interceptor `axios.interceptors.response` nem instância axios compartilhada configurada no projeto: tanto `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`) quanto `@maxvue/max-pinia` (`plugin.ts`, axios default carregado sob demanda) usam a instância padrão do `axios` e tratam o erro localmente (`console.error` + retorno `null` / `status.server.save.is_error`), sem repassar o erro para um ponto central.

Na prática, isso significa:
- Dispare os toasts de erro HTTP **no ponto de chamada**, checando o retorno `null` de `apiGetRoute`/`apiPostRoute` ou o estado `status.server.save.is_error`/`status.server.get.is_success` da store MaxPinia — não existe hoje um lugar único onde "basta" mapear status → toast.
- Se você registrar um `axios.interceptors.response` na instância default do `axios`, ele afetará **simultaneamente** `@maxvue/max-use`, `@maxvue/max-pinia` e todos os componentes com `import axios from 'axios'` direto, podendo duplicar toasts sobre erros que essas camadas já tratam localmente.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** exiba exceções brutas do sistema para o usuário em toasts de erro. Sempre mapeie para mensagens amigáveis e claras.
- **Não** duplique estilos de toasts globais inline. Mantenha os estilos visuais consistentes entre todos os componentes.
- **Não** bloqueie a interação do usuário para toasts informativos; utilize um tempo razoável de fechamento automático (tipicamente entre 1500ms e 3000ms).
- **Não** use Options API em componentes Vue que lidam com toasts; sempre use `<script setup lang="ts">`.
- Os comentários do código nos componentes Vue devem ser em Português do Brasil (pt-BR).
