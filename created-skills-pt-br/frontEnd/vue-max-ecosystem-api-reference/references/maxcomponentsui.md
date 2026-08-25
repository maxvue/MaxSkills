# MaxComponentsUi — Catálogo de API (`@maxvue/max-components-ui`)

> Referência extraída do código-fonte (`/home/johnattas/GitHub/MaxComponentsUi/src`). Cada entrada traz
> Import, Propósito, Props, v-model, Emits, Slots, Expose e um Exemplo mínimo. Descrições em pt-BR.
>
> **InputBase**: a maioria dos `MaxInput*` embrulha o wrapper `InputBase.vue` e faz `v-bind="props"`,
> herdando o conjunto de props do InputBase (`label`, `icon`/`i`, `message`, `done`/`error`/`caution`,
> `required`, `dark`/`light`, `noStatus`, etc.) mesmo quando não redeclaradas. Onde relevante isso está
> anotado por componente.
>
> **Export público**: nem todo componente está no `index.ts` — `MaxTableColumn` e
> `MaxTogglePopover` não são exportados pelo entry principal; `MaxTextInputFloatLabel` está **deprecado**
> (renderiza `<div>` vazio); `MaxInputFile`/`MaxTableColumn` são placeholders só-estilo. Detalhes na
> seção final "Stores, Helpers e Exports públicos".

---

## Componentes (A → Z)

> Props herdadas do `InputBase` disponíveis na maioria dos `MaxInput*` mesmo quando não redeclaradas:
> `label`, `icon`/`i`, `iconLeft`, `iconRight`, `message`/`msg`, `iconMessage`, `done`, `error`, `caution`,
> `required`, `float`, `disabled`, `textCenter`, `textRight`, `dark`, `light`, `noDone`, `noCaution`,
> `noError`, `noStatus`, `noIcon`, `inLine`, `class`.

---

### MaxAiIcon
Import: `import { MaxAiIcon } from '@maxvue/max-components-ui'`
Propósito: ícone de "IA" animado (pulsação) que exibe estado de conclusão com um check.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| animate | boolean | true | não | anima o ícone (pulsação) |
| noAnimate | boolean | false | não | atalho para desativar a animação (animate=false) |
| done | boolean | false | não | exibe o ícone de check e para a animação |
| rotate | number | — | não | rotação do ícone em graus |
| flip | 'horizontal' \| 'vertical' \| 'h' \| 'v' \| 'x' \| 'y' \| 'xy' | — | não | inversão do ícone |
| size | string \| number | '1rem' | não | tamanho do ícone (px ou multiplicador) |
| scale | string \| number | — | não | alias para o tamanho |
| width | string \| number | — | não | largura específica |
| height | string \| number | — | não | altura específica |

**Exemplo**
```vue
<MaxAiIcon :size="2" :done="processado" />
```

---

### MaxAnimateFade
Import: `import { MaxAnimateFade } from '@maxvue/max-components-ui'`
Propósito: wrapper de transição/animação de fade que apenas renderiza o slot padrão (captura `$attrs`).

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo a ser animado |

**Exemplo**
```vue
<MaxAnimateFade>
    <div v-if="show">Conteúdo</div>
</MaxAnimateFade>
```

---

### MaxAuthCard
Import: `import { MaxAuthCard } from '@maxvue/max-components-ui'`
Propósito: card de autenticação (login) puramente visual — não conhece HTTP/router/store; emite `submit` e `social`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| title | string | 'Acesse sua conta' | não | título do header |
| subtitle | string | 'Bem-vindo de volta' | não | subtítulo do header |
| icon | string | 'mdi:account-circle-outline' | não | ícone do header |
| providers | AuthProvider[] | [] | não | provedores de login social (`{ id, label, icon, class? }`); vazio oculta a seção |
| loading | boolean | false | não | estado de carregamento do botão entrar |
| error | string | '' | não | mensagem de erro |
| showRemember | boolean | true | não | exibe o checkbox "lembrar-me" |
| registerTo | RouteLocationRaw | — | não | rota do "Cadastre-se" (vazio oculta o link) |
| forgotTo | RouteLocationRaw | — | não | rota do "Esqueci a senha" (vazio oculta o link) |
| labels | AuthLabels | — | não | sobrescreve textos pt-BR (`email, password, remember, forgot, submit, socialDivider, registerPrompt, register`) |
| identifier | 'email' \| 'email-phone' | 'email' | não | tipo do campo de identificação |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| email | string (default '') | valor do e-mail |
| password | string (default '') | valor da senha |
| remember | boolean (default true) | checkbox lembrar-me |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| submit | `{ email: string; password: string; remember: boolean }` | disparado ao enviar o formulário |
| social | `providerId: string` | disparado ao clicar em um provedor social |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| header | — | substitui o cabeçalho (MaxTitle2) |
| extra | — | conteúdo extra abaixo dos campos |
| footer | — | substitui o rodapé (link de cadastro) |

**Exemplo**
```vue
<MaxAuthCard
    v-model:email="email"
    v-model:password="senha"
    :loading="loading"
    :error="erro"
    forgot-to="/recuperar"
    register-to="/cadastro"
    @submit="entrar"
/>
```

---

### MaxBadgeComponent
Import: `import { MaxBadgeComponent } from '@maxvue/max-components-ui'`
Propósito: badge (etiqueta) com ícone e cores derivadas; encapsula `Badge`/`OverlayBadge` do PrimeVue e repassa `$attrs` para o `Badge`.

**Observação PrimeVue:** repassa `$attrs` ao `<Badge>` do PrimeVue via `v-bind="attrs"`. Cores de fundo podem ser definidas por atributos `color-*` (ex.: `color-blue-600`). Declara explicitamente as props abaixo; demais atributos caem no Badge.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| icon | string | — | não | nome do ícone (ex: 'mdi:home') |
| i | string | — | não | alias para o ícone |
| label | string | — | não | texto do badge |
| value | string | — | não | alias para o texto |
| msg | string | — | não | alias para o texto |
| mensagem | string | — | não | alias para o texto |
| text | string | — | não | alias para o texto |
| txt | string | — | não | alias para o texto |
| number | string | — | não | alias para o texto |
| rotate | number | — | não | rotação do ícone |
| flip | 'horizontal' \| 'vertical' \| 'h' \| 'v' \| 'x' \| 'y' \| 'xy' | — | não | inversão do ícone |
| size | string \| number | — | não | tamanho do ícone |
| scale | string \| number | — | não | alias para o tamanho |
| width | string \| number | — | não | largura específica |
| height | string \| number | — | não | altura específica |
| iconColor | string | — | não | cor do ícone / círculo lateral |
| iconValue | string | — | não | valor exibido no círculo lateral |
| badge | any | — | não | usado apenas com overlay=true |
| overlay | boolean | — | não | usa OverlayBadge |
| background | string | — | não | cor de fundo |
| textColor | string | — | não | cor do texto |

**Exemplo**
```vue
<MaxBadgeComponent label="Novo" icon="mdi:star" background="var(--blue-600)" />
```

---

### MaxButton
Import: `import { MaxButton } from '@maxvue/max-components-ui'`
Propósito: botão do design system (encapsula `Button` do PrimeVue); sem `label` cai para `MaxIconButton`. Suporta navegação (`route`) e `action`.

**Observação PrimeVue:** repassa `props as ButtonProps` ao `<Button>` do PrimeVue (`v-bind="props"`). As props são tipadas por `MaxButtonsType`, que estende `Omit<PrimeButtonProps, 'size' | 'iconPos'>`.

