---
name: vue-toast-notifications-toastify-best-practices
description: "Use when displaying toast notifications or floating alerts in Vue 3. Standard requirement is MaxToast from @maxvue/max-components-ui triggered via Toast.show({ title, severity }) with ToastPayload."
---
# Notificações Toast no Vue 3 — MaxToast é o padrão

## Objetivo
Quando alguém pedir "um toast", "um toastzinho", "um aviso", "uma notificação flutuante" ou "um feedback de sucesso/erro" na UI, a resposta correta neste ecossistema é **sempre o MaxToast** do `@maxvue/max-components-ui`. Esta skill define o que é o MaxToast, como montá-lo e como dispará-lo.

---

## 1. O que é o MaxToast

O MaxToast é o sistema de toast **de primeira parte** do ecossistema Max. Ele tem três peças:

| Peça | O que é | Quando você toca nela |
|---|---|---|
| `<MaxToast />` | O **container visual**. Renderiza a fila de toasts no canto superior direito (fixo, `top: 74px; right: 16px`, z-index 9999). | **Uma única vez**, no `App.vue`. Nunca em componentes de página. |
| `Toast` | O **helper global** (fachada). É por aqui que você dispara toasts. | Em 99% dos casos. É a API pública. |
| `useToastStore` | A **store Pinia** (`defineStore('max-toast')`) que guarda a fila e os timers. | Só em casos avançados (ler `items`, controle fino). Prefira o helper. |

Visual pronto (não precisa estilizar): card colorido por severidade, ícone automático, título, mensagem secundária opcional, botão de fechar, barra de progresso que decresce, animação de entrada/saída, e **pausa automática do timer ao passar o mouse por cima**.

---

## 2. Montagem — uma vez só, no `App.vue`

O container é montado **uma única vez na raiz da aplicação**, fora do `<RouterView />`, para que os toasts sobrevivam à troca de rota. É exatamente assim que o engeapp faz (`resources/App.vue`):

```vue
<template>
    <div v-if="route.name">
        <!-- ...layouts e RouterView... -->
    </div>

    <MaxPopoverConfirm />
    <MaxToast />
</template>
```

Regras de montagem:
- **NÃO** monte `<MaxToast />` dentro de páginas, seções ou modais — só na raiz.
- **NÃO** passe props: `MaxToast` não tem nenhuma prop. Toda a configuração vai no payload de cada disparo.
- **NÃO** monte um segundo container de toast (de qualquer biblioteca) concorrendo com ele.
- Não é preciso `app.use(...)` nem importar CSS: o componente vem do plugin `MaxComponentsUi` já registrado em `resources/app.ts`, e o estilo é próprio do componente.

---

## 3. Disparo — `Toast.show({ title, severity })`

Esta é a forma canônica. Importe o helper `Toast` e chame `show`:

```typescript
import { Toast } from '@maxvue/max-components-ui';

Toast.show({ title: 'Projeto salvo com sucesso!', severity: 'success' });
```

### API completa do helper `Toast`

| Método | Assinatura | Efeito |
|---|---|---|
| `Toast.show(payload)` | `(payload: ToastPayload) => string` | Exibe o toast e retorna o `id` gerado. **Use este por padrão.** |
| `Toast.add(payload)` | `(payload: ToastPayload) => string` | Idêntico a `show` (alias). |
| `Toast.hide(id)` | `(id: string) => void` | Remove um toast específico antes do tempo. |
| `Toast.delete(id)` | `(id: string) => void` | Idêntico a `hide` (alias). |
| `Toast.clear()` | `() => void` | Remove todos os toasts visíveis de uma vez. |

### O payload (`ToastPayload`)

```typescript
interface ToastPayload {
    title: string;              // obrigatório — a linha principal, em negrito
    message?: string;           // opcional — linha secundária, menor (máx. 2 linhas, com ellipsis)
    severity?: ToastSeverity;   // default: 'info'
    icon?: string;              // opcional — nome de ícone (ex.: 'mdi:content-copy'); sobrescreve o ícone da severidade
    duration?: number;          // opcional — em MILISSEGUNDOS. Default: 4000
}
```

> **`title` é o único campo obrigatório.** Se você tem apenas uma frase para exibir, ela vai em `title` — não em `message`.

### As 5 severidades

`severity` aceita exatamente estes valores — nenhum outro:

