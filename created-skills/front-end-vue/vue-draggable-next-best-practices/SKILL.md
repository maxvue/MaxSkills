---
name: vue-draggable-next-best-practices
description: Use when implementing, configuring, reviewing, or debugging interactive drag-and-drop lists, item sorting, and board layouts using vue-draggable-next in Vue 3 components, and saving the sorted order to the AdonisJS backend. Triggers on draggable components, transition-group, event handlers (start, end, change), and syncing order changes.
---

# Melhores Práticas para Vue Draggable Next

## Objetivo
Padronizar a implementação de listas interativas do tipo arrastar e soltar (drag-and-drop) utilizando a biblioteca `vue-draggable-next` no Vue 3 (Composition API, TypeScript, SCSS) e garantir o salvamento em lote otimizado de elementos ordenados no backend AdonisJS utilizando transações.

## Instruções

### 1. Implementação no Front-end (Vue 3 & TypeScript)
Ao criar ou editar componentes Vue (arquivos `.vue`) que exijam reordenação, siga estas diretrizes:
- **Ordem dos Blocos**: Siga a ordem estrita do SFC (Single-File Component): `<template>`, `<script setup lang="ts">` e `<style scoped lang="scss">`.
- **Importação do Componente**: Importe `draggable` de `vue-draggable-next` como uma importação nomeada:
  ```typescript
  import { draggable } from 'vue-draggable-next'
  ```
- **Reatividade e v-model**: Use `v-model` para vincular o array reativo. Isso garante que a reatividade do Vue atualize a ordem do array automaticamente:
  ```html
  <draggable v-model="items" item-key="id" ghost-class="ghost-item" drag-class="dragging-item" handle=".drag-handle" @change="onOrderChange">
  ```
- **Atributos Obrigatórios**:
  - `item-key`: Uma string que representa o identificador único dos elementos (geralmente `"id"`).
  - `ghost-class`: Classe CSS aplicada ao espaço reservado (placeholder) de soltura.
  - `drag-class`: Classe CSS aplicada ao item que está sendo arrastado no momento.
  - `handle`: Seletor CSS para restringir o início do arrasto a um elemento de alça específico (ex: `".drag-handle"`).
- **Regra de Atributos em Linha Única**: Mantenha todos os atributos do componente `<draggable>` em uma única linha no template para seguir a convenção do Engeapp.
- **Slot de Item**: Use o slot `#item` para renderizar os elementos da lista. Sempre desestruture `{ element, index }`:
  ```html
  <template #item="{ element, index }">
    <div class="list-item">
      <span class="drag-handle">☰</span>
      <span>{{ element.title }}</span>
    </div>
  </template>
  ```
- **Manipulação de Alterações de Estado**: Use o evento `@change` para capturar atualizações de posição. O payload do evento contém uma propriedade `moved` com o `element`, `newIndex` e `oldIndex`.
- **Envio ao Backend**: Envie a nova ordenação ao backend no evento `@change` usando `axios.post` com a rota gerada por `apiGetRoute` do `@maxvue/max-use`. Exiba sobreposições/indicadores de salvamento para evitar cliques duplos. **Nunca use Inertia.js.**

### 2. Implementação no Back-end (AdonisJS)
Para persistir os itens reordenados de forma eficiente:
- **Processamento em Lote**: Envie apenas a lista de IDs e seu novo índice de posição para o backend (ex: `[{ id: 10, position: 0 }, { id: 12, position: 1 }]`).
- **Transações do Banco de Dados**: Envolva a atualização em lote em uma transação via `db.transaction()` do Lucid para garantir persistência atômica e consistente.
- **Atualizações com Lucid ORM**: Atualize os registros dentro da transação usando o query builder do Lucid.

---

## Exemplos