**Props** (via `MaxButtonsType`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string | — | não | texto do botão (sem label → renderiza MaxIconButton) |
| icon | string | — | não | ícone do botão |
| i | string | — | não | alias para o ícone |
| iconRight | string | — | não | ícone à direita |
| iconPos | 'left' \| 'right' | 'left' (computed) | não | posição do ícone |
| severity | 'secondary' \| 'success' \| 'info' \| 'whatsapp' \| 'warning' \| 'help' \| 'danger' \| 'contrast' | — | não | severidade/cor |
| size | string \| number \| null | — | não | tamanho do botão |
| sizeIcon | string \| number \| null | — | não | tamanho do ícone |
| iconSize | string \| number \| null | 1.4 | não | tamanho do ícone (alias) |
| loading | boolean | — | não | estado de carregamento |
| hoverScale | number \| null | — | não | ampliação ao passar o mouse |
| variant | 'outlined' \| 'text' \| 'link' | — | não | variante visual |
| dashed | boolean | — | não | borda tracejada com fundo transparente |
| uppercase | boolean | false | não | texto em maiúsculo |
| blank | string | — | não | link para abrir em nova aba |
| route | string \| null | null | não | rota de navegação (usa `goToRoute`) |
| data | any | {} | não | dados da navegação/action |
| params | any | {} | não | params da navegação |
| query | any | {} | não | query da navegação |
| transparent | boolean | — | não | fundo transparente |
| dark | boolean \| string \| number | undefined | não | ícone escuro relativo ao fundo |
| light | boolean \| string \| number | — | não | ícone claro relativo ao fundo |
| checked | boolean \| string \| number | — | não | ícone de checagem |
| plus | boolean \| string \| number | — | não | ícone de adição |
| hoverColor | string | — | não | cor no hover |
| rotate | number | — | não | rotação do ícone |
| flip | 'horizontal' \| 'vertical' \| 'h' \| 'v' \| 'x' \| 'y' \| 'xy' | — | não | inversão do ícone |
| scale | string \| number | — | não | alias para o tamanho |
| width / height | string \| number | — | não | dimensões específicas |
| action | `(data: { event: any; data?: any }) => void` | — | não | callback ao clicar (tem prioridade sobre o evento click, após route) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| click | `value: boolean` (true) | disparado no clique quando não há `route` nem `action` |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo customizado do botão (repassado ao slot #default do Button) |

**Exemplo**
```vue
<MaxButton label="Salvar" icon="mdi:content-save" :action="salvar" />
```

---

### MaxColorPicker
Import: `import { MaxColorPicker } from '@maxvue/max-components-ui'`
Propósito: seletor de cor (encapsula `ColorPicker` + `InputText` do PrimeVue dentro do `InputBase`) com validação de obrigatoriedade/comparação.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| defaultColor | string | 'ff0000' | não | cor exibida quando não há valor |
| format | 'hex' \| 'rgb' \| 'hsb' | 'hex' | não | formato da cor |
| inline | boolean | false | não | renderiza inline em vez de popup |
| panelClass | any | — | não | classe do painel |
| appendTo | 'body' \| 'self' \| string \| any | 'body' | não | destino do painel |
| autoZIndex | boolean | true | não | gerencia z-index automaticamente |
| baseZIndex | number | 0 | não | z-index base |
| inputId | string | — | não | id do input subjacente |
| ariaLabel | string | — | não | rótulo de acessibilidade |
| ariaLabelledby | string | — | não | associação de rótulo (a11y) |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |
| targetValue | string | — | não | valor para comparação de igualdade |
| placeholder | string | — | não | placeholder |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| (default) | any (default '') | valor da cor |

**Exemplo**
```vue
<MaxColorPicker v-model="cor" label="Cor" format="hex" />
```

---

### MaxDoneIcon
Import: `import { MaxDoneIcon } from '@maxvue/max-components-ui'`. Ícone estático de "concluído" (check verde em círculo). Sem props/emits/slots. Exemplo: `<MaxDoneIcon />`

---

### MaxEmptyDiv
Import: `import { MaxEmptyDiv } from '@maxvue/max-components-ui'`
Propósito: placeholder de "sem registros" com ícone e rótulo; totalmente configurável via `$attrs` e slots.

**Observação:** não declara `defineProps`; lê valores de `$attrs` (`icon`/`i`, `iconSize`, `label`). Suporta atributos de estilo `transparent` e `nospace`.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | substitui todo o conteúdo interno |
| icon | — | substitui apenas o ícone (default: MaxIcon com `attrs.icon ?? 'ph:empty'`) |
| label | — | substitui apenas o rótulo (default: `attrs.label ?? 'Sem Registros'`) |

**Exemplo**
```vue
<MaxEmptyDiv icon="ph:folder" label="Nada por aqui" />
```

---

### MaxErrorIcon
Import: `import { MaxErrorIcon } from '@maxvue/max-components-ui'`. Ícone estático de "erro" (X vermelho em círculo). Sem props/emits/slots. Exemplo: `<MaxErrorIcon />`

---

### MaxGrid
Import: `import { MaxGrid } from '@maxvue/max-components-ui'`
Propósito: container de grid flexível (flexbox com wrap e gap padronizado) com rótulo opcional posicionado na borda. (Arquivo `MaxGrid.vue`, classe `max-grid-cols`.)

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string \| null | — | não | rótulo exibido na borda superior |
| labelCenter | boolean | — | não | centraliza o rótulo |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo do grid |

**Exemplo**
```vue
<MaxGrid label="Endereço" gap-4>
    <MaxInputText label="Rua" v-model="rua" />
</MaxGrid>
```

---

### MaxGridCols
Import: `import { MaxGridCols } from '@maxvue/max-components-ui'`
Propósito: grid CSS de 24 colunas (`repeat(24, 1fr)`); repassa `$attrs` ao container.

**Observação:** não declara props; repassa `$attrs` ao `<div class="grid-cols">`.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | itens do grid (usam `span`/posicionamento por CSS) |

**Exemplo**
```vue
<MaxGridCols>
    <div style="grid-column: span 12">Metade</div>
</MaxGridCols>
```

---

### MaxIcon
Import: `import { MaxIcon } from '@maxvue/max-components-ui'`
Propósito: ícone padronizado que busca SVGs do Iconify (via `useIconStore`, com cache) e aplica cor/hover/tamanho. Sub-ícones opcionais de check/plus.

**Observação:** cores também podem ser definidas por atributos `color-*` / `hover-*` / `color-hover-*` (ex.: `color-blue-700`). `pointer` habilita cálculo de cor de hover.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| icon | string | — | não | nome do ícone (ex: 'mdi:home') |
| i | string | — | não | alias para o ícone |
| rotate | number | — | não | rotação em graus |
| flip | 'horizontal' \| 'vertical' \| 'h' \| 'v' \| 'x' \| 'y' \| 'xy' | — | não | inversão |
| size | string \| number | '1rem' | não | tamanho (px ou multiplicador em rem) |
| scale | string \| number | — | não | alias para o tamanho |
| width / height | string \| number | — | não | dimensões específicas |
| dark | boolean \| string \| number | undefined | não | escurecimento relativo ao fundo |
| light | boolean \| string \| number | undefined | não | clareamento relativo ao fundo |
| checked | boolean \| string \| number | — | não | exibe sub-ícone de check |
| plus | boolean \| string \| number | — | não | exibe sub-ícone de adição |
| color | string | undefined | não | cor do ícone |
| iconColor | string | — | não | cor do ícone (alias) |
| colorHover | string | — | não | cor no hover (atributo) |
| hoverColor | string | undefined | não | cor no hover |
| tooltip | string | — | não | tooltip (via v-tooltip) |

**Exemplo**
```vue
<MaxIcon icon="mdi:home" :size="1.5" color-blue-700 />
```

---

### MaxIconButton
Import: `import { MaxIconButton } from '@maxvue/max-components-ui'`
Propósito: botão de ícone clicável (encapsula `MaxIcon`); suporta navegação (`route`) e `action`, com escala no hover e debounce de reset.

**Observação:** props tipadas por `MaxButtonsType` (ver MaxButton). Repassa `{...props, ...attrs}` ao `MaxIcon` interno.

**Props** (via `MaxButtonsType`, destaques)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| icon / i | string | — | não | ícone |
| size | string \| number | — | não | tamanho (base 16px × size) |
| hoverScale | number \| null | 1.2 | não | escala ao passar o mouse |
| dark | boolean \| string \| number | 0.4 (efetivo) | não | escurecimento do ícone |
| light | boolean \| string \| number | — | não | clareamento do ícone |
| route | string \| null | — | não | rota de navegação |
| data / params / query | any | {} | não | dados da navegação/action |
| action | `(data: { event; data? }) => void` | — | não | callback ao clicar |
| _(demais props de MaxButtonsType)_ | | | | ver MaxButton |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| action | `value: boolean` (true) | disparado no clique quando não há `route` nem `action` |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | substitui o ícone padrão |

**Exemplo**
```vue
<MaxIconButton icon="mdi:delete" :action="remover" />
```

---

### MaxIconConfirm
Import: `import { MaxIconConfirm } from '@maxvue/max-components-ui'`
Propósito: botão de ícone que abre um popover de confirmação global (via `useConfirmStore`) posicionado sobre o próprio botão.

**Observação:** encapsula `MaxIconButton` (`v-bind="props"`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| icon / i | string | — | não | ícone |
| blank | string | — | não | link em nova aba |
| route | string | — | não | rota |
| data / params | any | — | não | dados |
| rotate | number | — | não | rotação |
| flip | 'horizontal' \| 'vertical' \| 'h' \| 'v' \| 'x' \| 'y' \| 'xy' | — | não | inversão |
| size / scale | string \| number | — | não | tamanho |
| message | string | 'Deseja continuar?' | não | mensagem de confirmação |
| messageIcon | string \| null | null | não | ícone da mensagem |
| acceptLabel | string | — | não | rótulo do botão "sim" |
| acceptIcon | string | — | não | ícone do botão "sim" |
| rejectProps | `{ label: string; icon?: string; action?: (event?) => void }` | `{ label: 'Não', action: () => {} }` | não | config do botão de rejeição |
| acceptProps | `{ label: string; icon?: string; action?: (event?) => void }` | `{ label: 'Sim', action: () => {} }` | não | config do botão de aceite |
| cancelIcon | string | — | não | ícone de cancelar |
| loading | boolean | false | não | estado de carregamento |
| width / height | string \| number | — | não | dimensões |
| dark | boolean \| string \| number | 0.4 | não | escurecimento do ícone |
| light | boolean \| string \| number | — | não | clareamento do ícone |
| checked | boolean \| string \| number | — | não | sub-ícone de check |
| plus | boolean \| string \| number | — | não | sub-ícone de adição |

**Exemplo**
```vue
<MaxIconConfirm
    icon="mdi:delete"
    message="Excluir este item?"
    :accept-props="{ label: 'Excluir', action: excluir }"
/>
```

---

### MaxInputAutoComplete
Import: `import { MaxInputAutoComplete } from '@maxvue/max-components-ui'`
Propósito: autocomplete com filtragem local de uma lista de opções (encapsula `AutoComplete` do PrimeVue dentro do `InputBase`, com `forceSelection`).

**Observação PrimeVue:** repassa `props` ao `<AutoComplete>` (`v-bind="props"`). Slot `#option` customizado (label + subLabel).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | '' | não | valor selecionado |
| options | any | [] | não | lista de opções para filtragem local |
| optionLabel | string | 'name' | não | campo usado como rótulo |
| optionValue | string | — | não | campo usado como valor |
| placeholder | string | 'SELECIONE' | não | placeholder |
| targetValue | string | — | não | valor de comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | any | objeto/valor selecionado (só emite quando não-string) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | atualização do valor selecionado |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| option | `slotProps` (via #option interno) | item da lista; usa `option[optionLabel]` e `option.subLabel` |

**Exemplo**
```vue
<MaxInputAutoComplete v-model="cidade" :options="cidades" option-label="nome" label="Cidade" />
```

---

### MaxInputAutoCompleteApi
Import: `import { MaxInputAutoCompleteApi } from '@maxvue/max-components-ui'`
Propósito: autocomplete que busca sugestões de uma API do backend Max (via `getCachedApiIDB` com `route` + `data`); filtra localmente os resultados.

**Observação PrimeVue:** props estendem `AutoCompleteProps` do PrimeVue (`interface props extends AutoCompleteProps`). O `<AutoComplete>` é configurado com `optionLabel="label"` e slot `#option` (usa `option.model` e `option.sub_label`).

**Props** (estende `AutoCompleteProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| route | string | — | sim | rota da API para buscar sugestões |
| data | any | {} | não | payload adicional enviado à API (dispara refetch ao mudar) |
| i | string | — | não | alias de ícone |
| icon | string | — | não | ícone (InputBase) |
| msg / message | string | — | não | mensagem de feedback |
| iconMessage | string | — | não | ícone da mensagem |
| done | string \| boolean \| null | undefined | não | estado de conclusão |
| error | string \| boolean \| null | — | não | erro |
| caution | string \| boolean \| null | undefined | não | atenção |
| required | boolean \| null | false | não | obrigatório |
| optionValue | string | — | não | campo do valor |
| optionLabel | string | 'label' | não | campo do rótulo |
| modelValue | AutoCompleteProps['modelValue'] | '' | não | valor selecionado |
| dropdownMode | — | 'blank' | não | (herdado de AutoCompleteProps) |
| multiple | boolean | false | não | (herdado) |
| minLength | number | 1 | não | (herdado) |
| delay | number | 300 | não | (herdado) |
| forceSelection | boolean | false | não | (herdado) |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | any | objeto selecionado (só emite quando não-string) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | atualização do valor selecionado |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| option | `slotProps` (via #option interno) | item; usa `option.model` e `option.sub_label` |

**Exemplo**
```vue
<MaxInputAutoCompleteApi
    v-model="cliente"
    route="clientes.buscar"
    :data="{ empresa_id: 1 }"
    label="Cliente"
/>
```

---

### MaxInputCep
Import: `import { MaxInputCep } from '@maxvue/max-components-ui'`
Propósito: entrada de CEP com máscara automática (`##.### - ###`) e validação via `cepIsValid`; emite `complete` quando válido.

**Observação PrimeVue:** encapsula `InputText` do PrimeVue com diretiva `v-maska` dentro do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | '' | não | valor do CEP (apenas números) |
| loading | boolean | false | não | estado de carregamento (ícone à direita) |
| targetValue | string | — | não | comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string | emite apenas os números do CEP |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | CEP apenas com números |
| complete | string | CEP completo/válido (apenas números) |

**Exemplo**
```vue
<MaxInputCep v-model="cep" label="CEP" @complete="buscarEndereco" />
```

---

### MaxInputCheckbox
Import: `import { MaxInputCheckbox } from '@maxvue/max-components-ui'`
Propósito: checkbox binário com rótulo (encapsula `Checkbox` do PrimeVue em modo `binary`).

**Observação PrimeVue:** repassa `props` ao `<Checkbox>` (`v-bind="props"`), com `binary` fixo. Atributo `circle` deixa a caixa arredondada.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | boolean | false | não | estado marcado |
| label | string | — | não | rótulo ao lado da caixa |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | boolean | estado do checkbox |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | boolean | atualização do estado |

**Exemplo**
```vue
<MaxInputCheckbox v-model="aceito" label="Aceito os termos" />
```

---

### MaxInputCoordinateDecimalLat
Import: `import { MaxInputCoordinateDecimalLat } from '@maxvue/max-components-ui'`
Propósito: entrada de latitude decimal com máscara dinâmica e validação de faixa (aprox. -33.8 a 5.3); emite `complete` quando válida.

**Observação PrimeVue:** encapsula `InputText` do PrimeVue com `v-maska` dentro do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string \| number | '' | não | valor da latitude |
| targetValue | string | — | não | comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string \| number | valor numérico da latitude |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | number \| string | valor da latitude |
| complete | number | disparado quando a latitude é válida |

**Exemplo**
```vue
<MaxInputCoordinateDecimalLat v-model="lat" label="Latitude" />
```

---

### MaxInputCoordinateDecimalLng
Import: `import { MaxInputCoordinateDecimalLng } from '@maxvue/max-components-ui'`
Propósito: entrada de longitude decimal com máscara `-7#.######` e validação de faixa (aprox. -74 a -32.4); emite `complete` quando válida.

**Observação PrimeVue:** encapsula `InputText` do PrimeVue com `v-maska` dentro do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string \| number | '' | não | valor da longitude |
| targetValue | string | — | não | comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string \| number | valor numérico (6 casas decimais) da longitude |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | number | valor da longitude (6 casas) |
| complete | number | disparado quando a longitude é válida |

**Exemplo**
```vue
<MaxInputCoordinateDecimalLng v-model="lng" label="Longitude" />
```

---

### MaxInputCpfCnpj
Import: `import { MaxInputCpfCnpj } from '@maxvue/max-components-ui'`
Propósito: entrada de CPF ou CNPJ com detecção automática do tipo pelo tamanho, máscara dinâmica e validação de dígito verificador; emite `complete` (debounced) quando completo.

**Observação PrimeVue:** encapsula `InputText` do PrimeVue com `v-maska` dentro do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string \| null | '' | não | documento (apenas números) |
| cpf | boolean | — | não | força máscara/validação de CPF |
| cnpj | boolean | — | não | força máscara/validação de CNPJ |
| targetValue | string | — | não | comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string | documento apenas com números (11 ou 14 dígitos) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | documento apenas com números |
| complete | string | disparado (debounce 500ms) quando o documento é válido |

**Exemplo**
```vue
<MaxInputCpfCnpj v-model="documento" label="CPF/CNPJ" @complete="validar" />
```

---

### MaxInputDatePicker
Import: `import { MaxInputDatePicker } from '@maxvue/max-components-ui'`
Propósito: seletor de data (encapsula `DatePicker` do PrimeVue dentro do `InputBase`); sincroniza string `YYYY-MM-DD HH:mm:ss` ↔ `Date` interno.

**Observação PrimeVue:** repassa `props` ao `<DatePicker>` (`v-bind="props"`) com `dateFormat` default `'dd/mm/yy'`. Reexpõe toda a interface de props do `InputBase`.

**Props** (destaques; herda toda a interface do InputBase)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue / value | any | '' | não | valor da data (string ou Date) |
| dateFormat | string | 'dd/mm/yy' | não | formato de exibição |
| placeholder | string | '' | não | placeholder |
| icon | string | 'solar:calendar-line-duotone' (default no template) | não | ícone |
| label | string | — | não | rótulo |
| done | string \| boolean \| null | undefined | não | conclusão manual |
| error | string \| boolean \| null | undefined | não | erro |
| caution | string \| boolean \| null | undefined | não | atenção |
| required | boolean | — | não | obrigatório |
| _(demais props do InputBase)_ | | | | class, i, disabled, float, msg, message, iconMessage, textCenter, textRight, dark, light, options, groupOptions, iconLeft/Right, optionValue/Label/Name, iconPos, inLine, noDone, noCaution, noError, noStatus, noIcon |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| (default) | any (default '') | data formatada como `YYYY-MM-DD HH:mm:ss` |

**Exemplo**
```vue
<MaxInputDatePicker v-model="data" label="Data de nascimento" required />
```

---

### MaxInputFile
Import: `import { MaxInputFile } from '@maxvue/max-components-ui'`. Componente sem template funcional — contém apenas estilos (`.input-file-main-div`) usados por outros componentes de arquivo. **Sem props/emits/slots/lógica.** `<script setup>` e `<template>` estão vazios; apenas o bloco `<style>` está presente.

---

### MaxInputFileProject
Import: `import { MaxInputFileProject } from '@maxvue/max-components-ui'`
Propósito: área de upload de documentos de "projeto" com drag & drop, ícones de arquivo, indicador de processamento por IA e envio automático via axios/FormData.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| files | DBFile[] | [] | não | lista inicial de arquivos |
| uploadData | any | — | não | dados adicionais enviados no FormData |
| auto | boolean | true | não | envia automaticamente os arquivos pendentes |
| url | string | — | não | URL de upload (prioridade sobre route/uploadRoute) |
| route | string | — | não | rota de upload (resolvida por `getRoute`) |
| ready | boolean | — | não | flag de prontidão |
| uploadRoute | string | — | não | rota alternativa de upload |
| buttons | MaxButtonsType[] | [] | não | botões de ação (ex.: "Preencher") |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| — | — | não expõe slots nomeados (renderização interna) |

**Exemplo**
```vue
<MaxInputFileProject :files="arquivos" route="documentos.upload" :upload-data="{ id }" />
```

---

### MaxInputFileUpload
Import: `import { MaxInputFileUpload } from '@maxvue/max-components-ui'`
Propósito: upload avançado de arquivos (encapsula `FileUpload` do PrimeVue) com múltiplos arquivos, thumbnails, progresso e integração com backend.

**Observação PrimeVue:** repassa `$attrs` ao `<FileUpload>` do PrimeVue (`v-bind="attrs"`). Configurações padrão: `name="file"`, `accept='.pdf, .jpg, .jpeg, .png, .doc, .docx'`, `auto=true`, `multiple=true`, `withCredentials=true`, `showCancelButton=false`. Declara explicitamente apenas as props abaixo; o restante (accept, auto, multiple, disabled, uploading, onSelect, onUpload, label-disabled etc.) é lido de `$attrs`.

**Props declaradas**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| token | string | — | não | token CSRF adicionado no header do upload |
| uploadData | Record<string, any> | {} | não | dados extras via FormData |
| label | string | '' | não | rótulo descritivo do campo |
| responseField | string | 'file' | não | campo da resposta da API com os dados do arquivo |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| (default) | any[] (default []) | lista de arquivos enviados/persistidos |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| file-click | file | clique em um arquivo já enviado |
| upload-error | event | erro no upload |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo/rótulo do campo (fallback: `displayLabel`) |
| error | — | conteúdo exibido em caso de erro |

**Exemplo**
```vue
<MaxInputFileUpload v-model="arquivos" label="Anexar" :upload-data="{ pasta: 'docs' }" url="/api/upload" />
```

---

### MaxInputFileUploadBig
Import: `import { MaxInputFileUploadBig } from '@maxvue/max-components-ui'`
Propósito: área grande de upload com drag & drop, animações Lottie de progresso/erro e seleção via clique (usa `useFileDialog`/`useDropZone`; não faz o POST — delega via `onSelect`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| accept | string | '.pdf, .jpg, .jpeg, .png, .doc, .docx' | não | tipos aceitos |
| multiple | boolean | true | não | permite múltiplos arquivos |
| disabled | boolean | false | não | desabilita a área |
| label | string | '' | não | rótulo descritivo (aceita HTML) |
| onSelect | `(event: { files: File[] }) => void` | — | não | callback ao selecionar/soltar arquivos |
| onUpload | `() => void` | — | não | callback após upload concluído |
| uploading | boolean | false | não | indica externamente estado de upload |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo da área de upload (fallback: ícone + label) |
| uploading | — | conteúdo durante o upload (fallback: animação Lottie) |
| error | — | conteúdo em caso de erro (fallback: animação Lottie) |

**Exemplo**
```vue
<MaxInputFileUploadBig label="Solte os arquivos aqui" :on-select="enviar" />
```

---

### MaxInputFileUploadButton
Import: `import { MaxInputFileUploadButton } from '@maxvue/max-components-ui'`
Propósito: variante compacta em forma de botão do upload (encapsula `MaxInputFileUpload` com `customUpload`); emite `upload` ao concluir.

**Observação:** não declara props próprias; repassa `$attrs` ao `MaxInputFileUpload` interno (`v-bind="attrs"`). Lê `attrs.ico`/`icon`/`i`, `attrs.label`, `attrs.modelValue`.

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| upload | files | disparado quando o upload é concluído |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | conteúdo do botão (fallback: ícone + label) |

**Exemplo**
```vue
<MaxInputFileUploadButton label="Enviar" icon="mdi:upload" @upload="onUpload" />
```

---

### MaxInputIconPicker
Import: `import { MaxInputIconPicker } from '@maxvue/max-components-ui'`
Propósito: seletor de ícones curados (Drawer com busca + VirtualScroller) que carrega lista e SVGs de endpoints do backend; envolve o trigger no `InputBase`.

**Observação PrimeVue:** usa `Drawer`, `VirtualScroller` e `InputText` do PrimeVue. Faz fetch em `listUrl` (GET) e `svgUrl` (POST em lotes de 200).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| color | string | — | não | cor aplicada ao ícone selecionado no trigger |
| disabled | boolean | false | não | desabilita o campo |
| float | boolean | — | não | FloatLabel |
| msg / message | string | — | não | mensagem de feedback |
| iconMessage | string | — | não | ícone da mensagem |
| label | string | — | não | rótulo |
| done | boolean | undefined | não | conclusão manual |
| error | string \| boolean | undefined | não | erro |
| caution | string \| boolean | undefined | não | atenção |
| required | boolean | false | não | obrigatório |
| placeholder | string | — | não | placeholder do trigger |
| listUrl | string | '/api/icons/picker' | não | URL para listar/buscar ícones (GET, `?q=`) |
| svgUrl | string | '/api/icons/picker/svg' | não | URL para buscar SVGs (POST `{ names }`) |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| (default) | string (default '') | nome do ícone selecionado |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | nome do ícone selecionado |

**Exemplo**
```vue
<MaxInputIconPicker v-model="icone" label="Ícone" />
```

---

### MaxInputMarkdown
Import: `import { MaxInputMarkdown } from '@maxvue/max-components-ui'`
Propósito: editor de Markdown WYSIWYG baseado em Tiptap (StarterKit + Underline, Link, Image, Table, tiptap-markdown) com barra de ferramentas; emite Markdown.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | '' | não | conteúdo em Markdown |
| label | string | — | não | rótulo |
| icon / i | string | — | não | ícone |
| disabled | boolean | false | não | desabilita a edição |
| float | boolean | — | não | FloatLabel |
| msg / message | string | — | não | mensagem |
| iconMessage | string | — | não | ícone da mensagem |
| done | boolean | — | não | conclusão |
| error | string \| boolean | — | não | erro |
| caution | string \| boolean | — | não | atenção |
| required | boolean | — | não | obrigatório |
| placeholder | string | — | não | placeholder do editor |
| minHeight | string | '200px' | não | altura mínima do conteúdo |
| maxHeight | string | '500px' | não | altura máxima do conteúdo |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string | conteúdo em Markdown (via `update:modelValue`) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | Markdown atualizado |

**Exemplo**
```vue
<MaxInputMarkdown v-model="descricao" label="Descrição" placeholder="Escreva..." />
```

---

### MaxInputMarkdownToolbar
Import: `import { MaxInputMarkdownToolbar } from '@maxvue/max-components-ui'`
Propósito: barra de ferramentas para um editor Tiptap (negrito, itálico, títulos, listas, blocos, link/imagem via popover, tabela, desfazer/refazer). Usado internamente por MaxInputMarkdown.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| editor | Editor \| null (`@tiptap/core`) | — | sim | instância do editor Tiptap a ser controlada |

**Exemplo**
```vue
<MaxInputMarkdownToolbar :editor="editor" />
```

---

### MaxInputNumber
Import: `import { MaxInputNumber } from '@maxvue/max-components-ui'`
Propósito: entrada numérica (encapsula `InputNumber` do PrimeVue dentro do `InputBase`) com validação de obrigatoriedade/comparação.

**Observação PrimeVue:** repassa `props` ao `<InputNumber>` (`v-bind="props"`), `fluid`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | '' | não | valor numérico |
| targetValue | string | — | não | comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |
| prefix | string | undefined | não | prefixo do valor |
| suffix | string | undefined | não | sufixo do valor |
| placeholder | string | undefined | não | placeholder |
| minFractionDigits | number | 2 | não | casas decimais mínimas |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | any | valor numérico |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | valor atualizado |

**Exemplo**
```vue
<MaxInputNumber v-model="preco" label="Preço" prefix="R$ " :min-fraction-digits="2" />
```

---

### MaxInputPhoneMail
Import: `import { MaxInputPhoneMail } from '@maxvue/max-components-ui'`
Propósito: campo unificado de e-mail OU telefone (WhatsApp) com máscara e ícone dinâmicos e validação (libphonenumber/regex). Encapsula `InputText` no `InputBase`.

**Observação PrimeVue:** encapsula `InputText` do PrimeVue com `v-maska:unmaskedValue.unmasked`. Atributos como `phone`/`whatsapp`/`zap` ou `email`/`mail` (via `$attrs`) forçam o método; label default 'Email ou Whatsapp'.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | '' | não | valor (e-mail ou telefone) |
| targetValue | string | — | não | comparação |
| label | string | — | não | rótulo (default dinâmico 'Email ou Whatsapp', ao contrário do padrão do InputBase) |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string | valor do campo (e-mail ou telefone com máscara) |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | valor atualizado |

**Exemplo**
```vue
<MaxInputPhoneMail v-model="contato" required />
```

---

### MaxInputRadio
Import: `import { MaxInputRadio } from '@maxvue/max-components-ui'`
Propósito: botão de rádio com rótulo/ícone opcional (encapsula `RadioButton` do PrimeVue); clique na área ativa o input.

**Observação PrimeVue:** repassa `$attrs` ao `<RadioButton>` do PrimeVue (`v-bind="attrs"`), com `inputId` gerado e `name` default 'radio-group'. Lê `attrs.label` e `attrs.icon`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | null | não | valor selecionado do grupo |
| value | any | null | não | valor deste rádio |
| name | string | 'radio-group' (fallback) | não | nome do grupo |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | any | valor selecionado do grupo |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | valor selecionado |

**Exemplo**
```vue
<MaxInputRadio v-model="opcao" :value="'a'" label="Opção A" name="grupo" />
```

---

### MaxInputSearch
Import: `import { MaxInputSearch } from '@maxvue/max-components-ui'`
Propósito: campo de busca com ícone de lupa/loading e debounce; emite `search` (300ms, mínimo 2 caracteres). Encapsula `InputText` no `InputBase`.

**Observação PrimeVue:** repassa `$attrs` ao `InputText` e ao `InputBase` (`v-bind="attrs"`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | '' | não | termo de busca |
| isLoading | boolean | false | não | exibe ícone de carregamento |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | string | termo de busca |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | termo atualizado |
| search | string | disparado (debounce 300ms, >1 caractere) |

**Exemplo**
```vue
<MaxInputSearch v-model="termo" :is-loading="carregando" @search="buscar" />
```

---

### MaxInputSelect
Import: `import { MaxInputSelect } from '@maxvue/max-components-ui'`
Propósito: dropdown de seleção (encapsula `Select` do PrimeVue no `InputBase`) com opções simples, agrupadas e carregamento assíncrono via `loadOptions`.

**Observação PrimeVue:** repassa `{...props, ...attrs}` ao `<Select>` do PrimeVue. Renderiza dois `<Select>` alternativos (agrupado quando `groupOptions` definido; simples caso contrário). Slot `#option` customizável.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | null | não | valor selecionado |
| loadOptions | `() => Promise<any[]>` | — | não | carrega opções ao abrir (before-show) |
| icon / i | string | — | não | ícone |
| optionValue | string | 'value' | não | campo do valor |
| optionLabel | string | 'label' | não | campo do rótulo |
| optionName | string | 'name' | não | campo do nome (texto exibido) |
| iconLeft | string | — | não | ícone à esquerda |
| iconRight | string | — | não | ícone à direita |
| iconDark | boolean \| number \| string | — | não | ícone escuro |
| iconLight | boolean \| number \| string | — | não | ícone claro |
| done | boolean | undefined | não | conclusão manual |
| error | string \| boolean \| null | undefined | não | erro |
| caution | string \| boolean \| null | undefined | não | atenção |
| required | boolean | false | não | obrigatório |
| iconMessage | string | — | não | ícone da mensagem |
| default | string \| number \| boolean \| null | undefined | não | valor padrão aplicado quando vazio |
| options | any[] | — | não | opções simples `[{ name, value, icon, sub_label }]` |
| groupOptions | SelectGroupOptions | — | não | opções agrupadas `[{ label, items: [] }]` |
| disabled | boolean | false | não | desabilita |
| filter | boolean | false | não | habilita filtro de busca |

**v-model**
| Model | Tipo | Descrição |
|-------|------|-----------|
| modelValue | any | valor selecionado |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | valor selecionado |
| before-show | event | disparado antes de abrir o overlay (dispara loadOptions) |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| option | `{ option, selected, index }` | customiza a renderização de cada opção |

**Exemplo**
```vue
<MaxInputSelect v-model="status" :options="statusList" option-value="id" option-label="nome" label="Status" filter />
```


---

<!-- continuação: MaxInputSwitch → MaxWaitIcon -->

> Componentes marcados como "(wrapper InputBase)" encapsulam um componente do PrimeVue dentro do wrapper
> interno `InputBase`, encaminhando `props`/`$attrs` (ex.: `class`, `placeholder`, `errMsg`, etc.) e as props
> padrão de campo listadas acima.

---

### MaxInputSwitch
Import: `import { MaxInputSwitch } from '@maxvue/max-components-ui'`
Propósito: interruptor (switch/toggle) para opções binárias, com pergunta/rótulo ao lado. Encapsula `ToggleSwitch` do PrimeVue dentro do `InputBase` (encaminha `$attrs` ao ToggleSwitch).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | boolean | false | não | Valor booleano do switch |
| question | string | — | não | Pergunta/rótulo exibido ao lado do switch |
| targetValue | string | — | não | Valor para comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | boolean | Valor do switch |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | boolean | Emitido ao alterar o switch |

**Exemplo**
```vue
<MaxInputSwitch v-model="ativo" question="Ativar notificações?" />
```

---

### MaxInputTextArea
Import: `import { MaxInputTextArea } from '@maxvue/max-components-ui'`
Propósito: área de texto multi-linha com redimensionamento automático. Encapsula `Textarea` do PrimeVue dentro do `InputBase` (encaminha `props` e `$attrs`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | '' | não | Valor do campo |
| targetValue | string | — | não | Valor para comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |
| autoResize | boolean | true | não | Redimensiona automaticamente |
| rows | string \| number | — | não | Nº fixo de linhas (sobrepõe cálculo automático) |
| minRows | number \| string | 1 | não | Mínimo de linhas |
| minLines | string \| number | — | não | Mínimo de linhas (alias, tem prioridade sobre minRows) |
| autofocus | boolean | — | não | Foco automático |
| maxRows | number | 10 | não | Máximo de linhas |
| wrap | string | — | não | Atributo wrap do textarea |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | any | Texto |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | Emitido ao alterar o texto |

**Exemplo**
```vue
<MaxInputTextArea v-model="descricao" label="Descrição" :minRows="3" />
```

---

### MaxInputText
Import: `import { MaxInputText } from '@maxvue/max-components-ui'`
Aliases: `InputText`, `InputField`, `MaxInputField`.
Propósito: entrada de texto padrão, com validação de obrigatoriedade e comparação de valores. Encapsula `InputText` do PrimeVue dentro do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| type | string | 'text' | não | Tipo do input HTML |
| modelValue | any | '' | não | Valor atual |
| targetValue | string | — | não | Valor esperado (valida igualdade) |
| placeholder | string \| undefined | — | não | Placeholder |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

Nota: usa `attrs.errMsg`/`error_message`/`error_msg` para customizar a mensagem de erro; mensagens automáticas: "Valor esperado: ..." (falha na comparação) e "Campo obrigatório".

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | any | Texto |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | Emitido ao alterar |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo extra dentro do InputBase (ao lado do input) |

**Exemplo**
```vue
<MaxInputText v-model="nome" label="Nome" required placeholder="Digite..." />
```

---

### MaxInputTextList
Import: `import { MaxInputTextList } from '@maxvue/max-components-ui'`
Propósito: editor de texto tipo "código", com numeração de linhas, indentação com Tab (4 espaços) e auto-indentação no Enter. Textarea nativa dentro do `InputBase` (encaminha `$attrs`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | '' | não | Conteúdo do editor |
| targetValue | string | — | não | Comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, label, done, error, caution, required — ver topo)_ | | | | |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | any | Convertido para string |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | Emitido ao alterar |

**Exemplo**
```vue
<MaxInputTextList v-model="codigo" label="Lista" />
```

---

### MaxInputToggle
Import: `import { MaxInputToggle } from '@maxvue/max-components-ui'`
Propósito: toggle com rótulos "verdadeiro/falso" laterais e valores customizáveis. Encapsula `ToggleSwitch` do PrimeVue (NÃO usa InputBase). Lê `label`, `labelCenter`, `labelTrue`/`true-label`, `labelFalse`/`false-label` via `$attrs`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | false | não | Valor atual |
| trueLabel | string | — | não | Rótulo do lado "verdadeiro" |
| falseLabel | string | — | não | Rótulo do lado "falso" |
| trueValue | any | true | não | Valor quando ligado |
| falseValue | any | false | não | Valor quando desligado |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | any | Valor do toggle |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | Emitido ao alterar |

**Exemplo**
```vue
<MaxInputToggle v-model="modo" true-label="Sim" false-label="Não" />
```

---

### MaxInputTypeAddress
Import: `import { MaxInputTypeAddress } from '@maxvue/max-components-ui'`
Propósito: select de tipo de logradouro (Rua, Avenida, Alameda, Praça, etc.), com detecção automática do tipo a partir da primeira palavra da prop `street`. Encapsula `MaxInputSelect` (encaminha `$attrs`, `optionLabel` default 'name', `optionValue` default 'value').

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | '' | não | Tipo selecionado |
| street | string | — | não | Nome da rua; a 1ª palavra define o tipo automaticamente (também aceita via `$attrs.street`) |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | string | Tipo de logradouro |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | string | Emitido ao selecionar ou ao detectar por `street` |

**Exemplo**
```vue
<MaxInputTypeAddress v-model="tipo" :street="endereco.logradouro" />
```

---

### MaxLink
Import: `import { MaxLink } from '@maxvue/max-components-ui'`
Propósito: wrapper de `router-link` navegando por nome de rota.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| route_name | string | — | não | Nome da rota de destino |
| route | string | — | não | Nome da rota (fallback de route_name) |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo do link |

**Exemplo**
```vue
<MaxLink route_name="dashboard">Ir</MaxLink>
```

---

### MaxLoader
Import: `import { MaxLoader } from '@maxvue/max-components-ui'`
Propósito: overlay de carregamento com ícone giratório (`MaxLoaderIcon`) e rótulo opcional. Todas as opções via `$attrs`.

**Props**
Não define `defineProps`. Consome via `$attrs`:
| Attr | Tipo | Default | Descrição |
|------|------|---------|-----------|
| show | boolean | true (se undefined) | Exibe ou não o loader |
| label | string | — | Rótulo exibido abaixo do ícone |

**Exemplo**
```vue
<MaxLoader :show="carregando" label="Carregando..." />
```

---

### MaxLoaderAi
Import: `import { MaxLoaderAi } from '@maxvue/max-components-ui'`
Propósito: overlay de carregamento "AI" com animação Lottie (DotLottie) e fundo semitransparente. Opções via `$attrs`.

**Props**
Não define `defineProps`. Consome via `$attrs`:
| Attr | Tipo | Default | Descrição |
|------|------|---------|-----------|
| show | boolean | true (se undefined) | Exibe ou não |
| label | string | — | Rótulo abaixo da animação |

**Exemplo**
```vue
<MaxLoaderAi :show="processando" label="Gerando..." />
```

---

### MaxLoaderIcon
Import: `import { MaxLoaderIcon } from '@maxvue/max-components-ui'`
Propósito: ícone SVG de spinner giratório (usa `currentColor`). Sem props formais; recebe `$attrs`. (Observação: no código `const attrs = useAttrs;` referencia a função, não a invoca.)

**Exemplo**
```vue
<MaxLoaderIcon />
```

---

### MaxLogo
Import: `import { MaxLogo } from '@maxvue/max-components-ui'`
Propósito: logotipo clicável envolto em `RouterLink` para "/".

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| src | string | 'get_file?file=logo.svg' | não | URL da imagem do logo |
| rounded | boolean | false | não | Aplica cantos arredondados |

**Exemplo**
```vue
<MaxLogo src="/logo.svg" />
```

---

### MaxMaps
Import: `import { MaxMaps } from '@maxvue/max-components-ui'`
Propósito: mapa Google (satélite) com marcador arrastável para editar latitude/longitude. Usa `vue3-google-map`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | { latitude: number; longitude: number } \| null | null | não | Coordenadas atuais |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | { latitude, longitude } | Coordenadas; atualizadas ao arrastar o marcador |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | { latitude, longitude } | Emitido ao mover o marcador ou mudar coordenadas |

**Exemplo**
```vue
<MaxMaps v-model="coords" />
```

---

### MaxModal
Import: `import { MaxModal } from '@maxvue/max-components-ui'`
Propósito: modal centralizado com botão de abertura, header (título/subtítulo) e conteúdo. Estado gerenciado pela `useModalStore` (apenas um modal aberto por vez). Botão padrão via `MaxButton`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| class | string | — | não | Classes CSS |
| icon / i | string | — | não | Ícone do botão |
| blank | string | — | não | Link para abrir em nova aba |
| route | string | — | não | Rota |
| label | string | — | não | Label do botão |
| title | string | — | não | Título do header |
| subTitle | string | — | não | Subtítulo do header |
| rotate | number | — | não | Rotação do ícone |
| flip | 'horizontal'\|'vertical'\|'h'\|'v'\|'x'\|'y'\|'xy' | — | não | Inversão do ícone |
| size / sizeIcon | string \| number | — | não | Tamanho do ícone |
| scale | string \| number | — | não | Alias de tamanho |
| loading | boolean | false | não | Estado de carregamento |
| width | string \| number | — | não | Largura |
| height | string \| number | — | não | Altura |
| dark | boolean \| string \| number \| undefined | 0.4 | não | Ícone escuro conforme fundo |
| light | boolean \| string \| number \| undefined | undefined | não | Ícone claro conforme fundo |
| checked | boolean \| string \| number \| undefined | — | não | Ícone de checagem |
| plus | boolean \| string \| number \| undefined | — | não | Ícone de adição |
| ignoreCanvas | boolean | false | não | data-html2canvas-ignore no overlay |
| noButton | boolean | false | não | Não renderiza botão de abertura |
| noHeader | boolean | false | não | Não renderiza header |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| button | (props) | Substitui o botão de abertura |
| header | — | Substitui o header |
| content | — | Conteúdo do modal |
| default | — | Conteúdo adicional |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| toggle | () => void | Abre/fecha o modal |
| is_show | ComputedRef<boolean> | Se está visível |
| show | (id) => void | Da store (exibe por id) |
| hide | () => void | Da store (oculta) |

**Exemplo**
```vue
<MaxModal title="Detalhes" label="Abrir">
  <template #content>...</template>
</MaxModal>
```

---

### MaxMsgLabels
Import: `import { MaxMsgLabels } from '@maxvue/max-components-ui'` (named export público do entry principal)
Propósito: exibe rótulos de mensagem/erro e o asterisco de obrigatoriedade.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| noErrors | boolean | false | não | Oculta todo o bloco |
| typeSelect | string | — | não | Classe de tipo aplicada ao container |
| obrigatorio | boolean | false | não | Exibe asterisco "*" |
| msgError | string | — | não | Mensagem de erro |
| msg | string | — | não | Mensagem informativa |

**Exemplo**
```vue
<MaxMsgLabels :obrigatorio="true" msgError="Campo inválido" />
```

---

### MaxPdfView
Import: `import { MaxPdfView } from '@maxvue/max-components-ui'`
Propósito: visualizador de PDF em modal fullscreen, com zoom (+/-), barra de progresso e paginação. Usa `vue-pdf-embed`. Abre automaticamente ao alterar a prop `file`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| file | any (string) | '' | não | URL/fonte do arquivo PDF (alterar abre o viewer) |

**Exemplo**
```vue
<MaxPdfView :file="pdfUrl" />
```

---

### MaxPhoneField
Import: `import { MaxPhoneField } from '@maxvue/max-components-ui'`
Aliases: `PhoneField`, `InputPhone`.
Propósito: campo de telefone internacional com seletor de DDI/bandeira e máscara dinâmica (Maska). Encapsula `Select` + `InputText` do PrimeVue dentro do `InputBase`. Modelo emite `DDI + dígitos` (debounced 500ms).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string \| undefined | — | não | Rótulo (default 'Telefone...', ao contrário do padrão do InputBase) |
| targetValue | string | — | não | Comparação |
| _(demais props do InputBase: icon/i, disabled, float, msg/message, iconMessage, done, error, caution, required — ver topo)_ | | | | |
| noLabel | boolean | false | não | Oculta o rótulo |
| noIcon | boolean | false | não | Oculta o ícone do WhatsApp |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue (defineModel) | any (default '') | Número completo (DDI + dígitos) |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| option | { option, selected, index } | Customiza item da lista de países |

**Exemplo**
```vue
<MaxPhoneField v-model="telefone" />
```

---

### MaxPopover
Import: `import { MaxPopover } from '@maxvue/max-components-ui'`
Propósito: popover posicionado dinamicamente relativo ao botão (com "picker"/triângulo), header opcional e conteúdo. Botão padrão via `MaxButton`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| class | string | — | não | Classes CSS |
| icon / i | string | — | não | Ícone do botão |
| blank | string | — | não | Link nova aba |
| route | string | — | não | Rota |
| label | string | — | não | Label do botão |
| title | string | — | não | Título do header |
| subTitle | string | — | não | Subtítulo do header |
| rotate | number | — | não | Rotação do ícone |
| flip | 'horizontal'\|'vertical'\|'h'\|'v'\|'x'\|'y'\|'xy' | — | não | Inversão do ícone |
| size / sizeIcon / iconSize | string \| number | 1.1 | não | Tamanho do ícone |
| scale | string \| number | — | não | Alias de tamanho |
| loading | boolean | false | não | Carregamento |
| width | string \| number | — | não | Largura |
| height | string \| number | — | não | Altura |
| dark | boolean\|string\|number\|undefined | 0.4 | não | Ícone escuro |
| light | boolean\|string\|number\|undefined | undefined | não | Ícone claro |
| checked | boolean\|string\|number\|undefined | — | não | Ícone de checagem |
| plus | boolean\|string\|number\|undefined | — | não | Ícone de adição |
| noPicker | boolean | false | não | Oculta o triângulo/picker |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| button | (props) | Substitui o botão |
| header | — | Substitui o header |
| content | — | Conteúdo |
| default | — | Conteúdo adicional |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| hide | () => void | Fecha |
| show | () => void | Abre (alias de toggle) |
| toggle | () => void | Alterna |

**Exemplo**
```vue
<MaxPopover title="Opções" icon="mdi:cog">
  <template #content>...</template>
</MaxPopover>
```

---

### MaxPopoverConfirm
Import: `import { MaxPopoverConfirm } from '@maxvue/max-components-ui'`
Propósito: popover de confirmação (Sim/Não) posicionado dinamicamente. É a camada de UI da `useConfirmStore` — normalmente montado uma vez na aplicação; a exibição é controlada pela store (ver `MaxTogglePopover`, `MaxUserAvatar`). Sem props.

**Comportamento**
- Lê da `useConfirmStore`: `message`, `messageIcon`, `rejectProps`, `acceptProps`, `x`, `y`, `width`, `height`, `show`.
- Ao aceitar/rejeitar, invoca `acceptProps.action` / `rejectProps.action` e chama `confirm_store.hide()`.

**Exemplo**
```vue
<!-- Montar uma vez, ex.: no App.vue -->
<MaxPopoverConfirm />
```

---

### MaxPopoverMenu
Import: `import { MaxPopoverMenu } from '@maxvue/max-components-ui'`
Propósito: menu suspenso (PrimeVue `Menu` popup) acionado por botão; itens com ícone, label, `route` (navega via `goToRoute`) ou `action({ event, data })`. Botão padrão via `MaxButton`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string | — | não | Texto do botão |
| icon / i | string | — | não | Ícone do botão |
| items | any[] | — | não | Itens do menu |
| model | any[] \| undefined | — | não | Itens do menu (alias) |
| rotate | number | — | não | Rotação do ícone |
| flip | 'horizontal'\|'vertical'\|'h'\|'v'\|'x'\|'y'\|'xy' | — | não | Inversão |
| size / iconSize / sizeIcon | string \| number | 1.1 | não | Tamanho do ícone |
| scale | string \| number | — | não | Alias de tamanho |
| width | string \| number | — | não | Largura |
| height | string \| number | — | não | Altura |
| dark | boolean\|string\|number\|undefined | 0.4 | não | Ícone escuro |
| light | boolean\|string\|number\|undefined | undefined | não | Ícone claro |
| checked | boolean\|string\|number\|undefined | — | não | Ícone de checagem |
| plus | boolean\|string\|number\|undefined | — | não | Ícone de adição |

Formato de item: `{ label, icon?/i?, route?, data?/props?/params?/query?, action?({ event, data }) }`.

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| button | — | Substitui o botão |
| item | { data: item } | Customiza a renderização de cada item |

**Exemplo**
```vue
<MaxPopoverMenu icon="mdi:dots-vertical" :items="[
  { label: 'Editar', icon: 'mdi:pencil', action: ({data}) => edit(data) },
  { label: 'Home', route: 'home' }
]" />
```

---

### MaxTable
Import: `import { MaxTable } from '@maxvue/max-components-ui'`
Propósito: tabela de dados estilizada. Encapsula `DataTable` do PrimeVue e encaminha `$attrs` (ex.: `:value`, `paginator`, etc.). Repassa todos os slots recebidos ao DataTable; o slot especial `buttons` gera uma `Column` de ações medindo largura automaticamente.

**Props**
Não define `defineProps` — todas as props do DataTable via `$attrs`. Sempre aplica `stripedRows`.

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| (qualquer nome de slot do DataTable) | slotProps do DataTable | Repassado ao DataTable (colunas, header, footer, etc.) |
| buttons | { data, index } | Coluna de ações renderizada por linha, largura auto |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| width | Ref<number> | Largura calculada da coluna de botões |

**Exemplo**
```vue
<MaxTable :value="rows">
  <template #buttons="{ data }">
    <MaxIconButton i="mdi:pencil" @click="edit(data)" />
  </template>
</MaxTable>
```

---

### MaxTableColumn
Import: (não exportado no index principal) — apenas re-exporta o `Column` do PrimeVue como importação interna; template vazio. Placeholder/estilos para a coluna da tabela (`p-datatable`). Sem props, sem slots, sem emits. Apenas fornece SCSS. Não é registrado no `index.ts`.

---

### MaxTableFields
Import: `import { MaxTableFields } from '@maxvue/max-components-ui'`
Propósito: tabela editável orientada a campos — renderiza inputs por coluna (`text`, `number`, `select`, `date`, `checkbox`, `textarea`, `auto-complete`, `auto-complete-api`, `phone-number`, `increment`) ou slots customizados, com coluna de botões de ação.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| list | any[] \| Record<string, any> | {} | não | Linhas (array ou objeto; objeto é convertido em array) |
| columns | MaxTableColumn[] | [] | não | Definição das colunas |
| headerButton | string | — | não | Texto do cabeçalho da coluna de ações |
| id | string | — | não | ID da tabela (default: `ulid()`) |
| emptyMessage | string | 'Nenhum registro encontrado' | não | Mensagem para lista vazia |
| buttonsWidth | string | — | não | Largura da coluna de botões |
| buttons | MaxButtonsType[] | — | não | Botões de ação por linha |

Coluna (`MaxTableColumn`) suporta: `field`, `header`, `slot`, `input`, `options`, `placeholder`, `required`, `route`, `data`, `width`/`size`/`minWidth`/`maxWidth`, `align`, `style`, `action({ row, field, value })`. Campos suportam notação com ponto (ex.: `user.name`).

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:field | { row, field, value, index? } | Emitido ao alterar o valor de um campo |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| header-{field} | { column } | Customiza o cabeçalho da coluna |
| buttons-header | — | Cabeçalho da coluna de ações |
| {col.slot ou col.field} | { data, value, index, field } | Célula customizada (quando `col.slot` e sem `col.input`) |
| buttons | { data, index } | Botões de ação por linha |
| empty | — | Conteúdo do estado vazio |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| tableId | ComputedRef<string> | ID resolvido da tabela |

**Exemplo**
```vue
<MaxTableFields
  :list="itens"
  :columns="[{ field: 'nome', header: 'Nome', input: 'text' }]"
  :buttons="[{ i: 'mdi:delete', action: remover }]"
  @update:field="onChange"
/>
```

---

### MaxTagSelect
Import: `import { MaxTagSelect } from '@maxvue/max-components-ui'`
Aliases: `MaxInputSelectTag`, `MaxSelectTag`.
Propósito: select estilizado como "tag" (chip colorido), com filtro, carregamento assíncrono de opções, cores por item e ícones. Encapsula `Select` do PrimeVue dentro do `InputBase` (encaminha `props`+`$attrs`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | null | não | Valor selecionado |
| loadOptions | () => Promise<any[]> | — | não | Carrega opções ao abrir |
| icon / i | string \| undefined | — | não | Ícone principal / alias |
| optionValue | string | 'value' | não | Campo do valor |
| optionLabel | string | 'label' | não | Campo do label |
| optionName | string | 'name' | não | Campo do name (exibido no chip) |
| iconLeft | string \| undefined | — | não | Ícone à esquerda |
| iconRight | string \| undefined | — | não | Ícone à direita |
| iconDark | boolean\|number\|string\|undefined | — | não | Ícone escuro |
| iconLight | boolean\|number\|string\|undefined | — | não | Ícone claro |
| done | boolean \| undefined | undefined | não | Conclusão |
| error | string\|null\|boolean\|undefined | undefined | não | Erro |
| caution | string\|null\|boolean\|undefined | undefined | não | Atenção |
| required | boolean \| undefined | false | não | Obrigatório |
| iconMessage | string \| undefined | — | não | Ícone da mensagem |
| default | string\|number\|boolean\|null\|undefined | undefined | não | Valor default (aplicado se vazio) |
| options | any[] | — | não | Opções simples |
| groupOptions | SelectGroupOptions | — | não | Opções agrupadas |
| disabled | boolean \| undefined | false | não | Desabilita |
| filter | boolean \| undefined | false | não | Habilita filtro |
| hasRemove | boolean \| undefined | — | não | Permite remoção |
| isButton | boolean \| undefined | false | não | Renderiza como botão de ícone |
| backgroundColor | string | 'var(--background-500)' | não | Cor de fundo padrão do chip |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue | any | Valor selecionado |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | any | Emitido ao selecionar |
| before-show | event | Emitido antes de abrir o overlay |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| option | { option, selected, index } | Customiza item da lista |
| btn-right | — | Conteúdo à direita do chip selecionado |

**Exemplo**
```vue
<MaxTagSelect v-model="tag" :options="opcoes" filter />
```

---

### MaxTagsList
Import: `import { MaxTagsList } from '@maxvue/max-components-ui'`
Propósito: lista de tags editável — cada tag é um `MaxTagSelect`; permite trocar, remover e adicionar novas tags (chip "+"). Encaminha `$attrs` ao container.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| options | any[] \| Record<string, any> | [] | não | Opções disponíveis para as tags |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| modelValue (defineModel) | any[] \| Record<string, any> (default []) | Lista de tags selecionadas |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| change | any[] | Emitido ao adicionar/trocar/remover uma tag |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| count | ComputedRef<number> | Quantidade de tags na lista |

**Exemplo**
```vue
<MaxTagsList v-model="tags" :options="opcoes" @change="onChange" />
```

---

### MaxTextInputFloatLabel
Import: `import { MaxTextInputFloatLabel } from '@maxvue/max-components-ui'`. Componente DESCONTINUADO (renderiza uma `<div>` vazia). Sem props/emits/slots. Exemplo: `<MaxTextInputFloatLabel />`

---

### MaxTitle1
Import: `import { MaxTitle1 } from '@maxvue/max-components-ui'`
Propósito: título "H1" (título em maiúsculas + subtítulo) com ícone opcional. Subtítulo aceita HTML (`v-html`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| h1 | string | — | não | Título (ou use `title`) |
| title | string | — | não | Título (alias de h1) |
| h2 | string | — | não | Subtítulo (ou use `subtitle`) |
| subtitle | string | — | não | Subtítulo (alias de h2) |
| icon / i / icone | string | — | não | Ícone (aliases) |
| iconSize / sizeIcon | string \| number | 1.3 | não | Tamanho do ícone |

**Exemplo**
```vue
<MaxTitle1 h1="Título" h2="Subtítulo" icon="mdi:home" />
```

---

### MaxTitle2
Import: `import { MaxTitle2 } from '@maxvue/max-components-ui'`
Propósito: título "H2" (variação menor, com opção de centralização). Subtítulo aceita HTML.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| center | boolean | — | não | Centraliza o conteúdo |
| h1 | string | — | não | Título (ou `title`) |
| title | string | — | não | Título (alias) |
| h2 | string | — | não | Subtítulo (ou `subtitle`) |
| subtitle | string | — | não | Subtítulo (alias) |
| icon / i / icone | string | — | não | Ícone (aliases) |
| iconSize / sizeIcon | string \| number | 1.3 | não | Tamanho do ícone |

**Exemplo**
```vue
<MaxTitle2 title="Seção" subtitle="Descrição" center />
```

---

### MaxToast
Import: `import { MaxToast } from '@maxvue/max-components-ui'`
Propósito: container de notificações toast (canto superior direito). É a camada de UI da `useToastStore` — montado uma vez (no `App.vue`, fora do `RouterView`); toasts são disparados via helper `Toast` ou pela store. Sem props. Pausa o timer no hover; barra de progresso e botão de fechar embutidos.

Payload de disparo (`ToastPayload`): `title` (obrigatório) · `message?` (linha secundária, 2 linhas com ellipsis) · `severity?` = `'success' | 'info' | 'warning' | 'error' | 'whatsapp'` (default `'info'`) · `icon?` (Iconify, sobrescreve o ícone da severidade) · `duration?` em ms (default `4000`).

Ícones automáticos por severidade: success → `mdi:check-circle-outline` · info → `mdi:information-outline` · warning → `mdi:alert-outline` · error → `mdi:close-circle-outline` · whatsapp → `mdi:whatsapp`.

**Exemplo**
```vue
<!-- Montar uma vez, no App.vue -->
<MaxToast />
<script setup>
import { Toast } from '@maxvue/max-components-ui';
Toast.show({ title: 'Salvo!', severity: 'success' });
Toast.show({ title: 'Falha ao salvar', message: 'Verifique sua conexão.', severity: 'error', duration: 5000 });
</script>
```

---

### MaxTogglePopover
Import: (não exportado no index principal) `MaxTogglePopover.vue`
Propósito: botão que dispara um popover de confirmação via `useConfirmStore` (posicionado no botão) — usa `MaxPopover` como wrapper e `MaxIconButton`/`MaxButton` como gatilho. (Não consta no `index.ts`.)

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| icon / i | string | — | não | Ícone do botão |
| blank | string | — | não | Link nova aba |
| route | string | — | não | Rota |
| data | any | — | não | Query data |
| params | any | — | não | Params |
| label | string | — | não | Label do botão (se definido, usa MaxButton) |
| rotate | number | — | não | Rotação do ícone |
| flip | 'horizontal'\|'vertical'\|'h'\|'v'\|'x'\|'y'\|'xy' | — | não | Inversão |
| size / scale | string \| number | — | não | Tamanho do ícone |
| message | string | 'Deseja continuar?' | não | Mensagem de confirmação |
| messageIcon | string | — | não | Ícone da mensagem |
| acceptLabel | string | — | não | Label do botão "sim" |
| acceptIcon | string | — | não | Ícone do botão "sim" |
| rejectProps | { label; icon?; action } | { label:'Não', action:()=>{} } | não | Config. do botão "não" |
| acceptProps | { label; icon?; action } | { label:'Sim', action:()=>{} } | não | Config. do botão "sim" |
| cancelIcon | string | — | não | Ícone de cancelar |
| loading | boolean | false | não | Carregamento |
| width / height | string \| number | — | não | Dimensões |
| dark | boolean\|string\|number\|undefined | 0.4 | não | Ícone escuro |
| light | boolean\|string\|number\|undefined | undefined | não | Ícone claro |
| checked | boolean\|string\|number\|undefined | — | não | Ícone de checagem |
| plus | boolean\|string\|number\|undefined | — | não | Ícone de adição |

**Slots**
| Nome | Props | Descrição |
|------|-------|-----------|
| button | — | Substitui o botão gatilho |

**Exemplo**
```vue
<MaxTogglePopover i="mdi:delete" message="Excluir?"
  :acceptProps="{ label:'Sim', action: remover }" />
```

---

### MaxTransitionFadeLight
Import: `import { MaxTransitionFadeLight } from '@maxvue/max-components-ui'`. Wrapper de `<Transition>` com fade de opacidade (0.5s). Sem props/emits. Slot `default` (conteúdo animado). Exemplo: `<MaxTransitionFadeLight><div v-if="show">...</div></MaxTransitionFadeLight>`

---

### MaxTransitionUp
Import: `import { MaxTransitionUp } from '@maxvue/max-components-ui'`. Wrapper de `<Transition>` com animação de deslizar para cima na entrada e para baixo na saída. Sem props/emits. Slot `default` (conteúdo animado). Exemplo: `<MaxTransitionUp><div v-if="show">...</div></MaxTransitionUp>`

---

### MaxUserAvatar
Import: `import { MaxUserAvatar } from '@maxvue/max-components-ui'`
Propósito: avatar do usuário (imagem ou iniciais do nome), com tooltip opcional e modo de remoção — no modo `remove`, exibe overlay "×" no hover e pede confirmação via `useConfirmStore` antes de emitir `remove`. Encapsula `Avatar` do PrimeVue.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| imageUrl | string | — | não | URL da imagem |
| name | string | — | não | Nome (gera iniciais/tooltip) |
| showTooltip | boolean | true | não | Exibe tooltip com o nome |
| routeImage | string \| null \| undefined | null | não | Rota para carregar a imagem |
| requestImageData | string \| null \| undefined | — | não | Rota para dados da imagem |
| remove | boolean | — | não | Ativa modo de remoção (overlay + confirmação) |
| labelRemove | string | — | não | Mensagem/label na confirmação de remoção |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| remove | — | Emitido após confirmar a remoção |

**Exemplo**
```vue
<MaxUserAvatar name="João" remove @remove="onRemove" />
```

---

### MaxWaitIcon
Import: `import { MaxWaitIcon } from '@maxvue/max-components-ui'`. Ícone SVG animado de "aguarde" (ampulheta com animação de rotação/fade), usando `currentColor`. Sem props/emits/slots. Exemplo: `<MaxWaitIcon />`

---

## Stores, Helpers e Exports públicos

### Instalação (plugin)
O `index.ts` exporta uma função `install(app, options)` e um `default { install }` — é um plugin Vue:
```ts
import MaxComponentsUi from '@maxvue/max-components-ui';
app.use(MaxComponentsUi, { /* options */ });
```
O `install`:
- Registra `PrimeVue` com locale pt-BR (`ptBR`) por padrão (sobrescrevível via `options.locale`).
- Aplica o tema `MaxStyle` (preset), com `darkModeSelector: '.dark'`, `prefix: 'max'`, `ripple: true`.
- Registra a diretiva `v-tooltip` (PrimeVue `Tooltip`).
- Aceita `options.theme`, `options.theme.options` e demais opções repassadas ao PrimeVue.

### Stores (Pinia)

Exportadas via `export * from './stores'` no index principal E pelo subpath `@maxvue/max-components-ui/stores`. O `stores/index.ts` re-exporta apenas: **useIconStore**, **usePopoverStore**, **useToastStore**. As stores **useConfirmStore** e **useModalStore** existem mas NÃO estão no barrel `stores/index.ts` (são importadas internamente pelos componentes via caminho relativo).

#### useToastStore — `defineStore('max-toast')`
Estado/métodos públicos (retornados):
- `items: Ref<ToastItem[]>` — fila de toasts visíveis.
- `add(payload: ToastPayload): string` — adiciona toast, inicia timer, retorna id. Defaults: `severity: 'info'`, `duration: 4000`ms.
- `remove(id: string): void` — remove um toast (limpa timer).
- `pause(id: string): void` — pausa o timer (usado no hover).
- `resume(id: string): void` — retoma o timer.
- `clear(): void` — remove todos.

Tipos: `ToastSeverity = 'success' | 'info' | 'warning' | 'error' | 'whatsapp'`; `ToastItem` (id, title, message?, severity, icon?, duration, createdAt, paused, remaining, timerId); `ToastPayload` (title, message?, severity?, icon?, duration?).

Uso:
```ts
import { useToastStore } from '@maxvue/max-components-ui';
useToastStore().add({ title: 'Ok', severity: 'success' });
```

#### useIconStore — `defineStore('icons')`
Estado/métodos públicos:
- `getIcon(icon_name: string): string | null` — retorna SVG do cache ou marca como "waiting" e retorna null; busca em lote via API `https://engeapp.com.br/api/icons` (debounced), com cache em `localStorage['all_icons']` e até 4 tentativas.
- `list_icons_waiting_request: ComputedRef<string[]>` — ícones aguardando requisição.
- `icons_data: Ref<Record<string, any>>` — mapa nome→SVG/estado.

#### usePopoverStore — `defineStore('popover')`
- `show_id: Ref<string | null>` — id do popover aberto.
- `hide()`, `show(id)`, `toggle(id)`.

#### useModalStore — `defineStore('modal')` (NÃO re-exportado no barrel)
- `show_id: Ref<string | null>`; `hide()`, `show(id)`, `toggle(id)`. Usado por `MaxModal`.

#### useConfirmStore — `defineStore('confirm.popover')` (NÃO re-exportado no barrel)
Estado/métodos:
- `message: Ref<string>` (default 'Deseja continuar?'), `messageIcon: Ref<string|null>`.
- `rejectProps` / `acceptProps: Ref<{ label; icon?; action? }>` (defaults 'Não'/'Sim').
- `show: Ref<boolean>`; posicionamento `x`, `y`, `width`, `height` (Refs numéricos).
- `count_loadeds: Ref<number>`.
- `hide(): void`.
Usado por `MaxPopoverConfirm`, `MaxTogglePopover` e `MaxUserAvatar`.

### Helpers

Exportado publicamente pelo `index.ts`: **`Toast`** (de `./helpers/Toast`).

#### Toast — `import { Toast } from '@maxvue/max-components-ui'`
Fachada global sobre a `useToastStore`:
- `Toast.add(payload: ToastPayload): string` — exibe e retorna id.
- `Toast.show(payload): string` — alias de add.
- `Toast.hide(id: string): void` — remove por id.
- `Toast.delete(id: string): void` — alias de hide.
- `Toast.clear(): void` — remove todos.
```ts
Toast.show({ title: 'Salvo!', severity: 'success' });
```

#### resolver / MaxComponentsUiResolver — subpath `@maxvue/max-components-ui/resolver`
Exportado via `package.json` `exports["./resolver"]` (arquivo `helpers/MaxComponentsUiResolver.ts`):
- `MaxComponentsUiResolver(): ComponentResolver` e alias `resolver` — resolver de auto-import (unplugin-vue-components); resolve aliases do `components-manifest.json` para `@maxvue/max-components-ui` e componentes PrimeVue para `@maxvue/max-components-ui/prime`.
```ts
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver';
```

#### Helpers internos (NÃO exportados publicamente pelo index)
Presentes em `src/helpers/`, usados internamente (importados por caminho relativo):
- `getCssSize(value: string | number): string` — number vira `${n}px`; string numérica idem; caso contrário retorna a string. Usado por vários componentes (MaxPopover, MaxPopoverMenu, MaxTableFields...).
- `gap(params): Record<string,string>` — gera CSS de gap/row-gap/column-gap.
- `paddingMargin(params): Record<string,string>` — gera CSS de padding/margin por direção (t/b/l/r/x/y/w/h).
- `getCached(key): Promise<any>` / `setCached(key, data): void` — leitura/escrita em `localStorage` (JSON com wrapper `{ key, data }`).

### Outros subpaths do pacote (`package.json exports`)
- `.` → índice principal (componentes + stores + Toast + install/plugin + tipos).
- `./preset` → `presetMaxUno` (preset UnoCSS).
- `./resolver` → resolver de auto-import.
- `./prime` → componentes PrimeVue reexportados como se fossem do Max (importação nomeada, não default).
- `./stores` → barrel das stores (useIconStore, usePopoverStore, useToastStore).

### Tipos públicos
`export * from './types'` no index principal expõe os tipos da lib (ex.: `MaxTableColumn`, `MaxButtonsType`, `SelectGroupOptions`, usados por MaxTableFields e MaxTagSelect).
