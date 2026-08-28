---
name: technical-documentation-best-practices
description: "Use when writing or improving technical documentation: READMEs, API endpoints, UI components, ADRs, changelogs, JSDoc/TSDoc, and Laravel/Vue doc patterns. Covers best practices, progressive disclosure, and templates."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Documentação Técnica

## Objetivo

Fornecer padrões, fluxos e templates reutilizáveis para produzir documentação técnica clara, manutenível e estruturada no ecossistema Engeapp (Laravel 13, Vue 3, TypeScript, MaxPinia e pacotes `@maxvue/*`). O idioma padrão de escrita e conversação é Português Brasileiro (pt-BR).

## Instruções

### 1. Princípios e Estrutura

1. **Audiência Primeiro:** Foque na necessidade de quem lê (desenvolvedor frontend/backend, integrador ou mantenedor).
2. **Hierarquia Rígida:** `#` (título único), `##` (seções principais), `###` (subseções). Nunca pule níveis.
3. **Código Funcional:** Especifique a linguagem nos blocos (```typescript, ```php, ```json, ```bash). Use dados realistas, nunca pseudocódigo genérico.
4. **Convenções do Ecossistema:**
   - **Backend:** Laravel 13 / PHP 8.4, rotas nomeadas Ziggy, migrations e models Eloquent.
   - **Frontend:** Vue 3 SPA (`<script setup lang="ts">`), stores `@maxvue/max-pinia`, helpers `@maxvue/max-use` (`apiGetRoute`, `apiPostRoute`) e componentes `@maxvue/max-components-ui`.

---

### 2. Checklist de Qualidade

- [ ] **Audiência e Contexto:** Objetivo e pré-requisitos claros.
- [ ] **Exemplos Executáveis:** Blocos de código com TypeScript/PHP estritos e tipos reais.
- [ ] **Rotas e APIs:** Nomes Ziggy pontilhados documentados (ex.: `'client.data'`), sem paths crus `/api/...`.
- [ ] **TSDoc / JSDoc:** `@param`, `@returns`, `@throws` e `@example` em APIs públicas.
- [ ] **Diagramas Mermaid:** Diagramas de fluxo/arquitetura claros quando o processo envolver múltiplos estágios.

---

### 3. Documentação TypeScript (JSDoc / TSDoc)

Documente todas as APIs públicas de composables, helpers e componentes:

```typescript
/**
 * Busca dados cacheados em localStorage com revalidação assíncrona.
 *
 * @template T - Tipo estruturado dos dados retornados.
 * @param routeName - Nome da rota Ziggy (ex: 'client.data').
 * @param options - Opções de cache e sincronização.
 * @returns Ref reativa com o valor sincronizado.
 *
 * @example
 * ```typescript
 * const client = useRefCachedApi<ClientData>('client.data', { defaultValue: null });
 * ```
 */
export function useRefCachedApi<T>(routeName: string, options?: UseCachedApiOptions<T>): Ref<T>;
```

---

### 4. Templates Padronizados

#### A. README.md de Projeto / Pacote

````markdown
# Nome do Pacote / Módulo

Breve descrição do propósito e escopo técnico.

## 🚀 Instalação & Setup

```bash
pnpm install @maxvue/nome-do-pacote
```

## 💡 Uso Rápido

```typescript
import { useExemplo } from '@maxvue/nome-do-pacote';

const { data, loading } = useExemplo();
```

## 📖 API & Configurações

| Prop / Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `modelValue` | `string` | `''` | Valor do input bidirecional |
| `disabled` | `boolean` | `false` | Desabilita interação |

## 🧪 Testes

```bash
pnpm test
```
````

#### B. Documentação de Endpoint de API

````markdown
### Endpoint: `cliente.data` (`GET`)

Busca dados cadastrais e contratos do cliente autenticado.

#### Autenticação & Consumo no Front
- Consumido via store `@maxvue/max-pinia` (`options.get.route: 'cliente.data'`) ou `apiGetRoute('cliente.data', { id })`.
- Autenticação por sessão web/cookie.

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | `string (ULID)` | Sim | Identificador do cliente |

#### Resposta de Sucesso (200 OK)

```json
{
  "data": {
    "id": "01HQXYZ...",
    "name": "Empresa Exemplo",
    "document": "12.345.678/0001-90"
  }
}
```
````

#### C. Documentação de Componente Vue 3

````markdown
### `MaxCustomCard.vue`

Componente de cartão para exibição de métricas e ações rápidas.

#### Props

| Prop | Tipo | Padrão | Descrição |
|---|---|---|---|
| `title` | `string` | Obrigatório | Título principal do cartão |
| `loading` | `boolean` | `false` | Exibe skeleton loader |

#### Eventos (Emits)

| Evento | Payload | Descrição |
|---|---|---|
| `update:modelValue` | `string` | Disparado na alteração do valor |
| `confirm` | `void` | Disparado ao clicar na ação primária |

#### Exemplo de Uso

```vue
<template>
  <MaxCustomCard title="Faturamento" :loading="isPending" @confirm="onRefresh" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
const isPending = ref(false);
function onRefresh() {}
</script>
```
````

#### D. Registro de Decisão Arquitetural (ADR)

````markdown
# ADR-001: Adoção do MaxPinia para Cache de Telas

## Status
Aceito (2026-08)

## Contexto
Necessidade de persistência local offline/rápida com sincronização em segundo plano para o Engeapp.

## Decisão
Adotar `@maxvue/max-pinia` como padrão obrigatório para stores de leitura de página, utilizando `isCached = ref(true)` e chaves derivadas por `getKey() = store.$id + id`.

## Consequências
- **Positivas:** Redução de latência percebida e zero requisições redundantes de navegação.
- **Negativas:** Necessidade de gerenciar revalidação e invalidação de cache via store.
````

#### E. CHANGELOG.md

````markdown
# Changelog

Todas as alterações notáveis seguem o padrão [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] - 2026-08-27
### Adicionado
- Integração com `@maxvue/max-components-ui` v2.
### Corrigido
- Tratamento de timeout em workers Horizon na fila `gemini`.
````

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR).
- **Sem Rotas Crus:** Nunca documente rotas com paths diretos `/api/...` no frontend — use sempre os nomes Ziggy pontilhados.
- **Sem Libs Diretas de Terceiros:** Documente componentes `@maxvue/max-components-ui` e utilitários `@maxvue/max-use`, não bibliotecas subjacentes cruas.
- **Fidelidade ao Código:** Nunca invente parâmetros ou props inexistentes — valide antes no repositório.