| `severity` | Cor do card | Ícone automático | Use para |
|---|---|---|---|
| `'success'` | verde/teal (`--success-650`) | `mdi:check-circle-outline` | Ação concluída: salvou, copiou, enviou, excluiu |
| `'info'` | azul (`--info-600`) — **default** | `mdi:information-outline` | Informação neutra, processo iniciado |
| `'warning'` | âmbar (`--warn-600`) | `mdi:alert-outline` | Ressalva, pendência, ação parcialmente concluída |
| `'error'` | vermelho (`--danger-600`) | `mdi:close-circle-outline` | Falha da operação |
| `'whatsapp'` | verde WhatsApp (`#128C7E`) | `mdi:whatsapp` | Eventos específicos de WhatsApp |

### Exemplos por caso de uso

```typescript
import { Toast } from '@maxvue/max-components-ui';

// Sucesso simples
Toast.show({ title: 'Cálculo concluído com sucesso!', severity: 'success' });

// Com mensagem secundária dando o detalhe
Toast.show({
    title: 'Projeto salvo',
    message: 'As alterações já estão disponíveis para a equipe.',
    severity: 'success'
});

// Erro — mensagem amigável, nunca a exceção crua
Toast.show({
    title: 'Não foi possível salvar o projeto',
    message: 'Verifique sua conexão e tente novamente.',
    severity: 'error'
});

// Aviso
Toast.show({ title: 'Este projeto possui pendências de homologação.', severity: 'warning' });

// Feedback rápido de cópia — duração curta e ícone customizado
Toast.show({
    title: 'Linha digitável copiada!',
    severity: 'success',
    icon: 'mdi:content-copy',
    duration: 1700
});

// Toast longo, fechado programaticamente quando a operação terminar
const id = Toast.show({ title: 'Exportando dados…', severity: 'info', duration: 60000 });
// …ao finalizar a exportação:
Toast.hide(id);
Toast.show({ title: 'Exportação concluída!', severity: 'success' });
```

### Duração e pausa

- `duration` é em **milissegundos**; o default é `4000`.
- Faixa recomendada: **1500–3000 ms** para confirmações rápidas, até **5000 ms** para erros que o usuário precisa ler.
- O timer **pausa sozinho** enquanto o mouse está sobre o toast e **retoma** ao sair — não infle a duração "para dar tempo de ler".
- Para um toast que só sai por ação, use uma `duration` alta e feche via `Toast.hide(id)`.

---

## 4. Uso avançado — a store `useToastStore`

Só quando o helper não basta (ex.: você precisa **ler** a fila de toasts ativos ou pausar/retomar programaticamente):

```typescript
import { useToastStore } from '@maxvue/max-components-ui';
// alternativa pelo subpath dedicado: from '@maxvue/max-components-ui/stores'

const toastStore = useToastStore();

toastStore.add({ title: 'Ok', severity: 'success' }); // retorna o id
toastStore.items;            // Ref<ToastItem[]> — fila reativa de toasts visíveis
toastStore.pause(id);        // pausa o timer
toastStore.resume(id);       // retoma o timer
toastStore.remove(id);       // remove um
toastStore.clear();          // remove todos
```

> A store exige Pinia ativo. Não a instancie no topo de um módulo que possa ser avaliado antes do `app.use(pinia)` — chame `useToastStore()` dentro da função/handler que roda em runtime. O helper `Toast` já faz isso por você (resolve a store a cada chamada), e por isso é seguro usá-lo em qualquer lugar.

---

## 5. Toast para o resultado do save de uma store MaxPinia

**Atenção:** `saveInServer()` da store `@maxvue/max-pinia` **não** retorna uma promise que resolve/rejeita conforme o resultado HTTP. Ela é `async`, mas captura todos os erros internamente e resolve para `undefined` quase imediatamente. Portanto **não** dispare o toast de sucesso logo após um `await store.saveInServer()` — ele apareceria mesmo em caso de falha.

O padrão correto é observar o **estado reativo de save** da store:

