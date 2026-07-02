---
name: adonisjs-google-analytics-ga4-integration-best-practices
description: Use when integrating, configuring, or querying the Google Analytics 4 (GA4) Data API in AdonisJS. Triggers on fetching traffic and conversion metrics by source/medium (UTM), handling Google OAuth2 tokens for GA4 access, caching analytics data using Redis, or executing background sync jobs for marketing attribution of solar/photovoltaic leads.
---

# Boas Práticas de Integração do Google Analytics 4 (GA4) no AdonisJS

## Objetivo
Estabelecer diretrizes seguras, eficientes e escaláveis para integrar e consultar a Data API do Google Analytics 4 (GA4) em aplicações baseadas no AdonisJS v6. Isso inclui gerenciar credenciais e tokens do Google OAuth2, recuperar métricas de tráfego e conversões de leads fotovoltaicos filtradas por parâmetros UTM, armazenar resultados em cache com o Redis e processar a sincronização de dados de forma assíncrona por meio do BullMQ.

## Instruções

### 1. Gerenciamento de Credenciais e Tokens (AdonisJS Ally)
- Integre-se ao **Google OAuth2** utilizando o `@adonisjs/ally` para obter a autorização e os tokens dos usuários.
- Solicite o escopo `https://www.googleapis.com/auth/analytics.readonly` durante o fluxo de autenticação.
- Persista de forma segura o `access_token`, `refresh_token` e o tempo de expiração do token (`expires_at`) no banco de dados, associando-os ao registro de credenciais de marketing do cliente/tenant.
- Sempre verifique se o `access_token` está expirado antes de chamar a API do GA4. Se estiver expirado, utilize o `refresh_token` para solicitar um novo token e atualize o banco de dados.

### 2. Inicialização do Cliente da Data API do GA4
- Utilize a biblioteca oficial `@google-analytics/data` (`BetaAnalyticsDataClient`).
- Inicialize o cliente dinamicamente utilizando o token de acesso recuperado para o cliente específico. Não utilize credenciais globais de conta de serviço se forem exigidos tokens OAuth específicos de cada cliente.
- Configure uma classe de serviço ou provider para instanciar o cliente:
  ```typescript
  import { BetaAnalyticsDataClient } from '@google-analytics/data'
  import { OAuth2Client } from 'google-auth-library'

  export class GoogleAnalyticsService {
    public getClient(accessToken: string): BetaAnalyticsDataClient {
      // O BetaAnalyticsDataClient espera um authClient (GoogleAuth/OAuth2Client),
      // não um access_token cru em `auth.credentials`.
      const oauthClient = new OAuth2Client()
      oauthClient.setCredentials({ access_token: accessToken })

      return new BetaAnalyticsDataClient({
        authClient: oauthClient,
      })
    }
  }
  ```

### 3. Consulta de Métricas do GA4 (Atribuição de Tráfego e Conversões por UTM)
- Construa consultas para buscar métricas de tráfego como `sessions` (sessões), `activeUsers` (usuários ativos), `screenPageViews` (visualizações de página) e eventos personalizados de conversão.
- Filtre os dados utilizando os filtros de dimensão `sessionSource` (ou `utm_source`) e `sessionMedium` (ou `utm_medium`) para atribuir corretamente o tráfego/leads às campanhas e canais de origem (ex: `google` / `cpc`, `meta` / `social`, campanhas de captação de leads fotovoltaicos).
- Garanta que os períodos (date ranges) sejam definidos dinamicamente. Sempre forneça períodos padrão (ex: últimos 30 dias) se nenhum for especificado.
- Exemplo de payload para requisição de relatório:
  ```typescript
  const [response] = await client.runReport({
    property: `properties/${propertyId}`,
    dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }],
    dimensions: [{ name: 'sessionSource' }, { name: 'sessionMedium' }],
    metrics: [{ name: 'sessions' }, { name: 'activeUsers' }, { name: 'conversions' }],
    dimensionFilter: {
      filter: {
        fieldName: 'sessionMedium',
        stringFilter: {
          matchType: 'CONTAINS',
          value: 'cpc',
          caseSensitive: false,
        },
      },
    },
  })
  ```

### 4. Estratégia de Cache com Redis
- Como a Data API do Google Analytics impõe limites estritos de cota (rate limits) por propriedade, armazene todas as respostas de relatórios em cache com o `@adonisjs/redis`.
- Defina um TTL (Time to Live) de cache de pelo menos 1 hora (ex: `3600` segundos) para consultas normais de painel.
- Gere chaves de cache exclusivas combinando o identificador do tenant/cliente, as métricas solicitadas, o filtro de origem e o período:
  ```typescript
  const cacheKey = `ga4:metrics:${clientId}:${startDate}:${endDate}`
  ```

### 5. Sincronização Assíncrona com BullMQ
- Evite chamadas HTTP em tempo real para a API do GA4 durante requisições HTTP normais de usuários (ex: ao carregar o dashboard).
- Execute um job em segundo plano agendado no BullMQ (`SyncGa4MetricsJob`) para buscar as métricas periodicamente (ex: diariamente à meia-noite) e persistir as estatísticas agregadas no banco de dados.
- Leia os dados a partir do banco de dados ao exibir as métricas no dashboard front-end. No front, consuma essas métricas agregadas por meio de uma store `@maxvue/max-pinia` (caminho string `/api/...` resolvido por `apiGetRoute`), e não via `axios.get` manual. Apenas dispare sincronizações manuais por meio de jobs se for explicitamente solicitado pelo usuário.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Credenciais Hardcoded:** Nunca salve IDs de cliente do Google, Client Secrets ou IDs de Propriedade no código. Use o `.env` e mapeie-os em `start/env.ts`.
- **Sem Chamadas Bloqueantes:** Não realize requisições diretas e síncronas para a API do Google em ações de Controllers. Use jobs enfileirados (`SyncGa4MetricsJob`) ou recupere valores do cache.
- **Isolamento de Tenants:** Garanta que todas as consultas de propriedades do GA4 estejam estritamente escopadas ao contexto do tenant ou cliente atual para evitar vazamento de dados entre clientes.
- **Tratamento Rígido de Erros:** Envolva todas as requisições à API em blocos try-catch. Trate de forma amigável tokens expirados, IDs de propriedade inválidos e erros de cota da API do Google, registrando-os por meio do serviço de Logger do AdonisJS.
