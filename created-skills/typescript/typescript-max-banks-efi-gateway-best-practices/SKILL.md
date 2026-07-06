---
name: typescript-max-banks-efi-gateway-best-practices
description: Use when designing, implementing, configuring, or debugging the Efí payment gateway (EfiGateway) inside the @maxvue/max-banks package. Triggers on files modifying EfiGateway code, managing Efí API client credentials (client_id/client_secret), setting up OAuth2/mTLS authentication, executing Pix charges (createPixCharge/getCharge) via Efí, and parsing Efí webhooks.
---

## Objetivo
Fornecer diretrizes estruturadas e melhores práticas para a integração do gateway de pagamento Efí (EfiGateway) dentro do pacote `@maxvue/max-banks`. Isso garante autenticação OAuth2/mTLS segura, abstração limpa do fluxo de Pix (`createPixCharge`/`getCharge`) e processamento resiliente de webhooks.

## Instruções

> **Convenção-alvo (não verificável no repositório atual):** O pacote `@maxvue/max-banks` e a classe `EfiGateway` são o **design-alvo** desta integração; eles ainda **não** existem em `/projects`. No monólito real (engeapp), a Efí é integrada exclusivamente pelo **SDK PHP** `efipay/sdk-php-apis-efi` (Laravel), não por um cliente Node/TypeScript. Portanto, nomes de arquivos, assinaturas de métodos e a interface `PaymentGateway` abaixo descrevem a convenção pretendida para o pacote Node — trate-os como alvo a seguir, não como fato já existente. As especificidades da **API HTTP da Efí** (endpoints, corpo, OAuth2/mTLS, webhooks) são fiéis à documentação oficial da Efí e valem independentemente da linguagem.

### 1. Configuração do Cliente de Baixo Nível (EfiHttpClient)
* **Certificado mTLS Obrigatório:** A API da Efí exige um certificado PKCS#12 (.p12) para todas as operações de Pix.
* **Injeção de Credenciais:** Injete `clientId`, `clientSecret` e certificados mTLS (caminho do arquivo `certificate` ou `certificateBuffer`) por meio do objeto de configuração. Nunca leia `process.env` diretamente.
* **Fluxo de Autenticação OAuth2:**
  - Gere um cabeçalho de autorização Basic codificando `${clientId}:${clientSecret}` em base64.
  - Realize um POST para `/oauth/token` enviando `{ grant_type: 'client_credentials' }` com o cabeçalho Basic e o agente mTLS configurado.
  - Armazene em cache o `access_token` e seu timestamp de expiração. Renove automaticamente o token 60 segundos antes de sua expiração real.
* **Isolamento do Cliente HTTP:** Construa requisições utilizando uma instância Axios/Fetch vinculada a um `https.Agent` customizado configurado com o certificado mTLS (opção `pfx`).

### 2. Implementação do EfiGateway (PaymentGateway)
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

> **Escopo (convenção-alvo, não confirmada em código):** Mantenha o `EfiGateway` restrito à superfície de **Pix**. A convenção pretendida é que a interface `PaymentGateway` declare somente `createPixCharge`, `getCharge` e `parseWebhook` e que `PaymentMethod` cubra apenas Pix nesta primeira versão. **Não** adicione API de cartão de crédito nem endpoints de plano/assinatura (`/v1/plan`, `/v1/subscription`, `payment_token`) ao gateway, e **não** modele assinaturas mapeando strings de status da Efí. Caso assinaturas venham a existir, a orientação de arquitetura é modelá-las por uma máquina de estados própria e orientada a eventos (nomes de arquivo, enum de status e transições ficam a critério da implementação real — os exemplos abaixo são sugestões, não nomes garantidos): estados como `incomplete`/`trialing`/`active`/`past_due`/`grace`/`canceled` e transições disparadas por eventos (`payment_confirmed`/`payment_failed`/`grace_expired`/`cancel`). Antes de assumir qualquer path ou identificador, verifique o código real do pacote quando ele existir.

### 3. Processamento e Validação de Webhooks
* **Fonte da Verdade:** Webhooks são a principal fonte da verdade para atualizações de status de transações.
* **Análise e Normalização:** Traduza os payloads de webhook da Efí em um `CanonicalWebhookEvent` usando uma `idempotencyKey` determinística igual ao `endToEndId` do Pix (com fallback para o `txid` e, na ausência de ambos, `'unknown'`) — **sem prefixo** (não use `efi:pix:` nem qualquer variante `efi:subscription:`; não há webhook de assinatura).
* **Segurança e Verificação:**
  - **mTLS na borda é o mecanismo primário/recomendado** de autenticação dos webhooks da Efí (o certificado cliente é validado no ingress/reverse-proxy antes de chegar à aplicação).
  - Como defesa em profundidade, valide adicionalmente as faixas de IP de origem (allowlist) e, se configurado, um token de cabeçalho compartilhado comparado de forma segura contra timing (comparação time-safe). Não há header HMAC por padrão.

### 4. Tratamento e Normalização de Erros
* Intercepte erros de resposta da API Efí e analise o payload de erro para lançar exceções padronizadas:
  - `401 Unauthorized` -> `AuthenticationError` (por exemplo, credenciais de cliente expiradas ou inválidas).
  - `400 Bad Request` com subcódigos Pix -> `InvalidPixPayloadError` (por exemplo, chave Pix inválida, txid expirado).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* Não acesse variáveis de ambiente de processo globais (`process.env`) dentro do código do cliente ou do gateway.
* Não utilize credenciais de API fixadas diretamente no código (hardcoded), as credenciais devem ser passadas dinamicamente.
* Nunca registre senhas brutas de certificados, segredos do cliente ou logs de payloads completos contendo detalhes confidenciais de clientes.
* Nunca tente contornar a lógica de renovação do token OAuth2; garanta que uma margem de tempo de segurança seja sempre utilizada.
