---
name: laravel-editorial-calendar-event-workflow-best-practices
description: "Use when implementing or managing Instagram editorial calendar events in Engeapp. Covers Event lifecycle states (CalendarEventStatusEnum), EventObserver job orchestration (CopywriterJob, GraphicEditorJob, ArtAnalystJob), Horizon gemini queue configuration, and slide-level revision workflows."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas do Fluxo de Trabalho de Eventos do Calendário Editorial no Laravel

## Objetivo
Padronizar o ciclo de vida, as transições de estado e a orquestração de jobs dos eventos do calendário editorial do Instagram (`App\Models\Calendar\Event`) no backend Laravel 13 / PHP 8.4 do engeapp. O modelo usa ULID (`HasUlids`), tabela `calendar_events`, o cast `status => App\Enums\Calendar\CalendarEventStatusEnum::class`, e é observado por `App\Observers\EventObserver` — registrado via `Event::observe(EventObserver::class)` em `AppServiceProvider::boot()` (não há atributo `#[ObservedBy]` no modelo). Isso assegura a execução sequencial e confiável dos jobs de agentes de IA e previne inconsistências de dados.

## Instruções

1. **Transições de Estado do Evento e Fluxo do Ciclo de Vida** (cases reais do enum `App\Enums\Calendar\CalendarEventStatusEnum` — um enum simples `: string`, SEM métodos de grafo de transição; não invente `canTransitionTo()`):
   - `planned`: Estado inicial; item adicionado ao calendário pelo agente coordenador, aguardando aprovação manual.
   - `planning_approved`: Gestor aprova o planejamento. O `EventObserver` dispara o `CopywriterJob`.
   - `script_drafted`: Rascunho de script salvo pelo Copywriter. O `EventObserver` dispara o `CopywriterReviewerJob`.
   - `script_ready`: Script refinado pelo Revisor. O `EventObserver` dispara o `GraphicEditorJob` (que só roda se `$event->script` não estiver vazio).
   - `art_ready`: Artes (`artworks`) geradas pelo Editor Gráfico; aguardando aprovação manual. Não dispara job automático.
   - `art_analysing`: Gestor reprovou um ou mais slides. O `EventObserver` dispara o `ArtAnalystJob`.
   - `art_rejected`: Análise consolidada pelo Analista de Artes. O `EventObserver` dispara novamente o `CopywriterJob`, agora em modo revisão.
   - `art_approved`: Aprovação manual das artes.
   - `replanning`: Reavaliação de tema/título/briefing pelo agente.
   - `scheduled`: Publicação agendada; consumida pelo `PublishEventJob`.
   - `published`: Conteúdo publicado com sucesso (estado terminal).
   - Os status `art_ready`, `art_approved`, `replanning`, `scheduled`, `published` e `planned` caem no `default => null` do `match` do observer — não acionam job automático.

2. **Orquestração via `EventObserver::updated()`**:
   - A fonte de verdade única do encadeamento status→Job é o `match ($newStatus)` DENTRO de `App\Observers\EventObserver::updated(Event $event)`. Não existe classe `AiPipeline`, método `dispatchForStatus()` nem trait `AdvancesEventStatus` — não os reintroduza. Todo o mapeamento vive no observer.
   - O observer só encadeia quando `$event->wasChanged('status')`; qualquer outra atualização é ignorada logo no início do método. Loga a transição no canal `gemini` e delega a métodos privados (`dispatchCopywriter`, `dispatchCopywriterReviewer`, `dispatchGraphicEditor`, `dispatchArtAnalyst`).
   - O encadeamento job→job também passa pelo observer: os jobs de IA NÃO usam Query Builder guardado. O avanço de status acontece quando as tools do agente (ex.: `SaveDraftScript`, `SaveArtAnalysis`) fazem `$event->update([...])` — um update de MODELO Eloquent, que dispara o `updated()` do observer e encadeia o próximo job. Por isso o `match` é a única cópia do mapa; não o duplique nos jobs.
   - `EventObserver` implementa `Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit`, garantindo que o próximo job só seja despachado após a transação da mudança de status ser commitada — evita que o worker leia um status ainda não persistido.
   - Não há gating por `ai_enabled` no encadeamento — o observer não consulta flag de cliente. Se precisar condicionar o disparo, faça-o dentro do próprio método `dispatch*` (como o guard de `$event->script` vazio em `dispatchGraphicEditor`), não com uma pipeline externa inexistente.

