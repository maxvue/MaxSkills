# Contrato de referência — billing-core em TypeScript puro

> Contrato ILUSTRATIVO de arquitetura. Estas assinaturas descrevem um design
> proposto para uma biblioteca de faturamento em TypeScript puro. Nenhum projeto
> de referência (`engeapp`, `MaxComponentsUi`, `MaxPinia`, `MaxUse`) contém hoje
> uma lib `billing-core`/`@maxvue/max-banks`, portanto os nomes e tipos abaixo
> NÃO estão validados contra código existente — trate-os como esqueleto a
> adaptar, não como API já publicada.

## Máquina de estados de assinatura

Status finitos (`SubscriptionStatus`):

- `incomplete` — pagamento inicial pendente.
- `trialing` — período de teste ativo.
- `active` — assinatura paga e vigente.
- `past_due` — falha no pagamento, em retentativa.
- `grace` — período de tolerância antes da suspensão.
- `canceled` — estado terminal (sem transições de saída).

Eventos (`SubscriptionEvent`): `start_trial`, `payment_confirmed`,
`payment_failed`, `grace_expired`, `cancel`.

Auxiliares de transição:

- `canTransition(status, event): boolean` — valida se o par status+evento é legal.
- `transition(status, event): SubscriptionStatus` — aplica a transição; lança
  `InvalidTransitionError` quando o par é inválido.
- `grantsAccess(status: SubscriptionStatus): boolean` — decide se o estado concede
  acesso. Regra proposta: `active`, `trialing` e `past_due` concedem; `grace`,
  `incomplete` e `canceled` não.

Nunca permita transição de saída a partir de `canceled`.

## Interface de gateway de pagamento

```typescript
export interface PaymentGateway {
    readonly name: string;
    createPixCharge(input: CreatePixChargeInput): Promise<Charge>;
    getCharge(txid: string): Promise<Charge>;
    parseWebhook(payload: unknown): CanonicalWebhookEvent;
}
```

Adaptadores concretos (ex.: `EfiGateway`, `InterGateway`) devem implementar essa
interface sem vazar tipos específicos do provedor para as camadas superiores.

## Representação monetária

Sempre inteiro em centavos, evitando ponto flutuante:

```typescript
export interface Money {
    amountCents: number;
    currency: 'BRL';
}
```

## Webhook canônico e idempotência

`parseWebhook` traduz o payload bruto de cada provedor para um
`CanonicalWebhookEvent` que carrega uma `idempotencyKey` única e determinística
(ex.: combinação de `txid` + `endToEndId`). O consumidor usa essa chave para
processar cada evento uma única vez, evitando cobrança/crédito duplicados.