```typescript
import { watch } from 'vue';
import { Toast } from '@maxvue/max-components-ui';

// `projectStore` é uma store @maxvue/max-pinia
projectStore.saveInServer(); // dispara o save (não é awaitable de forma confiável)

const stop = watch(
    () => [
        projectStore.status.server.save.is_success,
        projectStore.status.server.save.is_error,
    ],
    ([isSuccess, isError]) => {
        if (isSuccess) {
            Toast.show({ title: 'Projeto salvo com sucesso!', severity: 'success' });
            stop();
        } else if (isError) {
            const message = projectStore.status.server.save.error?.response?.data?.message;
            Toast.show({
                title: 'Falha ao salvar o projeto',
                message: message || 'Tente novamente em instantes.',
                severity: 'error'
            });
            stop();
        }
    }
);
```

Lembre-se de que o MaxPinia já faz **auto-save com debounce**: não dispare um toast de sucesso a cada tecla digitada. Reserve o toast para saves explícitos (botão "Salvar", conclusão de etapa).

---

## 6. Erros de API → toast

Não existe interceptor `axios.interceptors.response` central no projeto: `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`) e `@maxvue/max-pinia` usam a instância padrão do axios e tratam o erro localmente (`console.error` + retorno `null` / `status.server.save.is_error`).

Na prática:
- Dispare o toast de erro **no ponto de chamada**, checando o retorno `null` de `apiGetRoute`/`apiPostRoute` ou o `status.server.*` da store MaxPinia.
- Se você registrar um interceptor global no axios default, ele afetará simultaneamente `max-use`, `max-pinia` e imports diretos de `axios`, podendo **duplicar** toasts de erros já tratados localmente.

```typescript
const data = await apiGetRoute('projects.show', { project: id });

if (!data) {
    Toast.show({ title: 'Não foi possível carregar o projeto', severity: 'error' });
    return;
}
```

---

## 7. Exceção legada: `vue3-toastify`

Alguns arquivos do engeapp ainda importam `{ toast } from 'vue3-toastify'` (ex.: `useLogin.Store.ts`, `CheckoutBoleto.vue`, `VoipCallButton.vue`, `ProjectPage.vue`). Isso é **legado**.

- Em **código novo**: use `MaxToast`/`Toast`. Não introduza `vue3-toastify`.
- Ao **editar** um arquivo que já usa `vue3-toastify`: prefira migrar aquela chamada para `Toast.show(...)`, mapeando `type` → `severity` e `autoClose` → `duration`.
- Única justificativa para manter o toastify: um recurso que o MaxToast realmente não cobre — **HTML arbitrário na mensagem** (`dangerouslyHTMLString`) ou **`toast.promise` com estado de loading dinâmico**. Mesmo assim, **nunca** monte um `<ToastContainer />` concorrendo com o `<MaxToast />` (o toastify faz auto-mount preguiçoso do próprio container na primeira chamada).

Mapa de migração:

| vue3-toastify | MaxToast |
|---|---|
| `toast('Msg', { type: 'success' })` | `Toast.show({ title: 'Msg', severity: 'success' })` |
| `toast.error('Msg')` | `Toast.show({ title: 'Msg', severity: 'error' })` |
| `toast.warning('Msg')` | `Toast.show({ title: 'Msg', severity: 'warning' })` |
| `toast.info('Msg')` | `Toast.show({ title: 'Msg', severity: 'info' })` |
| `autoClose: 1700` | `duration: 1700` |
| `const id = toast(...)` / `toast.dismiss(id)` | `const id = Toast.show(...)` / `Toast.hide(id)` |

---

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use bibliotecas de toast de terceiros em código novo (`vue3-toastify`, `vue-toastification`, `primevue/toast`, `sonner`, etc.). O padrão é `MaxToast`.
- **NÃO** monte `<MaxToast />` mais de uma vez, nem fora do `App.vue`.
- **NÃO** invente severidades: só `success`, `info`, `warning`, `error`, `whatsapp`.
- **NÃO** exiba exceções brutas do sistema no toast. Mapeie sempre para mensagem amigável em pt-BR; o detalhe técnico vai para `console.error`.
- **NÃO** sobrescreva o CSS do `.max-toast-*` em componentes. O visual é do design system; se precisa de outra cor, é outra `severity`.
- **NÃO** use toast para erros de validação de campo de formulário — esses pertencem ao próprio input (`MaxInput` e afins). Toast é para feedback de operação.
- **NÃO** use Options API em componentes que disparam toasts; sempre `<script setup lang="ts">`.
- Os comentários do código nos componentes Vue devem ser em Português do Brasil (pt-BR).
