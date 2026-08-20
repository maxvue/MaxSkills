---
name: adonisjs-canva-api-integration-best-practices
description: Use when implementing, configuring, reviewing, or debugging integrations with the Canva API in an AdonisJS application, managing Canva OAuth 2.0 flows, uploading media assets to Canva, exporting or importing designs generated on Canva, or handling Canva webhook notifications for design updates.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer padrões de desenvolvimento robustos, seguros e resilientes para integrar a API do Canva em aplicações AdonisJS v6. Isso abrange gerenciamento de credenciais OAuth 2.0 multi-tenant, sincronização de assets de mídia (exportando assets gerados no backend para o Canva e importando os designs finalizados de volta), endpoints de webhook seguros e tratamento de rate limiting.

## Instruções

### 1. Integração do Fluxo OAuth 2.0 do Canva (AdonisJS Ally)
Ao implementar OAuth 2.0 com o Canva, estenda o AdonisJS Ally criando um driver customizado do Canva ou implementando um fluxo customizado, caso não exista de forma nativa.
- **Config & Env:** Defina as variáveis (`CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_CALLBACK_URL`) em `start/env.ts` usando `Env.schema.string()`.
- **Armazenamento de Tokens:** Salve as credenciais em um model dedicado `CanvaCredential`, chaveado por tenant (`solarCompanyId`). Inclua os campos `access_token`, `refresh_token` e `token_expires_at` (usando `DateTime` do Luxon).
- **Refresh de Tokens:** Implemente um helper de refresh de token dentro do service. Antes de qualquer requisição à API, verifique se o token expira em menos de 5 minutos e dispare o refresh se necessário:
  ```typescript
  if (credential.tokenExpiresAt && credential.tokenExpiresAt.diffNow('minutes').minutes < 5) {
    await this.refreshCanvaToken(credential)
  }
  ```

### 2. Canva Media Upload API
Para exportar assets gerados no backend para o Canva:
- **HTTP client:** AdonisJS v6 não possui cliente HTTP de primeira-parte. Use a API `fetch` nativa do Node 18+ (global, sem dependência extra). Se preferir uma biblioteca, instale `got` ou `axios`. Sempre cheque `response.ok` e trate erros antes de consumir o corpo (`await response.json()`).
- **Chunks & Tamanho:** Para arquivos grandes, faça streaming direto para evitar esgotamento de memória.
- **Endpoint:** `POST https://api.canva.com/v1/asset-uploads`
- **Formato da Requisição:** Use `multipart/form-data` com os campos `file`, `mime_type` e `asset_name`.
- **Tratamento Assíncrono:** A Upload API do Canva é assíncrona. Verifique o status do upload fazendo polling no endpoint informado nos metadados da resposta (`GET https://api.canva.com/v1/asset-uploads/{uploadId}`) até o status ser `completed` ou `failed`.

### 3. Listar e Importar Designs do Canva
Para trazer os designs finalizados de volta para a aplicação (por exemplo, armazenando assets exportados no Drive):
- **Listar designs:** `GET https://api.canva.com/v1/designs` filtrando por escopos de cliente/usuário.
- **Exportar design:** Chame `POST https://api.canva.com/v1/exports` para gerar saídas em PNG ou PDF de alta resolução.
- **Download para o Drive:** Faça streaming da saída a partir da URL de exportação gerada pelo Canva e salve usando o service `drive` do AdonisJS. Com `fetch` nativo, converta o corpo da resposta (web `ReadableStream`) para um stream Node antes de gravar:
  ```typescript
  import drive from '@adonisjs/drive/services/main'
  import { Readable } from 'node:stream'

  const response = await fetch(exportUrl)
  if (!response.ok || !response.body) {
    throw new Error(`Failed to download Canva export: ${response.status}`)
  }
  const nodeStream = Readable.fromWeb(response.body)
  await drive.use().putStream(destinationPath, nodeStream)
  ```

### 4. Processamento de Webhooks do Canva
- **Verificação:** Os webhooks do Canva exigem validação usando verificação de assinatura HMAC-SHA256. Verifique o header `X-Canva-Signature` contra o payload e a chave secreta do webhook:
  ```typescript
  import crypto from 'node:crypto'
  
  const hmac = crypto.createHmac('sha256', webhookSecret)
  hmac.update(rawRequestBody)
  const computedSignature = hmac.digest('hex')
  // Comparação constant-time para evitar timing attack
  if (
    computedSignature.length !== providedSignature.length ||
    !crypto.timingSafeEqual(Buffer.from(computedSignature), Buffer.from(providedSignature))
  ) {
    throw new Error('Invalid webhook signature')
  }
  ```
- **Delegação para Job:** Nunca processe atualizações de design diretamente dentro da resposta do controller HTTP do webhook. Envie imediatamente o payload para uma fila BullMQ e retorne uma resposta `200 OK` ao Canva dentro da janela de timeout de 3 segundos.

### 5. Rate Limiting e Resiliência
- **Rate Limit (HTTP 429):** A API do Canva impõe rate limits. Intercepte as respostas e verifique o status `429`. Implemente lógica de retry com backoff exponencial.
- **Circuit Breaker:** Se uma conexão falhar consecutivamente ou retornar `401 Unauthorized` (indicando permissão revogada), desative a credencial (`is_active = false`) e registre o evento com detalhes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** armazene client secrets do OAuth ou chaves de webhook no código-fonte. Sempre use `env.get()`.
- **NÃO** faça chamadas HTTP à API do Canva de forma síncrona dentro de transações de banco de dados, pois isso bloqueia conexões do pool.
- **NÃO** permita webhooks brutos não autenticados; a verificação HMAC é obrigatória.
- **NÃO** use buffers em memória (`fs.readFileSync`) para assets de mídia grandes. Sempre use streams de leitura/escrita.
