---
name: vue-draggable-next-best-practices
description: Use when implementing, configuring, reviewing, or debugging interactive drag-and-drop lists, item sorting, and board layouts using vue-draggable-next in Vue 3 components, and saving the sorted order to the Laravel backend. Triggers on draggable components, transition-group, event handlers (start, end, change), and syncing order changes.
---

# Melhores Práticas para Vue Draggable Next

## Objetivo
Padronizar a implementação de listas interativas do tipo arrastar e soltar (drag-and-drop) utilizando a biblioteca `vue-draggable-next` no Vue 3 (Composition API, TypeScript, SCSS) e garantir o salvamento em lote otimizado de elementos ordenados no backend Laravel utilizando transações (`DB::transaction`).

## Instruções

### 1. Implementação no Front-end (Vue 3 & TypeScript)
Ao criar ou editar componentes Vue (arquivos `.vue`) que exijam reordenação, siga estas diretrizes:
- **Ordem dos Blocos**: Siga a ordem estrita do SFC (Single-File Component): `<template>`, `<script setup lang="ts">` e `<style scoped lang="scss">`.
- **Importação do Componente**: Importe `VueDraggableNext` de `vue-draggable-next` (export nomeado) e registre-o localmente como `<draggable>`:
  ```typescript
  import { VueDraggableNext as draggable } from 'vue-draggable-next'
  ```
- **Reatividade e v-model**: Use `v-model` para vincular o array reativo. Isso garante que a reatividade do Vue atualize a ordem do array automaticamente:
  ```html
  <draggable v-model="items" ghost-class="ghost-item" drag-class="dragging-item" handle=".drag-handle" @change="onOrderChange">
  ```
- **Atributos Obrigatórios**:
  - `ghost-class`: Classe CSS aplicada ao espaço reservado (placeholder) de soltura.
  - `drag-class`: Classe CSS aplicada ao item que está sendo arrastado no momento.
  - `handle`: Seletor CSS para restringir o início do arrasto a um elemento de alça específico (ex: `".drag-handle"`).
- **Regra de Atributos em Linha Única**: Mantenha todos os atributos do componente `<draggable>` em uma única linha no template para seguir a convenção do Engeapp.
- **Slot Padrão (default)**: O `vue-draggable-next` usa o slot **default** com `v-for` para renderizar os elementos (NÃO o slot `#item`/`item-key`, que pertence ao `vuedraggable`/Sortable v4). Sempre forneça uma `:key` única:
  ```html
  <draggable v-model="items" handle=".drag-handle">
    <div v-for="element in items" :key="element.id" class="list-item">
      <span class="drag-handle">☰</span>
      <span>{{ element.title }}</span>
    </div>
  </draggable>
  ```
- **Manipulação de Alterações de Estado**: Use o evento `@change` para capturar atualizações de posição. O payload do evento contém uma propriedade `moved` com o `element`, `newIndex` e `oldIndex`.
- **Envio ao Backend (MaxPinia)**: NÃO faça `axios.post` manual. Toda alteração de dados de página passa por uma store `@maxvue/max-pinia`: vincule a lista a um campo **dentro de `store.data`** (ex.: `store.data.items`) e, no `@change`, atualize esse campo — o watcher interno do MaxPinia observa `cloneDeep(store.data)` (deep watch) e dispara o auto-save (debounced) na rota `options.save` automaticamente. Mutar propriedades top-level da store (ex.: `store.items`) **não** dispara o save.
  - **Atenção (list stores)**: NÃO defina as flags `isList`/`is_list` numa store cujo objetivo é persistir a reordenação — o MaxPinia trata `isList` como `isBlocked` e **pula** o auto-save. A store precisa de `isCached` + `options.get`/`options.save` (rotas em string) configurados para que o save ocorra.
  - **Indicador de salvamento**: leia o estado via objeto injetado `status` — `status.server.save.is_requesting` (ou `is_requesting_now`) — não use uma propriedade `isSaving` fabricada. **Nunca use Inertia.js.**

### 2. Implementação no Back-end (Laravel)
Para persistir os itens reordenados de forma eficiente:
- **Processamento em Lote**: Envie apenas a lista de IDs e seu novo índice de posição para o backend (ex: `[{ id: 10, position: 0 }, { id: 12, position: 1 }]`).
- **Validação**: Valide o payload com um FormRequest (ou `$request->validate()`).
- **Transações do Banco de Dados**: Envolva a atualização em lote em uma transação via `DB::transaction()` para garantir persistência atômica e consistente.
- **Atualizações com Eloquent**: Atualize os registros dentro da transação usando os models Eloquent (`App\Models\*`).

---

## Exemplos

