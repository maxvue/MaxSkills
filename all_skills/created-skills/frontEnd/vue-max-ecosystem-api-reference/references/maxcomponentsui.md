# MaxComponentsUi — Catálogo de API (`@maxvue/max-components-ui`)

> Referência extraída do código-fonte (`/home/johnattas/GitHub/MaxComponentsUi/src`). Contém todos os 110 componentes implementados. Cada entrada traz
> Import, Propósito, Props, v-model, Emits, Slots, Expose e um Exemplo mínimo. Descrições em pt-BR.
>
> **InputBase**: a maioria dos `MaxInput*` embrulha o wrapper `InputBase.vue` e faz `v-bind="props"`,
> herdando o conjunto de props do InputBase (`label`, `icon`/`i`, `message`, `done`/`error`/`caution`,
> `required`, `dark`/`light`, `noStatus`, etc.) mesmo quando não redeclaradas. Onde relevante isso está
> anotado por componente.
>
> **App Shell & Layout**: conjunto completo de componentes estruturais (`MaxApp`, `MaxContainerApp`, `MaxPageLayout`,
> `MaxPageMobileLayout`, `MaxPageContent`, `MaxTopMenu`, `MaxTopMenuSearchBar`, `MaxTopToolbar`, `MaxSideMenu`,
> `MaxSideMenuMobile`, `MaxBottomMenu`, `MaxUserSection`) com suporte a temas, breakpoints e controle de rotas.
>
> **Export público**: quase a totalidade dos componentes está exportada no `index.ts`. `MaxTableColumn` e
> `MaxTogglePopover` possuem uso interno ou auxiliar; `MaxTextInputFloatLabel` está **deprecado**
> (renderiza `<div>` vazio). Detalhes na seção final "Stores, Helpers e Exports públicos".

---

## Componentes (A → Z)

> Props herdadas do `InputBase` disponíveis na maioria dos `MaxInput*` mesmo quando não redeclaradas:
> `label`, `icon`/`i`, `iconLeft`, `iconRight`, `message`/`msg`, `iconMessage`, `done`, `error`, `caution`,
> `required`, `float`, `disabled`, `textCenter`, `textRight`, `dark`, `light`, `noDone`, `noCaution`,
> `noError`, `noStatus`, `noIcon`, `inLine`, `class`.

---

### InputBase
Import: `import { InputBase } from '@maxvue/max-components-ui'`
Propósito: wrapper base unificado para todos os campos de formulário (`MaxInput*`). Gerencia FloatLabel, layout flex/grid, ícones (esquerda, direita, principal), mensagens de validação e status (`done`, `caution`, `error`), asterisco de obrigatório (`required`), alinhamento de texto e suporte a temas claro/escuro.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| value / modelValue | any | — | não | Valor do input (suporta v-model) |
| label | string | — | não | Rótulo exibido acima ou como FloatLabel |
| icon / i | string | — | não | Ícone principal exibido no campo |
| iconLeft | string | — | não | Ícone posicionado à esquerda |
| iconRight | string | — | não | Ícone posicionado à direita |
| iconPos | 'left' \| 'right' | 'left' | não | Posição padrão do ícone |
| float | boolean | false | não | Ativa estilo de rótulo flutuante (FloatLabel) |
| disabled | boolean | false | não | Desabilita o componente |
| required | boolean | false | não | Indica preenchimento obrigatório (adiciona asterisco) |
| message / msg | string | — | não | Mensagem de feedback/instrução exibida abaixo do campo |
| iconMessage | string | — | não | Ícone exibido ao lado da mensagem de feedback |
| done | string \| boolean | — | não | Estado de sucesso/concluído (exibe ícone de check verde) |
| error | string \| boolean | — | não | Mensagem de erro ou estado inválido (borda/ícone vermelho) |
| caution | string \| boolean | — | não | Mensagem de alerta ou estado de atenção (borda/ícone laranja) |
| textCenter | boolean | false | não | Alinha o texto ao centro |
| textRight | boolean | false | não | Alinha o texto à direita |
| dark | boolean \| string \| number | — | não | Força ícone escuro referente ao fundo |
| light | boolean \| string \| number | — | não | Força ícone claro referente ao fundo |
| inLine | boolean | false | não | Layout em linha (horizontal) |
| noDone | boolean | false | não | Oculta o ícone de status done |
| noCaution | boolean | false | não | Oculta o ícone de status caution |
| noError | boolean | false | não | Oculta o ícone de status error |
| noStatus | boolean | false | não | Oculta todos os ícones de status (done, caution, error) |
| noIcon | boolean | false | não | Oculta o ícone principal |
| options | any[] | — | não | Lista de opções simples `[{ name, value, icon, sub_label }]` |
| groupOptions | SelectGroupOptions | — | não | Lista de opções agrupadas |
| loadOptions | `() => Promise<any[]>` | — | não | Função assíncrona para carregamento de opções |
| optionValue | string | 'value' | não | Chave do objeto para o valor selecionado |
| optionLabel | string | 'name' | não | Chave do objeto para o texto de exibição |
| optionName | string | — | não | Chave do objeto para o nome do campo |
| class | string | — | não | Classes CSS adicionais |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Elemento de entrada real (ex.: `<input>`, `<Select>`, `<AutoComplete>`) inserido dentro da moldura |

**Exemplo**
```vue
<InputBase label="Nome Completo" icon="mdi:account" :done="valido" :error="erroMsg">
  <input v-model="nome" class="w-full bg-transparent outline-none" />
</InputBase>
```

---

