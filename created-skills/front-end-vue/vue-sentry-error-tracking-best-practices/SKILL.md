---
name: vue-sentry-error-tracking-best-practices
description: Use when integrating, configuring, reviewing, or debugging Sentry error monitoring and performance tracking in a Vue 3 application. Triggers on Sentry initialization in Vue 3 (main.ts/app.ts), Sentry.init, capturing frontend exceptions, setting up Vue Router navigation tracking, Axios error breadcrumbs, and defining user context for error reporting.
---

# Boas Práticas para Rastreamento de Erros com Sentry no Vue 3

## Objetivo
Estabelecer diretrizes e padrões para integrar, configure e manter o Sentry para monitoramento de erros, rastreamento de navegação (breadcrumbs) e gravação de sessões de usuário em uma aplicação Vue 3, garantindo alta performance da aplicação, visibilidade de telemetria e conformidade com privacidade de dados (LGPD).

## Instruções

### 1. Instalação
Instale o pacote necessário do Sentry para Vue usando o gerenciador de pacotes do projeto (ex: npm ou yarn):
```bash
npm install @sentry/vue
```

### 2. Inicialização no Ponto de Entrada (app.ts / main.ts)
Inicialize o Sentry imediatamente antes de montar o aplicativo Vue. Importe o pacote `@sentry/vue` e inicialize-o com `Sentry.init`.

Exemplo de configuração em `resources/app.ts`:
```typescript
import { createApp } from 'vue';
import * as Sentry from '@sentry/vue';
import App from './App.vue';
import router from './Js/router';

const app = createApp(App);

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      Sentry.browserTracingIntegration({ router }),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    // Monitoramento de Performance (APM)
    tracesSampleRate: 0.1, // Ajuste com base no tráfego e orçamento
    // Gravação de Sessão (Replays)
    replaysSessionSampleRate: 0.1, // Taxa para sessões gerais
    replaysOnErrorSampleRate: 1.0, // Grava 100% das sessões com erro
    environment: import.meta.env.MODE || 'development',
  });
}

app.use(router).mount('#app');
```

### 3. Rastreamento de Contexto de Usuário e Tenancy
Associe erros a usuários ou organizações (tenants) específicos, garantindo a privacidade de dados. Faça isso dinamicamente usando `Sentry.setUser` assim que as informações da sessão do usuário forem carregadas.

Exemplo:
```typescript
import * as Sentry from '@sentry/vue';

export function setUserSentryContext(user: { id: string | number; role?: string }, tenantId: string | number) {
  Sentry.setUser({
    id: String(user.id),
  });
  
  Sentry.setTag('tenant_id', String(tenantId));
  if (user.role) {
    Sentry.setTag('user_role', user.role);
  }
}

export function clearUserSentryContext() {
  Sentry.setUser(null);
}
```

### 4. Breadcrumbs Personalizados com Axios
Para obter contexto preciso de requisições de API que falharam, integre o Sentry com interceptores do Axios, garantindo a remoção de informações sensíveis.

```typescript
import axios from 'axios';
import * as Sentry from '@sentry/vue';

axios.interceptors.request.use((config) => {
  Sentry.addBreadcrumb({
    category: 'api',
    message: `Enviando requisição ${config.method?.toUpperCase()} para ${config.url}`,
    level: 'info',
  });
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    Sentry.addBreadcrumb({
      category: 'api',
      message: `Requisição falhou: ${error.config?.method?.toUpperCase()} ${error.config?.url} - Status: ${error.response?.status}`,
      level: 'error',
      data: {
        status: error.response?.status,
        statusText: error.response?.statusText,
      },
    });
    return Promise.reject(error);
  }
);
```

### 5. Capturando Erros Manualmente
Use `Sentry.captureException` para capturar exceções de forma manual dentro de blocos catch:
```typescript
import * as Sentry from '@sentry/vue';

try {
  // executa alguma operação
} catch (error) {
  Sentry.captureException(error, {
    extra: {
      contextDetails: 'Detalhes adicionais para ajudar na depuração',
    },
  });
}
```

## Restrições
- **NÃO** insira a chave DSN de forma estática (hardcoded). Utilize variáveis de ambiente (ex: `import.meta.env.VITE_SENTRY_DSN`).
- **NÃO** envie Informações Pessoais Identificáveis (PII) ou tokens sensíveis (ex: senhas, cabeçalhos de autorização, dados de cartão de crédito) em tags, objetos de usuário ou breadcrumbs. Certifique-se de configurar `maskAllText: true` e `blockAllMedia: true` nas integrações de Session Replay.
- **NÃO** envie eventos para o Sentry em ambientes de desenvolvimento local. Faça a inicialização condicional ou verifique a presença da variável DSN antes de executar `Sentry.init`.
- **NÃO** configure 100% de monitoramento de transações (`tracesSampleRate: 1.0`) em produção a menos que expressamente solicitado, a fim de gerenciar e limitar os custos da conta Sentry. Use taxas de amostragem razoáveis (ex: `0.1` ou `0.2`).
