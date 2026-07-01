---
name: vue-bouncer-roles-permissions-integration-best-practices
description: Use when designing, implementing, configuring, or reviewing client-side roles and permissions checks in Vue 3 SFC templates or scripts, integrating with backend AdonisJS Bouncer policies, abilities, or dynamic user roles. Triggers on setting up custom directives (v-can), bouncer composables (useBouncer), Pinia auth store permission bindings, and Vue Router navigation guards utilizing metadata for authorization.
---

# Boas Práticas de Integração de Papéis e Permissões do Vue com Bouncer

## Objetivo
Estabelecer um mecanismo robusto, reativo e padronizado para validação de papéis (roles) e permissões (abilities) de usuário no frontend Vue 3, sincronizado com as políticas do AdonisJS Bouncer no backend e gerenciado dinamicamente com Pinia.

## Instruções

### 1. Sincronização de Tipos (TypeScript DTOs)
Defina uma estrutura compartilhada que represente as permissões do usuário. Essa estrutura deve corresponder ao formato de serialização do backend AdonisJS Bouncer.
* Use um mapa estritamente tipado onde as chaves são as ações/habilidades (abilities) e os valores são booleanos.
* Estenda a interface global `User` para incluir `permissions` e `role`.

Exemplo de estrutura em `/resources/Types/generated.d.ts`:
```typescript
declare global {
  type BouncerAbility = 'approveProject' | 'manageInstallations' | 'editProposal' | 'viewBilling';
  type UserRole = 'admin' | 'engenheiro' | 'instalador' | 'vendedor' | 'revisor' | 'cliente';

  interface User {
    id: string;
    name: string;
    email: string | null;
    avatar: string | null;
    role: UserRole;
    permissions: Record<BouncerAbility, boolean>;
    status: string;
  }
}
```

### 2. Vinculação na Store do Pinia (MaxPinia)
Não redefina a store de usuário aqui. Reuse a MESMA store de sessão `useUserStore` definida pela skill de auth-session, que já carrega os dados de sessão via `options.get` apontando para `apiGetRoute('/api/user/data')` e expõe `waitRequest`. As permissões e o papel já chegam dentro de `data` (formato serializado pelo AdonisJS Bouncer), portanto basta derivar getters de permissão a partir dessa store.
* A store é uma `@maxvue/max-pinia` Setup Store com `data: ref(null)` + `options.get` (sem GET manual).
* Adicione apenas os getters/funções de permissão (`hasPermission`, `hasRole`) à definição já existente, mantendo uma única fonte da verdade.

Exemplo (getters adicionados à store de sessão MaxPinia existente):
```typescript
import { defineStore } from '@maxvue/max-pinia';
import { ref, computed } from 'vue';
import { apiGetRoute } from '@maxvue/max-use';

export const useUserStore = defineStore('user', () => {
  // data + options.get definidos pela skill de auth-session; replicados aqui só por contexto
  const data = ref<User | null>(null);

  const permissions = computed(() => data.value?.permissions || {} as Record<BouncerAbility, boolean>);
  const role = computed(() => data.value?.role || null);

  const hasPermission = (ability: BouncerAbility): boolean => {
    // Administradores ignoram todas as verificações de permissão
    if (role.value === 'admin') return true;
    return !!permissions.value[ability];
  };

  const hasRole = (allowedRoles: UserRole[]): boolean => {
    if (!role.value) return false;
    return allowedRoles.includes(role.value);
  };

  return { data, permissions, role, hasPermission, hasRole };
}, {
  // mesma config da skill auth-session: carrega a sessão sem GET manual
  options: {
    get: () => apiGetRoute('/api/user/data'),
  },
});
```
> Importante: existe UMA única `useUserStore('user')`. Esta skill apenas acrescenta `permissions`, `role`, `hasPermission` e `hasRole`; o carregamento dos dados (`options.get` + `waitRequest`) pertence à store de sessão e não deve ser duplicado/conflitado.

### 3. Composable `useBouncer`
Implemente um hook cliente `useBouncer` em `/resources/Js/composables/useBouncer.ts` para facilitar checagens de autorização imperativas no bloco `<script setup>` de Single-File Components (SFC).
* O composable deve ser reativo a mudanças no usuário ativo ou no contexto do tenant.
* Deve retornar duas funções principais: `can` (valida permissão) e `is` (valida papel/role).

Exemplo:
```typescript
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

export function useBouncer() {
  const userStore = useUserStore();

  const can = (ability: BouncerAbility): boolean => {
    return userStore.hasPermission(ability);
  };

  const is = (allowedRoles: UserRole | UserRole[]): boolean => {
    const rolesArray = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    return userStore.hasRole(rolesArray);
  };

  return { can, is };
}
```

