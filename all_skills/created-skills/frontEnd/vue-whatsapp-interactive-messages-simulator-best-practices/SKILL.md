---
name: vue-whatsapp-interactive-messages-simulator-best-practices
description: "Use when designing, building, or debugging Vue 3 components/views that simulate WhatsApp interactive messages: text, media headers, quick replies, list messages, CTA buttons, SCSS/UnoCSS styling, and templates."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas para Simulador de Mensagens Interativas do WhatsApp no Vue 3

## Objetivo
Fornecer diretrizes de UI/UX, especificações de design system e padrões de desenvolvimento frontend em Vue 3 para implementar, estilizar e depurar simuladores de WhatsApp de alta fidelidade e editores de templates dentro do ecossistema EngeApp.

## Instruções

### 1. Estrutura e Arquitetura do Componente
Hoje o front de WhatsApp do engeapp já tem um editor + preview de template real: `ChatInputTemplatesPopover.vue` (`resources/Vue/Sections/supportChat/`) implementa dois painéis (`.template-side` para edição, `.template-side-right` para o preview, `display: grid; grid-template-columns: 1fr 1fr`), com o preview renderizado via `<ChatMessageMain :message="list_templates.message_render" direction="send" :showStatus="false" :requested="true" />` — o `message_render` vem de um `computed` em `getListTemplates.Store.ts` que resolve variáveis e marcações (`*negrito*`, ```código```) sobre `list_templates.data_send`. Ao construir ou estender um Simulador de WhatsApp / Editor de Templates, **reutilize esse padrão** e os componentes de renderização já existentes (`ChatMessageMain`, `ChatMessageContent`, `ChatMessageImageBaloon`, `ChatMessageButtonOptions`), em vez de criar artefatos inéditos do zero:
- **Separação de Responsabilidades:** Divida a interface em dois contêineres principais (form / preview), como já faz `ChatInputTemplatesPopover.vue`.
- **Ordenação no SFC e props/emits:** siga a ordenação de blocos e a tipagem de props/emits da skill base `vue`. Para o bloco de estilo, siga a convenção dominante do projeto: `<style lang="scss">` (sem `scoped`), como em `ChatMessageMain.vue`; use `scoped` apenas se necessário para evitar colisão de classes. Props/emits tipados são a recomendação para componentes NOVOS; ao estender os componentes de chat existentes (`ChatMessageMain` e filhos), respeite o padrão real deles, que propaga estado via `useAttrs()` + `v-bind="attrs"` em vez de props individuais (ex.: `ChatMessageMain.vue` usa `const attrs: any = useAttrs()` e repassa com `v-bind="attrs"` para `ChatMessageImageBaloon`/`ChatMessageContent`/`ChatMessageButtonOptions`).

### 2. Estilização do Simulador (SCSS e UnoCSS)
Para simular de forma fidedigna a interface do WhatsApp:
- **Cores e Temas:** os hex abaixo são referência de **aparência do WhatsApp** (nenhum existe hoje no projeto). Dentro do bloco de simulação, declare-os como variáveis CSS locais com par claro/escuro (ex.: `--wa-bg`, `--wa-bubble-send`) — não os espalhe soltos pelo SFC. **Fora** do bloco de simulação (ex.: o chat real em `ChatMessageContent.vue`), continue usando os tokens do design system (`var(--background-*)`), nunca hex hardcoded.
  - Fundo do WhatsApp (Modo Claro): `#efeae2` (com um padrão de papel de parede sutil, se aplicável).
  - Fundo do WhatsApp (Modo Escuro): `#0b141a`.
  - Balão de Mensagem Enviada (Modo Claro): `#d9fdd3` com texto `#111b21`.
  - Balão de Mensagem Enviada (Modo Escuro): `#005c4b` com texto `#e9edef`.
  - Texto Auxiliar/Meta (Cinza): `#667781` (Claro) ou `#8696a0` (Escuro).
- **Arquitetura do Balão:**
  - Garanta que o balão de mensagem tenha uma largura máxima de `85%` ou `320px` para se adequar a uma simulação móvel padrão.
  - Implemente um layout flexível limpo para cabeçalhos de mídia, texto do corpo, rodapé e botões interativos.

