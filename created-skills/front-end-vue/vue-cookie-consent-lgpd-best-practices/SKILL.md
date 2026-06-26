---
name: vue-cookie-consent-lgpd-best-practices
description: Use when implementing, updating, or reviewing cookie consent banners, managing user cookies, storing user preferences in compliance with LGPD, or utilizing the universal-cookie package in Vue 3. Triggers on LGPD banner creation, cookie preference updates, and universal-cookie wrapper setup.
---

## Objetivo
Fornecer diretrizes sólidas e padrões consistentes para o gerenciamento de cookies, banners de consentimento e conformidade com a LGPD (Lei Geral de Proteção de Dados) no frontend Vue 3 utilizando o pacote `universal-cookie` no ecossistema Engeapp.

## Instruções

## 1. Arquitetura de Estado das Preferências de Cookies (Pinia Store)
Crie uma store centralizada no Pinia para gerenciar os estados de consentimento do usuário e sincronizar as preferências. Em `resources/Stores/Setting/useCookieConsent.Store.ts`:
- Defina um estado reativo para cada categoria de cookies: `essential` (sempre verdadeiro), `analytics` (estatísticas) e `marketing`.
- Use uma flag `consented` para rastrear se o usuário já interagiu com o banner.
- Sincronize o estado com o `universal-cookie` para persistir as escolhas do usuário (ex: expiração de 365 dias).
- Forneça opções para "Aceitar Todos", "Rejeitar Todos" ou salvar configurações granulares.

### Boilerplate do Padrão da Store:
```typescript
import Cookies from 'universal-cookie';

const cookies = new Cookies();
const COOKIE_NAME = 'engeapp_cookie_consent';

export interface CookiePreferences {
    essential: boolean;
    analytics: boolean;
    marketing: boolean;
}

export const useCookieConsentStore = defineStore('cookieConsent', () => {
    const consented = ref<boolean>(false);
    const preferences = ref<CookiePreferences>({
        essential: true,
        analytics: false,
        marketing: false,
    });

    function init() {
        const saved = cookies.get(COOKIE_NAME);
        if (saved) {
            preferences.value = { ...preferences.value, ...saved };
            consented.value = true;
        }
    }

    function savePreferences(newPrefs: Partial<CookiePreferences>) {
        preferences.value = {
            ...preferences.value,
            ...newPrefs,
            essential: true // Sempre verdadeiro
        };
        consented.value = true;
        cookies.set(COOKIE_NAME, preferences.value, {
            path: '/',
            maxAge: 31536000, // 1 ano
            sameSite: 'lax',
            secure: window.location.protocol === 'https:'
        });
        
        applyTrackingScripts();
    }

    function acceptAll() {
        savePreferences({ analytics: true, marketing: true });
    }

    function rejectAll() {
        savePreferences({ analytics: false, marketing: false });
    }

    function applyTrackingScripts() {
        if (preferences.value.analytics) {
            // Habilita scripts de terceiros (ex: Google Analytics, Hotjar)
        } else {
            // Desabilita ou remove cookies/scripts de terceiros
        }
    }

    return {
        consented,
        preferences,
        init,
        savePreferences,
        acceptAll,
        rejectAll
    };
});
```

## 2. Componente de UI do Banner de Consentimento (Implementação `.vue`)
Garantir que os componentes sigam a estrutura SFC do Engeapp:
- **Ordem:** `<template>`, `<script setup lang="ts">`, `<style scoped lang="scss">`.
- **Formatação:** Mantenha todos os atributos das tags na mesma linha no `<template>`, sem quebras de linha.
- **Estilo:** Use SCSS scoped com variáveis para animações e transições suaves.

### Checklist de Design do Componente:
- **Layout não-bloqueante:** Posicionado como um banner flutuante ou barra inferior.
- **Preferências granulares:** Interface do tipo accordion ou modal que permita ao usuário ativar/desativar diferentes categorias de cookies.
- **Ações Claras:** Botões separados e claros para "Aceitar Todos", "Rejeitar Todos" e "Personalizar".

## 3. Gerenciamento Dinâmico de Scripts de Rastreamento
Scripts como o Google Tag Manager ou Hotjar devem ser bloqueados até que o consentimento seja concedido:
- Verifique `preferences.analytics` e `preferences.marketing` antes de injetar scripts de rastreamento de terceiros.
- Forneça métodos utilitários na store para inicializar tags dinamicamente.

## Restrições
- **Nunca** armazene informações pessoalmente identificáveis (PII) nos cookies.
- **Nunca** defina cookies `essential` como falsos; eles devem estar ativados por padrão.
- Não importe helpers de reatividade do Vue (ex: `ref`, `computed`) manualmente se o auto-import estiver ativo no `vite.config.ts`.
- Certifique-se de que todos os comentários nos componentes Vue e stores estejam escritos em Português do Brasil (`pt-BR`).
- Todas as declarações de atributos HTML nas tags Vue `<template>` devem permanecer em uma única linha (sem quebra de linha de atributos).
