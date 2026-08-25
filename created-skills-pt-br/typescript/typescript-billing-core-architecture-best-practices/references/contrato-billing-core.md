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

Tabela de transições propostas (status atual + evento → status resultante):

| Status atual | Evento              | Status resultante |
|---------------|---------------------|--------------------|
| `incomplete`  | `payment_confirmed` | `active`           |
| `incomplete`  | `start_trial`       | `trialing`         |
| `trialing`    | `payment_confirmed` | `active`           |
| `active`      | `payment_failed`    | `past_due`         |
| `past_due`    | `payment_confirmed` | `active`           |
| `past_due`    | `grace_expired`     | `grace`            |
| qualquer não-`canceled` | `cancel`  | `canceled`         |

Auxiliares de transição:

- `canTransition(status, event): boolean` — valida se o par status+evento é legal
  segundo a tabela acima.
- `transition(status, event): SubscriptionStatus` — aplica a transição; lança
  `InvalidTransitionError` quando o par é inválido.
- `grantsAccess(status: SubscriptionStatus): boolean` — decide se o estado concede
  acesso. Regra proposta: `active`, `trialing`, `past_due` e `grace` concedem
  (a suspensão de fato só ocorre em `canceled`); `incomplete` e `canceled` não.

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
`CanonicalWebhookEvent` que carrega uma `idempotencyKey` única e determinística,
igual ao `endToEndId` do Pix, com fallback para o `txid` e, na ausência de
ambos, `'unknown'` — sem prefixo (mesma regra da skill irmã
`typescript-max-banks-efi-gateway-best-practices`). O consumidor usa essa
chave para processar cada evento uma única vez, evitando cobrança/crédito
duplicados.
