---
name: adonisjs-ai-agents-domain-catalog-best-practices
description: Use when implementing, reviewing, or debugging any of the Maxdmin domain AI agents in AdonisJS (Vercel AI SDK + Gemini + BullMQ) — copywriter, copywriter reviewer, theme extractor, strategy manager, event replanner, protocol extractor, and graphic editor & art analyst. Triggers on *_agent.ts / *_job.ts files and the named agents/tools/models below (copywriter.ts, copywriter_reviewer.ts, theme_extractor.ts, strategy_manager.ts, replan_event, protocol_extractor_agent.ts, graphic_editor.ts, art_analyst.ts; tools like SaveScriptDetail, GetBrandPositioning, CreateCalendarItems, UpdateCalendarItem, GenerateEventArtwork, InsertCardData; models SocialMediaTheme, SupportProtocolReport, CalendarEvent). For cross-cutting patterns prefer the dedicated skills: adonisjs-ai-agents-tool-calling, -structured-outputs-zod, -multi-agent-orchestration, -observability-monitoring.
---

# Catálogo de Agentes de Domínio (AdonisJS + Vercel AI SDK + Gemini + BullMQ)

## Objetivo
Os 7 agentes de domínio do Maxdmin são instâncias do MESMO padrão (AgentConfig/factory + system prompt + tools com Zod + job BullMQ), diferindo apenas no domínio. Esta skill é o catálogo: descreve o esqueleto comum uma única vez e, por agente, preserva apenas os detalhes únicos (arquivos reais, tools, models, filas, particularidades de prompt).

## Padrão comum
Todos os agentes compartilham:
- **AgentConfig / factory:** função `createXxxAgent(...)` (ou classe `AgentInstagramXxx` com `typeData: 'structured-data'`) que retorna a config: modelo Gemini inicial, `maxSteps`, `maxCalls` e a lista de tools.
- **System prompt:** estruturado com tags XML (`<ENTRADA>`, `<TAREFA>`, `<REGRAS>`), saída em pt-BR (exceto prompts de geração de imagem, em inglês). Nunca inventar dados — usar só o que as tools retornam.
- **Tools com Zod:** function calling exclusivo; texto livre/JSON simulando tool é proibido. Contexto de brand/persona via `GetBrandPositioning` (arquétipo, tom de voz, paleta, `personagens_disponiveis`).
- **Multi-tenant:** isolar consultas passando a instância de `SocialMediaAgent`/tenant (`agentId`, `solarCompanyId`) às tools.
- **Dispatch via BullMQ:** job `XxxJob` com `queueName` estático, método estático `dispatch(...)`, `handle` que carrega o model, roda `executeAgent` de `#ai/agent_ai_request`, chama `saveAiCost(COSTABLE_TYPES.*, id, result)` e (quando há UI de calendário) `broadcastCalendarUpdate(agentId, solarCompanyId)`. Redis via `redisConfig` de `#config/redis`.

Para esses padrões transversais, **não duplique** — consulte:
`adonisjs-ai-agents-best-practices`, `adonisjs-ai-agents-tool-calling`, `adonisjs-ai-agents-structured-outputs-zod`, `adonisjs-ai-agents-multi-agent-orchestration`, `adonisjs-ai-agents-observability-monitoring`.

## Agentes

### 1. Copywriter
- **Arquivos:** `copywriter.ts` / `copywriter_job.ts`. Factory `createCopywriterAgent(event: CalendarEvent)`. Modelo `gemini-2.5-flash`, `maxSteps: 20`, `maxCalls: 2`.
- **Tools (ordem):** `GetCalendarEventData` → `GetBrandPositioning` → `SaveScriptDetail` (por slide) → `SaveDraftScript`.
- **Job:** `CopywriterJob`, fila `copywriter`, `dispatch` com `{ eventId, agentId, solarCompanyId }`; `isDone` quando `event.status === 'script_drafted'`; `saveAiCost(COSTABLE_TYPES.Event, ...)`.
- **Únicos:** dois modos — Criação (`planning_approved`: 1 slide p/ `traditional_post`/`reels`, 3–7 p/ `carousel`, usa `tema_base`) e Revisão (`art_rejected`: `SaveScriptDetail` só em slides `status_arte = "rejected"`). `visual_briefing` em prosa pt-BR (sujeito, cenário, gráficos, composição, paleta, coesão, pose de personagem). `character_ids` via `personagens_disponiveis` ou `[]`. Legenda ≤ 2.200 caracteres.

### 2. Copywriter Reviewer
- **Arquivos:** `copywriter_reviewer.ts`. Classe `AgentInstagramCopywriterReviewer`, `typeData: 'structured-data'`, `initialModel: 'gemini-2.5-flash'`, `maxSteps: 25`, `maxCalls: 2`.
- **Tools:** `GetCalendarEventData`, `GetBrandPositioning`, `SaveScriptDetail`, `SaveEventScript`.
- **Únicos:** revisor — enriquece `visual_briefing` com **checklist visual de 9 componentes**. Modo Total (`script_drafted` + todos `sem_arte_ainda`) vs. Parcial (vindo de `art_rejected`: só slides `rejected`, preserva `approved`/`pending`). `SaveEventScript` é a ÚLTIMA tool e muda status para `script_ready`. Legenda ≤ 2.200 caracteres.

