---
name: typescript-max-banks-efi-gateway-best-practices
description: Use when designing, implementing, configuring, or debugging the Efí payment gateway (EfiGateway) inside the @maxvue/max-banks package. Triggers on files modifying EfiGateway code, managing Efí API client credentials (client_id/client_secret), setting up OAuth2 authentication, executing Pix charges or credit card subscriptions via Efí, handling failed payments, and parsing Efí webhooks.
---

## Objetivo
Fornecer diretrizes estruturadas e melhores práticas para a integração do gateway de pagamento Efí (EfiGateway) dentro do pacote `@maxvue/max-banks`. Isso garante autenticação OAuth2/mTLS segura, abstração limpa dos fluxos de Pix e assinaturas de cartão de crédito, e processamento resiliente de webhooks.

## Instruções

## 1. Configuração do Cliente de Baixo Nível (EfiHttpClient)
* **Certificado mTLS Obrigatório:** A API da Efí exige um certificado PKCS#12 (.p12) para todas as operações de Pix.
* **Injeção de Credenciais:** Injete `clientId`, `clientSecret` e certificados mTLS (caminho do arquivo `certificate` ou `certificateBuffer`) por meio do objeto de configuração. Nunca leia `process.env` diretamente.
* **Fluxo de Autenticação OAuth2:**
  - Gere um cabeçalho de autorização Basic codificando `${clientId}:${clientSecret}` em base64.
  - Realize um POST para `/oauth/token` enviando `{ grant_type: 'client_credentials' }` com o cabeçalho Basic e o agente mTLS configurado.
  - Armazene em cache o `access_token` e seu timestamp de expiração. Renove automaticamente o token 60 segundos antes de sua expiração real.
* **Isolamento do Cliente HTTP:** Construa requisições utilizando uma instância Axios/Fetch vinculada a um `https.Agent` customizado configurado com o certificado mTLS (opção `pfx`).

## 2. Implementação do EfiGateway (PaymentGateway)
* Em conformidade estrita com a interface `PaymentGateway` do MaxBanks.
* **Representação Monetária Estrita:** Todos os valores monetários devem ser enviados e recebidos em centavos (valor inteiro). Converta os centavos para o formato decimal exigido pela API da Efí (por exemplo, `100` centavos é representado como a string `'1.00'`) dentro do adaptador.
* **Cobrança Imediata via Pix (`createPixCharge`):**
  - Caminho: `/v2/cob`
  - Estrutura do corpo:
    ```json
    {
      "calendario": { "expiracao": 3600 },
      "valor": { "original": "10.00" },
      "chave": "SUA_CHAVE_PIX",
      "devedor": {
        "cpf": "12345678909",
        "nome": "João da Silva"
      }
    }
    ```
  - Obtenha a imagem do QR code e o payload fazendo uma requisição GET para `/v2/loc/{locId}/qrcode`.
  - Exponha tanto a imagem do QR code codificada em base64 quanto a string bruta de "Copia e Cola EMV" (`pixCopiaECola`).

## 3. Gerenciamento de Cartão de Crédito e Assinaturas
* Para pagamentos com cartão de crédito e assinaturas recorrentes:
  - Utilize os tokens de pagamento gerados de forma segura no lado do cliente (nunca passe detalhes brutos do cartão diretamente pela API do seu backend).
  - Respeite o fluxo de assinaturas da Efí, que usa endpoints distintos e em ordem:
    - **Criar o plano:** `POST /v1/plan` (define nome, intervalo e repetições do ciclo). O plano é reutilizável entre assinantes.
    - **Criar a assinatura sobre o plano:** `POST /v1/plan/{id}/subscription` informando os `items` (valor em centavos) e os dados do cliente.
    - **Vincular o pagamento (cartão recorrente):** `POST /v1/subscription/{id}/pay` enviando o `payment_token` gerado no cliente e os dados de cobrança. É este passo que efetiva a recorrência no cartão.
    - **Cobranças avulsas (não recorrentes) de cartão:** use `POST /v1/charge` seguido de `POST /v1/charge/{id}/pay` com o `payment_token`.
  - Traduza os estados de assinatura da Efí para estados canônicos: `active`/`new` é mapeado para `active`, `unpaid`/`expired` é mapeado para `past_due` e `canceled` é mapeado para `canceled`.

## 4. Processamento e Validação de Webhooks
* **Fonte da Verdade:** Webhooks são a principal fonte da verdade para atualizações de status de transações.
* **Análise e Normalização:** Traduza os payloads de webhook da Efí em um `CanonicalWebhookEvent` usando uma `idempotencyKey` determinística formatada como `efi:pix:{txid}` ou `efi:subscription:{subscriptionId}`.
* **Segurança e Verificação:**
  - Webhooks da Efí devem ser validados verificando as faixas de IP de origem ou validando um token de cabeçalho customizado compartilhado durante o registro do webhook.

## 5. Tratamento e Normalização de Erros
* Intercepte erros de resposta da API Efí e analise o payload de erro para lançar exceções padronizadas:
  - `401 Unauthorized` -> `AuthenticationError` (por exemplo, credenciais de cliente expiradas ou inválidas).
  - `400 Bad Request` com subcódigos Pix -> `InvalidPixPayloadError` (por exemplo, chave Pix inválida, txid expirado).
  - Recusas de cartão de crédito -> `PaymentDeclinedError` com a mensagem específica fornecida pela Efí (por exemplo, saldo insuficiente, CVV incorreto).

## Restrições
* Não acesse variáveis de ambiente de processo globais (`process.env`) dentro do código do cliente ou do gateway.
* Não utilize credenciais de API fixadas diretamente no código (hardcoded), as credenciais devem ser passadas dinamicamente.
* Nunca registre senhas brutas de certificados, segredos do cliente ou logs de payloads completos contendo detalhes confidenciais de clientes.
* Nunca tente contornar a lógica de renovação do token OAuth2; garanta que uma margem de tempo de segurança seja sempre utilizada.
