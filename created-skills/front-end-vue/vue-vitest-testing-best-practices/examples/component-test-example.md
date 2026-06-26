# Exemplo de Teste de Componente Vue 3 (Vitest + Vue Test Utils)

Este exemplo demonstra como testar um componente Vue 3 (`UserCard.vue`) que recebe propriedades (props), emite eventos, utiliza componentes de UI stubbados e simula interações do usuário.

### Componente Alvo: `UserCard.vue`
```vue
<template>
  <div class="user-card" :class="{ 'is-admin': isAdmin }">
    <h2>{{ name }}</h2>
    <p>{{ email }}</p>
    
    <MaxButton 
      label="Editar Usuário" 
      icon="mdi:pencil" 
      @click="editUser" 
    />
    
    <MaxButton 
      v-if="canDelete" 
      label="Excluir" 
      severity="danger" 
      @click="confirmDelete" 
    />
  </div>
</template>

<script setup lang="ts">
import { MaxButton } from '@maxvue/max-components-ui';

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

### Arquivo de Teste: `UserCard.test.ts`
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import UserCard from './UserCard.vue';

// Função auxiliar para montar o componente com stubs necessários
function mountUserCard(props: Record<string, any> = {}) {
    return mount(UserCard, {
        props: {
            name: 'João Silva',
            email: 'joao@engeapp.com.br',
            ...props
        },
        global: {
            stubs: {
                // Stubbando o MaxButton para evitar renderizar dependências pesadas de UI
                MaxButton: {
                    template: '<button class="max-button-stub" @click="$emit(\'click\')">{{ label }}</button>',
                    props: ['label', 'severity', 'icon']
                }
            }
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
