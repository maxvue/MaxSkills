---
name: typescript-billing-core-architecture-best-practices
description: "Use when designing, implementing, reviewing, or debugging a pure TypeScript zero-framework subscription billing engine: subscription state machine, decoupled payment gateway interface, canonical webhook parser, and idempotency. NOT for Engeapp payment integration (which runs on PHP/Laravel with efipay and inter-co SDKs)."
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Aplicar arquitetura limpa em TypeScript puro ao projetar um mecanismo de faturamento de assinaturas e gateways de pagamento como biblioteca dedicada, garantindo desacoplamento total de frameworks web e runtimes de front-end.

## Contexto no ecossistema (leia antes de assumir consumidor)
Esta skill descreve um PADRÃO de arquitetura para uma biblioteca de faturamento em TS puro. Ela NÃO reflete o estado atual do `engeapp`: nos projetos de referência (`engeapp`, `MaxComponentsUi`, `MaxPinia`, `MaxUse`) não existe hoje uma lib `billing-core`/`@maxvue/max-banks`.

No `engeapp` real, a integração de pagamentos é feita em PHP dentro do backend Laravel 13, não por uma lib TypeScript consumida pelo Laravel (PHP não importa TS). A verdade-base é:
* SDKs PHP declarados em `composer.json`: `efipay/sdk-php-apis-efi` (Efí/Gerencianet) e `inter-co/pj-sdk-php` (Banco Inter).
* Código PHP correspondente: `app/Http/Integrations/Efi/`, `app/Services/Bank/EfiPaymentStatus.php`, o job `app/Jobs/ProcessEfiWebhookJob.php`, o controller `app/Http/Controllers/Api/Bank/Efi/EfiPaymentExecute.php` e o comando `SyncEfiPaymentsStatusCommand`.
* A fila é processada com `laravel/horizon`.

Portanto, aplique esta skill quando estiver construindo uma biblioteca TS autônoma de faturamento. Para a lógica de pagamentos existente do `engeapp`, trabalhe em PHP/Laravel, não aqui.

## Instruções

### 1. Restrição de TypeScript Puro e Zero-Framework
* Toda a lógica central de faturamento deve residir em uma biblioteca TypeScript pura dedicada (por exemplo, `billing-core`).
* **Sem Importações de Frameworks:** nenhuma importação de framework web (`vue` ou qualquer runtime específico) nos pacotes `core` e `node`. A biblioteca deve ser agnóstica ao consumidor.
* **Sem Acesso a Variáveis de Ambiente:** dentro da biblioteca, nunca leia `process.env` nem use provedores de configuração globais. Configurações, certificados e credenciais devem ser injetados explicitamente pela aplicação consumidora no boot.

### 2. Separação de Arquitetura em Camadas
Garanta a divisão estrita de responsabilidade entre os diretórios da biblioteca:
* **`core/` (Camada Isomórfica):**
  - Totalmente isomórfica (Node, navegador, runtimes edge).
  - Sem APIs nativas do Node.js (`node:*`, `fs`, `path`, etc.) nem dependências (Axios/Fetch) que dependam de globais do Node.
  - Contém enums, tipos canônicos e a máquina de estados de assinaturas.
* **`node/` (Camada de Ambiente Node.js):**
  - Contém implementações que exigem APIs do Node.js (leitura de arquivos para certificados, cliente mTLS, operações criptográficas).
  - Implementa os clientes de gateway, adaptadores HTTP e verificação de assinatura de webhook.

### 3. Máquina de Estados de Assinatura
* Mantenha uma máquina de estados finitos para as transições de status, com auxiliares `canTransition`/`transition` que lancem `InvalidTransitionError` em transições inválidas, e `grantsAccess` para decidir acesso.
* Nunca atualize status "na mão": sempre passe pela função de transição para preservar o ciclo de vida válido, e nunca permita saída do estado terminal `canceled`.
* Estados e eventos propostos, além da regra do estado terminal `canceled`, estão em `references/contrato-billing-core.md`.

### 4. Abstração Desacoplada de Gateway de Pagamento
* Todas as integrações devem depender de uma interface única de gateway (`PaymentGateway`), com adaptadores concretos por provedor (ex.: `EfiGateway`, `InterGateway`) que não vazem tipos específicos do provedor.
* Valores financeiros sempre como inteiro em centavos (`Money`) para evitar erros de ponto flutuante.
* A assinatura completa da interface e do tipo `Money` está em `references/contrato-billing-core.md`.

### 5. Parser de Webhook e Idempotência
* Trate o evento de webhook como fonte da verdade para confirmações de pagamento.
* Use um parser (`parseWebhook`) para traduzir o payload do provedor para um evento canônico que carregue uma `idempotencyKey` determinística igual ao `endToEndId` do Pix, com fallback para o `txid` e, na ausência de ambos, `'unknown'` — sem prefixo (mesma regra da skill irmã `typescript-max-banks-efi-gateway-best-practices`).
* O backend consumidor deve processar cada evento consultando a `idempotencyKey`/ID de transação para evitar cobrança ou crédito duplicados. No `engeapp` real esse papel NÃO está implementado: o job `ProcessEfiWebhookJob` roda em PHP sobre a fila do Horizon, mas a única proteção contra reprocessamento hoje é o guarda `$payment->status !== 'paid'` — não há chave de idempotência persistida nem índice único na tabela `bank_webhooks`, e reprocessar o mesmo webhook duplica o histórico em `webhook_data_received`.

### 6. Testes Unitários Isolados
* Teste a lógica de `core` e as transições de forma totalmente isolada.
* Faça mock de todas as requisições HTTP e interfaces de rede.
* Não dependa de banco de dados, migrações ou variáveis de ambiente ativas durante os testes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), sem exceção, independentemente do idioma do corpo desta skill.
- **Comentários de código:** escreva comentários em pt-BR.
* Nunca importe provedores, models ou controllers de frameworks dentro da biblioteca.
* Nunca coloque credenciais de pagamento ou leitura de variáveis de ambiente hardcoded.
* Nunca ignore a máquina de estados ao atualizar status de assinatura.
* Nunca permita transições a partir do estado terminal `canceled`.
* Não afirme que o backend Laravel do `engeapp` consome esta biblioteca TS: a integração real de Efí e Banco Inter é feita em PHP via SDKs `efipay/sdk-php-apis-efi` e `inter-co/pj-sdk-php`.
