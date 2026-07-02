---
name: vue-cookie-consent-lgpd-best-practices
description: Use when implementing, updating, or reviewing cookie consent banners, managing user cookies, storing user preferences in compliance with LGPD in Vue 3. Triggers on LGPD banner creation, cookie preference updates, and consent persistence via MaxUse (useStorage).
---

# Boas Práticas para Consentimento de Cookies e LGPD no Vue

## Objetivo
Fornecer diretrizes sólidas e padrões consistentes para o gerenciamento de cookies, banners de consentimento e conformidade com a LGPD (Lei Geral de Proteção de Dados) no frontend Vue 3 utilizando o `useStorage` do MaxUse (`@maxvue/max-use`, que reexporta o `@vueuse/core`) para persistência. O pacote `universal-cookie` **não** está instalado no projeto — não o utilize.

## Instruções

## 1. Arquitetura de Estado das Preferências de Cookies (Pinia Store)
Crie uma store centralizada no Pinia para gerenciar os estados de consentimento do usuário e sincronizar as preferências. Em `resources/Stores/Setting/useCookieConsent.Store.ts`:
- Defina um estado reativo para cada categoria de cookies: `essential` (sempre verdadeiro), `analytics` (estatísticas) e `marketing`.
- Use uma flag `consented` para rastrear se o usuário já interagiu com o banner.
- Persista o estado com o `useStorage` do MaxUse (`@maxvue/max-use`) — ele sincroniza reativamente o ref com o `localStorage` do navegador, carregando o valor salvo automaticamente na inicialização.
- Forneça opções para "Aceitar Todos", "Rejeitar Todos" ou salvar configurações granulares.

### Boilerplate do Padrão da Store:
```typescript
import { defineStore } from 'pinia';
// MaxUse reexporta o @vueuse/core; useStorage vem do índice do MaxUse
import { useStorage } from '@maxvue/max-use';

const STORAGE_KEY = 'engeapp_cookie_consent';

export interface CookiePreferences {
    essential: boolean;
    analytics: boolean;
    marketing: boolean;
}

export const useCookieConsentStore = defineStore('cookieConsent', () => {
    // useStorage já carrega o valor persistido e mantém tudo sincronizado no localStorage
    const preferences = useStorage<CookiePreferences>(STORAGE_KEY, {
        essential: true,
        analytics: false,
        marketing: false,
    });
    const consented = useStorage<boolean>(`${STORAGE_KEY}_consented`, false);

    function savePreferences(newPrefs: Partial<CookiePreferences>) {
        preferences.value = {
            ...preferences.value,
            ...newPrefs,
            essential: true // Sempre verdadeiro
        };
        consented.value = true; // persistido automaticamente pelo useStorage

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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca** armazene informações pessoalmente identificáveis (PII) nos cookies.
- **Nunca** defina cookies `essential` como falsos; eles devem estar ativados por padrão.
- Não importe helpers de reatividade do Vue (ex: `ref`, `computed`) manualmente se o auto-import estiver ativo no `vite.config.ts`.
- Certifique-se de que todos os comentários nos componentes Vue e stores estejam escritos em Português do Brasil (`pt-BR`).
- Todas as declarações de atributos HTML nas tags Vue `<template>` devem permanecer em uma única linha (sem quebra de linha de atributos).
