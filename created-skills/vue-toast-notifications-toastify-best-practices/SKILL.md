---
name: vue-toast-notifications-toastify-best-practices
description: Use when setting up, configuring, or triggering toast notifications in Vue 3 components, composables, or API interceptors using the vue3-toastify library. Triggers on success, error, warning toasts, custom toast configurations, and async promise-based toasts.
---

# Boas Práticas para Notificações Toast com vue3-toastify no Vue 3

## Objetivo
Estabelecer um padrão robusto e consistente para implementar, configurar e disparar notificações toast assíncronas e dinâmicas utilizando `vue3-toastify` no frontend Vue 3, alinhado com o design system do Engeapp.

## Instruções

### 1. Instalação e Configuração Global
Garanta que `vue3-toastify` está instalado e configure-o globalmente na inicialização da aplicação Vue (`app.ts` ou `main.ts`):

```typescript
import Vue3Toastify, { type ToastContainerOptions } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

app.use(Vue3Toastify, {
  autoClose: 3000,
  position: 'top-right',
  theme: 'colored',
  clearOnUrlChange: false,
} as ToastContainerOptions);
```

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

### 3. Toasts Assíncronos Baseados em Promises (`toast.promise`)
Para tarefas de longa duração, use `toast.promise` para exibir estados de carregamento, sucesso e erro de forma dinâmica. Para SALVAR dados de página, envolva o toast na promessa do save da store MaxPinia (`saveInServer()`) — nunca use `axios.post` manual (o auto-save/save da store já é o cliente HTTP correto).

```typescript
import { toast } from 'vue3-toastify';

// `projectStore` é uma store @maxvue/max-pinia; saveInServer() persiste o estado da página.
const salvarPromise = projectStore.saveInServer();

toast.promise(
  salvarPromise,
  {
    pending: 'Salvando dados do projeto...',
    success: 'Projeto salvo com sucesso! 👌',
    error: {
      render({ data }: any) {
        // Extrai mensagens de validação do backend AdonisJS se disponível
        const message = data?.response?.data?.message || 'Falha ao salvar o projeto.';
        return message;
      }
    }
  },
  {
    position: 'top-right',
  }
);
```

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

### 5. Tratamento Centralizado de Erros → Toast
Para exibir toasts automáticos em erros HTTP, NÃO registre um `axios.interceptors.response` próprio nesta (nem em qualquer) skill. A aplicação já possui **um único cliente HTTP compartilhado** (o mesmo usado por `@maxvue/max-use`/`@maxvue/max-pinia`); o mapeamento de status → toast deve viver ali, em um só lugar.

> **Atenção (ponto único):** Registrar um segundo interceptor que trate 401/422/500 em paralelo gera toasts duplicados e lógica conflitante. As skills `vue-tenant-client-context` e `vue-sentry` também tocam o ciclo de resposta — todas apenas reusam o cliente compartilhado, sem adicionar interceptores próprios.

O mapeamento centralizado (definido uma única vez, no setup do cliente HTTP compartilhado) deve seguir este formato:
```typescript
import { toast } from 'vue3-toastify';

// Handler registrado UMA vez no cliente HTTP compartilhado da aplicação (não em cada skill).
function mapHttpErrorToToast(error: any): void {
  if (error?.response) {
    const status = error.response.status;
    const message = error.response.data?.message || 'Ocorreu um erro inesperado.';

    if (status === 422) {
      toast.warning(`Erro de validação: ${message}`);
    } else if (status === 500) {
      toast.error(`Erro no servidor: ${message}`);
    } else if (status === 401) {
      toast.error('Sessão expirada. Por favor, faça login novamente.');
    }
  } else {
    toast.error('Erro de rede. Verifique sua conexão com a internet.');
  }
}
```

## Restrições
- **Não** exiba exceções brutas do sistema para o usuário em toasts de erro. Sempre mapeie para mensagens amigáveis e claras.
- **Não** duplique estilos de toasts globais inline. Mantenha os estilos visuais consistentes entre todos os componentes.
- **Não** bloqueie a interação do usuário para toasts informativos; utilize um tempo razoável de fechamento automático (tipicamente entre 1500ms e 3000ms).
- **Não** use Options API em componentes Vue que lidam com toasts; sempre use `<script setup lang="ts">`.
- Os comentários do código nos componentes Vue devem ser em Português do Brasil (pt-BR).
