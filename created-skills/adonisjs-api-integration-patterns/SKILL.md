---
name: adonisjs-api-integration-patterns
description: Use when creating, debugging, or enhancing integrations with external HTTP APIs in an AdonisJS ecosystem. Triggers on setting up custom API clients, managing API credentials, configuring request timeouts/retries, and processing webhooks or background integration tasks.
---

# Padrões de Integração com APIs Externas no AdonisJS

## Objetivo
Fornecer regras, padrões e melhores práticas para projetar, codificar e depurar integrações com APIs externas seguras, robustas e resilientes no AdonisJS v6.

## Instruções

### 1. Arquitetura e Estrutura de Diretórios
* **Serviços Dedicados**: Encapsule todas as comunicações de APIs externas dentro de classes de Serviço dedicadas. Crie-as sob `app/services/` (ex: `app/services/efi_payment_service.ts`, `app/services/whatsapp_api_service.ts`).
* **Sem Chamadas Diretas em Controllers**: Os controladores nunca devem realizar chamadas HTTP diretas a APIs externas. Eles devem depender da classe de serviço de API apropriada.
* **Payloads e Respostas Tipados**: Defina interfaces ou tipos TypeScript para todos os corpos de requisição e payloads de resposta esperados das APIs. Use-os para tipar parâmetros e valores de retorno dos serviços.

### 2. Injeção de Dependência
* Use o container de IoC do AdonisJS v6. Anote as classes de serviço com `@inject()` e injete dependências (como o `Logger`) através do construtor.
* Evite usar classes estáticas ou módulos singleton sem injeção, pois isso prejudica a testabilidade.

### 3. Gerenciamento Seguro de Credenciais e Configurações
* **Variáveis de Ambiente**: Defina todas as URLs base, credenciais e configurações de APIs externas no arquivo `.env` e valide-as em `start/env.ts`.
* **Serviço de Configuração**: Acesse as credenciais através do serviço `config` do AdonisJS ou importações diretas de `env` se estiver configurado.
* **Sem Hardcoding**: Nunca escreva credenciais diretamente no código nem as envie para o controle de versão.

### 4. Resiliência de Transporte, Timeouts e Retentativas
* **Fetch Nativo**: Use a API nativa `fetch` do Node.js.
* **Timeouts Obrigatórios**: Sempre especifique um limite de tempo (timeout) para evitar que requisições presas bloqueiem o event loop. Use `AbortSignal.timeout(ms)`.
* **Timeouts em Contexto Síncrono**: Mantenha os timeouts para requisições HTTP síncronas abaixo de 10 segundos.
* **Retentativas Resilientes**: Para endpoints instáveis ou falhas temporárias de rede, implemente um mecanismo de retentativa. Ao usar o BullMQ para tarefas em background, prefira a configuração de retentativa nativa de jobs do BullMQ com opções de backoff.

### 5. Operações Assíncronas e Filas (Offloading)
* Se uma operação de API for lenta ou não exigir resposta imediata ao usuário (ex: exportação de arquivos, sincronização de contatos, envio de mensagens em massa via WhatsApp), envie a tarefa para uma fila em background usando o BullMQ.
* Responda ao cliente imediatamente com um status `202 Accepted`.

### 6. Logging e Tratamento de Exceções
* **Logging Estruturado**: Registre todas as requisições enviadas e respostas recebidas (sucesso e falha) utilizando o serviço `logger` do AdonisJS.
* **Sanitização de Dados Sensíveis**: Remova explicitamente cabeçalhos de autorização (Authorization), chaves de API, dados de cartão de crédito e senhas antes de registrar logs ou passá-los para objetos de erro.
* **Exceções Personalizadas**: Envolva exceções brutas do cliente HTTP em exceções específicas do domínio (ex: crie uma classe `ExternalApiException`) para manter a lógica de domínio limpa e permitir o tratamento padronizado no manipulador global de exceções HTTP.

---

## Restrições
* **NÃO** realize requisições HTTP diretas dentro de controllers, models ou views.
* **NÃO** faça qualquer requisição a APIs externas sem configurar um timeout (o uso de `AbortSignal.timeout` é obrigatório).
* **NÃO** registre logs com tokens de autorização brutos, segredos de cliente ou informações de identificação pessoal (PII) sensíveis.
* **NÃO** ignore códigos de status de resposta; sempre verifique `response.ok` ou compare o código de status e trate as falhas explicitamente.

---

## Exemplos

### 1. Implementação Robusta de Serviço com Fetch Nativo e AbortSignal

```typescript
// app/services/whatsapp_api_service.ts
import { inject } from '@adonisjs/core'
import { Logger } from '@adonisjs/core/logger'
import env from '#start/env'
import { Exception } from '@adonisjs/core/exceptions'

interface WhatsAppMessagePayload {
  to: string
  body: string
}

interface WhatsAppMessageResponse {
  messages: { id: string }[]
}

export class ExternalApiException extends Exception {
  static status = 502
  static code = 'E_EXTERNAL_API_ERROR'
}

@inject()
export default class WhatsAppApiService {
  private baseUrl = env.get('WHATSAPP_API_BASE_URL')
  private accessToken = env.get('WHATSAPP_API_ACCESS_TOKEN')
  private phoneNumberId = env.get('WHATSAPP_PHONE_NUMBER_ID')

  constructor(protected logger: Logger) {}

  /**
   * Helper para ocultar credenciais sensíveis de URLs ou strings
   */
  private redact(str: string): string {
    // Não usar new RegExp(token) — tokens com metacaracteres ('(', '[', '+') lançam SyntaxError
    // ou silenciosamente falham no match (ex: '.' casa qualquer char), vazando o segredo nos logs.
    // Substituição por split/join é segura e não requer escape.
    if (!this.accessToken) return str
    return str.split(this.accessToken).join('***REDACTED***')
  }

  /**
   * Envia uma mensagem de texto via WhatsApp Cloud API
   */
  async sendTextMessage(
    payload: WhatsAppMessagePayload
  ): Promise<WhatsAppMessageResponse> {
    const url = `${this.baseUrl}/${this.phoneNumberId}/messages`
    const timeoutMs = 8000 // 8 segundos

    this.logger.debug({ url: this.redact(url), payload }, 'Enviando requisição para a WhatsApp Cloud API')

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.accessToken}`,
        },
        body: JSON.stringify({
          messaging_product: 'whatsapp',
          to: payload.to,
          type: 'text',
          text: { body: payload.body },
        }),
        signal: AbortSignal.timeout(timeoutMs),
      })

      const responseText = await response.text()
      this.logger.debug(
        { 
          status: response.status, 
          body: this.redact(responseText) 
        }, 
        'Resposta recebida da WhatsApp Cloud API'
      )

      if (!response.ok) {
        throw new ExternalApiException(
          `A requisição à WhatsApp Cloud API falhou com status ${response.status}: ${responseText}`,
          { status: response.status }
        )
      }

      return JSON.parse(responseText) as WhatsAppMessageResponse
    } catch (error: any) {
      this.logger.error(
        { 
          error: error.message, 
          stack: error.stack,
          url: this.redact(url) 
        }, 
        'Erro ao se comunicar com a WhatsApp Cloud API'
      )

      if (error.name === 'TimeoutError') {
        throw new ExternalApiException('A requisição à WhatsApp Cloud API expirou (timeout)', { status: 504 })
      }

      if (error instanceof ExternalApiException) {
        throw error
      }

      throw new ExternalApiException(`Erro de comunicação com a WhatsApp Cloud API: ${error.message}`, {
        status: 500,
        cause: error,
      })
    }
  }
}
```
