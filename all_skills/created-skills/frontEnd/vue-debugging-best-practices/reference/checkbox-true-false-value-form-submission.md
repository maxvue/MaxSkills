---
title: Checkbox true-value/false-value Not Submitted in Forms
impact: MEDIUM
impactDescription: true-value and false-value attributes don't affect native form submission - unchecked boxes send nothing
type: capability
tags: [vue3, v-model, forms, checkbox, form-submission]
---

# Checkbox true-value/false-value Not Submitted in Forms

**Impact: MEDIUM** - Vue's `true-value` and `false-value` attributes only affect the JavaScript binding, NOT native `<form>` submission. Unchecked checkboxes are never included in native form submissions by browsers, regardless of `false-value`.

This is a browser limitation, not a Vue issue. No engeapp esse fluxo não existe — não há `<form action>`/submit nativo nem `<input type="checkbox">`/`<input type="radio">` no projeto (`grep -rn '<form action' resources` = 0); tudo usa `MaxInputCheckbox` e persistência via `apiPostRoute`/MaxPinia. O ponto que importa aqui é transformar o estado booleano do checkbox no handler antes de enviar, não depender de um `false-value` implícito.

## Task Checklist

- [ ] Não confie em `false-value` para submissões — em `<form>` nativo ele nunca é enviado quando desmarcado
- [ ] No engeapp, transforme o estado do checkbox (`true`/`false`) no valor desejado (ex: `'yes'`/`'no'`) dentro do handler, antes de chamar `apiPostRoute`
- [ ] `true-value`/`false-value` só afetam o estado em JavaScript, nunca a submissão

**Problem - false-value not submitted (apenas em `<form>` nativo):**
```html
<script setup>
import { ref } from 'vue'

const status = ref('no')  // JavaScript value works correctly
</script>

<template>
  <form action="/api/update" method="POST">
    <!-- PROBLEM: When unchecked, nothing is submitted for this field -->
    <!-- Server receives no "status" field at all, not "no" -->
    <input type="checkbox" v-model="status" true-value="yes" false-value="no" name="status">
    <label>Active</label>
  </form>
</template>
```

**Solução real do engeapp - transforme o estado no handler antes do apiPostRoute:**
```html
<script setup>
import { ref } from 'vue'
import { apiPostRoute } from '@maxvue/max-use'

const isActive = ref(false)

async function submitForm() {
  // Transform checkbox state to desired value before sending
  const payload = {
    status: isActive.value ? 'yes' : 'no'
  }

  // No engeapp, mutações vão via apiPostRoute (nome de rota Ziggy pontilhado), não fetch cru
  await apiPostRoute('registro.update', payload)
}
</script>

<template>
  <MaxInputCheckbox v-model="isActive" label="Active" />
  <MaxButton @click="submitForm" label="Save" />
</template>
```

## Reference
- [Vue.js Form Input Bindings - Checkbox](https://vuejs.org/guide/essentials/forms.html#checkbox)