### MaxAccordion
Import: `import { MaxAccordion } from '@maxvue/max-components-ui'`
Aliases: `Accordion`.
Propósito: contêiner de acordeão expansível para seções de conteúdo agrupadas. Fornece contexto reativo via Context API (`ACCORDION_INJECTION_KEY`) para componentes `MaxAccordionItem`. Suporta expansão individual ou múltipla e renderização preguiçosa (`lazy`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| multiple | boolean | false | não | Permite múltiplos itens abertos simultaneamente |
| lazy | boolean | false | não | Monta o conteúdo dos itens apenas quando abertos pela primeira vez |
| expandIcon | string | 'mdi:chevron-down' | não | Ícone do item quando fechado |
| collapseIcon | string | 'mdi:chevron-up' | não | Ícone do item quando aberto |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| value (defineModel) | `string \| string[] \| undefined` | Identificador(es) do(s) item(ns) aberto(s) |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Itens do acordeão (`<MaxAccordionItem>`) |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| toggle | `(itemValue: string) => void` | Alterna a abertura/fechamento de um item por seu identificador |

**Exemplo**
```vue
<MaxAccordion v-model:value="abaAberta">
  <MaxAccordionItem value="1" title="Dados Gerais">
    <p>Conteúdo da primeira seção.</p>
  </MaxAccordionItem>
  <MaxAccordionItem value="2" title="Configurações">
    <p>Conteúdo da segunda seção.</p>
  </MaxAccordionItem>
</MaxAccordion>
```

---

### MaxAccordionItem
Import: `import { MaxAccordionItem } from '@maxvue/max-components-ui'`
Aliases: `AccordionItem`.
Propósito: item individual colapsável pertencente a um `MaxAccordion`. Possui cabeçalho clicável e acessível (`aria-expanded`, `aria-controls`), ícone de chevron sincronizado e transição de altura fluida.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| value | string | autogerado | não | Identificador único do item no acordeão |
| title | string | '' | não | Título exibido no cabeçalho do item |
| disabled | boolean | false | não | Desabilita a alternância de abertura |
| headerAriaLevel | number | 2 | não | Nível hierárquico ARIA (h2 a h6) para acessibilidade |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| header | — | Substitui o cabeçalho padrão do item |
| content / default | — | Conteúdo exibido quando o item está expandido |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| value | `Ref<string>` | Identificador resolvido do item |

**Exemplo**
```vue
<MaxAccordionItem value="perfil" title="Editar Perfil">
  <p>Formulário de perfil do usuário.</p>
</MaxAccordionItem>
```

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

### MaxApp
Import: `import { MaxApp } from '@maxvue/max-components-ui'`
Propósito: shell raiz e orquestrador principal de layout da aplicação. Decide dinamicamente se a página atual renderiza sem layout (`blankPages`), tela de login (`MaxAuthCard`) ou a interface completa autenticada (`MaxPageLayout`). Integra com `useSystemStore` e `useUserStore`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| screen | string | auto (`system.type_device`) | não | Força dispositivo ('desktop' \| 'mobile') |
| routeLogin | string | — | não | Endpoint de submissão do formulário de login |
| routeProviders | string | — | não | Endpoint de listagem de provedores sociais (OAuth) |
| routeUser | string | — | não | Endpoint para obtenção dos dados do usuário logado |
| allowUserName | boolean | false | não | Permite autenticação via nome de usuário |
| allowEmail | boolean | true | não | Permite autenticação via e-mail |
| allowPhone | boolean | false | não | Permite autenticação via telefone (SMS/OTP) |
| blankPages | string[] | `[]` | não | Lista de rotas que renderizam sem cabeçalho/menu |
| addItems | `Array<Record<string, any>>` | `[]` | não | Ações do botão "+ Adicionar Novo" no topo e no FAB |
| bottomTabs | `BottomTab[]` | padrão Engeapp | não | Configuração das abas da barra inferior móvel |
| bottomShowLabels | boolean | false | não | Exibe texto sob os ícones na barra inferior mobile |
| sideMenuGroups | `MenuGroup[]` | `[]` | não | Grupos e links para a gaveta de navegação mobile |
| sideMenuItems | any[] | `[]` | não | Itens simples para o menu móvel |
| avatarPath | string | `'/avatar/'` | não | Caminho base para fotos de perfil dos usuários |
| logo | string | — | não | Caminho/URL ou nome de rota da logo da aplicação |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile | — | Clique na ação de perfil do usuário |
| settings | — | Clique na ação de configurações |
| support | — | Clique no link de suporte |
| toggleDarkMode | — | Alternância do modo escuro/claro |
| logout | — | Disparo da ação de logout |
| endImpersonate | — | Clique para encerrar impersonação de usuário |
| fabClick | — | Clique no botão de ação central móvel (FAB) |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| blank | — | Conteúdo quando a rota é designada como layout limpo |
| login | — | Substitui o formulário de login padrão |
| authenticated / default | — | Área principal renderizada dentro do layout autenticado |

**Exemplo**
```vue
<MaxApp
  logo="/images/logo.svg"
  route-login="/api/auth/login"
  route-user="/api/auth/me"
  @logout="efetuarLogout"
>
  <RouterView />
</MaxApp>
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

### MaxBadge
Import: `import { MaxBadge } from '@maxvue/max-components-ui'`
Aliases: `Badge`, `Tag`, `MaxTag`.
Propósito: badge e etiqueta visual moderna com suporte a cálculos de luminância relativa WCAG (`resolveBadgeColors`), estilo neon translúcido com brilho, indicador de status circular (`done`, `error`, `caution`, etc.), ícone Iconify e overlay/contador numérico.

**Props** (via `MaxBadgeProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string \| number | — | **sim** | Texto ou valor principal do badge |
| icon | string | — | não | Nome do ícone Iconify à esquerda do texto |
| color | string | `'var(--blue-600)'` | não | Cor base (hex, rgb ou CSS var); contrastes de texto/fundo são calculados automaticamente |
| neon | boolean | false | não | Aplica efeito neon translúcido com borda suave e brilho |
| status | `MaxBadgeStatus` | — | não | Círculo de status à esquerda ('done' \| 'success' \| 'error' \| 'danger' \| 'info' \| 'help' \| 'warn' \| 'caution') |
| overlay | boolean \| string \| number | — | não | Exibe contador de notificação ou status simplificado no canto |
| uppercase | boolean | true | não | Transforma o texto em caixa-alta por padrão |
| noUppercase | boolean | false | não | Desativa a caixa-alta preservando o texto original |
| size | string \| number | — | não | Tamanho do badge ('large', 'xlarge' ou valor customizado) |
| background | string | — | não | Sobrescrita manual da cor de fundo |
| textColor | string | — | não | Sobrescrita manual da cor do texto |

**Exemplo**
```vue
<MaxBadge label="Em Andamento" status="caution" :neon="true" />
<MaxBadge label="Mensagens" icon="mdi:email" :overlay="5" color="#10b981" />
```

---

### MaxBadgeButton
Import: `import { MaxBadgeButton } from '@maxvue/max-components-ui'`
Aliases: `BadgeButton`.
Propósito: botão de alternância interativo encapsulando o `MaxBadge`. Suporta estado ligado/desligado via `v-model` (`boolean | number`), atributos de acessibilidade (`aria-pressed`) e eventos reativos de ativação.

**Props** (via `MaxBadgeButtonProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string \| number | — | **sim** | Texto do badge |
| icon | string | — | não | Ícone do badge |
| color | string | `'var(--blue-600)'` | não | Cor ativa do badge |
| neon | boolean | false | não | Estilo visual neon |
| status | `MaxBadgeStatus` | — | não | Círculo indicador de status |
| overlay | boolean \| string \| number | — | não | Pílula ou contador de notificação |
| uppercase | boolean | true | não | Caixa-alta no texto |
| size | string \| number | — | não | Dimensão do botão |
| modelValue | boolean \| number | false | não | Estado ativo/inativo (suporta v-model) |
| disabled | boolean | false | não | Desabilita o clique no botão |
| onClick | `(event, state) => void` | — | não | Callback disparado no clique |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: boolean \| number` | Atualização do v-model de seleção |
| change | `value: boolean \| number` | Notificação de mudança de estado |
| click | `(event: MouseEvent, state: boolean \| number)` | Disparo de clique com estado atual |
| active | `event: MouseEvent` | Disparado ao alternar para o estado ativo |
| deactive | `event: MouseEvent` | Disparado ao alternar para o estado inativo |

**Exemplo**
```vue
<MaxBadgeButton v-model="filtroAtivo" label="Somente Pendentes" icon="mdi:filter" />
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

### MaxBottomMenu
Import: `import { MaxBottomMenu } from '@maxvue/max-components-ui'`
Propósito: barra de navegação inferior voltada a interfaces mobile (estilo bottom navigation). Oferece abas com ícone e rótulo, correspondência automática com a rota ativa (incluindo rotas secundárias via `matches`), botão de ação flutuante (FAB) central com recorte curvado SVG e integração com menu popup.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| tabs | `BottomTab[]` | padrão Engeapp | não | Lista de abas `{ name, label, icon, matches? }` |
| addItems | `Array<Record<string, any>>` | `[]` | não | Ações do botão central "+ Adicionar" |
| showFab | boolean | auto (se houver addItems ou slot) | não | Força a exibição ou ocultação do botão de ação central FAB |
| curved | boolean | true | não | Aplica recorte côncavo SVG moderno ao redor do FAB |
| showLabels | boolean | false | não | Exibe rótulos textuais sob os ícones das abas |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| fabClick | — | Clique no botão central FAB |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| fab | — | Substitui o botão de ação central FAB por um componente customizado |

**Exemplo**
```vue
<MaxBottomMenu
  :tabs="[
    { name: 'dashboard', label: 'Início', icon: 'mdi:home' },
    { name: 'pedidos', label: 'Pedidos', icon: 'mdi:cart', matches: ['pedido_detalhe'] },
    { name: 'perfil', label: 'Conta', icon: 'mdi:account' }
  ]"
  :show-labels="true"
/>
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

### MaxButtonConfirm
Import: `import { MaxButtonConfirm } from '@maxvue/max-components-ui'`
Propósito: botão de ação que abre um popover flutuante de confirmação antes de executar uma ação (ex.: exclusão, cancelamento). Conecta-se à store `useConfirmStore` e posiciona o popover ancorado ao próprio botão.

**Props** (herda `ConfirmProps` e atributos de botão)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| label | string | — | não | Rótulo do botão principal |
| icon / i | string | — | não | Ícone do botão principal |
| severity | string | 'danger' | não | Severidade visual do botão ('secondary', 'danger', etc.) |
| variant | 'outlined' \| 'text' \| 'link' | — | não | Estilo do botão principal |
| loading | boolean | false | não | Estado de carregamento do botão |
| message | string | 'Deseja continuar?' | não | Pergunta exibida no balão de confirmação |
| messageIcon | string | — | não | Ícone exibido no balão de confirmação |
| accept | `() => void` | — | não | Ação executada ao clicar no botão de confirmação ("Sim") |
| reject | `() => void` | — | não | Ação executada ao cancelar a confirmação ("Não") |
| acceptLabel | string | 'Sim' | não | Texto do botão de confirmação |
| rejectLabel | string | 'Não' | não | Texto do botão de rejeição |
| acceptIcon | string | 'mdi:check' | não | Ícone do botão de confirmação |
| rejectIcon | string | 'mdi:close' | não | Ícone do botão de rejeição |
| acceptSeverity | string | 'danger' | não | Severidade do botão de confirmação |
| rejectSeverity | string | 'secondary' | não | Severidade do botão de rejeição |

**Exemplo**
```vue
<MaxButtonConfirm
  label="Excluir Registro"
  icon="mdi:trash-can"
  severity="danger"
  message="Tem certeza que deseja apagar este item permanentemente?"
  :accept="deletarItem"
/>
```

---

### MaxChart
Import: `import { MaxChart } from '@maxvue/max-components-ui'`
Propósito: componente de renderização gráfica assíncrona baseado em Chart.js. Permite desenhar gráficos vetoriais responsivos em HTML5 Canvas, suportando temas, tooltips reativos e múltiplos tipos de visualização (`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| type | `MaxChartType` | 'bar' | não | Tipo de gráfico ('bar' \| 'line' \| 'pie' \| 'doughnut' \| 'radar' \| 'polarArea' \| 'bubble' \| 'scatter') |
| data | `MaxChartData` | null | não | Objeto de dados contendo `labels` e `datasets` compatível com Chart.js |
| options | `MaxChartOptions` | `{ maintainAspectRatio: false }` | não | Configuração e opções de customização do Chart.js |
| plugins | `MaxChartPlugin[]` | null | não | Lista de plugins específicos do Chart.js |
| ariaLabel | string | — | não | Rótulo para leitores de tela e acessibilidade do canvas |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| loaded | `chart: MaxChartInstance` | Emitido quando a biblioteca carrega e a instância do gráfico é montada |
| select | `{ originalEvent, index, datasetIndex }` | Emitido ao clicar sobre uma barra, linha ou fatia do gráfico |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| chartInstance | `Ref<Chart \| null>` | Instância bruta do Chart.js |
| getChart | `() => Chart \| null` | Método que retorna a instância atual do gráfico |
| update | `() => void` | Força a re-renderização do gráfico |
| destroy | `() => void` | Destrói a instância do gráfico e limpa listeners |

**Exemplo**
```vue
<MaxChart
  type="doughnut"
  :data="{
    labels: ['Concluídos', 'Pendentes', 'Cancelados'],
    datasets: [{ data: [12, 5, 2], backgroundColor: ['#10b981', '#f59e0b', '#ef4444'] }]
  }"
  style="height: 280px;"
/>
```

---

### MaxChips
Import: `import { MaxChips } from '@maxvue/max-components-ui'`
Aliases: `Chips`.
Propósito: campo de formulário para inserção e gestão de múltiplos tokens/tags (chips). Suporta valores simples (strings e números) ou objetos com labels e chaves customizáveis, remoção via teclado (Backspace), bloqueio de duplicatas e integração completa com o layout do `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | `ChipItem[]` | `[]` | não | Array de chips selecionados (suporta v-model) |
| placeholder | string | — | não | Texto exibido quando a lista de chips está vazia |
| allowDuplicate | boolean | false | não | Permite inclusão de tags repetidas |
| max | number | — | não | Quantidade máxima de chips permitidos |
| addOnBlur | boolean | false | não | Adiciona automaticamente o chip ao perder o foco do campo |
| separator | `string \| RegExp` | `','` | não | Separador de digitação para dividir valores colados/digitados |
| asObject | boolean | false | não | Armazena os itens como objetos `{ label, value }` |
| objectLabelKey | string | 'label' | não | Propriedade do objeto a ser exibida visualmente |
| objectValueKey | string | 'value' | não | Propriedade do objeto correspondente ao valor |
| removable | boolean | true | não | Permite remover chips clicando no ícone de fechar |
| disabled | boolean | false | não | Desabilita o campo e a remoção de chips |
| label | string | — | não | Rótulo integrado ao InputBase |
| float | boolean | false | não | Estilo de rótulo flutuante |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: ChipItem[]` | Disparado na adição ou remoção de qualquer chip |
| add | `payload: { originalEvent, value }` | Disparado ao adicionar um novo chip |
| remove | `payload: { originalEvent, value }` | Disparado ao excluir um chip existente |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| chip | `{ value }` | Customiza o conteúdo de cada chip |
| removeicon | — | Ícone do botão de remoção do chip |
| default | — | Conteúdo adicional |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| inputRef | `Ref<HTMLInputElement>` | Referência ao input de texto |
| focus | `() => void` | Aplica o foco ao campo de entrada de texto |

**Exemplo**
```vue
<MaxChips v-model="tags" label="Tags do Artigo" placeholder="Digite e tecle Enter..." />
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

### MaxContainerApp
Import: `import { MaxContainerApp } from '@maxvue/max-components-ui'`
Propósito: contêiner raiz de aplicação que padroniza o enquadramento em tela cheia (`100vw` / `100vh`), layout flex vertical e tratamento de transições globais.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Componentes estruturais do aplicativo (cabeçalho, barra lateral, rotas) |

**Exemplo**
```vue
<MaxContainerApp>
  <RouterView />
</MaxContainerApp>
```

---

### MaxCreditCard
Import: `import { MaxCreditCard } from '@maxvue/max-components-ui'`
Propósito: componente visual de cartão de crédito/débito realista com animação 3D de alternância entre frente e verso (flip). Detecta automaticamente a bandeira do cartão (Visa, Mastercard, Elo, Amex, Hipercard, Diners, Discover, JCB) renderizando o logotipo em SVG de alta definição, exibindo dados mascarados e chip metálico ilustrado.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| number | string \| number \| null | — | não | Número do cartão digitado (ex.: '4111 1111 1111 1111') |
| cvv | string \| number \| null | — | não | Código verificador impresso no verso do cartão |
| name | string \| null | 'NOME DO TITULAR' | não | Nome do titular impresso no cartão |
| date | string \| number \| null | — | não | Validade do cartão no formato MMAA (ex.: '12/30') |
| cardType | string \| null | auto | não | Força a bandeira ('visa', 'mastercard', 'elo', 'amex', etc.) em vez de auto-detectar |
| side | 'front' \| 'back' | 'front' | não | Face visível atual do cartão (rotaciona suavemente em 3D) |

**Exemplo**
```vue
<MaxCreditCard
  :number="cartao.numero"
  :name="cartao.titular"
  :date="cartao.validade"
  :cvv="cartao.cvv"
  :side="focoNoCvv ? 'back' : 'front'"
/>
```

---

### MaxDividers
Import: `import { MaxDividers } from '@maxvue/max-components-ui'`
Aliases: `MaxDivider`.
Propósito: organizador e divisor de layout de múltiplos painéis (split-pane). Suporta disposição em colunas lado a lado (`in-column`) ou empilhamento em linhas verticais (`in-line`), redimensionamento móvel responsivo baseado em breakpoint e navegação fluida entre os painéis com controle de painel ativo.

**Props** (via `MaxDividersProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| direction | 'in-column' \| 'in-line' | 'in-column' | não | Orientação dos painéis (colunas ou linhas) |
| inLine | boolean | false | não | Atalho booleano para dividir em linhas horizontais empilhadas |
| inColumn | boolean | true | não | Atalho booleano para dividir em colunas verticais lado a lado |
| modelValue | 1 \| 2 | 1 | não | Painel ativo em visualizações móveis (suporta v-model) |
| active | 1 \| 2 | 1 | não | Painel ativo móvel controlado por `v-model:active` |
| breakpoint | number \| 'sm' \| 'md' \| 'lg' \| 'xl' | 1024 | não | Limite de largura de tela abaixo do qual ativa o modo mobile |
| mobile | boolean | auto | não | Força explicitamente o modo mobile independente da largura da janela |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: 1 \| 2` | Atualização do painel ativo |
| update:active | `value: 1 \| 2` | Atualização do painel ativo móvel |
| next | — | Avanço para o segundo painel |
| back | — | Retorno para o primeiro painel |
| resize | `sizes: [number, number]` | Disparado ao redimensionar os painéis |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| first | — | Conteúdo do primeiro painel (lado esquerdo / topo) |
| second-header | — | Cabeçalho específico do segundo painel em modo mobile |
| second | — | Conteúdo do segundo painel (lado direito / rodapé) |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| nextPanel | `() => void` | Avança programaticamente para o segundo painel |
| backPanel | `() => void` | Retorna programaticamente para o primeiro painel |
| setActivePanel | `(panel: 1 \| 2) => void` | Define o painel visível |

**Exemplo**
```vue
<MaxDividers v-model="painelAtivo" in-column>
  <template #first>
    <ListaClientes @selecionar="painelAtivo = 2" />
  </template>
  <template #second>
    <DetalhesCliente @voltar="painelAtivo = 1" />
  </template>
</MaxDividers>
```

---

### MaxDoneIcon
Import: `import { MaxDoneIcon } from '@maxvue/max-components-ui'`. Ícone estático de "concluído" (check verde em círculo). Sem props/emits/slots. Exemplo: `<MaxDoneIcon />`

---

### MaxDrawer
Import: `import { MaxDrawer } from '@maxvue/max-components-ui'`
Aliases: `Drawer`.
Propósito: painel deslizante sobreposto (gaveta / slide-over panel). Ideal para formulários laterais, filtros avançados e detalhes contextuais. Inclui controle de rolagem de página (`useScrollLock`), captura acessível de foco (`useFocusTrap`), fechamento via Escape e máscara translúcida com animação fluida.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| visible | boolean | false | não | Controla se a gaveta está visível (suporta v-model:visible) |
| position | 'left' \| 'right' \| 'top' \| 'bottom' \| 'full' | 'right' | não | Borda da tela a partir da qual o painel surge |
| header | string \| null | null | não | Título exibido no cabeçalho da gaveta |
| dismissable | boolean | true | não | Permite fechar clicando na máscara externa de fundo |
| closeOnEscape | boolean | true | não | Permite fechar pressionando a tecla Escape |
| showCloseIcon | boolean | true | não | Exibe o botão de fechamento com ícone no topo |
| modal | boolean | true | não | Exibe a máscara de sobreposição escurecida no fundo |
| baseZIndex | number | 1100 | não | Camada z-index base da sobreposição |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:visible | `value: boolean` | Disparado na abertura ou fechamento da gaveta |
| show | — | Disparado após a conclusão da animação de abertura |
| hide | — | Disparado após o fechamento da gaveta |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| container | — | Substitui toda a estrutura de contêiner do painel |
| header | — | Substitui o cabeçalho padrão |
| closeicon | — | Customiza o ícone do botão de fechar |
| default | — | Conteúdo principal da gaveta |
| footer | — | Rodapé da gaveta (ex.: botões de confirmação e cancelamento) |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| open | `() => void` | Abre programaticamente o painel |
| close | `() => void` | Fecha o painel |
| toggle | `() => void` | Alterna a visibilidade |
| is_show | `ComputedRef<boolean>` | Retorna se o painel está aberto |

**Exemplo**
```vue
<MaxDrawer v-model:visible="exibirFiltros" header="Filtros Avançados" position="right">
  <FiltroFormulario />
  <template #footer>
    <MaxButton label="Aplicar Filtros" @click="aplicar" />
  </template>
</MaxDrawer>
```

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

### MaxImage
Import: `import { MaxImage } from '@maxvue/max-components-ui'`
Propósito: visualizador e editor profissional de imagens. Oferece lightbox em tela cheia com zoom, rotação, atalhos de teclado e modal integrado de recorte e edição da imagem (crop) que gera saídas em Data URL base64, Blob e objeto File pronto para envio em formulários `multipart/form-data`.

**Props** (via `MaxImageProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| src | string | — | não | URL, data URI ou caminho da imagem |
| alt | string | — | não | Texto alternativo de acessibilidade |
| width | string \| number | — | não | Largura do elemento de imagem inline |
| height | string \| number | — | não | Altura do elemento de imagem inline |
| fit | 'contain' \| 'cover' \| 'fill' \| 'none' \| 'scale-down' | 'cover' | não | Modo de ajuste CSS `object-fit` |
| preview | boolean | true | não | Permite abrir o visualizador de imagem ampliada ao clicar |
| allowEdit | boolean | false | não | Exibe botão de recorte e edição de imagem na barra do visualizador |
| imageClass | string \| string[] \| Record<string, boolean> | — | não | Classes CSS aplicadas diretamente à tag `<img>` |
| imageStyle | StyleValue | — | não | Estilos CSS inline aplicados à imagem |
| onEdit | `(payload: MaxImageEditPayload) => void \| Promise<void>` | — | não | Callback de salvamento da imagem recortada |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:src | `src: string` | Emitido quando a imagem é editada e seu src atualizado |
| edit | `payload: MaxImageEditPayload` | Dados da imagem após recorte e edição `{ dataUrl, blob, file, width, height, mimeType }` |
| crop | `payload: MaxImageEditPayload` | Alias do evento de recorte |
| show | — | Disparado na abertura do visualizador ampliado |
| hide | — | Disparado no fechamento do visualizador |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| image | — | Substitui o elemento de imagem padrão |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| showPreview | `() => void` | Abre manualmente o visualizador ampliado em tela cheia |
| hidePreview | `() => void` | Fecha o visualizador ampliado |
| openEditor | `() => void` | Abre a ferramenta de recorte e edição |

**Exemplo**
```vue
<MaxImage
  src="/fotos/usuario.jpg"
  alt="Foto do perfil"
  :preview="true"
  :allow-edit="true"
  @edit="enviarFotoAoServidor"
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

### MaxInputCreditCard
Import: `import { MaxInputCreditCard } from '@maxvue/max-components-ui'`
Propósito: campo de formulário para preenchimento do número do cartão de crédito. Aplica máscara dinâmica por Maska (`#### #### #### ####`), validação de dígitos via algoritmo de Luhn (`isValidCreditCard`) e feedback automático de status no `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | `''` | **sim** | Número do cartão com formatação (suporta v-model) |
| label | string | `'Número do cartão'` | não | Rótulo exibido no campo |
| required | boolean | false | não | Torna o preenchimento obrigatório |
| _(demais props do InputBase: icon, float, message, done, error, etc.)_ | | | | |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: string` | Número do cartão formatado com máscara |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| unmaskedValue | `Ref<string>` | Número do cartão apenas com dígitos limpos (sem espaços) |

**Exemplo**
```vue
<MaxInputCreditCard v-model="cartao.numero" required />
```

---

### MaxInputCreditCardCvv
Import: `import { MaxInputCreditCardCvv } from '@maxvue/max-components-ui'`
Propósito: campo especializado para digitação do código de segurança do cartão de crédito (CVV/CVC). Aplica máscara puramente numérica, limite configurável de caracteres (`len`, padrão 3) e validação de conclusão.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | `''` | **sim** | Código CVV (suporta v-model) |
| label | string | `'CVV'` | não | Rótulo do campo |
| len | number | 3 | não | Quantidade esperada de dígitos (3 para Visa/Master, 4 para Amex) |
| required | boolean | false | não | Preenchimento obrigatório |
| _(demais props do InputBase)_ | | | | |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: string` | Dígitos do código de segurança |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| unmaskedValue | `Ref<string>` | Valor limpo do CVV |

**Exemplo**
```vue
<MaxInputCreditCardCvv v-model="cartao.cvv" :len="3" required />
```

---

### MaxInputCreditCardDate
Import: `import { MaxInputCreditCardDate } from '@maxvue/max-components-ui'`
Propósito: campo de digitação da data de expiração/validade do cartão de crédito. Aplica máscara automática no formato `MM/AA`, valida que o mês informado está no intervalo válido de 01 a 12 e integra feedback visual com `InputBase`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string | `''` | **sim** | Data no formato 'MM/AA' (suporta v-model) |
| label | string | `'Validade'` | não | Rótulo do campo |
| required | boolean | false | não | Preenchimento obrigatório |
| _(demais props do InputBase)_ | | | | |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: string` | Validade formatada |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| unmaskedValue | `Ref<string>` | Apenas os 4 dígitos MMAA sem barra |

**Exemplo**
```vue
<MaxInputCreditCardDate v-model="cartao.validade" required />
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

### MaxInputOTP
Import: `import { MaxInputOTP } from '@maxvue/max-components-ui'`
Aliases: `InputOTP`, `InputOtp`, `MaxInputOtp`.
Propósito: campo de código de verificação em duas etapas (2FA / OTP / token SMS). Oferece caixas de digitação separadas por dígito com avanço e retrocesso automático de foco, suporte a colagem direta de texto completo, modo máscara (ocultar números digitados), agrupamento visual e validação numérica.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | string \| number | `''` | não | Código OTP completo (suporta v-model) |
| length / len | number | 6 | não | Quantidade total de dígitos do código OTP |
| groupLength | number | — | não | Quantidade de dígitos em cada grupo separado visualmente |
| separator | boolean \| string | false | não | Exibe divisor entre os grupos |
| separatorChar | string | `'-'` | não | Caractere separador visual |
| integerOnly | boolean | true | não | Aceita estritamente números de 0 a 9 |
| mask | boolean | false | não | Oculta os caracteres digitados (estilo campo de senha) |
| autofocus | boolean | false | não | Foca na primeira caixa ao montar o componente |
| disabled | boolean | false | não | Desabilita todos os campos |
| label | string | — | não | Rótulo via InputBase |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: string` | Código OTP montado |
| complete | `value: string` | Disparado imediatamente quando todas as caixas são preenchidas |
| change | `value: string` | Disparado em cada alteração de caractere |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| separator | — | Customiza o elemento separador entre grupos de caixas |
| default | — | Conteúdo adicional |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| focus | `(index?: number) => void` | Move o foco para uma caixa específica (padrão 0) |
| clear | `() => void` | Limpa todos os dígitos digitados |

**Exemplo**
```vue
<MaxInputOTP v-model="codigo2FA" :length="6" :autofocus="true" @complete="validarToken" />
```

---

### MaxInputPhone
Import: `import { MaxInputPhone } from '@maxvue/max-components-ui'`
Aliases: `MaxPhoneField`, `PhoneField`, `InputPhone`.
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
<MaxInputPhone v-model="telefone" />
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

### MaxLikeButton
Import: `import { MaxLikeButton } from '@maxvue/max-components-ui'`
Aliases: `LikeButton`.
Propósito: botão de curtir/gostei interativo com contador animado, persistência opcional no localStorage para controle de cooldown e prevenção de votos repetidos (`repeat`/`allowRepeat`), ícones distintos para os estados curtido/não-curtido e badge com a contagem total.

**Props** (via `MaxLikeButtonProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | number | 0 | não | Quantidade total de curtidas (suporta v-model) |
| liked | boolean | false | não | Estado se o usuário atual já curtiu (suporta v-model:liked) |
| onlyIcon | boolean | false | não | Exibe apenas o ícone e badge sem rótulo de texto |
| noNumber | boolean | false | não | Oculta o contador numérico de likes |
| label | string | `'Gostei'` | não | Rótulo do botão |
| icon | string | — | não | Ícone padrão |
| iconTrue / iconLiked | string | `'mdi:thumb-up'` | não | Ícone quando curtido |
| iconFalse | string | `'mdi:thumb-up-outline'` | não | Ícone quando não curtido |
| repeat / allowRepeat | boolean \| number | false | não | Permite repetir o like após intervalo em minutos (true = 60 min, ou minutos customizados) |
| id | string | — | não | Identificador único do item para gravação de cooldown no localStorage |
| storageKey | string | — | não | Chave customizada para persistência local |
| disabled | boolean | false | não | Desabilita interação |
| loading | boolean | false | não | Estado de carregamento |
| size | string \| number | — | não | Tamanho do botão ('small', 'large', etc.) |
| badgeClass | string | — | não | Classes CSS para o contador |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: number` | Atualização do número total de likes |
| update:liked | `value: boolean` | Atualização do estado de curtido |
| click | `(event: MouseEvent, state: { liked: boolean, count: number })` | Notificação de clique com estado atual |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo adicional dentro do botão |

**Exemplo**
```vue
<MaxLikeButton v-model="post.likes" v-model:liked="post.usuarioCurtiu" id="post-1042" />
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

### MaxListBox
Import: `import { MaxListBox } from '@maxvue/max-components-ui'`
Aliases: `ListBox`, `Listbox`.
Propósito: lista de seleção de alto desempenho com suporte a filtro de pesquisa, seleção simples ou múltipla, virtual scroll para lidar com listas de milhares de registros, slots ricos e suporte a carregamento local ou via endpoint de API.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| modelValue | any | — | não | Valor selecionado (ou array de valores no modo múltiplo) |
| options | any[] | `[]` | não | Lista de itens para seleção |
| optionValue | string | 'value' | não | Propriedade que identifica o valor do item |
| optionLabel | string | 'label' | não | Propriedade com o texto principal de exibição |
| optionSubLabel | string | 'sublabel' | não | Propriedade secundária exibida abaixo do label |
| multiple | boolean | false | não | Permite seleção de múltiplos registros |
| filter | boolean | false | não | Exibe barra de pesquisa no topo da lista |
| filterPlaceholder | string | `'Pesquisar...'` | não | Placeholder do campo de busca |
| virtualScroller | boolean | false | não | Ativa virtual scrolling para listas volumosas |
| itemSize | number | 40 | não | Altura em pixels de cada item no virtual scroll |
| emptyMessage | string | `'Nenhum resultado encontrado'` | não | Mensagem quando a lista ou busca está vazia |
| loading | boolean | false | não | Estado de carregamento da lista |
| disabled | boolean | false | não | Desabilita interação com a lista |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| update:modelValue | `value: any` | Item selecionado (ou array de itens) |
| change | `{ value: any, option: any }` | Disparado na alteração de seleção |
| filter | `term: string` | Disparado quando o termo de busca é alterado |
| load-error | `error: unknown` | Disparado caso ocorra falha na requisição da lista |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| header | — | Conteúdo fixado no topo da lista |
| option | `{ option, selected, index }` | Customiza a renderização de cada linha da lista |
| loader | — | Indicador de carregamento customizado |
| empty | — | Conteúdo exibido quando não há itens |
| footer | — | Conteúdo fixado no rodapé da lista |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| listElem | `Ref<HTMLElement>` | Referência ao elemento contêiner da lista |

**Exemplo**
```vue
<MaxListBox
  v-model="cidadeSelecionada"
  :options="cidades"
  option-label="nome"
  option-value="id"
  :filter="true"
  :virtual-scroller="true"
/>
```

---

### MaxLoadScreen
Import: `import { MaxLoadScreen } from '@maxvue/max-components-ui'`
Propósito: tela global de carregamento e bloqueio reativa da aplicação. Conecta-se diretamente à store `useLoadingStore` e renderiza camadas de sobreposição com backdrop blur e itens direcionados gerenciados por `MaxLoadScreenTarget`. Não requer props.

**Exemplo**
```vue
<!-- Declarado no template raiz da aplicação, ex.: MaxApp ou App.vue -->
<MaxLoadScreen />
```

---

### MaxLoadScreenTarget
Import: `import { MaxLoadScreenTarget } from '@maxvue/max-components-ui'`
Propósito: alvo de carregamento direcionado que projeta via `<Teleport>` uma tela de feedback visual e progresso para um seletor específico do DOM ou tela cheia. Suporta animações Lottie (`.lottie_icon`), ícones Iconify e estados de etapas (`loading`, `done`, `waiting`, `error`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| target | `LoadingTarget` | — | **sim** | Objeto contendo o seletor `target` (ex.: 'body' ou '#painel') e array de etapas `items` |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Substitui o layout padrão de exibição das mensagens de carregamento |

**Exemplo**
```vue
<MaxLoadScreenTarget :target="{ target: '#painel-relatorio', items: [{ message: 'Gerando PDF...', status: 'loading' }] }" />
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

### MaxMenuVerticalItem
Import: `import { MaxMenuVerticalItem } from '@maxvue/max-components-ui'`
Aliases: `MenuVerticalItem`.
Propósito: primitiva para itens de navegação vertical em barras laterais. Renderiza botão de ícone responsivo, detecta se o item corresponde à rota/página atual via `useSystemStore`, aplica estilo de aba ativa e limpa o campo de busca global ao navegar.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| items | `SideMenuItem[]` | — | **sim** | Lista de itens de navegação lateral com rótulo, ícone e rota associada |
| textCenter | boolean | false | não | Centraliza o texto do rótulo |

**Exemplo**
```vue
<MaxMenuVerticalItem :items="menuLateralItens" />
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

### MaxPageContent
Import: `import { MaxPageContent } from '@maxvue/max-components-ui'`
Aliases: `PageContent`.
Propósito: contêiner principal para a área de conteúdo das páginas do sistema. Define espaçamento padrão responsivo (padding), altura flexível e rolagem vertical independente dentro do layout principal.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo da página atual (views e componentes) |

**Exemplo**
```vue
<MaxPageContent>
  <h1>Título da Página</h1>
  <p>Conteúdo da view...</p>
</MaxPageContent>
```

---

### MaxPageLayout
Import: `import { MaxPageLayout } from '@maxvue/max-components-ui'`
Aliases: `PageLayout`.
Propósito: layout mestre completo e responsivo da aplicação. Alterna automaticamente entre modo desktop (com `MaxSideMenu`, `MaxTopMenu`, `MaxTopToolbar` e `MaxPageContent`) e modo mobile (com `MaxPageMobileLayout`), gerenciando logo, menus, eventos de logout, perfil e tema.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| screen | string | auto (`system.type_device`) | não | Força dispositivo ('desktop' \| 'mobile') |
| logo | string | — | não | Caminho, URL ou nome de rota da logo |
| addItems | `Array<Record<string, any>>` | `[]` | não | Ações rápidas para o menu de criação do topo e FAB |
| bottomTabs | `BottomTab[]` | padrão Engeapp | não | Abas inferiores na visão mobile |
| bottomShowLabels | boolean | false | não | Exibe texto sob ícones no menu inferior móvel |
| sideMenuGroups | `MenuGroup[]` | `[]` | não | Grupos de menu da gaveta móvel |
| sideMenuItems | any[] | `[]` | não | Itens da gaveta móvel |
| avatarPath | string | `'/avatar/'` | não | Caminho base para avatares dos usuários |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile | — | Clique na opção de perfil |
| settings | — | Clique na opção de configurações |
| support | — | Clique no suporte |
| toggleDarkMode | — | Alternância do modo escuro/claro |
| logout | — | Ação de deslogar do sistema |
| endImpersonate | — | Encerramento de sessão impersonada |
| fabClick | — | Clique no botão de ação móvel (FAB) |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Área principal do conteúdo renderizado dentro do layout |

**Exemplo**
```vue
<MaxPageLayout logo="/logo.svg" @logout="sair">
  <RouterView />
</MaxPageLayout>
```

---

### MaxPageMobileLayout
Import: `import { MaxPageMobileLayout } from '@maxvue/max-components-ui'`
Aliases: `PageMobileLayout`.
Propósito: layout especializado para visualizações em smartphones e tablets. Oferece cabeçalho compacto, gaveta lateral deslizante (`MaxSideMenuMobile`), barra inferior fixa (`MaxBottomMenu`) e área de rolagem isolada.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| logo | string | — | não | Logo do cabeçalho móvel |
| addItems | `Array<Record<string, any>>` | `[]` | não | Ações rápidas do FAB inferior |
| bottomTabs | `BottomTab[]` | padrão Engeapp | não | Configuração das abas da barra inferior |
| bottomShowLabels | boolean | false | não | Exibe rótulos textuais sob as abas |
| sideMenuGroups | `MenuGroup[]` | `[]` | não | Grupos da gaveta lateral móvel |
| sideMenuItems | any[] | `[]` | não | Itens individuais da gaveta |
| avatarPath | string | `'/avatar/'` | não | Caminho base dos avatares |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile / settings / support / toggleDarkMode / logout / endImpersonate / fabClick | — | Eventos repassados do shell móvel |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo principal da página |
| bugs | — | Acesso ao modal/botão de reporte de bugs |
| bottom-menu | — | Substitui a barra inferior |
| side-menu | — | Substitui a gaveta lateral |
| switcher | — | Alternador de empresa/organização |

**Exemplo**
```vue
<MaxPageMobileLayout logo="/logo-mobile.svg" @logout="sair">
  <RouterView />
</MaxPageMobileLayout>
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

### MaxSideMenu
Import: `import { MaxSideMenu } from '@maxvue/max-components-ui'`
Aliases: `SideMenu`.
Propósito: menu lateral de navegação desktop com recolhimento animado, exibição de logo configurável com resolução dinâmica via `getRoute`, divisão em seções de páginas e configurações e sincronização com `useListMenusStore`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| logo | string | — | não | Logo exibida no topo (aceita URL, data URI ou nome de rota registrado) |

**Exemplo**
```vue
<MaxSideMenu logo="/images/logo-sistema.svg" />
```

---

### MaxSideMenuMobile
Import: `import { MaxSideMenuMobile } from '@maxvue/max-components-ui'`
Aliases: `SideMenuMobile`.
Propósito: menu gaveta móvel que se abre lateralmente via `MaxDrawer`. Exibe perfil completo do usuário logado, avatar (`MaxUserAvatar`), grupos de menus expansíveis, botão de alternância de tema e ações de perfil e logout.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| groups | `MenuGroup[]` | `[]` | não | Grupos de navegação `{ title?, items }` |
| items | any[] | `[]` | não | Itens de menu planos (opcional) |
| avatarPath | string | `'/avatar/'` | não | Caminho dos avatares |
| showThemeToggle | boolean | false | não | Exibe alternador de tema claro/escuro no rodapé |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile | — | Clique no perfil |
| settings | — | Clique em configurações |
| support | — | Clique em suporte |
| toggleDarkMode | — | Alternância de tema escuro |
| logout | — | Clique em sair |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| switcher | — | Slot para seletor de empresa/conta ativa |

**Exemplo**
```vue
<MaxSideMenuMobile :groups="gruposDoMenu" @logout="sair" />
```

---

### MaxStats
Import: `import { MaxStats } from '@maxvue/max-components-ui'`
Aliases: `Stats`.
Propósito: componente de apresentação de métricas, totais e KPIs essenciais. Calcula automaticamente as cores de fundo, texto e ícone de cada item respeitando taxas de luminância relativa e contraste WCAG (`resolveStatItemColors`). Suporta disposição responsiva em cards completos, pílulas compactas ou modo automático.

**Props** (via `MaxStatsProps`)
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| items | `MaxStatsItem[]` | `[]` | não | Array de indicadores `{ label, sublabel?, icon, color, value }` |
| allowLineBreak | boolean | false | não | Permite quebra de linha quando houver muitos itens; falso ativa rolagem horizontal suave |
| layout | 'auto' \| 'cards' \| 'pills' | 'auto' | não | Formato visual dos indicadores (auto comuta para pílulas no mobile) |

**Tipos Associados**
```ts
export interface MaxStatsItem {
  label: string;
  sublabel?: string;
  icon: string;
  color: string;
  value: string | number;
}
```

**Exemplo**
```vue
<MaxStats
  :items="[
    { label: 'Projetos Concluídos', value: 148, icon: 'mdi:check-circle', color: '#10b981', sublabel: '+12% este mês' },
    { label: 'Em Negociação', value: 34, icon: 'mdi:handshake', color: '#3b82f6' },
    { label: 'Atrasados', value: 3, icon: 'mdi:alert', color: '#ef4444' }
  ]"
  layout="cards"
/>
```

---

### MaxTab
Import: `import { MaxTab } from '@maxvue/max-components-ui'`
Aliases: `Tab`.
Propósito: cabeçalho individual de aba dentro de um `MaxTabList`. Registra-se dinamicamente no contexto do `MaxTabs`, manipula atributos de acessibilidade ARIA (`role="tab"`, `aria-selected`, `aria-controls`), e suporta ativação por foco com teclado (`selectOnFocus`).

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| value | string | — | **sim** | Identificador da aba que conecta com o `MaxTabPanel` correspondente |
| disabled | boolean | false | não | Desabilita a aba impedindo seleção |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Texto ou ícone do cabeçalho da aba |

**Exemplo**
```vue
<MaxTab value="dados">Dados Gerais</MaxTab>
```

---

### MaxTabItem
Import: `import { MaxTabItem } from '@maxvue/max-components-ui'`
Aliases: `TabItem`.
Propósito: componente unificado de aba e conteúdo para a API clássica e declarativa do `MaxTabs`. Injeta-se no contêiner pai registrando título, ícone e painel de conteúdo em uma única tag.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| title | string | — | não | Título da aba |
| icon / i | string | — | não | Ícone exibido no título da aba |
| value | string \| number | autogerado | não | Identificador único da aba |
| actionButtonLabel | string | — | não | Rótulo para botão de ação integrado ao cabeçalho |
| actionButtonIcon | string | — | não | Ícone do botão de ação |
| actionButton | `(event?: MouseEvent) => unknown` | — | não | Ação executada ao clicar no botão da aba |
| disabled | boolean | false | não | Desabilita a aba |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| title | — | Substitui o título do cabeçalho |
| default | — | Conteúdo exibido dentro do painel da aba |

**Exemplo**
```vue
<MaxTabItem title="Endereço" icon="mdi:map-marker" value="endereco">
  <FormularioEndereco />
</MaxTabItem>
```

---

### MaxTabList
Import: `import { MaxTabList } from '@maxvue/max-components-ui'`
Aliases: `TabList`.
Propósito: contêiner para os cabeçalhos de abas (`MaxTab`). Gerencia rolagem horizontal com setas de navegação suave quando em overflow (`scrollable`), preserva foco de teclado e alinha bordas indicadoras ativas.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Elementos `<MaxTab>` a serem renderizados na lista |

**Exemplo**
```vue
<MaxTabList>
  <MaxTab value="1">Aba 1</MaxTab>
  <MaxTab value="2">Aba 2</MaxTab>
</MaxTabList>
```

---

### MaxTabPanel
Import: `import { MaxTabPanel } from '@maxvue/max-components-ui'`
Aliases: `TabPanel`.
Propósito: painel de conteúdo associado a uma aba. Conecta-se ao `MaxTab` de mesmo `value`. Suporta renderização preguiçosa (`lazy`), montando no DOM somente quando ativado pela primeira vez e mantendo o estado dos componentes internos preservado.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| value | string | — | **sim** | Identificador que casa com o `value` do `MaxTab` |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Conteúdo a ser exibido quando este painel for selecionado |

**Exemplo**
```vue
<MaxTabPanel value="dados">
  <p>Conteúdo da aba de dados.</p>
</MaxTabPanel>
```

---

### MaxTabPanels
Import: `import { MaxTabPanels } from '@maxvue/max-components-ui'`
Aliases: `TabPanels`.
Propósito: contêiner estrutural que agrupa todos os painéis `<MaxTabPanel>` sob um mesmo `<MaxTabs>`.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Painéis `<MaxTabPanel>` |

**Exemplo**
```vue
<MaxTabPanels>
  <MaxTabPanel value="tab1">Painel 1</MaxTabPanel>
  <MaxTabPanel value="tab2">Painel 2</MaxTabPanel>
</MaxTabPanels>
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

### MaxTabs
Import: `import { MaxTabs } from '@maxvue/max-components-ui'`
Aliases: `Tabs`.
Propósito: sistema modular e acessível de abas. Substitui o TabView do PrimeVue fornecendo contexto reativo via Context API (`TABS_INJECTION_KEY`) para subcomponentes modulares (`MaxTabList`, `MaxTab`, `MaxTabPanels`, `MaxTabPanel`) e para a sintaxe clássica (`MaxTabItem`). Oferece cache em localStorage (`cached`), rolagem automática (`scrollable`), navegação por setas e renderização lazy.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| title | string | `''` | não | Título opcional da seção de abas |
| icon | string | `'x'` | não | Ícone do cabeçalho |
| id | string \| number | — | não | Identificador único para salvar a aba ativa em cache |
| cached | boolean | true | não | Salva a última aba ativa em localStorage |
| lazy | boolean | false | não | Renderiza os painéis sob demanda na primeira abertura |
| selectOnFocus | boolean | false | não | Seleciona automaticamente a aba ao receber foco via teclado |
| scrollable | boolean | false | não | Permite rolagem horizontal com botões se houver muitas abas |
| showNavigators | boolean | true | não | Exibe botões de seta nas pontas em modo scrollable |
| spread | boolean | false | não | Distribui as abas uniformemente por toda a largura |
| actionButtonLabel | string | — | não | Rótulo para botão de ação à direita |
| actionButtonIcon | string | — | não | Ícone do botão de ação |
| actionButton | `(event?: MouseEvent) => unknown` | — | não | Callback do botão de ação |

**v-model**
| Nome | Tipo | Descrição |
|------|------|-----------|
| value (defineModel) | `string \| number` | Identificador da aba atualmente ativa |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Lista de abas e painéis |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| select | `(value: string) => void` | Seleciona programaticamente uma aba |
| navigate | `(direction: 1 \| -1) => void` | Avança ou recua a aba ativa |

**Exemplo**
```vue
<MaxTabs v-model:value="abaAtiva" :scrollable="true">
  <MaxTabList>
    <MaxTab value="geral">Visão Geral</MaxTab>
    <MaxTab value="detalhes">Detalhes</MaxTab>
  </MaxTabList>
  <MaxTabPanels>
    <MaxTabPanel value="geral"><VisaoGeral /></MaxTabPanel>
    <MaxTabPanel value="detalhes"><Detalhes /></MaxTabPanel>
  </MaxTabPanels>
</MaxTabs>
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

### MaxTopMenu
Import: `import { MaxTopMenu } from '@maxvue/max-components-ui'`
Aliases: `TopMenu`.
Propósito: barra de navegação superior principal da aplicação. Integra a barra de busca rápida (`MaxTopMenuSearchBar`), menu dropdown de criação rápida ("+ Adicionar Novo"), atalhos para chat, voip e notificações, widget de perfil do usuário (`MaxUserSection`) e botão de alternância do menu lateral.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| addItems | `Array<Record<string, any>>` | `[]` | não | Ações disponíveis no botão "+ Adicionar Novo" |
| avatarPath | string | `'/avatar/'` | não | Caminho base para avatares de usuário |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile / settings / support / toggleDarkMode / logout / endImpersonate | — | Eventos repassados da seção de usuário |

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| search | — | Substitui ou complementa a barra de pesquisa |
| add | — | Customiza o botão de adicionar |
| chat / notifications / voip / live | — | Ícones de atalho e contadores no topo |
| user | — | Substitui o componente de perfil |
| mobile-center / mobile-actions | — | Áreas reservadas para personalização na barra móvel |

**Exemplo**
```vue
<MaxTopMenu :add-items="itensCriacaoRapida" @logout="sair" />
```

---

### MaxTopMenuSearchBar
Import: `import { MaxTopMenuSearchBar } from '@maxvue/max-components-ui'`
Aliases: `TopMenuSearchBar`.
Propósito: campo de busca global instantânea posicionado na barra superior. Abre por atalho universal de teclado `Ctrl+F` ou `Cmd+F` (prevenindo o comportamento padrão do navegador), fecha ao teclar `Escape` e sincroniza o termo digitado reativamente com a store `useSearchBarStore`.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| placeholder | string | `'Pesquisar'` | não | Texto de orientação exibido no campo |
| screen | string | auto (`system.type_device`) | não | Força comportamento 'desktop' ou 'mobile' |

**Exemplo**
```vue
<MaxTopMenuSearchBar placeholder="Pesquisar projetos, clientes ou rotas (Ctrl+F)..." />
```

---

### MaxTopToolbar
Import: `import { MaxTopToolbar } from '@maxvue/max-components-ui'`
Aliases: `TopToolbar`.
Propósito: barra de ferramentas secundária horizontal. Exibe botões de ação contextuais da página corrente, suporte a submenus em cascata com atraso de fechamento inteligente (1 segundo de tolerância após saída do mouse) e sincronização com `useTopToolbarStore`.

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| plus | — | Slot para botões adicionais no final da barra |

**Exemplo**
```vue
<MaxTopToolbar />
```

---

### MaxTopToolbarSubmenu
Import: `import { MaxTopToolbarSubmenu } from '@maxvue/max-components-ui'`
Aliases: `TopToolbarSubmenu`.
Propósito: componente de submenu suspenso para a barra de ferramentas `MaxTopToolbar`. Suporta árvores aninhadas de itens e controle reativo de eventos de abertura/fechamento.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| items | any[] | — | **sim** | Lista de itens aninhados `{ label, icon, items?, action?, route? }` |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| keep-open | — | Sinaliza que o ponteiro está sobre um submenu filho |
| schedule-close | — | Agenda fechamento por temporizador |
| item-click | `item: any` | Clique em um item folha do menu |

**Exemplo**
```vue
<MaxTopToolbarSubmenu :items="itensDoSubmenu" @item-click="executarAcao" />
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

### MaxUserSection
Import: `import { MaxUserSection } from '@maxvue/max-components-ui'`
Aliases: `UserSection`.
Propósito: widget de usuário para o cabeçalho. Mostra avatar (`MaxUserAvatar`), nome, empresa, alternador de modo escuro/claro, aviso visual de impersonação de conta ("SAIR DO MODO ESPELHO") e menu dropdown com rotas de perfil, configurações, suporte e logout.

**Props**
| Prop | Tipo | Default | Obrigatório | Descrição |
|------|------|---------|-------------|-----------|
| name | string | — | não | Nome exibido do usuário |
| companyName | string | — | não | Nome da empresa/organização |
| userId | string \| number | — | não | Identificador do usuário para carregar avatar |
| avatarUrl | string | — | não | URL direta para a foto do avatar |
| darkMode | boolean | false | não | Estado do modo escuro |
| isImpersonated | boolean | false | não | Indica se a sessão atual é de impersonação |
| version | string | — | não | Versão do sistema exibida na base do menu |
| items | any[] | — | não | Substitui a lista de itens padrão do menu suspenso |
| onlyAvatar | boolean | false | não | Modo compacto (exibe somente o avatar sem nomes) |
| screen | 'desktop' \| 'mobile' | 'desktop' | não | Modo de apresentação |

**Emits**
| Evento | Payload | Descrição |
|--------|---------|-----------|
| profile | — | Clique em "Meu perfil" |
| settings | — | Clique em "Configurações" |
| toggleDarkMode | — | Alternância do tema claro/escuro |
| support | — | Clique em "Suporte" |
| logout | — | Clique em "Sair" |
| endImpersonate | — | Clique em encerrar impersonação |

**Expose**
| Nome | Tipo | Descrição |
|------|------|-----------|
| openMenu | `() => void` | Abre o menu dropdown |
| closeMenu | `() => void` | Fecha o menu dropdown |

**Exemplo**
```vue
<MaxUserSection
  :name="usuario.nome"
  :company-name="usuario.empresa"
  :user-id="usuario.id"
  @logout="sair"
/>
```

---

### MaxWaitIcon
Import: `import { MaxWaitIcon } from '@maxvue/max-components-ui'`. Ícone SVG animado de "aguarde" (ampulheta com animação de rotação/fade), usando `currentColor`. Sem props/emits/slots. Exemplo: `<MaxWaitIcon />`

---

### TransitionFade
Import: `import { TransitionFade } from '@maxvue/max-components-ui'`
Propósito: wrapper de transição suave de fade (opacidade). Aplica transição de opacidade com duração de 200ms e atraso de saída para alternâncias limpas entre elementos ou visões condicionais (`v-if` / `v-show`).

**Slots**
| Slot | Props | Descrição |
|------|-------|-----------|
| default | — | Elemento ou componente único envolvido na transição |

**Exemplo**
```vue
<TransitionFade>
  <div v-if="carregando">Carregando dados...</div>
  <div v-else>Dados carregados com sucesso!</div>
</TransitionFade>
```

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

Exportadas via `export * from './stores'` no index principal E pelo subpath `@maxvue/max-components-ui/stores`.
O barrel `stores/index.ts` re-exporta as seguintes stores especializadas:

1. **useConfirmStore** (`useConfirm.Store.ts`) — estado e posicionamento do balão popover de confirmação para ações de exclusão/críticas (`MaxButtonConfirm`, `MaxIconConfirm`, `MaxTogglePopover`).
2. **useIconStore** (`useIcon.Store.ts`) — cache em `localStorage['all_icons']` e requisição em lote debounced de SVGs da API Iconify (`MaxIcon`, `MaxAiIcon`).
3. **useListMenusStore** (`useListMenus.Store.ts`) — gerenciamento reativo da árvore de menus de navegação (menu lateral e atalhos de topo).
4. **useLoadingStore** (`useLoading.Store.ts`) — fila de tarefas assíncronas ativas e mapeamento de alvos para telas de bloqueio (`MaxLoadScreen`, `MaxLoadScreenTarget`).
5. **useLoginStore** (`useLogin.Store.ts`) — fluxo e estado de autenticação (login, senha, 2FA/OTP, OAuth e recuperação de senha).
6. **useModalStore** (`useModal.Store.ts`) — controle de visibilidade única de janelas modais (`MaxModal`).
7. **usePopoverStore** (`usePopover.Store.ts`) — controle de popovers simples flutuantes (`MaxPopover`).
8. **useSearchBarStore** (`useSearchBar.Store.ts`) — termo de pesquisa rápida e controle de foco da barra global (`MaxTopMenuSearchBar`).
9. **useSystemStore** (`useSystem.Store.ts`) — contexto de execução da aplicação: dispositivo móvel vs desktop (`type_device`), página ativa (`page`), estado aberto/fechado do menu lateral e reload.
10. **useToastStore** (`useToast.Store.ts`) — fila, timers, pausa em hover e remoção de notificações flutuantes toast (`MaxToast`).
11. **useTopToolbarStore** (`useTopToolbar.Store.ts`) — botões de contexto, rotas e visibilidade da barra horizontal secundária (`MaxTopToolbar`).
12. **useUserStore** (`useUser.Store.ts`) — dados do usuário autenticado (`data`), configurações (modo escuro), avatar e status de impersonação.

### Helpers Públicos

Exportados pelo `index.ts`:

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

#### Configuração do App Shell — `import { configureMaxApp, getMaxAppConfig, resetMaxAppConfig } from '@maxvue/max-components-ui'`
Configuração inicial do shell de aplicação (`MaxApp`) no bootstrap do projeto:
```ts
configureMaxApp({
  routeLogin: '/api/auth/login',
  routeUser: '/api/auth/me',
  blankPages: ['login', 'recuperar-senha']
});
```

#### Cache Keys — `import { clearMaxCache, registerMaxCacheKey, isMaxCacheKey, ICON_CACHE_KEY } from '@maxvue/max-components-ui'`
Gerenciamento padronizado de chaves salvas em `localStorage`.

#### WCAG e Luminância de Cores — `import { adjustToWcagLuminance, getWcagRelativeLuminance, resolveStatItemColors, resolveBadgeColors, BADGE_STATUS_COLORS } from '@maxvue/max-components-ui'`
Cálculo de luminância e contraste acessível (WCAG AA/AAA) para componentes de métricas (`MaxStats`) e etiquetas (`MaxBadge`):
- `resolveStatItemColors(color, isDark)`: devolve `{ bg, text, icon }` com contraste perfeito em temas claro e escuro.
- `resolveBadgeColors(color, isDark)`: calcula tons de fundo e texto para badges e tags.

#### Limpeza de Cache de Autenticação — `import { clearAuthOtpCache } from '@maxvue/max-components-ui'`
Limpa tokens temporários de 2FA e tentativas de envio de código OTP.

#### resolver / MaxComponentsUiResolver — subpath `@maxvue/max-components-ui/resolver`
Exportado via `package.json` `exports["./resolver"]`:
- `MaxComponentsUiResolver(): ComponentResolver` e alias `resolver` — resolver de auto-import (unplugin-vue-components); mapeia aliases do `components-manifest.json` para `@maxvue/max-components-ui` e componentes PrimeVue para `@maxvue/max-components-ui/prime`.
```ts
import { MaxComponentsUiResolver } from '@maxvue/max-components-ui/resolver';
```

### Outros subpaths do pacote (`package.json exports`)
- `.` → índice principal (110 componentes + 12 stores + Toast + install/plugin + helpers de cores e app + tipos).
- `./preset` → `presetMaxUno` (preset UnoCSS).
- `./resolver` → resolver de auto-import para unplugin-vue-components.
- `./prime` → componentes PrimeVue reexportados para interoperabilidade.
- `./stores` → barrel das 12 stores Pinia.

### Tipos públicos
`export * from './types'` e `export type * from './types/chart'` expõem todas as interfaces da biblioteca:
- Modelos de dados e props: `MaxStatsItem`, `MaxStatsProps`, `MaxBadgeProps`, `MaxBadgeButtonProps`, `MaxBadgeStatus`, `MaxImageProps`, `MaxImageEditPayload`, `MaxDividersProps`, `MaxLikeButtonProps`, `BottomTab`, `MenuGroup`, `SideMenuItem`.
- Gráficos: `MaxChartType`, `MaxChartData`, `MaxChartOptions`, `MaxChartPlugin`, `MaxChartInstance`.
- Cores e estilo: `StatItemColors`, `BadgeColors`, `MaxButtonsType`, `SelectGroupOptions`.
