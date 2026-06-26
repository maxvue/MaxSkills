---
name: adonisjs-edge-templates-best-practices
description: Use when creating, modifying, reviewing, or styling Edge.js template views in AdonisJS v6, rendering server-side layouts, utilizing components and slots, configuring custom Edge tags or helpers, or composing HTML email templates. Triggers on Edge view files (.edge), edge.global, and Edge.render calls.
---

# Boas Práticas de Templates Edge no AdonisJS

## Objetivo
Fornecer uma arquitetura padronizada e diretrizes para criar, modificar, estilizar e renderizar templates Edge.js no AdonisJS v6, garantindo segurança contra ataques XSS, reutilização otimizada de componentes, herança limpa de layouts e renderização adequada de variáveis.

## Instruções
1. **Herança de Layout**:
   - Utilize `@layout('layouts/nome')` para herdar de um template base.
   - Defina áreas de injeção de conteúdo dinâmico utilizando `@section('nome')` e `@end`.
   - Mantenha componentes comuns do layout (cabeçalhos, rodapés, barras laterais) modularizados.

2. **Reutilização de Componentes & Slots**:
   - Utilize `@component('components/button', { label: 'Clique aqui' })` para reutilizar trechos de HTML.
   - Empregue slots para injeção de conteúdo HTML aninhado dentro de componentes. Acesse-os usando `$slots.main()` ou slots nomeados como `$slots.header()`.
   - Defina tags personalizadas do Edge e auxiliares globais dentro de `start/view.ts` ou de providers de view para manter os templates limpos de cálculos complexos em JavaScript.

3. **Sanitização de Dados e Escape**:
   - Sempre sanitize dados dinâmicos utilizando a sintaxe de interpolação padrão: `{{ user.name }}`.
   - Use chaves triplas `{{{ rawHtml }}}` somente ao renderizar conteúdo HTML confiável ou configurações JSON serializadas (por exemplo, variáveis de dados do servidor para hidratação inicial do SPA). Seja extremamente cauteloso com saídas raw para evitar vulnerabilidades de Cross-Site Scripting (XSS).
   - Serialize os models do Lucid ORM usando `.toJSON()` ou serializadores DTO específicos antes de enviá-los ao renderizador de views, evitando a passagem de estruturas circulares internas ou propriedades ocultas.

4. **Templates de Email e Mídia Dinâmica**:
   - Para templates de e-mail, utilize propriedades de estilo CSS inline ou layouts CSS simples, evitando scripts modernos ou frameworks complexos de estilização.
   - Para templates destinados à renderização com Puppeteer, garanta as dimensões corretas do aspect-ratio, carregue os assets localmente ou via URLs absolutas e aguarde o carregamento completo dos recursos.

5. **Contexto de Renderização**:
   - Dentro dos controllers, utilize a propriedade `view` do Contexto HTTP: `async index({ view }) { return view.render('pages/home') }`.
   - Para contextos offline (por exemplo, disparadores de e-mail, comandos Ace, filas/BullMQ), resolva o renderizador global `edge`: `import edge from 'edge.js'` e chame `edge.render('emails/welcome', data)`.

## Restrições
- **NÃO Utilize Interpolação Raw para Inputs de Usuário**: NUNCA use `{{{ user_input }}}` para exibir dados enviados por usuários.
- **NÃO Insira Lógica de Negócios nos Templates**: Mantenha os templates estritamente orientados à apresentação. Não faça consultas de banco de dados, condicionais complexas ou cálculos extensos em arquivos Edge; delegue para services, controllers ou helpers personalizados.
- **NÃO Utilize Caminhos Relativos para Recursos Absolutos**: Ao referenciar recursos do lado do cliente (imagens, folhas de estilo, fontes) em templates de e-mail, sempre utilize URLs absolutas (por exemplo, prefixadas com o host) em vez de caminhos relativos (`/images/logo.png`), pois estes falharão ao serem abertos em um cliente de e-mail.
