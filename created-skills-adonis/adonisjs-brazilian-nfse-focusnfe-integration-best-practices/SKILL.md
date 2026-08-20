---
name: adonisjs-brazilian-nfse-focusnfe-integration-best-practices
description: Use when integrating, reviewing, or debugging Brazilian NFS-e (Nota Fiscal de Serviço Eletrônica) issuance, cancellation, and queries using FocusNFe API in AdonisJS v6. Triggers on billing invoice paid events, parsing FocusNFe webhooks, tax calculations (ISS, PIS, COFINS, CSLL), and environment variable configuration for Brazilian fiscal services.
author: Johnattas Conrady Gomes Santana
---
# AdonisJS Brazilian NFS-e FocusNFe Integration Best Practices

## Objetivo
Estabelecer padrões de código rígidos e diretrizes arquiteturais para a integração com a API FocusNFe, com o objetivo de automatizar a emissão, consulta e cancelamento de NFS-e (Nota Fiscal de Serviço Eletrônica) brasileira no AdonisJS v6. A integração deve ser resiliente, assíncrona, desacoplada do ciclo de vida HTTP principal e em conformidade com as regras tributárias brasileiras (ISS, PIS, COFINS, CSLL, IRRF).

## Instruções

### 1. Configuração de Variáveis de Ambiente
Todos os parâmetros de integração devem ser declarados e validados em `start/env.ts`. Não acesse `process.env` diretamente dentro das camadas de serviço. Use o serviço `Env` do AdonisJS.

```typescript
// start/env.ts
export default await Env.create(new URL('../', import.meta.url), {
  FOCUSNFE_API_URL: Env.schema.string({ format: 'url' }),
  FOCUSNFE_TOKEN: Env.schema.string(),
  FOCUSNFE_SANDBOX: Env.schema.boolean(),
  // ... outras variáveis de ambiente
})
```

### 2. Validação de Dados do Cliente com VineJS
Antes de enviar qualquer fatura de faturamento para o serviço de NFS-e, valide os dados do tomador usando o VineJS para garantir a formatação correta e evitar rejeições de validação das autoridades fiscais municipais.

```typescript
import vine from '@vinejs/vine'

export const receiverValidator = vine.compile(
  vine.object({
    cpfCnpj: vine.string().regex(/^(?:\d{11}|\d{14})$/), // Apenas dígitos estritos de CPF ou CNPJ
    email: vine.string().email(),
    razaoSocial: vine.string().minLength(3).maxLength(100),
    inscricaoMunicipal: vine.string().optional(),
    endereco: vine.object({
      logradouro: vine.string(),
      numero: vine.string(),
      complemento: vine.string().optional(),
      bairro: vine.string(),
      codigoMunicipio: vine.string().fixedLength(7), // Código IBGE do município
      uf: vine.string().fixedLength(2),
      cep: vine.string().regex(/^\d{8}$/),
    }),
  })
)
```

### 3. Implementação do Serviço FocusNFe Core
Implemente um serviço dedicado (`app/services/focusnfe_service.ts`) para encapsular a comunicação com a API da FocusNFe. Esse serviço deve permanecer desacoplado de objetos de requisição HTTP específicos e focar puramente na construção do payload, envio de requisições HTTP e análise das respostas.

```typescript
// app/services/focusnfe_service.ts
import env from '#start/env'
import logger from '@adonisjs/core/services/logger'
import Invoice from '#models/invoice'

export default class FocusNfeService {
  private baseUrl: string
  private token: string

  constructor() {
    this.baseUrl = env.get('FOCUSNFE_API_URL')
    this.token = env.get('FOCUSNFE_TOKEN')
  }

  /**
   * Constrói o payload e solicita a emissão da NFS-e.
   * `ref` é a referência idempotente GERADA PELO CLIENTE (não devolvida pela FocusNFe).
   * Receba o `Invoice` model diretamente; o `ref` deve ser persistido ANTES do envio.
   */
  async issueNfse(invoice: Invoice) {
    const ref = invoice.nfseReferenceId
    const payload = this.buildIssuancePayload(invoice)
    const url = `${this.baseUrl}/v2/nfse?ref=${ref}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(this.token + ':').toString('base64')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`FocusNFe API error: ${JSON.stringify(errorData)}`)
      }

      return await response.json()
    } catch (error) {
      logger.error({ err: error }, 'Falha ao se comunicar com a API FocusNFe')
      throw error
    }
  }

  /**
   * Calcula as alíquotas brasileiras e constrói o payload JSON
   */
  private buildIssuancePayload(invoice: Invoice) {
    // Alíquotas e valores devem ser representados com precisão. Evite erros de ponto flutuante.
    const serviceValue = Number(invoice.amount)
    const issAliquota = Number(invoice.issAliquot || 2.00) // ex: 2.00%
    const issValue = (serviceValue * issAliquota) / 100

    return {
      data_emissao: new Date().toISOString().split('T')[0],
      prestador: {
        cnpj: env.get('COMPANY_CNPJ'),
        inscricao_municipal: env.get('COMPANY_IM'),
        codigo_municipio: env.get('COMPANY_IBGE'),
      },
      tomador: {
        cnpj: invoice.client.cnpj,
        razao_social: invoice.client.name,
        email: invoice.client.email,
        endereco: {
          logradouro: invoice.client.address.street,
          numero: invoice.client.address.number,
          bairro: invoice.client.address.neighborhood,
          codigo_municipio: invoice.client.address.ibgeCode,
          uf: invoice.client.address.state,
          cep: invoice.client.address.zipCode,
        },
      },
      servico: {
        aliquota: issAliquota,
        valor_servicos: serviceValue,
        codigo_servico_116: invoice.serviceCode116 || '1.05', // ex: Licenciamento/software
        iss_retido: 'nao',
        item_lista_servico: invoice.serviceListItem || '0105',
      },
    }
  }
}
```

### 4. Processamento de Job em Background via BullMQ
Nunca emita ou consulte NFS-e de forma síncrona durante o tratamento de requisições HTTP de usuários. Em vez disso, envie tarefas usando o BullMQ.
- **Evento de ativação**: Assine o evento `billing:invoice:paid` dentro de um event listener.
- **Execução da Job**: Dispache o `GenerateNfseJob` com o ID da fatura (`invoice`).
- **Estratégia de reprocessamento**: Configure um exponencial backoff no job para lidar com quedas de conexão temporárias ou latência alta nos servidores municipais.

```typescript
// app/jobs/generate_nfse_job.ts
import { Job } from 'bullmq'
import { randomUUID } from 'node:crypto'
import FocusNfeService from '#services/focusnfe_service'
import Invoice from '#models/invoice'