### 4. Diretiva Personalizada `v-can`
Registre uma diretiva personalizada global `v-can` no arquivo `/resources/app.ts` para fazer checagens declarativas de permissão nos templates Vue.
* **Modo Ocultar (Padrão):** Se o usuário não tiver a permissão, remova o elemento do DOM ou defina `display: none`.
* **Modo Desabilitar (Modifier `.disable`):** Se o usuário não tiver a permissão, adicione o atributo `disabled` e classes de estilo apropriadas (como `is-disabled`, `pointer-events-none`). Isso é crucial para manter a visibilidade do botão de ação, mas impedi-lo de ser clicado.
* **Reatividade obrigatória:** a diretiva NÃO pode avaliar apenas em `mounted`. Como as permissões mudam em login/logout/troca de tenant, aplique a checagem via um `watchEffect` (criado em `mounted`, descartado em `unmounted`) para que o elemento seja reavaliado sempre que a store de usuário mudar.

Exemplo de registro no `app.ts`:
```typescript
import { createApp, watchEffect, type WatchStopHandle } from 'vue';
import App from './App.vue';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

const app = createApp(App);

// Armazena o stop handle do efeito reativo por elemento
const stops = new WeakMap<HTMLElement, WatchStopHandle>();

const applyCan = (el: HTMLElement, binding: any) => {
  const userStore = useUserStore();
  const ability = binding.value as BouncerAbility;
  const modifiers = binding.modifiers;

  // watchEffect reage a mudanças de permissions/role (login/logout/troca de usuário)
  const stop = watchEffect(() => {
    const hasAccess = userStore.hasPermission(ability);

    if (hasAccess) {
      // Restaura o estado original quando a permissão passa a existir
      el.style.display = '';
      el.removeAttribute('disabled');
      el.classList.remove('opacity-50', 'pointer-events-none', 'cursor-not-allowed');
      return;
    }

    if (modifiers.disable) {
      el.setAttribute('disabled', 'true');
      el.classList.add('opacity-50', 'pointer-events-none', 'cursor-not-allowed');
    } else {
      el.style.display = 'none';
    }
  });

  stops.set(el, stop);
};

app.directive('can', {
  mounted(el: HTMLElement, binding) {
    applyCan(el, binding);
  },
  updated(el: HTMLElement, binding) {
    // Reavalia se o valor da ability mudar
    stops.get(el)?.();
    applyCan(el, binding);
  },
  unmounted(el: HTMLElement) {
    stops.get(el)?.();
    stops.delete(el);
  }
});
```

Exemplo de uso em templates:
```html
<!-- Comportamento padrão (oculta o elemento do DOM) -->
<MaxButton v-can="'approveProject'" label="Aprovar Projeto" />

<!-- Modificador disable (mantém visível mas desabilita interação) -->
<MaxButton v-can.disable="'editProposal'" label="Editar Proposta" />
```

### 5. Guards de Navegação no Vue Router
Garanta a segurança de navegação nas rotas do cliente usando metadados de rotas (`Route Metadata`).
* Defina `meta.requiresAuth` e `meta.requiredAbility` ou `meta.requiredRoles` nas rotas do roteador.
* Faça a validação assincronamente no hook global de navegação do roteador dentro de `/resources/Js/router.ts`.

Exemplo:
```typescript
import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/settings/billing',
      component: () => import('@/Vue/Pages/BillingPage.vue'),
      meta: {
        requiresAuth: true,
        requiredAbility: 'viewBilling',
        requiredRoles: ['admin']
      }
    }
  ]
});

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  // Aguarda a inicialização dos dados da store de usuário se necessário
  if (userStore.waitRequest) {
    await userStore.waitRequest();
  }

  const isAuthenticated = !!userStore.data;

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login' });
  }

  if (to.meta.requiredAbility) {
    const ability = to.meta.requiredAbility as BouncerAbility;
    if (!userStore.hasPermission(ability)) {
      return next({ name: 'unauthorized' });
    }
  }

  if (to.meta.requiredRoles) {
    const roles = to.meta.requiredRoles as UserRole[];
    if (!userStore.hasRole(roles)) {
      return next({ name: 'unauthorized' });
    }
  }

  next();
});
```

## Restrições
* **NÃO ignore a validação de Backend:** A checagem de autorização no frontend serve apenas para fins de melhoria de UX. Sempre garanta que controllers e middlewares no AdonisJS validem os dados e bloqueiem requisições de verdade.
* **Evite o uso de Papéis (Roles) Estáticos:** Dê preferência a checagens de *Abilities* (`can('edit')`) sobre *Roles* (`is('admin')`) sempre que possível. Papéis costumam mudar e adquirir flexibilidade dinâmica no futuro.
* **NÃO armazene dados sensíveis de forma insegura:** Qualquer dado renderizado condicionalmente na tela deve ser obtido através de APIs que validem os privilégios do usuário ativo no backend.
* **NÃO quebre diretivas de componentes personalizados:** Ao utilizar `v-can.disable` em componentes UI Vue customizados, garanta que esses componentes repassem a propriedade `disabled` e classes CSS aos elementos nativos HTML subjacentes.
