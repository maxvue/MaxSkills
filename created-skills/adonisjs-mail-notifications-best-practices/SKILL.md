---
name: adonisjs-mail-notifications-best-practices
description: Use when configuring, creating, sending, or debugging transactional emails and notifications in an AdonisJS ecosystem. Triggers on mail configuration, mail templates, SMTP/SES/Resend drivers, and queues integration for mails in Node.js.
---

# Melhores Práticas para Envio de E-mails e Notificações no AdonisJS

## Objetivo
Estabelecer convenções e padrões rígidos para configuração, design, envio e depuração de e-mails transacionais e notificações no framework AdonisJS v6, utilizando o pacote oficial `@adonisjs/mail`, templates Edge.js, tratamento consistente de logs e processamento assíncrono via filas (BullMQ).

## Instruções

### 1. Configuração do Projeto e Provedores (Drivers)
* **Arquivo de Configuração (`config/mail.ts`):** Garanta que o serviço de e-mail seja configurado utilizando o helper `defineConfig` de `@adonisjs/mail`.
* **Variáveis de Ambiente (`start/env.ts`):** Sempre valide as variáveis relacionadas ao envio de e-mails (ex: `MAIL_MAILER`, `SMTP_HOST`, `SMTP_PORT`, `RESEND_API_KEY`) para evitar falhas em tempo de execução. Use `Env.schema.enum(['smtp', 'resend'])` para `MAIL_MAILER` de modo que o valor coincida sempre com uma chave de `mailers`.
* **Seleção do Driver:** Use drivers como SMTP, SES ou Resend em ambientes de produção, e drivers como `memory` ou `ethereal` para testes e desenvolvimento local a fim de evitar o envio de e-mails reais.

Exemplo de configuração (`config/mail.ts`):
```typescript
import env from '#start/env'
import { defineConfig, drivers } from '@adonisjs/mail'

const mailConfig = defineConfig({
  // `default` deve ser uma das chaves de `mailers` (ex.: 'smtp' | 'resend').
  // Valide MAIL_MAILER em start/env.ts com Env.schema.enum(['smtp', 'resend']).
  default: env.get('MAIL_MAILER', 'smtp'),
  mailers: {
    smtp: drivers.smtp({
      host: env.get('SMTP_HOST'),
      port: env.get('SMTP_PORT'),
      secure: false,
      auth: {
        type: 'login',
        user: env.get('SMTP_USERNAME'),
        pass: env.get('SMTP_PASSWORD'),
      },
    }),
    resend: drivers.resend({
      key: env.get('RESEND_API_KEY'),
    }),
  },
})

export default mailConfig
```

### 2. Criação de Mailers (`BaseMail`)
* **Scaffolding:** Sempre crie classes Mailer através do comando Ace:
  ```bash
  node ace make:mail <MailerName>
  ```
  Isso gera o mailer na pasta `app/mails/<mailer_name>.ts` (mapeada no subcaminho `#mails/*`).
* **Padrão de Design:** Evite realizar consultas pesadas no banco de dados dentro do construtor do Mailer. Em vez disso, busque os dados no controller ou job e passe as instâncias de models já resolvidas ao construtor.
* **Propriedades no Construtor:** Use a funcionalidade de promoção de propriedades de construtor do TypeScript para uma declaração limpa de parâmetros.

Exemplo de Mailer (`app/mails/welcome_email.ts`):
```typescript
import { BaseMail } from '@adonisjs/mail'
import User from '#models/user'

export default class WelcomeEmail extends BaseMail {
  subject = 'Seja bem-vindo ao Engeapp!'

  constructor(private user: User) {
    super()
  }

  prepare() {
    this.message
      .to(this.user.email)
      .from('no-reply@engeapp.com.br', 'Equipe Engeapp')
      .htmlView('emails/welcome', { user: this.user })
  }
}
```

### 3. Criação de Templates de E-mail HTML (Edge.js)
* **Estrutura de Diretórios:** Salve os templates de e-mail em `resources/views/emails/`.
* **Estrutura do HTML/CSS:** Mantenha os layouts simples, baseados em tabelas ou CSS leve inline. Clientes de e-mail comuns não possuem suporte completo a recursos modernos como CSS Grid, Flexbox ou utilitários do UnoCSS.
* **Compatibilidade:** Utilize marcações limpas e fontes do sistema para garantir compatibilidade entre leitores de e-mail como Outlook e Gmail.

Exemplo de Template (`resources/views/emails/welcome.edge`):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Bem-vindo ao Engeapp</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border: 1px solid #dddddd; padding: 30px;">
    <tr>
      <td>
        <h1 style="color: #333333;">Olá, {{ user.fullName }}!</h1>
        <p style="color: #666666; line-height: 1.5;">
          Obrigado por se cadastrar no Engeapp. Estamos muito felizes em ter você conosco!
        </p>
      </td>
    </tr>
  </table>
</body>
</html>
```

### 4. Processamento Assíncrono com Filas (Integração com BullMQ)
* **Nunca envie e-mails de forma síncrona dentro de requisições HTTP.** Isso aumenta a latência da resposta e expõe o servidor a timeouts de conexão SMTP.
* **Delegação para Fila:** Crie um Job dedicado em background para processar e disparar os e-mails.

Exemplo de Job (`app/jobs/send_email_job.ts`):
```typescript
import { Job } from 'bullmq'
import mail from '@adonisjs/mail/services/main'
import WelcomeEmail from '#mails/welcome_email'
import User from '#models/user'

export interface SendEmailPayload {
  userId: number
}

export default class SendEmailJob {
  static readonly queueName = 'emails'

  static async handle(job: Job<SendEmailPayload>) {
    const { userId } = job.data
    const user = await User.find(userId)

    if (!user) {
      throw new Error(`Usuário com ID ${userId} não encontrado para envio do e-mail.`)
    }

    // Envio utilizando a instância do Mailer
    await mail.send(new WelcomeEmail(user))
  }
}
```

### 5. Resiliência, Tratamento de Erros e Logs
* **Geração de Logs:** Envolva o disparo dos e-mails com blocos try/catch e utilize o serviço de logger oficial do AdonisJS.
* **Tentativas Automáticas:** Configure tentativas de reenvio com atraso exponencial (exponential backoff) no gerenciador de filas (BullMQ) para lidar com quedas temporárias de rede ou do provedor SMTP.

```typescript
import logger from '@adonisjs/core/services/logger'

try {
  await mail.send(new WelcomeEmail(user))
} catch (error) {
  logger.error({ error, userId: user.id }, 'Falha ao enviar e-mail de boas-vindas')
  throw error // Relance o erro para que o BullMQ realize a tentativa de reenvio
}
```

## Restrições
* **NÃO** escreva HTML inline como string dentro de `BaseMail`. Use sempre templates do Edge.js (`.edge`) localizados em `resources/views/emails/` para manter a organização visual do código.
* **NÃO** bloqueie o processo do HTTP realizando requisições de e-mail de forma síncrona. Use filas do `BullMQ` ou filas nativas do AdonisJS.
* **NÃO** armazene chaves de API ou credenciais de e-mail diretamente no código. Carregue-as sempre a partir do arquivo `.env` e faça a validação no `start/env.ts`.
