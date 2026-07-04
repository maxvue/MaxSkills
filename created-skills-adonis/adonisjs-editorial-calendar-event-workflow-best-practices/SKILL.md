---
name: adonisjs-editorial-calendar-event-workflow-best-practices
description: Use when developing, reviewing, debugging, or maintaining the editorial calendar event lifecycle, event state transitions (planned, planning_approved, script_drafted, script_ready, art_ready, art_analysing, art_rejected, scheduled, published, failed, replanning), orchestrating AI copywriter, copywriter reviewer, graphic editor, or art analyst jobs, or handling publication queues and commands in AdonisJS. Triggers on editing calendar states, managing event job pipelines, and handling social media publishing flows.
---

## Objetivo
Estabelecer padrões e regras padronizados para gerenciar, depurar e implementar o ciclo de vida dos eventos do calendário editorial, suas transições de estado e os jobs assíncronos de orquestração de agentes de IA usando AdonisJS v6 e BullMQ.

## Instruções

### 1. Ciclo de Vida do Status do Evento do Calendário Editorial
Garanta que todas as consultas ao banco de dados, transições de estado e regras de negócio respeitem os seguintes estados canônicos de um `CalendarEvent`:
* **`planned`**: Estado inicial gerado pelo `StrategyManagerJob` estratégico, contendo apenas ideias e instruções base.
* **`planning_approved`**: Acionado quando o usuário aprova a fase de planejamento. Este estado dispara automaticamente o `CopywriterJob`.
* **`script_drafted`**: Definido quando o `CopywriterJob` termina de gerar a copy inicial do post e os briefings dos slides usando a tool `SaveDraftScript`.
* **`script_ready`**: Definido quando o `CopywriterReviewerJob` revisa, ajusta e aprova o roteiro usando a tool `SaveEventScript`.
* **`art_ready`**: Definido automaticamente pela tool `GenerateEventArtwork` dentro do `GraphicEditorJob` assim que todos os slides do roteiro possuem uma arte gerada (o path existe).
* **`art_analysing`**: Definido caso o usuário dê continuidade ao workflow do evento mas existam slides rejeitados. Dispara o `ArtAnalystJob` para sintetizar o feedback.
* **`art_rejected`**: Definido pela tool `SaveArtAnalysis` ao final do `ArtAnalystJob`, retornando o evento à fase de copywriter para revisão.
* **`replanning`**: Definido quando uma regeneração completa é acionada (ex: por falhas repetidas de arte ou reinício manual). Dispara o `ReplanEventJob` e retorna a `planned` ao concluir.
* **`scheduled`**: Definido quando o usuário aprova todos os slides em `art_ready`, agendando o post para publicação automática em `startAt`.
* **`published`**: Definido quando o `PublishEventJob` publica o conteúdo com sucesso nas plataformas Meta (Instagram/Facebook).
* **`failed`**: Definido quando a publicação falha, armazenando a mensagem de erro na coluna `publishError`.

### 2. Tools de Transição de Estado
Verifique e implemente as tools corretas para mudanças de estado em controllers ou jobs de IA:
* **`SaveDraftScript`**: Integra no `CopywriterJob`. Deve receber `event_id` e a copy em markdown. Transiciona o status do evento para `script_drafted`.
* **`SaveEventScript`**: Integra no `CopywriterReviewerJob`. Deve receber `event_id` e a copy final. Transiciona o status do evento para `script_ready` e limpa `rejectionObservations`.
* **`GenerateEventArtwork`**: Integra no `GraphicEditorJob`. Gera e salva as imagens individualmente por slide. Transiciona automaticamente o status do evento para `art_ready` quando `generated_slides >= total_slides`.
* **`SaveArtAnalysis`**: Integra no `ArtAnalystJob`. Registra os elementos visuais aprovados e rejeitados e, em seguida, transiciona o status do evento para `art_rejected`.
* **`UpdateCalendarItem`**: Integra no `ReplanEventJob`. Atualiza os temas e instruções base, retornando o status para `planned`.

### 3. Modo de Revisão (Regeneração Parcial)
Ao lidar com um evento com status `art_rejected` ou em transição a partir dele:
* **Agente Copywriter**: Deve entrar no "Modo de Revisão". Deve ler as revisões anteriores via `GetCalendarEventData` e revisar **APENAS** os slides marcados com `status = 'rejected'` em `CalendarEventArtwork`. Slides marcados como `approved` devem permanecer intocados.
* **Agente Copywriter Reviewer**: Na revisão parcial, deve verificar e refinar **APENAS** os slides rejeitados que foram modificados.
* **Agente Graphic Editor**: Deve gerar novas artes **APENAS** para os slides com `status = 'rejected'`. Deve pular a geração de arte para slides com `status = 'approved'` para evitar a duplicação de custos de geração de imagem.

### 4. Orquestração de Filas e Jobs no BullMQ
Valide que os workers escutam suas respectivas filas e se comportam de forma determinística conforme o status do evento:
* **`strategy-manager`**: Trata a configuração inicial dos itens do calendário.
* **`copywriter`**: Processa `planning_approved` (nova criação) ou `art_rejected` (revisão parcial).
* **`copywriter-reviewer`**: Processa `script_drafted`.
* **`graphic-editor`**: Processa `script_ready` (gera novas artes para slides pendentes/rejeitados).
* **`art-analyst`**: Processa `art_analysing` para compilar o feedback de rejeição.
* **`replan-event`**: Processa o status `replanning` para atualizar os parâmetros base do post.
* **`publish-event`**: Envia os assets e textos finais para as Meta Graph APIs.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** acione o `CopywriterJob` manualmente se o status já for `script_drafted` ou `script_ready`, a menos que explicitamente solicitado ou em transição de retorno a partir de `art_rejected`.
* **NÃO** regenere artes para slides que já estão marcados como `approved` na tabela `CalendarEventArtwork` do banco de dados.
* **NÃO** permita transições de status que pulem a sequência (ex: transicionar diretamente de `planned` para `script_ready`).
* **NÃO** escreva consultas SQL cruas para atualizações de status do evento; sempre use hooks e eventos do model do Lucid ORM para uma integração adequada.
* **NUNCA** edite o título do post ou o roteiro se o status do evento for `scheduled` ou `published`.
