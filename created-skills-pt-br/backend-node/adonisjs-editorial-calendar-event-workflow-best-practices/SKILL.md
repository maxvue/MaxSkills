---
name: adonisjs-editorial-calendar-event-workflow-best-practices
description: Use when developing, reviewing, debugging, or maintaining the editorial calendar event lifecycle, event state transitions (planned, planning_approved, script_drafted, script_ready, art_ready, art_analysing, art_rejected, scheduled, published, failed, replanning), orchestrating AI copywriter, copywriter reviewer, graphic editor, or art analyst jobs, or handling publication queues and commands in AdonisJS. Triggers on editing calendar states, managing event job pipelines, and handling social media publishing flows.
---

## Objetivo
Estabelecer padrões e regras recomendadas para gerenciar, depurar e implementar o ciclo de vida dos eventos de calendário editorial, suas transições de status e os jobs assíncronos de orquestração de agentes de IA usando AdonisJS v6 e BullMQ.

## Instruções

### 1. Ciclo de Vida de Status de Eventos do Calendário Editorial
Garanta que todas as consultas ao banco de dados, transições de estado e lógica de negócios respeitem os seguintes status canônicos de um `CalendarEvent`:
* **`planned`**: Estado inicial gerado pelo job estratégico `StrategyManagerJob`, contendo apenas ideias e instruções básicas.
* **`planning_approved`**: Ativado quando o usuário aprova o planejamento. Este estado dispara automaticamente o `CopywriterJob`.
* **`script_drafted`**: Definido quando o `CopywriterJob` conclui a geração do script inicial do post e do briefing visual dos slides usando a ferramenta `SaveDraftScript`.
* **`script_ready`**: Definido quando o `CopywriterReviewerJob` revisa, ajusta e aprova o script usando a ferramenta `SaveEventScript`.
* **`art_ready`**: Definido automaticamente pela ferramenta `GenerateEventArtwork` dentro do `GraphicEditorJob` assim que todos os slides do script possuírem uma arte gerada (caminho da imagem preenchido).
* **`art_analysing`**: Definido se o usuário prossegue no fluxo, mas há slides rejeitados no post. Isso dispara o `ArtAnalystJob` para consolidar o feedback visual.
* **`art_rejected`**: Definido pela ferramenta `SaveArtAnalysis` ao final do `ArtAnalystJob`, fazendo com que o evento retorne para a fase do copywriter para revisão.
* **`replanning`**: Definido quando uma regeneração completa é acionada (ex.: por falhas repetidas na geração de artes ou reinício manual). Dispara o `ReplanEventJob` e retorna para `planned` após a conclusão.
* **`scheduled`**: Definido quando o usuário aprova todos os slides em `art_ready`, agendando a publicação automática no horário configurado em `startAt`.
* **`published`**: Definido quando o `PublishEventJob` publica o conteúdo com sucesso nas plataformas da Meta (Instagram/Facebook).
* **`failed`**: Definido em caso de falha de publicação, registrando a mensagem de erro correspondente na coluna `publishError`.

### 2. Ferramentas de Transição de Status
Verifique e implemente as ferramentas corretas para as mudanças de estado em controllers ou jobs de IA:
* **`SaveDraftScript`**: Integrada no `CopywriterJob`. Deve receber o `event_id` e o texto do script em Markdown. Avança o status do evento para `script_drafted`.
* **`SaveEventScript`**: Integrada no `CopywriterReviewerJob`. Deve receber o `event_id` e o script final. Avança o status do evento para `script_ready` e limpa o campo `rejectionObservations`.
* **`GenerateEventArtwork`**: Integrada no `GraphicEditorJob`. Gera e salva imagens de forma individual por slide. Avança automaticamente o status do evento para `art_ready` quando `generated_slides >= total_slides`.
* **`SaveArtAnalysis`**: Integrada no `ArtAnalystJob`. Registra elementos visuais aprovados e reprovados e altera o status do evento para `art_rejected`.
* **`UpdateCalendarItem`**: Integrada no `ReplanEventJob`. Atualiza os temas básicos e instruções do post, retornando o status para `planned`.

### 3. Modo de Revisão (Regeneração Parcial)
Ao processar um evento com status `art_rejected` ou em transição a partir dele:
* **Agente Copywriter**: Deve entrar no "Modo Revisão". Deve ler as revisões anteriores via `GetCalendarEventData` e revisar **APENAS** os slides marcados com `status = 'rejected'` em `CalendarEventArtwork`. Slides com status `approved` devem ser mantidos sem alterações.
* **Agente Revisor de Copywriter**: Na revisão parcial, deve verificar e detalhar **APENAS** os slides que foram modificados devido a rejeições anteriores.
* **Agente Editor Gráfico**: Deve gerar novas artes **APENAS** para os slides com `status = 'rejected'`. Deve pular a geração de imagens para slides com `status = 'approved'` para evitar custos desnecessários com IA.

### 4. Orquestração de Filas e Jobs (BullMQ)
Valide se os workers escutam suas respectivas filas e se comportam de forma determinística com base no status do evento:
* **`strategy-manager`**: Configura o planejamento inicial de itens do calendário.
* **`copywriter`**: Processa status `planning_approved` (nova criação) ou `art_rejected` (revisão parcial).
* **`copywriter-reviewer`**: Processa status `script_drafted`.
* **`graphic-editor`**: Processa status `script_ready` (gera novas artes para slides pendentes ou rejeitados).
* **`art-analyst`**: Processa status `art_analysing` para compilar feedbacks de rejeição de arte.
* **`replan-event`**: Processa status `replanning` para atualizar parâmetros base de postagens.
* **`publish-event`**: Envia os textos e mídias finais para as APIs da Meta Graph.

## Restrições
* **NÃO** dispare o `CopywriterJob` manualmente se o status do evento já for `script_drafted` ou `script_ready`, a menos que solicitado explicitamente ou em fluxo de retorno de `art_rejected`.
* **NÃO** regenere artes de slides que já estão marcados com o status `approved` na tabela `CalendarEventArtwork` do banco de dados.
* **NÃO** permita transições de status que pulem a sequência lógica do fluxo (ex.: transitar direto de `planned` para `script_ready`).
* **NÃO** utilize consultas SQL puras para atualizar o status dos eventos; sempre utilize Lucid ORM model hooks e eventos do framework para manter a integridade dos dados.
* **NUNCA** edite o título ou o script de um post se o status do evento for `scheduled` ou `published`.
