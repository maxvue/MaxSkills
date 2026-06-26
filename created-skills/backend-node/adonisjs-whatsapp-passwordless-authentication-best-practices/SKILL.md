---
name: adonisjs-whatsapp-passwordless-authentication-best-practices
description: Use when implementing, configuring, reviewing, or debugging passwordless authentication flows via WhatsApp OTP in AdonisJS v6 using session auth (guard web), including generating secure codes, rate-limiting, sending messages via WhatsApp Cloud API, and validating logins.
---

# Melhores Práticas para Autenticação Sem Senha via WhatsApp no AdonisJS

## Objetivo
Estabelecer um fluxo de autenticação sem senha (passwordless) seguro, prático e robusto via One-Time Password (OTP) do WhatsApp no AdonisJS v6, garantindo alta proteção contra abusos/força bruta, rate limiting adequado e geração transparente de sessões de usuário (auth por sessão+cookie, guard `web`).

## Instruções

### 1. Geração de OTP Criptograficamente Segura
* Não utilize geradores de números aleatórios inseguros. Sempre use `randomInt` do módulo `node:crypto` para gerar um código de verificação numérico de 6 dígitos.
* Exemplo de geração de OTP:
  ```typescript
  import { randomInt } from 'node:crypto'

  export function generateOtp(): string {
    return randomInt(100000, 999999).toString()
  }
  ```

### 2. Armazenamento Temporário e Expiração Rápida (Redis)
* Armazene os OTPs gerados no Redis para acesso rápido, baixa latência e expiração automática.
* Use um prefixo de chave consistente, como `otp:phone_number`, e defina um tempo de vida (TTL) curto entre 5 a 10 minutos.
* Mantenha a chave simples e garanta que ela seja removida assim que validada (uso único).
* Exemplo de armazenamento de OTP:
  ```typescript
  import redis from '@adonisjs/redis/services/main'

  // Armazena o OTP com expiração de 5 minutos (300 segundos)
  await redis.setex(`otp:${phoneNumber}`, 300, otp)
  ```

### 3. Envio de WhatsApp Utilizando Serviço Dedicado
* Integre com o `WhatsAppService` (da skill `adonisjs-whatsapp-cloud-api-integration-best-practices`) para enviar o OTP.
* Sempre utilize um Template do WhatsApp registrado (ex: `auth_otp_code`) em vez de texto livre para garantir conformidade com os padrões comerciais da Meta e maior taxa de entrega.
* Exemplo de chamada de template:
  ```typescript
  import { WhatsAppService } from '#services/whatsapp_service'

  const whatsapp = new WhatsAppService()
  
  // Exemplo enviando componente de OTP dinâmico
  await whatsapp.sendTemplate(phoneNumber, 'auth_otp_code', 'pt_BR', [
    {
      type: 'body',
      parameters: [
        { type: 'text', text: otp }
      ]
    },
    {
      type: 'button',
      sub_type: 'url',
      index: '0',
      parameters: [
        { type: 'text', text: otp } // Se estiver usando o parâmetro de cópia de código no botão
      ]
    }
  ])
  ```

### 4. Rate Limiting para Rotas de Solicitação e Verificação
* Implemente rate limiting baseado em Redis (da skill `adonisjs-security-shield-rate-limiting-best-practices`) para evitar abusos na API, exaustão de tokens e tentativas de adivinhação por força bruta.
* Limite as solicitações de geração de OTP (ex: no máximo 3 requisições a cada 15 minutos por número de telefone/IP).
* Limite as solicitações de validação de OTP (ex: no máximo 5 tentativas a cada 15 minutos por IP/número de telefone).
* Registre os limitadores em `start/limiter.ts`:
  ```typescript
  import limiter from '@adonisjs/limiter/services/main'

  export const sendOtpLimiter = limiter.define('send_otp', (ctx) => {
    const phone = ctx.request.input('phone')
    return limiter
      .allowRequests(3)
      .every('15 mins')
      .usingKey(`send_otp_${phone}_${ctx.request.ip()}`)
  })

  export const verifyOtpLimiter = limiter.define('verify_otp', (ctx) => {
    const phone = ctx.request.input('phone')
    return limiter
      .allowRequests(5)
      .every('15 mins')
      .usingKey(`verify_otp_${phone}_${ctx.request.ip()}`)
  })
  ```

### 5. Controller de Verificação e Validação de Login
* Valide os parâmetros da requisição usando o VineJS. Normalize os números de telefone para o formato E.164.
* Verifique se o OTP existe no Redis e se coincide com o enviado.
* Remova o OTP imediatamente após a verificação bem-sucedida.
* Busque o usuário correspondente ao número de telefone.
  - Se o usuário existir: Autentique-o.
  - Se o usuário não existir: Inicie o fluxo de cadastro/onboarding ou crie a conta automaticamente (de acordo com os requisitos de negócio).
* Utilize o guard de sessão (`auth.use('web').login(user)`) para emitir a sessão. Esse é o modelo de auth padrão do projeto (sessão+cookie, sessões em DB, 30 dias). Access Tokens (OAT) só devem ser emitidos em cenários M2M/MCP, nunca como caminho padrão do login web.
* Exemplo de lógica do Controller de Validação de Login:
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'
  import redis from '@adonisjs/redis/services/main'
  import User from '#models/user'

  export default class AuthOtpController {
    async requestOtp({ request, response }: HttpContext) {
      const { phone } = request.only(['phone']) // validado via vine
      const otp = generateOtp()

      await redis.setex(`otp:${phone}`, 300, otp)
      await sendOtpViaWhatsApp(phone, otp) // integração com WhatsAppService

      return response.ok({ message: 'OTP enviado com sucesso.' })
    }

    async verifyOtp({ request, response, auth }: HttpContext) {
      const { phone, code } = request.only(['phone', 'code']) // validado via vine
      const cachedCode = await redis.get(`otp:${phone}`)

      if (!cachedCode || cachedCode !== code) {
        return response.badRequest({ errors: [{ message: 'Código de verificação inválido ou expirado.' }] })
      }

      // Consome o OTP - deleta-o do Redis
      await redis.del(`otp:${phone}`)

      // Recupera ou cria o usuário
      let user = await User.findBy('phone', phone)
      let isNewUser = false

      if (!user) {
        // Se for cadastro automático:
        user = await User.create({ phone })
        isNewUser = true
      }

      // Emite a sessão (modelo de auth padrão: guard `web`, sessão+cookie)
      await auth.use('web').login(user)

      // Apenas em cenários M2M/MCP (NÃO no login web padrão) emita um OAT:
      // const token = await User.accessTokens.create(user)

      return response.ok({
        message: 'Autenticado com sucesso.',
        isNewUser,
        user,
      })
    }
  }
  ```

## Restrições
* NÃO use o gerador padrão `Math.random()` para a criação do código. Sempre utilize inteiros aleatórios criptograficamente seguros.
* NÃO retorne o código OTP nas respostas HTTP (ex: no JSON de resposta de `requestOtp`). O OTP deve ser entregue EXCLUSIVAMENTE via WhatsApp.
* NÃO armazene os OTPs em tabelas de banco de dados sem um índice e uma limpeza/expiração automática e rápida via TTL (o uso do Redis é altamente recomendado sobre o banco de dados Lucid para OTPs temporários).
* NÃO permita tentativas infinitas de verificação de OTP. Sempre aplique um rate limiter estrito na rota de validação para mitigar ataques de força bruta.
* NÃO exponha se um número de telefone existe ou não em erros de verificação. Mantenha as respostas de erro idênticas ('Código de verificação inválido ou expirado.').