### Frontend: Componente de Lista Reordenável (`TodoList.vue`)
```vue
<template>
  <div class="todo-list-container">
    <h2 class="title">Lista de Tarefas</h2>
    <draggable v-model="todoItems" item-key="id" ghost-class="ghost-item" drag-class="dragging-item" handle=".drag-handle" @change="handleOrderChange" class="draggable-list">
      <template #item="{ element }">
        <div class="todo-item">
          <div class="drag-handle">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M2 8a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm10-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
            </svg>
          </div>
          <span class="todo-text">{{ element.name }}</span>
        </div>
      </template>
    </draggable>
    <div v-if="isSaving" class="saving-overlay">
      Salvando nova ordenação...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { draggable } from 'vue-draggable-next'
import axios from 'axios'

interface TodoItem {
  id: number
  name: string
  position: number
}

const props = defineProps<{
  initialItems: TodoItem[]
}>()

// Inicializa a lista com base nas props
const todoItems = ref<TodoItem[]>([...props.initialItems])
const isSaving = ref<boolean>(false)

// Envia a nova ordenação para o backend
const handleOrderChange = async () => {
  isSaving.value = true

  // Mapeia a nova estrutura de ordenação para envio
  const payload = todoItems.value.map((item, index) => ({
    id: item.id,
    position: index,
  }))

  try {
    await axios.post(apiPostRoute('todos.reorder'), { items: payload })
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped lang="scss">
.todo-list-container {
  padding: 1.5rem;
  background-color: #1e1e2e;
  border-radius: 8px;
  color: #cdd6f4;
  position: relative;

  .title {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  .draggable-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .todo-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    background-color: #313244;
    border-radius: 6px;
    border: 1px solid #45475a;

    .drag-handle {
      cursor: grab;
      margin-right: 1rem;
      color: #a6adc8;

      &:active {
        cursor: grabbing;
      }
    }

    .todo-text {
      font-size: 1rem;
    }
  }

  .ghost-item {
    opacity: 0.5;
    background-color: #45475a;
    border: 1px dashed #f38ba8;
  }

  .dragging-item {
    opacity: 0.9;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  }

  .saving-overlay {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background-color: #a6e3a1;
    color: #11111b;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }
}
</style>
```

### Backend: Controller AdonisJS (`TodosController.ts`)
```typescript
import type { HttpContext } from '@adonisjs/core/http'
import vine from '@vinejs/vine'
import db from '@adonisjs/lucid/services/db'
import Todo from '#models/todo'

const reorderValidator = vine.compile(
  vine.object({
    items: vine.array(
      vine.object({
        id: vine.number().positive(),
        position: vine.number().min(0),
      })
    ),
  })
)

export default class TodosController {
  async reorder({ request, auth }: HttpContext) {
    const { items } = await request.validateUsing(reorderValidator)
    const userId = auth.user!.id

    await db.transaction(async (trx) => {
      for (const item of items) {
        await Todo.query({ client: trx })
          .where('id', item.id)
          .where('user_id', userId)
          .update({ position: item.position })
      }
    })

    return { message: 'Ordem atualizada com sucesso!' }
  }
}
```

---

## Restrições
- **Uso Estrito de Composition API**: NÃO use a Options API (`data`, `methods`, etc.).
- **Proibido Inertia.js**: Nunca importe ou use `@inertiajs/vue3`. Use `axios` com `apiPostRoute` do `@maxvue/max-use`.
- **Provedor de item-key Obrigatório**: Nunca omita o atributo `item-key` no componente `<draggable>`.
- **Transições de CSS**: Ao envolver o `<draggable>` em transições, use `<transition-group>` dentro do componente ao invés de `<transition>`.
- **Transação de Banco Obrigatória**: NÃO execute atualizações de posição no AdonisJS sem usar transações de banco de dados (`db.transaction`).
- **Chamada de Componente em Linha Única**: Garanta que a tag de abertura `<draggable>` e todas as suas propriedades fiquem em uma única linha no template HTML/Vue.
- **Comentários em Português**: Todos os comentários inseridos no código dentro do ecossistema do Engeapp DEVEM estar em português do Brasil (pt-BR).
