---
name: adonisjs-ai-streaming-responses-gemini-best-practices
description: Use when implementing, configuring, or debugging server-side streaming responses from Google Gemini or other LLMs in AdonisJS v6. Triggers on setting up HTTP stream controllers, returning Vercel AI SDK streamText or streamObject, handling SSE headers, and troubleshooting output buffer/compression issues.
---

# Boas Práticas para Respostas de Streaming de IA (Gemini) no AdonisJS v6

## Objetivo
Implementar respostas de streaming robustas e em tempo real a partir do Google Gemini (ou outros LLMs) usando o Vercel AI SDK em controllers do AdonisJS v6, garantindo a configuração correta de Server-Sent Events (SSE), gerenciamento do ciclo de vida da conexão do cliente e desativação do buffering de saída.

## Instruções

### 1. Implementação no Controller e Envio do Stream (Piping)
Para fazer o streaming de respostas de texto dinamicamente, utilize a função `streamText` do Vercel AI SDK (`ai`) e direcione (pipe) o fluxo para a resposta do AdonisJS.

- Importe `streamText` e o provedor Google AI.
- Configure os headers de streaming apropriados para evitar buffering no proxy e no navegador.
- Use `response.stream()` para transmitir o stream bruto ou use `result.pipeDataStreamToResponse(response.response)` para formatar a resposta no protocolo padrão do Vercel AI SDK.

#### Exemplo de Configuração de Stream Padrão:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import { google } from '@ai-sdk/google'
import { streamText } from 'ai'

export default class AiStreamingController {
  public async generate({ request, response }: HttpContext) {
    const { prompt } = request.only(['prompt'])

    // Desativa buffering de saída e compressão para SSE
    response.header('Content-Type', 'text/event-stream')
    response.header('Cache-Control', 'no-cache, no-transform')
    response.header('Connection', 'keep-alive')
    response.header('X-Accel-Buffering', 'no') // Ignora buffering do Nginx

    const result = await streamText({
      model: google('gemini-2.5-flash'),
      prompt: prompt,
    })

    // Pipe do data stream diretamente para o objeto de resposta nativo do Node.js
    result.pipeDataStreamToResponse(response.response)
  }
}
```

### 2. Desativação do Middleware de Compressão
O AdonisJS pode possuir middlewares globais de compressão (ex: gzip/brotli). A compressão retém os chunks do streaming em buffer e os envia de uma vez só ao final da requisição.
- Garanta que a rota ignore a compressão. Se utilizar um middleware de compressão, configure-o para excluir rotas iniciadas com `/api/ai/stream` ou verifique headers como `x-no-compression` ou `Cache-Control: no-transform`.
- Caso utilize Nginx, certifique-se de configurar `proxy_buffering off;` para seus endpoints de streaming, ou envie o header `X-Accel-Buffering: no`.

### 3. Gerenciamento de Desconexão do Cliente (Abort)
Quando um cliente fecha a conexão (ex: fecha a aba do navegador ou cancela a requisição), você deve interromper a chamada do LLM para evitar consumo desnecessário de tokens e custos de API.
- O Vercel AI SDK lida com o cancelamento da stream automaticamente quando o leitor da stream subjacente é fechado.
- Se estiver realizando iterações manuais ou utilizando wrappers customizados, escute o evento `close` da requisição do Node.js:
```typescript
request.request.on('close', () => {
  // Lógica para abortar a chamada do LLM / limpar recursos
})
```

## Restrições
- **NÃO** utilize `response.send()` ou retorne uma string simples para endpoints de streaming. Isso envia todo o payload de uma única vez, anulando o propósito do streaming.
- **NÃO** deixe a compressão ativada em rotas de streaming. Sempre verifique se os chunks estão sendo recebidos progressivamente no cliente.
- **NÃO** se esqueça do header `X-Accel-Buffering: no` se a aplicação estiver atrás de um proxy Nginx, caso contrário o Nginx reterá o stream no buffer.
