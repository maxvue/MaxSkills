---
name: adonisjs-edge-templates-best-practices
description: Use when composing HTML templates renderizados pelo backend AdonisJS v6 com Edge.js para casos server-side legítimos — e-mails transacionais e documentos para PDF (Puppeteer) —, incluindo layouts, componentes/slots, tags/helpers customizados e escape seguro. NÃO use para views de página da aplicação (essas são SPA Vue Router consumindo /api via stores @maxvue/max-pinia). Triggers on Edge files (.edge) de e-mail/PDF, edge.global, e edge.render em mailers/queues/comandos.
---

# Boas Práticas de Templates Edge no AdonisJS

## Objetivo
Fornecer uma arquitetura padronizada e diretrizes para criar, modificar, estilizar e renderizar templates Edge.js no AdonisJS v6 nos casos server-side legítimos deste projeto: **e-mails transacionais** e **documentos HTML destinados a PDF (Puppeteer)**. Garante segurança contra XSS, reutilização de componentes e herança limpa de layouts.

> **Escopo (importante):** O EngeApp é uma **SPA pura** (Vue Router; o Adonis serve um catch-all HTML). Páginas da aplicação NÃO são renderizadas server-side com Edge, e os dados de página vêm de stores `@maxvue/max-pinia` via `GET /api/...` — nunca de variáveis injetadas em um template Edge. Use Edge apenas para e-mail e PDF.

## Instruções
1. **Herança de Layout (e-mail/PDF)**:
   - Utilize `@layout('emails/layouts/base')` para herdar de um template base de e-mail ou de documento PDF.
   - Defina áreas de injeção de conteúdo dinâmico utilizando `@section('nome')` ... `@end`.
   - Mantenha trechos comuns (cabeçalho do e-mail, rodapé/assinatura, blocos de boilerplate) modularizados.

2. **Reutilização de Componentes & Slots**:
   - Para componentes de linha única (sem slots), use `@!component('components/button', { label: 'Clique aqui' })`.
   - Para componentes com slots, use o bloco e declare os slots com `@slot`. Dentro do componente acesse `{{{ await $slots.main() }}}` e slots nomeados como `{{{ await $slots.header() }}}`:
     ```edge
     {{-- chamada --}}
     @component('emails/components/card', { title: 'Orçamento' })
       @slot('header')
         <h1>{{ title }}</h1>
       @endslot
       <p>Detalhes do sistema fotovoltaico...</p>
     @endcomponent

     {{-- emails/components/card.edge --}}
     <div class="card">
       {{{ await $slots.header() }}}
       {{{ await $slots.main() }}}
     </div>
     ```
   - Defina tags personalizadas do Edge e helpers globais via `edge.global(...)` em `start/view.ts` (ou em um provider de view) para manter os templates limpos de cálculos complexos em JavaScript.

3. **Sanitização de Dados e Escape**:
   - Sempre sanitize dados dinâmicos utilizando a sintaxe de interpolação padrão: `{{ user.name }}`.
   - Use chaves triplas `{{{ rawHtml }}}` somente ao renderizar conteúdo HTML confiável (por exemplo, corpo de e-mail montado a partir de blocos próprios, ou saída de slots). Seja extremamente cauteloso com saídas raw para evitar vulnerabilidades de Cross-Site Scripting (XSS). NÃO use chaves triplas para "hidratar" SPA — a SPA obtém dados via `GET /api/...` por stores `@maxvue/max-pinia`.
   - Serialize os models do Lucid ORM (v6) usando `.toJSON()` / `.serialize()` ou serializadores DTO específicos antes de enviá-los ao renderizador, evitando passar estruturas circulares ou propriedades ocultas.

4. **Templates de Email e Mídia Dinâmica**:
   - Para templates de e-mail, utilize propriedades de estilo CSS inline ou layouts CSS simples, evitando scripts modernos ou frameworks complexos de estilização.
   - Para templates destinados à renderização com Puppeteer, garanta as dimensões corretas do aspect-ratio, carregue os assets localmente ou via URLs absolutas e aguarde o carregamento completo dos recursos.

5. **Contexto de Renderização**:
   - A renderização de Edge neste projeto acontece em contextos offline/server-side, não em views de página. Para e-mails, prefira a integração de mailers do AdonisJS (`mail`), que usa Edge para o corpo da mensagem.
   - Para renderizar diretamente (e-mail manual, geração de PDF via Puppeteer, comandos Ace, filas/BullMQ), resolva o renderizador `edge`: `import edge from 'edge.js'` e chame `await edge.render('emails/welcome', data)`. O HTML resultante é então enviado por e-mail ou passado ao Puppeteer para gerar o PDF.

## Restrições
- **NÃO Utilize Interpolação Raw para Inputs de Usuário**: NUNCA use `{{{ user_input }}}` para exibir dados enviados por usuários.
- **NÃO Insira Lógica de Negócios nos Templates**: Mantenha os templates estritamente orientados à apresentação. Não faça consultas de banco de dados, condicionais complexas ou cálculos extensos em arquivos Edge; delegue para services, controllers ou helpers personalizados.
- **NÃO Utilize Caminhos Relativos para Recursos Absolutos**: Ao referenciar recursos do lado do cliente (imagens, folhas de estilo, fontes) em templates de e-mail, sempre utilize URLs absolutas (por exemplo, prefixadas com o host) em vez de caminhos relativos (`/images/logo.png`), pois estes falharão ao serem abertos em um cliente de e-mail.