### 3. Theme Extractor
- **Arquivos:** `theme_extractor.ts` / `theme_extraction_job.ts`. Factory `createThemeExtractorAgent()`. Modelo `gemini-2.5-flash`. Prompt com tags `<ENTRADA>`/`<TAREFA>`/`<REGRAS>`.
- **Job:** `ThemeExtractionJob`, fila `theme-extraction` (`queueName` estático). Formata `baseContents` em Markdown (`contentLines`); salva briefing em `agentContent`; `saveAiCost(COSTABLE_TYPES.SocialMediaTheme, theme.id, result)`.
- **Model:** `SocialMediaTheme` — PK ULID via `@beforeCreate`/`ulid()`; `baseContents` e `schedule` como JSONB (prepare/consume); `belongsTo(SolarCompany)`, `hasMany(CalendarEvent)`.
- **Únicos:** processa anexos brutos (texto, transcrições de áudio, PDFs, imagens) num briefing editorial unificado. Validar ≥ 1 conteúdo base antes de enfileirar.

### 4. Strategy Manager
- **Arquivos:** `strategy_manager.ts` / `strategy_manager_job.ts`. Classe `AgentInstagramStrategyManager`, `typeData: 'structured-data'`, modelo `gemini-3.5-flash`, `maxSteps: 30`, `maxCalls: 5`.
- **Tools:** `GetReadyThemes` (temas fixos→data exata; livres→1 slot no período; vincular `theme_id`), `GetBrandPositioning`, `CreateCalendarItems` (status `'planned'`, formatos só `'carousel'`/`'traditional_post'`, campo `instructions` por post).
- **Job:** `StrategyManagerJob`, fila `strategy-manager`, `dispatch` com `{ agentId, solarCompanyId, periodStart, periodEnd, conflictStrategy }`; `findOrFail(agentId)`; `saveAiCost` com `COSTABLE_TYPES.SocialMediaAgent`; `broadcastCalendarUpdate`.
- **Únicos:** gera calendário editorial mensal (16–20 posts, 4–5/semana), alterna formatos (nunca consecutivos), horários ideais (7–9h, 12–13h, 17–19h). Sem datas passadas; sem vídeo (reels/stories proibidos).

### 5. Event Replanner
- **Arquivos:** agente de replanejamento + job `ReplanEventJob`, fila `replan-event` (status `'replanning'`). Modelo `gemini-3.5-flash`, `maxSteps: 10`, `maxCalls: 2`.
- **Tools (ordem):** `GetBrandPositioning` → recuperar evento + motivo da rejeição/feedback → replanejar → `UpdateCalendarItem`.
- **Únicos:** incorpora feedback do usuário como diretriz de alta prioridade; gera tema/conceito/briefing COMPLETAMENTE novo (nunca repete o rejeitado). Atualiza só título, tema e instruções — NÃO altera formato, data ou tipo de mídia. SSE/WebSocket após conclusão.

### 6. Protocol Extractor
- **Arquivos:** `protocol_extractor_agent.ts` / `analyze_protocol_job.ts`. Factory `createProtocolExtractorAgent(cardId: string): AgentConfig`. Modelo `gemini-2.5-flash` ou `gemini-3.1-flash-lite`, `temperature: 0`. Prompt com `<ENTRADA>`/`<TAREFA>`/`<REGRAS>`.
- **Tools:** `InsertCardData` (1x por protocolo distinto), `NoProtocolFound` (fallback), `GetProtocolMessages`.
- **Job:** `analyze_protocol_job.ts`, fila `protocol-extraction`, `dispatch(cardId/commentId)`; retry backoff exponencial (3 tentativas, 5000ms). Persiste em transação Lucid (`db.transaction()`); `saveAiCost('SupportProtocolReport', reportId, result)`.
- **Models:** `SupportProtocolReport`, `SupportProtocol`.
- **Únicos:** extrai protocolos de concessionária ("protocolo", "solicitação", "chamado", "ticket", "SS", dígitos longos); NUNCA extrai CPF/CNPJ, UC/conta contrato, coordenadas, specs de equipamento. Calcula `data_limite` por `tipo_submissao` (Parecer de Acesso/Vistoria = dias úteis; Obras = dias corridos), feriados via DB/serviço (sem hardcode).

### 7. Graphic Editor & Art Analyst
- **Graphic Editor:** `createGraphicEditorAgent` em `graphic_editor.ts`. Modelo `gemini-3.5-flash`. Tools: `GetBrandPositioning`, `GetCalendarEventData`, `GenerateEventArtwork` (Imagen). Gera arte só p/ slides `sem_arte_ainda`/`rejected` (nunca `approved`/`pending`). Prompts de imagem em **inglês**; `visual_text` copiado **literalmente em português** entre aspas; consistência facial via imagens de referência; coesão de iluminação/paleta no carrossel. Ao gerar todas as artes → status `'art_ready'`.
- **Art Analyst:** `createArtAnalystAgent` em `art_analyst.ts`. Modelo `gemini-2.5-pro`. Tools: `GetCalendarEventData`, `SaveArtAnalysis` (sempre a ÚLTIMA tool). Cruza visuais aprovados/reprovados com pontos do gestor → consolida `approved_elements`/`rejected_elements` → status `'art_rejected'` (devolve ao Copywriter).
- **Models:** `CalendarEvent`, `CalendarEventArtwork`, `CalendarEventArtworkAnalysis` — salvar em transação.

## Restrições gerais
- Nunca pular `GetBrandPositioning`/`GetCalendarEventData` antes de salvar.
- Nunca inventar dados, personagens ou porta-vozes; `personagens` vazio → `[]` / sem rostos humanos.
- Respeitar a ordem e a tool final de cada agente (ex.: `SaveEventScript`, `SaveArtAnalysis`).
- Persistência multi-protocolo/artwork sempre em transação Lucid; conexões Redis/DB liberadas nos workers.
