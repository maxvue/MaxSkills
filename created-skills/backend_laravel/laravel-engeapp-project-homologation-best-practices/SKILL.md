---
name: laravel-engeapp-project-homologation-best-practices
description: "Use when managing solar PV project homologation in Engeapp. Covers concessionaire regulations via ConcessionaireSubsidiaryRegulation, HasProtocol trait, Protocol::booted hook, and Vue SPA MaxPinia integration. Covers objectives and connection regulations."
author: Johnattas Conrady Gomes Santana
---
# Homologação de Projetos no EngeApp (Laravel + Vue)

## Objetivo
Padronizar o fluxo de homologação de projetos fotovoltaicos junto às concessionárias no engeapp: validar limites técnicos da concessionária, registrar e sincronizar protocolos entre projeto e card do planner, e expor tudo ao front-end respeitando o contrato MaxPinia/Ziggy do projeto.

## Instruções

### 1. Validação das normas técnicas da concessionária

Use o model `App\Models\Concessionaire\ConcessionaireSubsidiaryRegulation` (tabela `concessionaires_subsidiaries_regulations`) como fonte de verdade dos limites aceitos. Ele expõe seis atributos appended, um por combinação fase × tensão fase-neutro:

- `mono_127`, `mono_220` (1 fase)
- `bi_127`, `bi_220` (2 fases)
- `tri_127`, `tri_220` (3 fases)

Cada atributo retorna um **array de combinações** (não um escalar), lido de `ConcessionaireSubsidiaryRegulationData` (`concessionaires_subsidiaries_regulations_data`). Cada linha traz `circuit_breaker` (disjuntor, A), `wire_phase`/`wire_neutral`/`wire_ground` (bitolas, mm²) e `maximum_load`. Itere para validar o dimensionamento antes de despachar o envio:

```php
$regulation = ConcessionaireSubsidiaryRegulation::findOrFail($id);

// Ex.: rede monofásica 127V — array de opções disjuntor↔cabo aceitas.
$permitido = collect($regulation->mono_127)->contains(
    fn (array $limite) => $limite['circuit_breaker'] >= $disjuntorProjetado
        && $limite['wire_phase'] >= $bitolaFaseProjetada,
);

if (! $permitido) {
    // Bloqueie o envio: o projeto viola a norma vigente.
}
```

Prefira `$regulation->mono_127` (atributo) a consultar `data` cru — o atributo já filtra `amount_phases` e `voltage_phase_neutral`. O model já declara `protected $with = ['data']` (eager por padrão), então não é preciso encadear `with('data')` manualmente; note ainda que os atributos appended fazem sua própria query filtrada (`$this->data()->where(...)->get()`) e não reaproveitam a relação eager-loaded. **Nunca** deixe um projeto seguir para envio violando a `ConcessionaireSubsidiaryRegulation` selecionada para a filial/classe do projeto (a tabela não tem coluna de vigência/status — a norma correta é obtida por filial + `class`/`regulation_code`, não por uma flag de "ativa").

### 2. Ciclo de vida e sincronização do protocolo

Toda interação com a concessionária gera um `App\Models\Protocol\Protocol`. Models que se associam a protocolos usam a trait `App\Traits\HasProtocol` (ex.: `Project`, `PlannerCard`).

Entenda com precisão a **divisão de responsabilidades** — este é o ponto que mais gera erro:

- **Criação:** `HasProtocol::setProtocol($data)` cria o protocolo e o compartilha com os models contraparte via `protocolCounterparts()` (sobrescrito em `Project` → card e `PlannerCard` → projeto). O método **retorna `null`** se faltar qualquer chave obrigatória: `department`, `occurrence_at`, `description`.

  ```php
  $card->setProtocol([
      'department'    => 'concessionair_web',
      'occurrence_at' => now(),
      'description'   => 'Projeto enviado para análise da concessionária.',
      // opcionais: protocol, expires_at, notify_client, notify_designer, notify_solar_company...
  ]);
  ```

  `department` é vocabulário controlado (não é texto livre): os valores aceitos são `internal_affairs`, `concessionair_web`, `concessionair_phone`, `concessionair_email`, `concessionair_internal_affairs`, `reclame_aqui`, `procon`, `Consumidor.gov`, `aneel`, `juridical`, `other` (ver `list_department_protocol` em `ListCardDialogProtocols.vue`). Um valor fora dessa lista fica sem label/ícone na UI.

- **Edições:** a sincronização de **atualizações** NÃO passa por `setProtocol()`. Ela é feita pelo hook `static::saved` em `Protocol::booted()`, que a cada save re-anexa o protocolo aos dois lados (`syncWithoutDetaching`) e chama `updateExpiresAt()` no card. O hook `static::deleted` recalcula os prazos ao remover.

Não reimplemente essa sincronização manualmente nos controllers — deixe a trait cobrir a criação e o `booted()` cobrir as edições/remoções.

Para prazos: o campo `expires_at` do `Protocol` alimenta `PlannerCard::updateExpiresAt()`, e esse recálculo **já é automático** — o hook `Protocol::booted()` chama `updateExpiresAt()` tanto em `static::saved` quanto em `static::deleted`. Também já existe reprocessamento em lote: `php artisan planner:update-expires-at` (`App\Console\Commands\UpdatePlannerCardExpiresAtCommand`, hoje sem agendamento registrado). Não crie um novo job/scheduler para recalcular `expires_at` — o único gap real é o *alerta* de prazo iminente (notificar antes do vencimento), que de fato não existe hoje.

### 3. Onde colocar a lógica de homologação

Não coloque validação de norma nem persistência dentro de controllers. O engeapp organiza regras de negócio na camada `app/Services` (ex.: `Services/Project`, `Services/Signature`).

> **Não existe hoje um `HomologationService` no projeto.** Se a lógica de homologação crescer, crie um service dedicado seguindo o padrão existente da pasta `Services/`. Não importe nem chame `HomologationService` como se já existisse.

Um service de homologação deveria orquestrar:
1. Validar os inputs técnicos contra a `ConcessionaireSubsidiaryRegulation` selecionada (seção 1).
2. Verificar documentos obrigatórios (ex.: procuração via `ProjectPowerOfAttorneyDocument`).
3. Criar o `Protocol` via `setProtocol()` no `Project`/`PlannerCard` (seção 2).
4. Respeitar as flags de notificação (`notify_client`, `notify_designer`, `notify_solar_company`) e delegar o envio a Jobs assíncronos.

### 4. Exposição ao front-end (Vue 3 SPA)

O front é uma SPA Vue 3 com Vue Router; siga o contrato do ecossistema Max e Ziggy:

- **Todo GET passa por uma store MaxPinia** (`@maxvue/max-pinia`) — nunca busque dados direto no componente. As `options` da store recebem rotas em `get.route`/`save` e uma `key`; o status vem de `status.server.get.is_success`/`is_requested`.
- **Rotas são NOMES Ziggy pontilhados** (Ziggy está configurado), resolvidos por `apiGetRoute`/`apiPostRoute` de `@maxvue/max-use`. Nunca monte strings `/api/...` à mão.
- **Sem inputs/selects/buttons nativos** e sem vueuse/lodash/PrimeVue crus: use os componentes `Max*` de `@maxvue/max-components-ui` (formulários, upload, indicadores de status) e os composables de `@maxvue/max-use` para reatividade, datas e validação.
- Não há camada `services/` no front — o transporte fica na store.
- Comentários de código em pt-BR.

## Restrições
- **Idioma:** comunique-se com o humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