export default class GenerateNfseJob {
  static get key() {
    return 'GenerateNfseJob'
  }

  async handle(job: Job) {
    const { invoiceId } = job.data
    const invoice = await Invoice.findOrFail(invoiceId)

    if (invoice.nfseStatus === 'authorized') {
      return
    }

    // O `ref` é a chave de idempotência GERADA PELO CLIENTE e enviada à FocusNFe
    // como query string (?ref=...). A FocusNFe NÃO devolve esse valor — por isso
    // ele deve ser gerado e persistido ANTES do envio, para correlacionar o webhook.
    if (!invoice.nfseReferenceId) {
      invoice.nfseReferenceId = randomUUID()
      await invoice.save()
    }

    // Instancie o service manualmente: jobs BullMQ puros não passam pelo
    // container IoC, então o construtor não recebe dependências injetadas.
    const focusNfeService = new FocusNfeService()
    await focusNfeService.issueNfse(invoice)

    invoice.nfseStatus = 'processing'
    await invoice.save()
  }
}
```

### 5. Recebimento de Webhook e Idempotência
Trate as atualizações de status (ex: autorizada, rejeitada, cancelada) de forma assíncrona, criando um endpoint que recebe webhooks enviados pela FocusNFe.
- **Localização do Controller**: `app/controllers/focusnfe_webhooks_controller.ts`
- **Idempotência**: Verifique se a atualização contém um novo status e evite processamento duplicado efetuando um travamento de registro no banco (row lock).
- **Armazenamento de arquivos**: Uma vez autorizada a NFS-e, salve a URL do PDF e do XML diretamente no registro da fatura e envie um e-mail de notificação para o tenant.

```typescript
// app/controllers/focusnfe_webhooks_controller.ts
import { HttpContext } from '@adonisjs/core/http'
import Invoice from '#models/invoice'
import db from '@adonisjs/lucid/services/db'

export default class FocusNfeWebhooksController {
  async handle({ request, response }: HttpContext) {
    // Validar token secreto antes de processar — qualquer chamante com o reference pode
    // forçar transição de status sem essa verificação.
    // Configure FOCUSNFE_WEBHOOK_SECRET no env e passe-o como parâmetro de query/path ao
    // registrar a URL de callback na FocusNFe (ex: /api/webhooks/focusnfe?token=SECRET).
    const secret = env.get('FOCUSNFE_WEBHOOK_SECRET')
    const provided = request.qs().token ?? request.header('x-webhook-token') ?? ''
    if (!secret || provided !== secret) {
      return response.status(401).json({ error: 'Unauthorized' })
    }

    const payload = request.all()
    const { reference, status, caminho_xml_nota, caminho_pdf_nota } = payload

    // Um `return` dentro do callback da transação gerenciada apenas resolve o valor
    // da transação — NÃO retorna do método handle. Capture o resultado e ramifique DEPOIS.
    const result = await db.transaction(async (trx) => {
      const invoice = await Invoice.query()
        .useTransaction(trx)
        .where('nfseReferenceId', reference)
        .forUpdate()
        .first()

      if (!invoice) {
        return { status: 'not_found' as const }
      }

      // Evita reprocessamento se o status já for o mesmo
      if (invoice.nfseStatus === status) {
        return { status: 'duplicate' as const }
      }

      invoice.nfseStatus = status
      if (status === 'authorized') {
        invoice.nfseXmlUrl = caminho_xml_nota
        invoice.nfsePdfUrl = caminho_pdf_nota
      }

      await invoice.save()
      return { status: 'ok' as const }
    })

    if (result.status === 'not_found') {
      return response.notFound({ error: 'Invoice not found for reference' })
    }
    if (result.status === 'duplicate') {
      return response.ok({ message: 'Already processed' })
    }

    return response.ok({ received: true })
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Chamadas Síncronas**: Nunca realize requisições HTTP da API FocusNFe diretamente em controllers ou fluxos de requisição do usuário. Delegue sempre para workers do BullMQ executando em segundo plano.
- **Variáveis de Ambiente Estritas**: Não utilize `process.env` diretamente dentro dos arquivos. Importe e use `env.get()` configurado em `#start/env`.
- **Convenção de Chaves no Banco**: Mantenha a consistência com o restante do repositório; tabelas de faturas e de auditoria tributária devem usar **ULID** gerados de forma automática no hook `@beforeCreate()` da model.
- **Idempotência no Webhook**: Todos os manipuladores de webhook devem usar transações com travamento de linha (`forUpdate()`) para evitar concorrência e condições de corrida que corrompam os dados.
- **Alíquotas Não Hardcoded**: Alíquotas de tributos não devem ser embutidas em código estático. Devem ser parametrizadas nas faturas, carregadas dinamicamente de arquivos de configuração ou lidas do banco de dados.
