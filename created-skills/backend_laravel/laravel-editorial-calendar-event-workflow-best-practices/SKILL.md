---
name: laravel-editorial-calendar-event-workflow-best-practices
description: "Use ao desenvolver, revisar ou depurar o ciclo de vida e transições dos eventos do calendário editorial (App\\Models\\SocialMedia\\CalendarEvent) no SocialMediaApp/Laravel 13: enum CalendarEventStatus (planned…published, art_rejected, replanning), encadeamento dos agentes de IA (Copywriter, Reviewer, GraphicEditor, ArtAnalyst) via AiPipeline e CalendarEventObserver, e jobs na fila gemini."
---

# Boas Práticas do Fluxo de Trabalho de Eventos do Calendário Editorial no Laravel

## Objetivo
Padronizar e garantir o ciclo de vida, as transições de estado e a orquestração de jobs dos eventos do calendário editorial (`App\Models\SocialMedia\CalendarEvent`) no backend Laravel 13 (projeto `SocialMediaApp`, portado do `EngeApp`). O modelo usa ULID e `SoftDeletes`, tem o cast `status => App\Enums\CalendarEventStatus::class` e é observado por `CalendarEventObserver` via atributo `#[ObservedBy]`. Isso assegura a execução sequencial e confiável dos jobs de agentes de IA e previne inconsistências de dados.

## Instruções
1. **Transições de Estado do Evento e Fluxo do Ciclo de Vida** (cases reais do enum `App\Enums\CalendarEventStatus`; use `canTransitionTo()` para validar o grafo manual):
   - `planned`: Estado inicial quando um evento é planejado estrategicamente.
   - `planning_approved`: Definido quando o gestor aprova o planejamento. Dispara o `CopywriterJob`.
   - `script_drafted`: Definido após o `CopywriterJob` salvar o roteiro inicial. Dispara o `CopywriterReviewerJob`.
   - `script_ready`: Definido após o `CopywriterReviewerJob` refinar o texto. Dispara o `GraphicEditorJob`.
   - `art_ready`: Definido após o `GraphicEditorJob` gerar as imagens dos slides (`artworks`). A partir daqui o gestor pode ir para `art_approved`, `art_rejected` ou `art_analysing`.
   - `art_approved`: Aprovação manual das artes; único caminho para `scheduled`.
   - `scheduled`: Pronto para agendamento/publicação; único caminho para `published`.
   - `art_analysing`: Disparado quando o gestor rejeita um ou mais slides. Dispara o `ArtAnalystJob`.
   - `art_rejected`: Definido após o `ArtAnalystJob` consolidar as revisões visuais. Dispara o `CopywriterJob` em modo de revisão (transição `art_rejected → script_drafted`, fora do grafo manual — ver Instrução 2).
   - `replanning`: Reavaliação de título/briefing; retorna o evento para `planned`.
   - `published`: Post publicado com sucesso (estado terminal).
   - Não existe estado `failed` — uma falha de agente NÃO muda o `status`; apenas grava `status_message` (ver Instrução 3).

2. **Orquestração via `AiPipeline` + `CalendarEventObserver`**:
   - O mapa único de encadeamento status→Job vive em `App\Services\SocialMedia\AiPipeline::dispatchForStatus(CalendarEvent $event)`. Ele é a fonte de verdade única e é gated por `$event->client?->ai_enabled` — nada é despachado se a IA estiver desligada para o cliente.
   - `CalendarEventObserver` (implementa `Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit`) reage ao evento Eloquent `updated()` apenas quando `wasChanged('status')` e delega para `AiPipeline::dispatchForStatus`. Usa-se para transições feitas via `update()` do Eloquent (ex.: workflow manual movido pelos controllers).
   - Cuidado com o encadeamento job→job: os Jobs de IA avançam o status por ESCRITA GUARDADA com Query Builder (`CalendarEvent::query()->...->update(...)` no trait `App\Jobs\Ai\Concerns\AdvancesEventStatus`), que NÃO dispara eventos Eloquent — logo o observer sozinho não encadearia. Por isso o próprio trait chama `AiPipeline::dispatchForStatus` diretamente após uma transição bem-sucedida, reusando o mesmo mapa. Não duplique esse `match` em outro lugar.
   - O `ShouldHandleEventsAfterCommit` garante que o próximo Job só seja despachado após a transação da mudança de status ser commitada, evitando que o worker leia um status ainda não persistido.

3. **Configurações de Queue, Retry, Timeout e Falha dos Jobs de IA** (`StrategyManagerJob`, `CopywriterJob`, `CopywriterReviewerJob`, `GraphicEditorJob`, `ArtAnalystJob`, `ThemeExtractionJob`, `ReplanEventJob` em `App\Jobs\Ai`):
   - Atribua todos à fila `gemini` chamando `$this->onQueue('gemini')` no construtor. Garanta o supervisor correspondente no Horizon.
   - Implemente `ShouldBeUnique` com `uniqueId()` retornando o id do evento, para impedir jobs concorrentes duplicados sobre o mesmo evento.
   - Timeouts típicos de jobs de IA ficam entre `180` e `240` segundos (ex.: `CopywriterJob` usa `$timeout = 240`; `ArtAnalystJob` usa `180`). Alinhe com a config do Horizon.
   - Use backoff exponencial `public array $backoff = [60, 120, 300];` com `public int $tries = 3;`.
   - No `failed(?Throwable $exception)`, chame `reportFinalAgentFailure($exception, $this->event)` (trait `HasAgentAiRequest`). Este NÃO reverte o `status` — ele apenas loga no canal `gemini` e, para `CalendarEvent`, grava a mensagem em `status_message` (visível na UI). Não reintroduza reset para `planned`.

4. **Revisão em Nível de Slide (Rejeição de Arte)**:
   - Quando artes são reprovadas, o `ArtAnalystJob` sintetiza o feedback do gestor em um registro na tabela `calendar_event_arts_analysis` (modelo `App\Models\SocialMedia\CalendarEventArtsAnalysis`, coluna FK `event_id`), gravando `approved_elements` e `rejected_elements`. O acesso é por `CalendarEventArtsAnalysis::where('event_id', $id)` — não há relação `artsAnalysis` no modelo `CalendarEvent`.
   - O `CopywriterJob` subsequente (modo revisão, status `art_rejected`) instrui o `CopywriterAgent` a ler o histórico de análises e revisar APENAS os slides impactados via a tool `SaveScriptDetail`, finalizando com `SaveDraftScript`. Os detalhes de roteiro ficam na relação `scriptDetails` (`hasMany(CalendarEventScriptDetail::class, 'event_id')`, tabela `calendar_event_script_details`); slides inalterados devem ser mantidos intactos para economizar tokens e tempo de execução.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill está escrito.
- **Proteção da Queue:** Nunca atribua agentes de IA ou jobs de processamento pesado à queue `default`. Sempre use a queue `gemini`.
- **Segurança Transacional:** Nunca dispare jobs dentro de transações de banco de dados; confie no `CalendarEventObserver` (`ShouldHandleEventsAfterCommit`) ou em `AiPipeline` chamado após escrita guardada para evitar race conditions.
