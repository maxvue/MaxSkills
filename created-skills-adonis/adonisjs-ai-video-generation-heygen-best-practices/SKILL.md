---
name: adonisjs-ai-video-generation-heygen-best-practices
description: Use when implementing, reviewing, or configuring AI avatar video generation using the HeyGen API, orchestrating video creation from script, handling HeyGen webhooks for render completions, or downloading and storing completed MP4 video files in AdonisJS v6. Triggers on HeyGenService, createVideoFromAvatar, heygenWebhook, and avatar video jobs.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas para Geração de Vídeo por IA do HeyGen no AdonisJS

## Objetivo
Padronizar a implementação, configuração e execução de geração assíncrona de vídeos de avatar por IA usando a API HeyGen no AdonisJS v6. Isso inclui agendamento de fluxos via BullMQ, gerenciadores seguros de webhook, mecanismo de fallback por polling e download resiliente do arquivo de vídeo armazenado via `@adonisjs/drive`.

## Instruções

### 1. Configuração da Integração da API
- Armazene as credenciais da API HeyGen (`HEYGEN_API_KEY`, `HEYGEN_WEBHOOK_SECRET`) no arquivo `.env` e carregue-as através de `start/env.ts` e de uma configuração de serviço dedicada.
- Use `axios` ou `fetch` nativo dentro de uma classe `HeyGenService` dedicada (registrada no container de IoC do AdonisJS) para gerenciar comunicações externas com os endpoints do HeyGen.

### 2. Fluxo de Geração de Vídeo
- Implemente `createVideoFromAvatar(scriptText: string, avatarId: string, voiceId: string)` no `HeyGenService`.
- Envie a solicitação de geração para `POST https://api.heygen.com/v2/video/generate` usando a configuração de avatar apropriada.
- Salve o `video_id` retornado do HeyGen no banco de dados sob o modelo de rastreamento de vídeo correspondente (ex: vídeo institucional/comercial de proposta fotovoltaica) e atualize seu status para `rendering`.

### 3. Processamento Assíncrono com BullMQ
- Use o BullMQ (`#services/queue_service`) para gerenciar o ciclo de vida do vídeo.
- Despache um `HeyGenVideoJob` assim que um roteiro (script) estiver pronto e aprovado.
- Use filas para realizar a chamada inicial de geração do HeyGen, verificar o status periodicamente (polling como fallback) e processar o download do vídeo final sem bloquear a thread principal da aplicação.

### 4. Manipulador Resiliente de Webhook
- Crie um `HeygenWebhookController` para receber os eventos enviados pela API do HeyGen.
- **Verificar assinatura ANTES de persistir:** Valide o HMAC-SHA256 do payload usando `HEYGEN_WEBHOOK_SECRET` (já declarado em `start/env.ts`). Compare em tempo constante com `crypto.timingSafeEqual`, sempre precedido da checagem de comprimento dos buffers — a API nativa lança `RangeError` com tamanhos diferentes. Rejeite com 401 se inválido. Só então persista no banco:
  ```typescript
  import crypto from 'node:crypto'
  import env from '#start/env'

  const rawBody = request.raw() ?? ''
  const provided = request.header('heygen-signature') ?? ''
  const expected = crypto.createHmac('sha256', env.get('HEYGEN_WEBHOOK_SECRET')).update(rawBody).digest('hex')

  const providedBuffer = Buffer.from(provided)
  const expectedBuffer = Buffer.from(expected)

  if (
    providedBuffer.length !== expectedBuffer.length ||
    !crypto.timingSafeEqual(providedBuffer, expectedBuffer)
  ) {
    return response.status(401).json({ error: 'Invalid signature' })
  }
  ```
- Persista o payload bruto da requisição na tabela de banco de dados `Webhook` após a verificação, garantindo trilhas de auditoria.
- Retorne uma resposta rápida `200 OK` para o originador do webhook do HeyGen imediatamente para evitar timeouts.
- Ao receber o evento `video_status.completed`, despache um job de background para realizar o download e o armazenamento do vídeo gerado.

### 5. Armazenamento do Arquivo e Persistência no Banco de Dados
- Baixe a stream do vídeo MP4 concluído a partir da URL fornecida pelo HeyGen usando um cliente compatível com streams (ex: `axios` com `responseType: 'stream'`).
- Persista o arquivo através do serviço `@adonisjs/drive` (`drive.use().putStream(key, stream)`), nunca com `node:fs/promises` direto, mantendo consistência com o padrão de armazenamento das skills irmãs (geração de imagens).
- Defina uma chave única usando o ID do registro e um ULID (ex: `videos/${record.id}_${ulid()}.mp4`).
- Atualize o modelo com a chave do Drive do vídeo e mude o status. Dispare atualizações em tempo real no frontend usando `@adonisjs/transmit` (SSE) se necessário.

### 6. Tratamento de Erros e Política de Tentativas (Retry)
- Envolva todas as chamadas da API HeyGen e a lógica de download de arquivos em blocos try-catch robustos.
- Lide com limites de taxa da API (HTTP 429) e timeouts de rede graciosamente através de um mecanismo de retentativas com backoff exponencial.
- Se o HeyGen retornar um estado de falha na renderização (`video_status.failed`), atualize o status do modelo no banco de dados para `failed` e registre os detalhes do erro.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO Realize Operações Síncronas Bloqueantes:** Não realize polling longo ou requisições de download de arquivos de forma síncrona na thread da requisição HTTP. Sempre delegue essas tarefas aos workers em background do BullMQ.
- **NÃO Vaze Credenciais:** Nunca insira chaves de API, segredos de webhook ou credenciais de serviço de forma estática no código. Carregue-os dinamicamente de variáveis de ambiente.
- **Armazenamento via Drive:** Sempre persista arquivos de vídeo através do serviço `@adonisjs/drive` usando chaves relativas. Não use `node:fs/promises` nem caminhos absolutos estáticos no código.
- **Sem Processamento Direto no Webhook:** Os controladores de webhook devem apenas registrar o evento e agendar jobs em segundo plano. Nunca execute atualizações no banco de dados ou pipelines de download diretamente no ciclo de vida HTTP do webhook.