### Frontend: Componente de Lista Reordenável (`TodoList.vue`)
```vue
<template>
  <div relative p-6 bg-surface text-default rounded-lg>
    <MaxTitle1 h2="Lista de Tarefas" mb-4 />
    <draggable v-model="todoItems" ghost-class="ghost-item" drag-class="dragging-item" handle=".drag-handle" @change="handleOrderChange" flex="~ col" gap-2>
      <div v-for="element in todoItems" :key="element.id" flex items-center px-4 py-3 bg-muted border="~ base rounded-md">
        <div class="drag-handle" mr-4 cursor-grab text-muted>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2 8a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm10-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0-3a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
          </svg>
        </div>
        <span text-base>{{ element.name }}</span>
      </div>
    </draggable>
    <div v-if="todosStore.status.server.save.is_requesting" absolute top-4 right-4 px-3 py-1 bg-primary text-white rounded text-xs>
      Salvando nova ordenação...
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VueDraggableNext as draggable } from 'vue-draggable-next'
import { useTodosStore } from '@/stores/todos'

interface TodoItem {
  id: number
  name: string
  position: number
}

// Store MaxPinia: faz o GET inicial dos dados e o auto-save (debounced) ao alterar store.data.
const todosStore = useTodosStore()

// Lista reativa vinda de store.data. O v-model do draggable reordena store.data.items,
// e o watcher interno (deep watch em cloneDeep(store.data)) dispara o auto-save em options.save.
const todoItems = computed<TodoItem[]>({
  get: () => todosStore.data.items,
  set: (value) => (todosStore.data.items = value),
})

// Indicador de salvamento: leia direto o objeto `status` injetado pelo MaxPinia
// (`todosStore.status.server.save.is_requesting`) no template — não fabrique um `isSaving` próprio.

// Reescreve as posições dentro de store.data.items; o MaxPinia detecta a mudança e salva.
const handleOrderChange = () => {
  todosStore.data.items = todoItems.value.map((item, index) => ({
    ...item,
    position: index,
  }))
}
</script>

<style scoped lang="scss">
.ghost-item {
  opacity: 0.5;
  border: 1px dashed var(--primary);
}

.dragging-item {
  opacity: 0.9;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.drag-handle {
  &:active {
    cursor: grabbing;
  }
}
</style>
```

### Frontend: Definição da Store MaxPinia (`stores/todos.ts`)
A store precisa de `isCached` e das rotas `options.get`/`options.save` (strings) para que o GET inicial e o auto-save funcionem. NÃO defina `isList`/`is_list` — isso bloquearia o save.
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface TodoItem {
  id: number
  name: string
  position: number
}

export const useTodosStore = defineStore('todos', () => {
  // Ativa o cache/persistência e o watcher de auto-save do MaxPinia.
  const isCached = ref(true)

  // A lista fica DENTRO de data para que o deep watch em cloneDeep(store.data) dispare o save.
  const data = ref<{ items: TodoItem[] }>({ items: [] })

  // Rotas em string: GET inicial e POST de auto-save (debounced).
  const options = ref({
    get: '/api/todos',
    save: '/api/todos/reorder',
  })

  return { isCached, data, options }
})
```

### Backend: FormRequest + Controller Laravel (`ReorderTodosRequest.php` / `TodosController.php`)
```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ReorderTodosRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'items' => ['required', 'array'],
            'items.*.id' => ['required', 'integer', 'min:1'],
            'items.*.position' => ['required', 'integer', 'min:0'],
        ];
    }
}
```

```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\ReorderTodosRequest;
use App\Models\Todo;
use Illuminate\Support\Facades\DB;

class TodosController extends Controller
{
    public function reorder(ReorderTodosRequest $request)
    {
        $items = $request->validated()['items'];
        $userId = $request->user()->id;

        // Transação para persistência atômica e consistente.
        DB::transaction(function () use ($items, $userId) {
            foreach ($items as $item) {
                Todo::where('id', $item['id'])
                    ->where('user_id', $userId)
                    ->update(['position' => $item['position']]);
            }
        });

        return response()->json(['message' => 'Ordem atualizada com sucesso!']);
    }
}
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Uso Estrito de Composition API**: NÃO use a Options API (`data`, `methods`, etc.).
- **Proibido Inertia.js**: Nunca importe ou use `@inertiajs/vue3`. A persistência da ordenação é feita pela store `@maxvue/max-pinia` (auto-save debounced para `/api/...`), nunca por `axios.post` manual.
- **Slot Padrão Obrigatório**: Use o slot default com `v-for` e `:key` única. NÃO use `item-key`/slot `#item` (isso é API do `vuedraggable`, não do `vue-draggable-next`).
- **Transições de CSS**: Ao envolver o `<draggable>` em transições, use `<transition-group>` dentro do componente ao invés de `<transition>`.
- **Transação de Banco Obrigatória**: NÃO execute atualizações de posição no Laravel sem usar transações de banco de dados (`DB::transaction`).
- **Chamada de Componente em Linha Única**: Garanta que a tag de abertura `<draggable>` e todas as suas propriedades fiquem em uma única linha no template HTML/Vue.
- **Comentários em Português**: Todos os comentários inseridos no código dentro do ecossistema do Engeapp DEVEM estar em português do Brasil (pt-BR).
