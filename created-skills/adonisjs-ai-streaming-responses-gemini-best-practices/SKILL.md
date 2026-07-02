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
- Para enviar apenas os tokens de texto, use `result.pipeTextStreamToResponse(response.response)`. Para emitir o protocolo de mensagens do Vercel AI SDK (consumido pelos hooks `@ai-sdk/vue`), use `result.pipeUIMessageStreamToResponse(response.response)`. **Confirme o nome exato do método contra a versão do pacote `ai` instalada** — em versões anteriores ele se chamava `pipeDataStreamToResponse`. Ambos recebem o objeto `ServerResponse` nativo do Node (`response.response`).
- **Headers:** `pipeTextStreamToResponse` escreve DIRETAMENTE no `ServerResponse` nativo (chama `response.response.writeHead(...)` internamente), então headers definidos via `response.header(...)` do AdonisJS (que só são liberados pelo `writeHead()` interno do AdonisJS) são silenciosamente descartados. Passe os headers no próprio pipe — `result.pipeTextStreamToResponse(response.response, { headers: { ... } })` — ou defina-os no response nativo com `response.response.setHeader(...)` antes do pipe. Não use `response.header(...)` aqui.
- **Content-Type:** `pipeTextStreamToResponse` emite um stream de texto puro (`text/plain; charset=utf-8`) SEM o framing SSE (`data:`/`event:`), então NÃO anuncie `text/event-stream` para ele — um cliente `EventSource`/parser SSE não conseguirá interpretá-lo (consuma via `fetch` + `ReadableStream`). Use `text/event-stream` apenas com `pipeUIMessageStreamToResponse` (protocolo de dados/SSE do AI SDK) ou SSE escrito à mão.

#### Exemplo de Configuração de Stream Padrão:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import { google } from '@ai-sdk/google'
import { streamText } from 'ai'

export default class AiStreamingController {
  public async generate({ request, response }: HttpContext) {
    const { prompt } = request.only(['prompt'])

    const result = await streamText({
      model: google('gemini-2.5-flash'),
      prompt: prompt,
    })

    // Pipe do stream de texto diretamente para o objeto de resposta nativo do Node.js.
    // Confira o nome do método na versão instalada do pacote `ai`:
    //   - pipeTextStreamToResponse  -> apenas tokens de texto (text/plain)
    //   - pipeUIMessageStreamToResponse -> protocolo de mensagens/SSE (hooks @ai-sdk/vue)
    //
    // IMPORTANTE: passe os headers no próprio pipe. Headers definidos via
    // response.header(...) do AdonisJS são descartados, pois pipeTextStreamToResponse
    // chama writeHead() diretamente no ServerResponse nativo.
    result.pipeTextStreamToResponse(response.response, {
      headers: {
        'Cache-Control': 'no-cache, no-transform', // desativa buffering/compressão
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no', // ignora buffering do Nginx
      },
    })
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

### 4. Alternativa: push de tokens via AdonisJS Transmit
O streaming HTTP direto (acima) é o caminho mais simples quando o cliente está aguardando ativamente a resposta de uma única requisição. Quando os tokens precisam ser entregues em um canal de eventos compartilhado (ex.: várias abas/dispositivos do mesmo usuário, ou continuar uma geração em background), use o **AdonisJS Transmit** (SSE), que é a camada de realtime padrão do projeto.
- Crie/assine um canal Transmit por sessão de conversa (ex.: `ai/chat/:conversationId`).
- No loop `for await (const part of result.textStream)`, faça `transmit.broadcast()` de cada delta para o canal.
- O front consome via cliente Transmit, sem GET/polling manual.
Escolha um dos dois mecanismos por endpoint — não duplique o mesmo fluxo de tokens em HTTP stream e Transmit simultaneamente.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** utilize `response.send()` ou retorne uma string simples para endpoints de streaming. Isso envia todo o payload de uma única vez, anulando o propósito do streaming.
- **NÃO** deixe a compressão ativada em rotas de streaming. Sempre verifique se os chunks estão sendo recebidos progressivamente no cliente.
- **NÃO** se esqueça do header `X-Accel-Buffering: no` se a aplicação estiver atrás de um proxy Nginx, caso contrário o Nginx reterá o stream no buffer.
