---
name: laravel-editorial-calendar-event-workflow-best-practices
description: Use when developing, reviewing, debugging, or maintaining the editorial calendar event lifecycle, event state transitions (planned, planning_approved, script_drafted, script_ready, art_ready, art_analysing, art_rejected, scheduled, published, failed, replanning), orchestrating AI copywriter, copywriter reviewer, graphic editor, or art analyst jobs, or handling publication queues, commands, and schedules in Laravel. Triggers on editing calendar states, managing event job pipelines, and handling social media publishing flows using Laravel Horizon and queues.
---

# Boas Práticas do Fluxo de Trabalho de Eventos do Calendário Editorial no Laravel

## Objetivo
Padronizar e garantir o ciclo de vida, as transições de estado e a orquestração de jobs dos eventos do calendário editorial (`CalendarEvent`) no backend Laravel 13 (`SocialMediaApp`/`engeapp`). Isso assegura a execução sequencial e confiável dos jobs de agentes de IA e previne inconsistências de dados.

## Instruções
1. **Transições de Estado do Evento e Fluxo do Ciclo de Vida**:
   - `planned`: Estado inicial quando um evento é planejado estrategicamente.
   - `planning_approved`: Definido quando o gestor aprova o planejamento. Dispara o `CopywriterJob`.
   - `script_drafted`: Definido após o `CopywriterJob` salvar o roteiro inicial. Dispara o `CopywriterReviewerJob`.
   - `script_ready`: Definido após o `CopywriterReviewerJob` refinar o texto. Dispara o `GraphicEditorJob`.
   - `art_ready`: Definido após o `GraphicEditorJob` gerar as imagens dos slides (`artworks`).
   - `art_approved` / `scheduled`: Definido mediante aprovação manual, pronto para agendamento.
   - `art_analysing`: Disparado quando o gestor rejeita um ou mais slides. Dispara o `ArtAnalystJob`.
   - `art_rejected`: Definido após o `ArtAnalystJob` consolidar as revisões visuais. Dispara o `CopywriterJob` em modo de revisão.
   - `published`: Post publicado com sucesso via Meta API.
   - `replanning`: Reavaliação de título/briefing para reiniciar o planejamento.

2. **Orquestração via Observer (`EventObserver`)**:
   - Todas as transições assíncronas de jobs devem ser conectadas através do `EventObserver` dentro do evento `updated`.
   - O observer deve implementar `Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit` para garantir que os jobs sejam disparados somente após as transações de banco de dados serem commitadas.
   - Evite executar mudanças de estado diretamente nos handles dos jobs que possam contornar ou conflitar com o observer.

3. **Configurações de Retry, Timeout e Queue dos Jobs**:
   - Atribua todos os jobs de execução de IA (`StrategyManagerJob`, `CopywriterJob`, `CopywriterReviewerJob`, `GraphicEditorJob`, `ArtAnalystJob`) à queue `gemini`.
   - Configure os timeouts: jobs de IA normalmente exigem `$timeout = 240` a `300` segundos. Garanta que isso esteja alinhado com as configurações do supervisor do Horizon.
   - Implemente arrays de backoff exponencial, ex: `public array $backoff = [60, 120, 300];` com `public int $tries = 3;`.
   - Garanta que o callback `failed()` esteja sempre implementado nos jobs para reverter o estado do evento a um ponto seguro (ex: retornar a `planned` ou registrar mensagens de erro em `status_message`).

4. **Revisão em Nível de Slide (Rejeição de Arte)**:
   - Quando um slide é rejeitado, o `ArtAnalystJob` grava uma consolidação de `approved_elements` e `rejected_elements` na tabela `calendar_event_arts_analysis` (via relacionamento `artsAnalysis`).
   - O `CopywriterJob` subsequente deve ler essa análise e apenas regenerar ou editar os detalhes de roteiro (tabela `scriptDetails`) dos slides que foram rejeitados. Slides inalterados devem ser mantidos intactos para economizar tokens e tempo de execução.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill está escrito.
- **Proteção da Queue:** Nunca atribua agentes de IA ou jobs de processamento pesado à queue `default`. Sempre use a queue `gemini`.
- **Segurança Transacional:** Nunca dispare jobs dentro de transações de banco de dados; confie em hooks de event listener ou hooks `afterCommit()` para evitar race conditions.
