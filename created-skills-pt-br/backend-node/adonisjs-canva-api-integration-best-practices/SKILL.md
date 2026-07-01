---
name: adonisjs-canva-api-integration-best-practices
description: Use when implementing, configuring, reviewing, or debugging integrations with the Canva API in an AdonisJS application, managing Canva OAuth 2.0 flows, uploading media assets to Canva, exporting or publishing designs created on Canva directly to the social media calendar, or handling Canva webhook notifications for design updates.
---

## Objetivo
Estabelecer padrões de desenvolvimento robustos, seguros e resilientes para integrar a API do Canva a aplicações AdonisJS v6. Isso abrange o gerenciamento de credenciais OAuth 2.0 multi-tenant, sincronização de mídias, endpoints de webhook seguros e tratamento de limites de requisição (rate limiting).

## Instruções

### 1. Integração do Fluxo OAuth 2.0 do Canva (AdonisJS Ally)
Ao implementar o OAuth 2.0 com o Canva, estenda o AdonisJS Ally criando um driver personalizado para o Canva ou implementando um fluxo customizado se não for nativo.
- **Configurações & Env:** Defina as variáveis (`CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_CALLBACK_URL`) no arquivo `start/env.ts` usando `Env.schema.string()`.
- **Armazenamento de Tokens:** Salve as credenciais no model `SocialMediaCredential`. Inclua os campos `access_token`, `refresh_token` e `token_expires_at` (usando o `DateTime` do Luxon).
- **Renovação de Tokens:** Implemente um helper para renovação de token dentro do serviço. Antes de qualquer requisição à API, verifique se o token expira em menos de 5 minutos e execute a renovação se necessário:
  ```typescript
  if (credential.tokenExpiresAt && credential.tokenExpiresAt.diffNow('minutes').minutes < 5) {
    await this.refreshCanvaToken(credential)
  }
  ```

### 2. API de Upload de Mídias do Canva
Para exportar mídias geradas no backend diretamente para o Canva:
- **Cliente HTTP:** Use `@adonisjs/core/services/http` ou Axios para realizar as requisições HTTP.
- **Chunks & Tamanho:** Para arquivos grandes, faça o envio via stream diretamente para evitar esgotamento de memória no servidor.
- **Endpoint:** `POST https://api.canva.com/v1/asset-uploads`
- **Formato da Requisição:** Use `multipart/form-data` com os campos `file`, `mime_type` e `asset_name`.
- **Processamento Assíncrono:** A API de Upload do Canva é assíncrona. Verifique o status do envio fazendo polling no endpoint fornecido nos metadados de resposta (`GET https://api.canva.com/v1/asset-uploads/{uploadId}`) até que o status seja `completed` ou `failed`.

### 3. Listar e Importar Designs do Canva
Para puxar designs finalizados de volta para o calendário editorial:
- **Listar designs:** `GET https://api.canva.com/v1/designs` filtrando pelos escopos do cliente/usuário.
- **Exportar design:** Chame `POST https://api.canva.com/v1/exports` para gerar saídas em PNG ou PDF de alta resolução.
- **Download para o Drive:** Faça o download em stream da URL de exportação gerada pelo Canva e salve utilizando o serviço `drive` do AdonisJS:
  ```typescript
  import drive from '@adonisjs/drive/services/main'
  
  const response = await this.httpClient.get(exportUrl, { responseType: 'stream' })
  await drive.use().putStream(destinationPath, response.data)
  ```

### 4. Processamento de Webhooks do Canva
- **Verificação:** Os webhooks do Canva exigem validação usando assinatura HMAC-SHA256. Verifique o cabeçalho `X-Canva-Signature` contra o payload recebido e a chave secreta do webhook:
  ```typescript
  import crypto from 'node:crypto'
  
  const hmac = crypto.createHmac('sha256', webhookSecret)
  hmac.update(rawRequestBody)
  const computedSignature = hmac.digest('hex')
  if (computedSignature !== providedSignature) {
    throw new Error('Assinatura do webhook inválida')
  }
  ```
- **Desacoplamento de Tarefas:** Nunca processe as atualizações de design diretamente no fluxo do controller de webhook HTTP. Envie o payload imediatamente para uma fila do BullMQ e retorne uma resposta `200 OK` ao Canva dentro do limite de 3 segundos permitido.

### 5. Limites de Requisição (Rate Limiting) e Resiliência
- **Limite de Requisições (HTTP 429):** A API do Canva aplica limites de taxa. Intercepte as respostas, verifique o status `429` e implemente uma lógica de retentativas com backoff exponencial.
- **Circuit Breaker:** Se uma conexão falhar consecutivamente ou retornar `401 Unauthorized` (indicando permissão revogada), desative a credencial (`is_active = false`) e registre o evento com logs detalhados.

## Restrições
- **NÃO** armazene segredos de cliente do OAuth ou chaves de webhook diretamente no código-fonte. Sempre utilize `env.get()`.
- **NÃO** faça chamadas HTTP para a API do Canva de forma síncrona dentro de transações de banco de dados, pois isso bloqueia as conexões do pool.
- **NÃO** permita webhooks não autenticados; a validação HMAC é obrigatória.
- **NÃO** utilize buffers em memória (`fs.readFileSync`) para mídias grandes. Sempre utilize streams de leitura/escrita.
