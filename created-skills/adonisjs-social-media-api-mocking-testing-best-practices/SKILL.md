---
name: adonisjs-social-media-api-mocking-testing-best-practices
description: Use when implementing, reviewing, or debugging unit/integration tests for social media API integrations (Meta/Instagram, YouTube, TikTok, LinkedIn, Bluesky, X/Twitter, Pinterest) or external HTTP webhooks in AdonisJS v6 using Japa. Triggers on HTTP client mocking, api test suites, mocking the native fetch HTTP client (via nock), and webhook payload signature simulation.
---

## Objetivo
Fornecer padrões de projeto, melhores práticas e diretrizes para simular APIs de redes sociais externas (Meta, LinkedIn, YouTube, X, Pinterest, Bluesky) e eventos de webhooks em testes de unidade e integração no AdonisJS v6 usando o Japa.

## Instruções
1. **Mocking de Requisições HTTP Externas**:
   - NÃO faça chamadas reais a endpoints de produção de APIs de redes sociais durante os testes.
   - Use `nock` para interceptar e mockar requisições de rede de saída. O cliente HTTP padrão é o `fetch` nativo do Node (undici); para que o `nock` intercepte essas chamadas, ative o interceptador de `fetch` global (`nock` >= 14 com `globalThis.fetch`, ou habilite o suporte a undici) — caso contrário o mock não terá efeito.
   - Declare os interceptores de mock durante o setup do grupo de testes (`group.setup` ou `test.setup`) e restaure/limpe-os em `teardown`.
   - Estruture as respostas mockadas para imitar os payloads exatos da API, incluindo respostas de erro.

2. **Simulação de Webhooks**:
   - Construa payloads de eventos de webhook fictícios que correspondam à estrutura enviada pela respectiva rede social (ex: Webhook do Meta/Instagram).
   - Gere assinaturas seguras de payload usando HMAC-SHA256 com a chave secreta do webhook configurada para passar pelo middleware de verificação de assinatura (ex: `X-Hub-Signature-256`).
   - Use o cliente de API do Japa para enviar requisições HTTP POST com os cabeçalhos de assinatura gerados para os endpoints de teste.

3. **Testes de Resiliência e Casos de Borda**:
   - Escreva testes simulando códigos de status HTTP como `429 Too Many Requests` (limite de taxa), `401 Unauthorized` (tokens expirados) e erros de servidor `5xx`.
   - Simule timeouts de rede para garantir que comportamentos de fallback e estratégias de retry (ex: atraso ou backoff do BullMQ) funcionem como esperado.

4. **Transações do Lucid ORM**:
   - Utilize transações limpas do banco de dados em testes de integração. Integre o hook de testes transacionais para que cada operação de banco em um teste sofra rollback automaticamente ao final de sua execução.

## Exemplos
### Mocking de Chamadas HTTP (fetch nativo) usando Nock
```typescript
import { test } from '@japa/runner'
import nock from 'nock'
import InstagramService from '#services/instagram_service'

test.group('Instagram Service - Publish Post', (group) => {
  group.each.teardown(() => {
    nock.cleanAll()
  })

  test('successfully publishes a photo to Instagram Feed', async ({ assert }) => {
    // Intercept outbound post creation request
    nock('https://graph.facebook.com/v20.0')
      .post('/123456789/media', {
        image_url: 'https://example.com/photo.jpg',
        caption: 'Hello World',
      })
      .reply(200, { id: 'media_container_id' })

    nock('https://graph.facebook.com/v20.0')
      .post('/123456789/media_publish', {
        creation_id: 'media_container_id',
      })
      .reply(200, { id: 'post_id' })

    const service = new InstagramService()
    const result = await service.publishPhoto('123456789', {
      imageUrl: 'https://example.com/photo.jpg',
      caption: 'Hello World',
    })

    assert.equal(result.id, 'post_id')
  })
})
```

### Simulação de Webhooks com Verificação de Assinatura
```typescript
import { test } from '@japa/runner'
import crypto from 'node:crypto'
import env from '#start/env'

test.group('Instagram Comments Webhook', () => {
  test('handles incoming comments webhook with valid signature', async ({ client }) => {
    const payload = {
      object: 'instagram',
      entry: [
        {
          id: 'instagram_page_id',
          time: 123456789,
          changes: [
            {
              field: 'comments',
              value: {
                id: 'comment_id',
                text: 'Nice photo!',
                from: { id: 'user_id', username: 'user1' },
              },
            },
          ],
        },
      ],
    }

    const payloadString = JSON.stringify(payload)
    // Generate Meta-compliant HMAC-SHA256 signature
    const signature = crypto
      .createHmac('sha256', env.get('META_APP_SECRET'))
      .update(payloadString)
      .digest('hex')

    const response = await client
      .post('/webhooks/instagram')
      .json(payload)
      .header('x-hub-signature-256', `sha256=${signature}`)

    response.assertStatus(200)
  })
})
```

## Restrições
- Nunca faça requisições HTTP reais para APIs externas no seu conjunto de testes.
- Não faça mock de toda a interface da classe se estiver realizando testes de integração; em vez disso, simule na camada de transporte HTTP usando nock (interceptando o `fetch` nativo).
- Nunca exponha chaves secretas do Meta ou credenciais sensíveis codificadas em testes; sempre recupere-as de variáveis de ambiente ou arquivos de configuração.
