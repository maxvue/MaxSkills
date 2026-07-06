---
name: vue-brand-positioning-character-management-best-practices
description: "Use quando criar, modificar, estilizar ou depurar componentes, páginas ou stores @maxvue/max-pinia em Vue 3 que lidam com posicionamento de marca, perfis de personagens, personas de agentes, upload de imagens de referência facial e listas de temas. Cobre formulários com salvamento automático, uploads e listagens (TabBrandPositioning, TabCharacters, TabThemes, store de characters)."
---

# Boas Práticas de Gerenciamento de Posicionamento de Marca e Personagens em Vue

## Objetivo
Estabelecer diretrizes claras, padrões e convenções de fluxo reativo para gerenciar formulários de posicionamento de marca, personas de personagens e uploads de imagens de referência no front-end do aplicativo em Vue 3, utilizando componentes do design system e gerenciamento de estado do Pinia.

## Instruções

### 1. Estrutura do SFC e Convenções de Script Setup
* **Composition API:** Sempre utilize `<script setup lang="ts">` para a lógica dos componentes. A Options API é estritamente proibida.
* **Ordem de Blocos:** Mantenha os blocos do SFC na ordem: `<template>`, `<script setup lang="ts">` e `<style scoped lang="scss">`.
* **Formatação do SFC:** Use recuo de 4 espaços, aspas simples para strings e ponto e vírgula obrigatório.
* **Atributos inline no Template:** Formate as tags/componentes Vue dentro do `<template>` com todos os atributos na mesma linha (ex: `<MaxInputText v-model="name" label="Name" />`).
* **Comentários:** Escreva todos os comentários de código estritamente no idioma Português do Brasil (`pt-BR`).

### 2. Formulários de Posicionamento de Marca
* Implemente formulários reativos com salvamento automático para as diretrizes da marca (ex: tom de voz, público-alvo, configurações de logotipo) para evitar perda de dados.
* Use `<MaxInputTextArea>` para campos de texto multilinha (como guias de estilo ou perfis de público) com um layout de grade padrão (`MaxGrid`).
* Vincule o estado a uma store dedicada do `@maxvue/max-pinia` (ex: `useBrandPositioningStore`). O carregamento inicial dos dados (GET) e o salvamento automático devem vir da própria store: configure `options.get.route` e `options.save` na definição da store como **nomes de rota (Ziggy)** pontilhados (ex.: `route: 'brand_positioning.data'`, `save: 'brand_positioning.save'`) — a store chama `apiGetRoute`/`apiPostRoute` internamente, que resolvem o nome para a URL `/api/...` via Ziggy; NÃO passe caminhos string `/api/...` nem envolva os valores de config com esses helpers, e NÃO implemente auto-save manual com `watch` + `setTimeout`/`axios.post`. O MaxPinia já faz o debounce e o auto-save ao mutar o estado.

### 3. Perfil de Personagem e Gerenciamento de Porta-Vozes
* Use o sistema de grade padrão (`MaxGrid`) com espaçamento adequado de linhas/colunas para os detalhes do perfil do personagem (ex: nome, descrição física detalhada, traços).
* **Upload de Rostos de Personagens:** Utilize o componente de upload grande personalizado (`MaxInputFileUploadBig`) para permitir o envio de imagens de referência facial de alta qualidade para geração de imagens por IA.
* Gerencie os estados de carregamento e salvamento de upload com loaders reativos (`uploadingFor` ou `saving`) para desabilitar o envio do formulário enquanto um upload estiver em andamento.
* Forneça um layout de listagem interativa mostrando avatares de personagens, status ativo e opções simples de edição/exclusão.

### 4. Modais e Confirmações
* Envolva os formulários de criação e edição de personagens em componentes `<MaxModal>` para preservar o foco do espaço de trabalho.
* Implemente diálogos de confirmação de exclusão (usando `<MaxModal>` ou sistemas de confirmação do `@maxvue/max-components-ui`) antes de excluir perfis de personagens ou arquivos de referência carregados.

### 5. Notificações de Toast e Tratamento de Erros
* Trate as respostas da integração da API de forma limpa. Dispare um `Toast` reativo do `@maxvue/max-components-ui` para feedback de sucesso ou erro.
* Trate os erros de validação de forma amigável. Destaque os campos de entrada usando atributos de validação (`error`, `done`) envolvidos em `<InputBase>` onde aplicável.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** utilize Options API. Sempre utilize `<script setup lang="ts">`.
* **Estilização (House Rule):** Faça layout, espaçamento e cores via atributos do UnoCSS attributify (`presetMaxUno`) e tokens do tema (ex.: `p0`, `s50`, `s100`, `s33`, `s25`, `w-flex`) — essa é a convenção real do projeto. Reserve o bloco opcional `<style scoped lang="scss">` apenas para estilos que não são expressáveis via attributify. **NÃO** use CSS puro nem Tailwind CSS.
* **NÃO** escreva comentários de código em inglês. Todos os comentários de código devem ser em Português do Brasil (`pt-BR`).
* **NÃO** quebre os parâmetros do template em várias linhas. Mantenha todos os atributos na mesma linha dentro do template.
* **NÃO** use diálogos nativos do navegador (ex: `confirm()`, `alert()`) para avisos de exclusão. Use confirmações em modais personalizados.
