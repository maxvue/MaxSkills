---
name: vue-frontend-bug-fixing-best-practices
description: "Use when diagnosing and fixing front-end bugs in Engeapp (Vue 3 + TS + MaxPinia + UnoCSS + MaxComponentsUi + MaxUse): reactivity issues, TS errors, store cache/auto-save, HMR, and routing. Covers objectives, project stack, and frontend bug fixing."
author: Johnattas Conrady Gomes Santana
---
# Correção de Bugs do Front-End Vue — Melhores Práticas

Skill especializada para diagnosticar e corrigir bugs do front-end no projeto EngeApp seguindo o ciclo: **evidência → classificação → diagnóstico de causa raiz → correção → validação**.

## Objetivo

Diagnosticar e corrigir bugs do front-end em projetos Vue 3 + TypeScript + MaxPinia (`@maxvue/max-pinia`) + UnoCSS + MaxComponentsUi + MaxUse, atacando a causa raiz em vez de mascarar sintomas, respeitando convenções e bibliotecas próprias do ecossistema.

## Stack e Arquitetura do Front-End

| Tecnologia | Versão / Padrão | Convenção Obrigatória |
|---|---|---|
| **Vue 3** | Composition API | `<script setup lang="ts">` estrito em todos os componentes |
| **TypeScript** | Strict Mode | Tipagem estrita; validação via `npm run typecheck:tsgo` |
| **@maxvue/max-pinia** | Store local | Camada de cache + auto-save debounced. Todo GET/save de página passa por store MaxPinia |
| **@maxvue/max-use** | Lib local | Composables (`useRefCachedApi`), helpers no namespace `_`, rotas Ziggy via `apiGetRoute`/`apiPostRoute` |
| **@maxvue/max-components-ui** | Lib local | Componentes `Max*` auto-importados. Em código novo, use `MaxModal`/`MaxDialog` (não PrimeVue direto) |
| **UnoCSS** | Attributify | Preset `presetMaxUno` — sem classes utilitárias Tailwind cruas |
| **Vite & Unplugin** | Auto-import | Auto-import de composables, helpers e componentes `Max*` |

---

## Fluxo de Diagnóstico e Correção

### 1. Diagnóstico por Domínio

- **Reatividade & Estado:**
  - Evite mutações diretas fora do ciclo do Vue ou perda de reatividade por desestruturação de `reactive`/`ref` (use `toRefs` ou `storeToRefs`).
  - Em stores MaxPinia: verifique `isCached = ref(true)` e `getKey() = store.$id + (store.id ?? options.id)`.
- **Comunicação HTTP & Rotas:**
  - As funções `apiGetRoute` e `apiPostRoute` recebem o **nome Ziggy pontilhado** da rota (ex: `'client.data'`), nunca caminhos `/api/...`.
  - A autenticação é baseada em cookie de sessão (`guard web`). O MaxUse já inclui `withCredentials: true`.
- **Componentes e Modais:**
  - Use os componentes `Max*` de `@maxvue/max-components-ui` (ex: `MaxModal`, `MaxInputText`, `MaxButton`, `MaxToast`).
  - Evite imports diretos de componentes PrimeVue em código novo.
- **Estilização e UnoCSS:**
  - Em `<style lang="scss" scoped>`, use `:deep()` apenas quando necessário estilizar slots/filhos de componentes Max*.

---

### 2. Regras de Correção

1. **Ataque a Causa Raiz:** Nunca mascare valores nulos no template com `user?.profile?.name || 'N/A'` se o bug real for ausência de carregamento do perfil.
2. **Respeite o Padrão do SFC:**
   ```vue
   <template>
     <!-- template inline e acessível -->
   </template>

   <script setup lang="ts">
   // imports, props, emits, stores e lógica reativa
   </script>

   <style lang="scss" scoped>
   // estilos complementares
   </style>
   ```
3. **Plano de Correção:** Apresente sempre a causa raiz, os arquivos afetados e o impacto antes de aplicar edições de grande porte.

---

### 3. Validação Pós-Correção

```bash
# 1. Checagem de tipos estrita
npm run typecheck:tsgo

# 2. Linting de código
npm run lint

# 3. Testes unitários (quando aplicável)
npm run test
```

---

### 4. Atualização de Bibliotecas Locais (`storage/libs/`)

Se o defeito estiver no código-fonte das bibliotecas locais (`MaxComponentsUi`, `MaxUse`, `MaxPinia`):
1. Altere o fonte em `storage/libs/<lib>/src/`.
2. Execute `npm run build` dentro da pasta da biblioteca.
3. Reinicie o servidor de desenvolvimento do EngeApp.

> *Nota: Os diretórios em `storage/libs/` são symlinks para os repositórios correspondentes.*

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR).
- **Sem Edição Manual de DTOs:** Nunca edite `resources/Types/generated.d.ts` manualmente — ele é gerado pelo backend.
- **Sem `axios` Direto:** Mutações de API devem usar `apiPostRoute`/`apiPutRoute` do `@maxvue/max-use`.
- **Sem Rotas Crus:** Nunca passe caminhos `/api/...` para os helpers de rotas.