### 3. Simulação de Componentes Interativos
- **Cabeçalhos de Mídia:** Suporte a imagens (`<img>`), vídeos (`<video>`) e marcadores para documentos. Aplique bordas arredondadas e proporções responsivas (geralmente `16:9` ou `1:1`).
- **Botões de Resposta Rápida (Quick Reply):** Renderizados como botões de ação separados abaixo do balão de mensagem.
  - O WhatsApp suporta a exibição de até 3 botões de resposta rápida.
  - Limite máximo de 20 caracteres por texto de botão.
- **Botões de Chamada para Ação (CTA):** Renderizados dentro ou acoplados à parte inferior do balão.
  - Suporte a dois tipos de botão: "Visitar Site" e "Ligar para Telefone". Use ícones do Iconify aceitos por `MaxButton`/`Icon`, sempre prefixados pela coleção (ex.: `icon="material-symbols:call"`); não fixe o prefixo `mdi:`, o projeto usa coleções variadas. Detalhes de prefixo/coleção: ver `vue-max-ecosystem-api-reference`.
  - O WhatsApp suporta a exibição de até 2 botões de CTA.
  - Limite máximo de 20 caracteres por texto de botão.
- **Mensagens de Lista (List Messages):** Renderizadas como um botão clicável interativo (ex: "Ver opções" ou "Selecionar itens").
  - Limite máximo de 24 caracteres para o texto do botão.
  - Limite a lista pop-up de opções a no máximo 10 linhas (divididas em seções opcionais).

### 4. Validações no Frontend (Limites da Meta)
Implemente contadores de caracteres ativos e estados de validação no formulário de edição usando propriedades computadas (`computed`) sobre o estado dos inputs. Não introduza bibliotecas de schema (ex.: Zod) — elas não fazem parte do stack do engeapp; a validação é feita com `computed` e com os estados/mensagens dos inputs do `MaxComponentsUi` (ex.: `InputField`, usado no editor de template real em `ChatInputTemplatesPopover.vue`; `InputBase` é o wrapper base, reservado para casos de campo customizado). Notifique o usuário com mensagens de erro ou atenção do input quando os limites forem excedidos:
- **Texto do Corpo:** Máximo de 1024 caracteres.
- **Texto do Cabeçalho (caso não seja mídia):** Máximo de 60 caracteres.
- **Texto do Rodapé:** Máximo de 60 caracteres.
- **Variáveis/Parâmetros:** Certifique-se de detectar variáveis (`{{1}}`, `{{2}}`, etc.) e renderizar dinamicamente campos de entrada separados para preenchimento.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** ignore as regras da Composition API. Nunca utilize a Options API.
- **NÃO** utilize cores de tema hardcoded. Utilize variáveis CSS ou tokens do UnoCSS que respondam corretamente ao alternador global de modo escuro/claro do sistema.
- **NÃO** realize requisições à API da Meta diretamente dentro dos componentes visuais. (a) Todo GET de dados de página e todo salvamento de template devem passar por uma store `@maxvue/max-pinia` (ver `vue-pinia-state-management-best-practices` e `vue-max-stack-frontend-best-practices` para o contrato completo — `options.get.route`/`options.save`, chave de cache real via `getKey()`); (b) as rotas são sempre **NOMES de rota Ziggy pontilhados**, nunca strings de path `/api/...`. Exemplos reais do domínio WhatsApp: `useRefCachedApi('whatsapp.templates.all', ...)` em `getListTemplates.Store.ts`, e `apiPostRoute('support.whatsapp.send.message.template', send_data)` em `ChatInputTemplatesPopover.vue`.
- **NÃO** ligue ações de botão fora do padrão do projeto. Os botões do `MaxComponentsUi` recebem o handler pela prop `:action` (ou `@click`), nunca ficam sem handler, e todos os atributos de layout ficam inline em uma única linha no `<template>`. No código real de WhatsApp do engeapp (pasta `resources/Vue/Sections/supportChat/`) o botão é o wrapper/alias `Botao` (ex.: `<Botao :label="\`${sending ? 'Enviando' : 'Enviar'}\`" :action="sendTemplate" :icon="..." pr-10 />` em `ChatInputTemplatesPopover.vue`); o alias `MaxButton` também existe no projeto. Mantenha a prop `:action` e os atributos inline em ambos.
