---
name: adonisjs-meta-api-outbound-rate-limiting-best-practices
description: Use when implementing, reviewing, or debugging outbound API rate limiting, request throttling, or concurrency control for Meta/Instagram Graph APIs using Redis in AdonisJS. Triggers on files modifying MetaService, outbound API client throttling, processing Meta API rate limit headers (x-app-usage, x-business-use-case-usage), or managing dynamic BullMQ job delays.
---

## Objetivo
Estabelecer diretrizes padrão e padrões de implementação para o throttling resiliente de chamadas de API de saída e o gerenciamento de rate limit para integrações com a Meta (Graph API do Facebook/Instagram) usando Redis e BullMQ no AdonisJS v6.

## Instruções

### 1. Parsing dos Cabeçalhos de Rate Limit da Meta
A Meta retorna informações de rate limit em cabeçalhos a cada resposta. Implemente um parsing robusto para:
- `x-app-usage`: Indica o limite no nível da aplicação. Exemplo: `{"call_count": 80, "total_cputime": 10, "total_time": 15}`.
- `x-business-use-case-usage`: Indica os limites no nível de negócio/página. Exemplo: `{"1234567890":[{"call_count":15,"total_cputime":5,"total_time":7,"type":"instagram","estimated_time_to_regain_access":0}]}`.

Faça o parsing desses cabeçalhos com segurança no seu cliente de requisições (por exemplo, dentro de `MetaRequestMixin` após uma requisição `fetch`) e atualize as estatísticas de uso no Redis:
```typescript
const appUsageRaw = response.headers.get('x-app-usage')
if (appUsageRaw) {
  const appUsage = JSON.parse(appUsageRaw)
  const maxUsage = Math.max(appUsage.call_count ?? 0, appUsage.total_cputime ?? 0, appUsage.total_time ?? 0)
  await redis.setex(`meta:rate_limit:app`, 300, maxUsage.toString())
}
```

### 2. Throttling Proativo e Controle de Concorrência com Redis
- **Throttling Proativo:** Antes de executar qualquer requisição de saída à Meta, verifique o nível de uso armazenado no Redis.
  - Se o uso estiver entre **80% e 90%**, introduza um delay artificial proativo (por exemplo, 500ms - 2000ms) para espaçar as requisições.
  - Se o uso estiver **acima de 90%**, aplique throttling agressivo e enfileire as requisições ou adie os jobs em background imediatamente.
- **Locks de Concorrência (Semáforos):** Use semáforos baseados em Redis para garantir que operações críticas (como etapas de publicação concorrentes) sejam espaçadas e não disparem penalidades de rate limit por concorrência.

### 3. Delays Dinâmicos de Jobs no BullMQ para Resiliência
Quando jobs em background falham devido a uma exceção de rate limit (HTTP 429 ou códigos 4, 17, 341):
- Extraia o `estimated_time_to_regain_access` do cabeçalho `x-business-use-case-usage`.
- Calcule o delay de retry em milissegundos:
  - Se especificado, use `estimated_time_to_regain_access * 60 * 1000` (mais um buffer de segurança de 30 segundos).
  - Se não especificado, use um delay robusto por padrão (por exemplo, 5 minutos: `300,000` ms).
- Redespache ou adie o job dinamicamente usando os métodos de fila do BullMQ em vez de confiar em retries estáticos imediatos:
```typescript
// Dentro do handle do Worker/Job:
try {
  await metaService.publishEvent(event)
} catch (error) {
  if (error instanceof MetaRateLimitException) {
    const delay = error.estimatedTimeToRegainAccessMs || 300_000
    logger.warn({ eventId: event.id, delay }, 'Meta API rate limited. Delaying job.')
    await instagramQueue.add('publish-event', { eventId: event.id }, { delay })
    return // Reconhece o job atual como tratado/movido
  }
  throw error // Deixa o retry padrão tratar outras falhas
}
```

### 4. Normalização de Erros
Garanta que o handler de exceções mapeie os códigos de erro de rate limit da Meta (`4`, `17`, `341`) para uma `MetaRateLimitException` customizada. Capture e faça o parsing dos cabeçalhos de resposta ao lançar essa exceção para que o delay seja legível pelos jobs/workers.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- Não faça requisições de API externas diretamente usando `fetch` ou `axios` em controllers ou jobs sem passar pelo pipeline central `MetaService` / `MetaRequestMixin`.
- Não armazene estados de rate limit em variáveis locais em memória. Use Redis para garantir o rastreamento preciso de estado distribuído em deployments multi-processo/multi-servidor.
- Nunca deixe a versão da Graph API do Facebook hardcoded; obtenha-a da configuração ou de variáveis de ambiente (`env.get('META_GRAPH_VERSION')`).