3. **Configurações de Queue, Retry, Timeout e Falha dos Jobs de IA** (`CopywriterJob`, `CopywriterReviewerJob`, `GraphicEditorJob`, `ArtAnalystJob` em `App\Jobs\Instagram`, todos usando as traits `HasAgentAiRequest, Queueable`):
   - Atribua à fila `gemini` chamando `$this->onQueue('gemini')` no construtor. Garanta o supervisor correspondente no Horizon. (Exceção: `PublishEventJob` não usa IA — é só HTTP para a Graph API da Meta — e roda na fila `default`.)
   - Timeouts alinhados ao Horizon: `CopywriterJob` usa `$timeout = 240`; `ArtAnalystJob` usa `$timeout = 180`. Use backoff exponencial `public array $backoff = [60, 120, 300];` com `public int $tries = 3;`.
   - `ShouldBeUnique` com `uniqueId()` retornando o id do evento aparece APENAS em `PublishEventJob` (evita dupla publicação). Os jobs de IA NÃO implementam `ShouldBeUnique`; em vez disso protegem-se por guard de status no início do `handle()` (revalidam `$this->event->fresh()->status` e cancelam silenciosamente se inesperado). Siga esse padrão em novos jobs de IA — não force `ShouldBeUnique` onde a base não usa.
   - Ao fim do `handle()`, `CopywriterJob`, `CopywriterReviewerJob` e `GraphicEditorJob` chamam `$this->throwIfIncomplete($response, 'script_drafted')` (trait `HasAgentAiRequest`): lança `AgentAiIncompleteException` se `isDone()` for falso, forçando o retry da fila. `ArtAnalystJob` é a exceção: seu `handle()` NÃO chama `throwIfIncomplete` — termina direto em `broadcastCalendarUpdate`, sem forçar retry via `isDone()`.
   - No `failed(?\Throwable $exception)`, `CopywriterJob`, `CopywriterReviewerJob` e `GraphicEditorJob` chamam `$this->reportFinalAgentFailure($exception, $this->event)` (trait `HasAgentAiRequest`) — ele cria um registro `Bug` de auto-report APENAS em produção e NÃO altera o status. `ArtAnalystJob::failed()` NÃO chama `reportFinalAgentFailure` (logo, sem auto-report de Bug) — apenas loga no canal `gemini`.
   - O tratamento de status em falha é POR JOB, não uniforme: o `CopywriterJob::failed()` reseta o evento para `planned` e grava `status_message` ("Erro ao elaborar o script. Aprove o briefing novamente para tentar."), depois retransmite via `broadcastCalendarUpdate`. Já o `ArtAnalystJob::failed()` apenas loga e NÃO reseta status nem faz auto-report. Ou seja: existe reset para `planned` no fluxo real do Copywriter — não afirme o contrário.

4. **Revisão em Nível de Slide (Rejeição de Arte)**:
   - Quando artes são reprovadas, o `ArtAnalystJob` anexa as imagens geradas (`artworks` com `path` não nulo, como `StoredImage`) e sintetiza o feedback do gestor em um registro na tabela `calendar_event_arts_analysis` (modelo `App\Models\Calendar\CalendarEventArtworkAnalysis`, FK `event_id`), gravando `approved_elements` e `rejected_elements` via a tool `SaveArtAnalysis`.
   - O acesso é pela relação `artsAnalysis()` no `Event` (`hasMany(CalendarEventArtworkAnalysis::class, 'event_id')->latest()`) — ela EXISTE; use `$event->artsAnalysis()->latest()->first()` ou `->exists()`. O `SaveArtAnalysis` avança o evento para `art_rejected`, o que faz o observer encadear o `CopywriterJob` em modo revisão.
   - O `CopywriterJob` em modo revisão (status inicial `art_rejected`) instrui o `AgentInstagramCopywriter` a ler a análise consolidada e revisar APENAS os slides reprovados via a tool `SaveScriptDetail`, finalizando com `SaveDraftScript`. Os detalhes de roteiro ficam na relação `scriptDetails` (`hasMany(CalendarEventScriptDetail::class, 'event_id')`, tabela `calendar_event_script_details`); slides inalterados devem ser mantidos intactos para economizar tokens e tempo.

## Restrições
- **Idioma:** Comunique-se com o usuário humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
- **Proteção da Queue e Segurança Transacional:** ver itens 2 e 3 acima (fila `gemini`, `ShouldHandleEventsAfterCommit`).

## Onde está no código
- `App\Models\Calendar\Event` (tabela `calendar_events`)
- `App\Enums\Calendar\CalendarEventStatusEnum`
- `App\Observers\EventObserver`
- `App\Jobs\Instagram\*`
- `App\Models\Calendar\CalendarEventArtworkAnalysis` (tabela `calendar_event_arts_analysis`)
