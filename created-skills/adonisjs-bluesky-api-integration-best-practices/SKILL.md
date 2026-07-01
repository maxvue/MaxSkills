---
name: adonisjs-bluesky-api-integration-best-practices
description: Use when implementing, configuring, or debugging integrations with the Bluesky social network using the AT Protocol (@atproto/api) in AdonisJS. Triggers on setting up BlueskyService, managing DID authentication, posting rich text with facets, uploading image blobs, and handling Bluesky API rate limits.
---

# Boas Práticas de Integração com a API do Bluesky em AdonisJS

## Objetivo
Fornecer padrões, diretrizes de codificação e boas práticas para desenvolver, depurar e testar integrações com a API do Bluesky utilizando a biblioteca `@atproto/api` em aplicativos AdonisJS v6.

## Instruções

### 1. Encapsulamento Arquitetural
* **Serviço Dedicado**: Encapsule todas as comunicações com o Bluesky e o AT Protocol dentro de um serviço dedicado (ex: `app/services/bluesky_service.ts`).
* **Gerenciamento de Sessão**: O estado da sessão (`AtpSessionData`) é volátil. Para tarefas em segundo plano (background jobs), realize a autenticação usando a senha do aplicativo (App Password) dinamicamente ou carregue/salve tokens de sessão em um cache seguro (ex: Redis). Não armazene dados de sessão ativos em variáveis de estado dentro de ciclos de vida de requisições HTTP sem estado.
* **Sem Requisições Diretas no Controller**: Os controllers nunca devem importar diretamente a biblioteca `@atproto/api` ou fazer requisições de rede diretas para os endpoints do Bluesky. Eles devem injetar e invocar o `BlueskyService`.

### 2. Fluxo de Autenticação e Senhas de Aplicativo (App Passwords)
* **App Passwords**: Nunca use a senha master do Bluesky. Sempre gere uma App Password dedicada para o aplicativo.
* **Criptografia**: Armazene as credenciais (identificador e App Password) criptografadas no banco de dados se elas forem gerenciadas por inquilino (tenant), utilizando o serviço `encryption` do AdonisJS.
* **Validação de Ambiente**: Valide as credenciais globais do sistema no arquivo `start/env.ts`.

### 3. Resolução de Rich Text (Facets)
* **Detecção Automática**: O Bluesky exige que links e menções de usuários sejam explicitamente definidos em "facets" com intervalos precisos de índices de bytes.
* **Helper RichText**: Use a classe `RichText` da biblioteca `@atproto/api` para analisar o texto, detectar links/menções e construir o payload de facets necessário.
* **Resolução do Agente**: Chame `detectFacets(agent)` na instância do `RichText` antes de enviar o post. Isso garante que as menções de usuários sejam resolvidas corretamente para seus respectivos DIDs por meio de consulta à API.

### 4. Upload de Mídia (Blobs)
* **Etapas Separadas**: O upload de mídia (imagens) para o Bluesky é um processo de duas etapas:
  1. Faça o upload do arquivo de imagem como um blob binário usando `agent.uploadBlob()`.
  2. Insira os metadados de referência do blob retornados (CID e mimeType) no bloco `embed` do registro do post sob o tipo `app.bsky.embed.images`.
* **Uploads Sequenciais**: Envie múltiplas imagens de forma sequencial (usando um laço `for...of`) em vez de concorrente via `Promise.all` para evitar timeouts de rede ou problemas de limite de taxa nos endpoints de blob.
* **Textos Alternativos (Alt)**: Sempre exija e forneça texto alternativo (`alt`) para todas as imagens enviadas para estar em conformidade com os padrões de acessibilidade do Bluesky.

### 5. Resiliência, Limites de Taxa (Rate Limits) e Exceções
* **Timeout da API**: Sempre configure timeouts apropriados para as requisições da API.
* **Tratamento de Rate Limits**: Trate os códigos de erro do AT Protocol de forma adequada. Se uma requisição disparar um limite de taxa (HTTP 429), capture o erro, registre nos logs o tempo restante/limites e lance uma exceção de domínio personalizada (ex: `BlueskyApiException`) para que os workers em segundo plano (ex: BullMQ) possam tentar novamente com backoff.

---

## Restrições
* **NÃO** envie posts com texto puro contendo links ou menções sem antes resolvê-los usando facets do `RichText`; caso contrário, eles aparecerão como texto normal e não serão clicáveis.
* **NÃO** salve senhas de aplicativo (App Passwords) ou nomes de usuário fixos no código (hardcoded) ou no controle de versão.
* **NÃO** envie uploads de imagens concorrentes usando `Promise.all`. Faça o envio sequencialmente.
* **NÃO** omita os atributos de texto alternativo (`alt`) para imagens nos posts.

