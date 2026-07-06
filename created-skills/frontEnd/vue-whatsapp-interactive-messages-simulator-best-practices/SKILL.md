---
name: vue-whatsapp-interactive-messages-simulator-best-practices
description: "Use when designing, building, modifying, styling, or debugging Vue 3 components, composables, or views that simulate and preview WhatsApp interactive messages — text, media headers, quick replies, list messages, call-to-action buttons, or template creation forms. Triggers on WhatsAppSimulator, template builders, and preview panels for the WhatsApp Cloud API."
---

# Boas Práticas para Simulador de Mensagens Interativas do WhatsApp no Vue 3

## Objetivo
Fornecer diretrizes de UI/UX, especificações de design system e padrões de desenvolvimento frontend em Vue 3 para implementar, estilizar e depurar simuladores de WhatsApp de alta fidelidade e editores de templates dentro do ecossistema EngeApp.

## Instruções

### 1. Estrutura e Arquitetura do Componente
Ao construir o Simulador de WhatsApp ou Editor de Templates, siga as convenções do projeto Vue 3:
- **Separação de Responsabilidades:** Divida a interface em dois contêineres principais usando `MaxGrid` ou CSS Grid:
  1. **Painel do Formulário (`.template-editor-form`):** Onde o usuário edita cabeçalhos, texto do corpo, rodapé e botões interativos.
  2. **Painel do Simulador (`.whatsapp-preview-container`):** Pré-visualização visual de alta fidelidade da interface do WhatsApp (simulando uma tela de celular/viewport mobile).
- **Ordenação no SFC:** Siga rigorosamente a ordem de blocos: `<template>` -> `<script setup lang="ts">` -> `<style scoped lang="scss">`.
- **Props e Emits:** Use props estritamente tipadas (`defineProps`) e eventos (`defineEmits`) para propagar o estado atual do template para o simulador.

### 2. Estilização do Simulador (SCSS e UnoCSS)
Para simular de forma fidedigna a interface do WhatsApp:
- **Cores e Temas:**
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
  - Suporte a dois tipos de botão: "Visitar Site" e "Ligar para Telefone". Use ícones do Iconify aceitos por `MaxButton`/`Icon` — pode ser um nome curto (ex.: `icon="open-in-new"`, `icon="phone"`) ou o nome completo de uma coleção (ex.: `icon="material-symbols:call"`). Não fixe o prefixo `mdi:`; o projeto usa coleções variadas.
  - O WhatsApp suporta a exibição de até 2 botões de CTA.
  - Limite máximo de 20 caracteres por texto de botão.
- **Mensagens de Lista (List Messages):** Renderizadas como um botão clicável interativo (ex: "Ver opções" ou "Selecionar itens").
  - Limite máximo de 24 caracteres para o texto do botão.
  - Limite a lista pop-up de opções a no máximo 10 linhas (divididas em seções opcionais).

### 4. Validações no Frontend (Limites da Meta)
Implemente contadores de caracteres ativos e estados de validação no formulário de edição usando propriedades computadas (`computed`) sobre o estado dos inputs. Não introduza bibliotecas de schema (ex.: Zod) — elas não fazem parte do stack do engeapp; a validação é feita com `computed` e com os estados/mensagens dos inputs do `MaxComponentsUi` (ex.: `InputBase`). Notifique o usuário com mensagens de erro ou atenção do input quando os limites forem excedidos:
- **Texto do Corpo:** Máximo de 1024 caracteres.
- **Texto do Cabeçalho (caso não seja mídia):** Máximo de 60 caracteres.
- **Texto do Rodapé:** Máximo de 60 caracteres.
- **Variáveis/Parâmetros:** Certifique-se de detectar variáveis (`{{1}}`, `{{2}}`, etc.) e renderizar dinamicamente campos de entrada separados para preenchimento.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** ignore as regras da Composition API. Nunca utilize a Options API.
- **NÃO** utilize cores de tema hardcoded. Utilize variáveis CSS ou tokens do UnoCSS que respondam corretamente ao alternador global de modo escuro/claro do sistema.
- **NÃO** realize requisições à API da Meta diretamente dentro dos componentes visuais. Todo GET de dados de página e todo salvamento de template devem passar por uma store `@maxvue/max-pinia` (MaxPinia), que cuida do cache e do auto-save/debounced para o backend — não faça `axios.get/post` manuais nem salvamentos por submit. As rotas são sempre **NOMES de rota Ziggy pontilhados** (Ziggy está configurado no projeto), nunca strings de path `/api/...`. Nas stores, as rotas vão em `options.get.route` e `options.save` (ex.: `get: { route: 'support.whatsapp.templates' }`, `save: 'support.whatsapp.template.save'`, `key: '...'`; lembre que `options.key` é a chave de identificação da store, não a chave de cache). Para chamadas imperativas pontuais fora da store, use `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` passando o nome da rota (ex.: `apiPostRoute('support.whatsapp.send.message.template', send_data)`). Exponha o estado da store através de composables limpos para os componentes visuais.
- **NÃO** ligue ações de botão fora do padrão do projeto. Botões do `MaxComponentsUi` recebem o handler pela prop `:action` (ou `@click`), não devem ficar sem handler. Ex.: `<MaxButton label="Cancelar" icon="close" severity="danger" light :action="cancelar" />`.
- **NÃO** quebre atributos de layout no `<template>` em várias linhas. Mantenha todos os atributos inline em uma única linha (ex.: `<MaxButton label="Cancelar" icon="close" severity="danger" light :action="cancelar" />`).
