# Exemplo de Teste de Componente Vue 3 (Vitest + Vue Test Utils)

Este exemplo demonstra como testar um componente Vue 3 (`UserCard.vue`) que recebe propriedades (props), emite eventos, utiliza componentes de UI stubbados e simula interações do usuário.

O arquivo de teste vive em `tests/Js/` (único diretório coberto pelo `include` do `vitest.config.ts`) e importa o alvo por caminho relativo profundo até `resources/`, nunca colocalizado ao lado do SFC.

### Componente Alvo: `resources/Vue/Components/User/UserCard.vue`
```vue
<template>
  <div class="user-card" :class="{ 'is-admin': isAdmin }">
    <h2>{{ name }}</h2>
    <p>{{ email }}</p>
    
    <MaxButton label="Editar Usuário" icon="mdi:pencil" @click="editUser" />
    
    <MaxButton v-if="canDelete" label="Excluir" severity="danger" @click="confirmDelete" />
  </div>
</template>

<script setup lang="ts">
// MaxButton NÃO é importado: o unplugin-vue-components + MaxComponentsUiResolver
// (vite.config.ts) resolve os componentes Max* automaticamente no build real.

const props = withDefaults(defineProps<{
  name: string;
  email: string;
  isAdmin?: boolean;
  canDelete?: boolean;
}>(), {
  isAdmin: false,
  canDelete: false
});

const emit = defineEmits<{
  edit: [email: string];
  delete: [];
}>();

const editUser = () => {
  emit('edit', props.email);
};

const confirmDelete = () => {
  emit('delete');
};
</script>

<style scoped lang="scss">
.user-card {
  padding: 16px;
  border: 1px solid var(--surface-border);
  
  &.is-admin {
    border-color: var(--primary-color);
  }
}
</style>
```

---

### Arquivo de Teste: `tests/Js/userCard.test.ts`
```typescript
// @vitest-environment jsdom
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { config, mount } from '@vue/test-utils';
import { defineComponent, h } from 'vue';

import UserCard from '../../resources/Vue/Components/User/UserCard.vue';

// No build real, MaxButton é resolvido pelo unplugin-vue-components e nunca
// importado no SFC. Sob o vitest.config.ts esse resolver não existe, então
// registramos um stub global equivalente — sem alterar a convenção do componente.
config.global.components = {
    MaxButton: defineComponent({
        props: ['label', 'severity', 'icon'],
        setup: (props, { attrs }) => () => h('button', { class: 'max-button-stub', ...attrs }, props.label)
    })
};

// Função auxiliar para montar o componente com as props padrão do cenário
function mountUserCard(props: Record<string, any> = {}) {
    return mount(UserCard, {
        props: {
            name: 'João Silva',
            email: 'joao@engeapp.com.br',
            ...props
        }
    });
}

describe('UserCard.vue', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renderiza os dados do usuário corretamente', () => {
        const wrapper = mountUserCard();
        
        // Verifica se o nome e email são renderizados no HTML
        expect(wrapper.text()).toContain('João Silva');
        expect(wrapper.text()).toContain('joao@engeapp.com.br');
    });

    it('aplica a classe is-admin quando o usuário é administrador', () => {
        const wrapper = mountUserCard({ isAdmin: true });
        
        // Verifica se a classe CSS reativa foi aplicada
        expect(wrapper.classes()).toContain('is-admin');
    });

    it('não exibe o botão de exclusão por padrão', () => {
        const wrapper = mountUserCard();
        
        // Procura por botões que contenham o texto 'Excluir'
        const buttons = wrapper.findAll('.max-button-stub');
        const deleteButton = buttons.find(b => b.text().includes('Excluir'));
        
        expect(deleteButton).toBeUndefined();
    });

    it('exibe o botão de exclusão se canDelete for true', () => {
        const wrapper = mountUserCard({ canDelete: true });
        
        const buttons = wrapper.findAll('.max-button-stub');
        const deleteButton = buttons.find(b => b.text().includes('Excluir'));
        
        expect(deleteButton).toBeDefined();
    });

    it('emite o evento edit com o email do usuário ao clicar em editar', async () => {
        const wrapper = mountUserCard();
        
        // Encontra o botão de editar e dispara o clique
        const editButton = wrapper.findAll('.max-button-stub').find(b => b.text().includes('Editar Usuário'));
        expect(editButton).toBeDefined();
        
        await editButton!.trigger('click');
        
        // Verifica se o evento 'edit' foi emitido com o argumento correto
        expect(wrapper.emitted('edit')).toBeTruthy();
        expect(wrapper.emitted('edit')?.[0]).toEqual(['joao@engeapp.com.br']);
    });

    it('emite o evento delete ao clicar em excluir', async () => {
        const wrapper = mountUserCard({ canDelete: true });
        
        const deleteButton = wrapper.findAll('.max-button-stub').find(b => b.text().includes('Excluir'));
        expect(deleteButton).toBeDefined();
        
        await deleteButton!.trigger('click');
        
        // Verifica se o evento 'delete' foi disparado
        expect(wrapper.emitted('delete')).toBeTruthy();
    });
});
```