---

## Examples

### 1. Implementação do Bluesky Service no AdonisJS v6

```typescript
// app/services/bluesky_service.ts
import { inject } from '@adonisjs/core'
import { Logger } from '@adonisjs/core/logger'
import { AtpAgent, RichText } from '@atproto/api'
import { Exception } from '@adonisjs/core/exceptions'
import env from '#start/env'

export class BlueskyApiException extends Exception {
  static status = 502
  static code = 'E_BLUESKY_API_ERROR'
}

interface PostImagePayload {
  buffer: Buffer
  mimeType: string
  alt: string
}

interface PostPayload {
  text: string
  images?: PostImagePayload[]
}

@inject()
export default class BlueskyService {
  private agent: AtpAgent

  constructor(protected logger: Logger) {
    // Instancia o AtpAgent apontando para o serviço social padrão do Bluesky
    // (BskyAgent foi descontinuado em favor de AtpAgent nas versões atuais de @atproto/api)
    this.agent = new AtpAgent({ service: 'https://bsky.social' })
  }

  /**
   * Autentica o agente usando as credenciais configuradas.
   * Em apps multi-tenant, passe as credenciais dinamicamente.
   */
  private async authenticate(identifier?: string, appPassword?: string): Promise<void> {
    const handle = identifier || env.get('BLUESKY_IDENTIFIER')
    const password = appPassword || env.get('BLUESKY_APP_PASSWORD')

    if (!handle || !password) {
      throw new BlueskyApiException('As credenciais do Bluesky não estão configuradas.', { status: 401 })
    }

    try {
      this.logger.debug({ handle }, 'Tentando autenticação na API do Bluesky')
      await this.agent.login({ identifier: handle, password })
      this.logger.debug('Autenticado com sucesso no Bluesky')
    } catch (error: any) {
      this.logger.error({ error: error.message }, 'Falha ao autenticar no Bluesky')
      throw new BlueskyApiException(`Falha no login do Bluesky: ${error.message}`, { status: 401 })
    }
  }

  /**
   * Publica um post com rich text e anexos de imagem sequenciais opcionais.
   */
  async createPost(payload: PostPayload, identifier?: string, appPassword?: string) {
    await this.authenticate(identifier, appPassword)

    try {
      // 1. Processa o Rich Text e detecta facets (links/menções)
      const rt = new RichText({ text: payload.text })
      await rt.detectFacets(this.agent)

      const postData: Record<string, any> = {
        $type: 'app.bsky.feed.post',
        text: rt.text,
        facets: rt.facets,
        createdAt: new Date().toISOString(),
      }

      // 2. Faz o upload de imagens sequencialmente se fornecidas
      if (payload.images && payload.images.length > 0) {
        const embeddedImages: any[] = []

        for (const img of payload.images) {
          this.logger.debug({ mimeType: img.mimeType }, 'Enviando blob de imagem para o Bluesky')
          
          const uploadRes = await this.agent.uploadBlob(img.buffer, {
            encoding: img.mimeType,
          })

          if (!uploadRes.data?.blob) {
            throw new BlueskyApiException('Falha ao enviar blob de imagem para a API do Bluesky.')
          }

          embeddedImages.push({
            image: uploadRes.data.blob,
            alt: img.alt || '',
          })
        }

        postData.embed = {
          $type: 'app.bsky.embed.images',
          images: embeddedImages,
        }
      }

      this.logger.debug('Enviando post para o feed do Bluesky')
      const response = await this.agent.post(postData)

      this.logger.info({ uri: response.uri, cid: response.cid }, 'Post no Bluesky publicado com sucesso')
      return {
        uri: response.uri,
        cid: response.cid,
        permalink: this.buildPermalink(response.uri),
      }
    } catch (error: any) {
      this.logger.error({ error: error.message }, 'Erro ao publicar no Bluesky')
      throw new BlueskyApiException(`Erro na API do Bluesky: ${error.message}`, {
        status: error.status || 500,
        cause: error,
      })
    }
  }

  /**
   * Formata um at-uri padrão para um link público da web
   * Exemplo: at://did:plc:xyz/app.bsky.feed.post/123 -> https://bsky.app/profile/did:plc:xyz/post/123
   */
  private buildPermalink(uri: string): string {
    const parts = uri.replace('at://', '').split('/')
    const did = parts[0]
    const rkey = parts[2]
    return `https://bsky.app/profile/${did}/post/${rkey}`
  }
}
```
