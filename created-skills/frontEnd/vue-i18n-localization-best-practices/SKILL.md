---
name: vue-i18n-localization-best-practices
description: Use when implementing, configuring, customizing, or debugging internationalization (i18n) and localization features in Vue 3 applications, managing translation keys, using vue-i18n, formatting dates and currencies locally, or switching locales dynamically. Triggers on vue-i18n setup, $t usage, translation JSON files, and dynamic locale switching components.
---

## Objetivo
Estabelecer diretrizes consistentes e padrões arquiteturais para a implementação, gerenciamento e manutenção de internacionalização (i18n) e localização em aplicações Vue 3 no ecossistema Engeapp.

## Instruções
Ao implementar ou modificar configurações de múltiplos idiomas, siga as seguintes melhores práticas:

### 1. Inicialização do Projeto e Carregamento Dinâmico (Lazy Loading)
Não carregue todos os arquivos JSON de tradução de forma estática na inicialização da aplicação. Implemente o carregamento dinâmico e assíncrono para otimizar o tamanho do bundle e a performance.

```typescript
// i18n.ts
import { createI18n } from 'vue-i18n';

export const SUPPORT_LOCALES = ['pt-BR', 'en', 'es'];

export const i18n = createI18n({
  legacy: false, // Deve usar o modo Composition API
  locale: 'pt-BR',
  fallbackLocale: 'en',
  globalInjection: true,
  messages: {} // Inicialmente vazio, carregado dinamicamente
});

const loadedLanguages: string[] = [];

export function setI18nLanguage(locale: string) {
  i18n.global.locale.value = locale;
  // Persistimos o locale ativo apenas no cliente. Isso NAO faz os helpers de
  // @maxvue/max-use (apiGetRoute/apiPostRoute) enviarem Accept-Language — esse
  // mecanismo automatico nao existe no MaxUse. Para negociar o locale com o
  // backend Adonis, registre o cabecalho explicitamente no init da app via
  // setApiRequestConfig, pois so cabecalhos registrados por ali sao enviados:
  //   setApiRequestConfig({ headers: { 'Accept-Language': () => localStorage.getItem('locale') ?? 'pt-BR' } })
  localStorage.setItem('locale', locale);
  document.querySelector('html')?.setAttribute('lang', locale);
}

export async function loadLocaleMessages(locale: string) {
  if (i18n.global.locale.value === locale) {
    return Promise.resolve(setI18nLanguage(locale));
  }

  if (loadedLanguages.includes(locale)) {
    return Promise.resolve(setI18nLanguage(locale));
  }

  try {
    const messages = await import(`./locales/${locale}.json`);
    i18n.global.setLocaleMessage(locale, messages.default);
    loadedLanguages.push(locale);
    return setI18nLanguage(locale);
  } catch (error) {
    console.error(`Falha ao carregar mensagens do locale para: ${locale}`, error);
  }
}
```

### 2. Estrutura de Chaves de Tradução (JSON)
Organize as chaves de tradução em namespaces estruturados (por página/domínio) para garantir a manutenibilidade e evitar colisões de nomes.

```json
// locales/pt-BR.json
{
  "common": {
    "buttons": {
      "save": "Salvar Alterações",
      "cancel": "Cancelar"
    },
    "alerts": {
      "success": "Operação realizada com sucesso."
    }
  },
  "dashboard": {
    "welcome": "Bem-vindo de volta, {name}!",
    "status": {
      "active": "Ativo",
      "inactive": "Inativo"
    }
  }
}
```

### 3. Uso em Componentes Vue SFC (Composition API)
Sempre use a Composition API (`<script setup lang="ts">`). Estilize com UnoCSS no modo **attributify** (`presetMaxUno`) e tokens de tema — não use SCSS nem `<style scoped>`. Siga a ordem padrão de blocos: `<template>`, `<script>`.

```vue
<!-- MeuComponente.vue -->
<template>
  <div flex flex-col gap-4>
    <p>{{ $t('dashboard.welcome', { name: userName }) }}</p>
    <MaxButton :label="$t('common.buttons.save')" @click="saveChanges" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const userName = ref<string>('João Silva');

function saveChanges(): void {
  // Traduzir dentro do bloco de lógica
  console.log(t('common.alerts.success'));
}
</script>
```

### 4. Pluralização e Interpolação
- Use interpolação nomeada: `t('dashboard.welcome', { name: userName })`
- Use a sintaxe de pluralização do vue-i18n:
  ```json
  "emails": "nenhum e-mail | 1 e-mail | {count} e-mails"
  ```
  Uso no template (use `$t`/`t` com o `count`; o helper legado `$tc` esta deprecado no modo Composition API do vue-i18n v9+):
  ```html
  <p>{{ $t('dashboard.emails', { count: emailCount }, emailCount) }}</p>
  ```

### 5. Formatação de Datas e Moedas (API Intl)
Use os recursos de formatação nativos do Vue ou integrações diretas com a API `Intl` do navegador, utilizando o locale ativo do `vue-i18n`.

```typescript
// Usando a API Intl alinhada com o locale ativo
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat(locale.value, {
    style: 'currency',
    currency: locale.value === 'pt-BR' ? 'BRL' : locale.value === 'es' ? 'EUR' : 'USD'
  }).format(value);
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat(locale.value, {
    dateStyle: 'medium'
  }).format(date);
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** utilize a Options API nos componentes Vue ou definições de configuração do i18n no formato legado.
- **Não** importe arquivos de tradução de forma estática no ponto de entrada da aplicação (`app.ts`), exceto o locale base de fallback se for estritamente necessário.
- **Não** utilize strings de texto localizadas diretamente (hardcoded) dentro dos componentes. Todo texto visível deve ser referenciado usando chaves de tradução.
- **Não** quebre os atributos do template Vue em várias linhas. Mantenha todos os parâmetros na mesma linha (estilo inline).
- **Não** escreva comentários em outro idioma que não seja o Português do Brasil (pt-BR) dentro dos componentes Vue, mesmo ao implementar suporte a múltiplos idiomas.
