---
name: vue-dayjs-date-manipulation-best-practices
description: "Use when formatting, parsing, or comparing dates and times in Vue 3 with Day.js. Covers @maxvue/max-use composables (useDateFormat, useTimeAgo), timezones, durations, and strict parsing."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Manipulação de Datas com Day.js no Vue 3

> **Prefira as composables do `@maxvue/max-use` para datas.** O `dayjs ^1.11.21` está no `package.json` do EngeApp, mas para formatação e tempo relativo a via padrão do frontend é `useDateFormat` e `useTimeAgo` de `@maxvue/max-use` (wrappers seguros do VueUse, já com fallback e locale pt-BR). Use o Day.js **diretamente** apenas quando precisar de recursos avançados (timezone, durations, parsing estrito) que essas composables não cobrem.

## Objetivo
Estabelecer padrões seguros, reativos e localizados para operações de data/hora no frontend Vue 3 do EngeApp, evitando desvios de fuso entre backend e frontend e garantindo consistência de formato pt-BR.

## Estado atual no projeto (verdade-base)
- **Não existe inicialização centralizada de Day.js.** O `resources/app.ts` não importa `dayjs`, e não há `dayjs.extend(...)`, `dayjs/plugin/*` nem `dayjs/locale/pt-br` em `resources/`.
- O único uso real de Day.js hoje é **direto dentro de um componente** — `resources/Vue/Pages/AdminCompaniesPage.vue` faz `import dayjs from 'dayjs'` e `dayjs(value).format('DD/MM/YYYY HH:mm')`, sem plugins nem locale.
- Antes de escrever formatação nova com Day.js, verifique se `useDateFormat`/`useTimeAgo` de `@maxvue/max-use` já resolvem — na maioria dos casos resolvem.
- Para aritmética e comparação de datas, a via real do projeto também já são os helpers de `@maxvue/max-use` (ex: `isSameDay` em `resources/Stores/calendar/useSocialMediaAgent.Store.ts`), não Day.js cru.

## Instruções

### 1. Formatação simples e tempo relativo — use @maxvue/max-use
Para exibir datas ou tempo relativo, use as composables existentes em vez de embrulhar o Day.js manualmente. Elas já tratam valor nulo/inválido e retornam objeto reativo.

```typescript
import { useDateFormat, useTimeAgo } from '@maxvue/max-use';

const dataFormatada = useDateFormat('2026-05-24', 'DD/MM/YYYY'); // → '24/05/2026'
const comHora = useDateFormat(new Date(), 'DD/MM/YYYY HH:mm');    // → '24/05/2026 14:30'
const relativo = useTimeAgo(algumaData, 'abbrev');                // → '2 dias', '4h'...
```

`useDateFormat` aceita `Date | number | string | null | undefined` (inclusive refs/getters) e, se o valor for `null`/`undefined`, faz fallback para a data atual. Esse fallback **não** cobre strings/valores malformados (ex: `''`, `'abc'`, `'0000-00-00'`): eles não são `null`/`undefined`, então passam direto para o VueUse e podem renderizar `'Invalid Date'`. O wrapper não substitui a validação de conteúdo de string vinda de API/usuário — veja a Restrição "Sempre valide".

### 2. Formatos Padrão
Ao formatar (via `useDateFormat` ou Day.js), use sempre as strings de formato brasileiras:
- **Apenas Data:** `DD/MM/YYYY` (ex: `20/06/2026`)
- **Apenas Hora:** `HH:mm` (ex: `14:30`)
- **Data e Hora:** `DD/MM/YYYY HH:mm` (ex: `20/06/2026 14:30`)
- **Payload de API / Banco:** `YYYY-MM-DD HH:mm:ss` (ex: `2026-06-20 14:30:00`)

### 3. Extensão de plugins do Day.js (só quando necessário)
Day.js é modular: recursos como `utc`, `timezone`, `customParseFormat`, `relativeTime` e `duration` exigem carregar o plugin com `dayjs.extend(...)` **antes** do uso. Como o projeto ainda não tem inicialização central, você tem duas opções ao precisar desses recursos:

1. **Preferível:** criar um helper compartilhado em `resources/Helpers/` (o diretório real de helpers do EngeApp — note o `H` maiúsculo; **não existe** `resources/js/`) que estende e exporta o Day.js, e importar sempre desse helper:

```typescript
// resources/Helpers/dayjs.ts
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import 'dayjs/locale/pt-br';

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(customParseFormat);
dayjs.locale('pt-br');

export default dayjs;
```

2. Se for um caso isolado (como o `AdminCompaniesPage.vue` atual), pode estender no próprio módulo — mas centralize assim que um segundo componente precisar do mesmo plugin, para não repetir `extend`/locale.

### 4. Parsing Seguro
- **Strings só com data (proteção de fuso):** ao parsear datas ISO sem hora (ex: `'2026-06-20'`), o navegador pode interpretá-las como UTC e deslocar o dia. Anexe `'T00:00:00'` para forçar horário local:
  ```typescript
  // Evite
  const data = dayjs('2026-06-20'); // pode deslocar o dia conforme o fuso

  // Recomendado
  const dataLocal = dayjs('2026-06-20' + 'T00:00:00');
  ```
- **Formatos customizados:** para strings como `DD/MM/YYYY`, informe o formato explícito (requer o plugin `customParseFormat` estendido):
  ```typescript
  const dataAnalisada = dayjs('20/06/2026', 'DD/MM/YYYY');
  ```

### 5. Fuso Horário (requer plugins utc + timezone estendidos)
- **Converter UTC da API para o local do usuário:**
  ```typescript
  const horaLocal = dayjs.utc(apiTimestamp).local().format('DD/MM/YYYY HH:mm');
  ```
- **Fixar um fuso específico:**
  ```typescript
  const horaSP = dayjs().tz('America/Sao_Paulo');
  ```

### 6. Aritmética e Comparação — prefira os helpers de @maxvue/max-use
Para cálculos e comparações de data, use primeiro os helpers auto-importados de `@maxvue/max-use` em vez de Day.js cru:

```typescript
const proximaSemana = addTime(dataBase, 7, 'days');           // Date | null
const diferencaDias = diffInDays(dataInicio, dataFim);        // valor ABSOLUTO
const jaPassou = isPast(dataVencimento);
const eFuturo = isFuture(dataVencimento);
const mesmoDia = isSameDay([dataSelecionada, dataInicio, dataFim]); // recebe array de datas
const noPeriodo = inDateInterval(data, inicio, fim);
const passouHoras = hasPassedHours(data, 24);
const relativo = timeAgo(data, 'abbrev');
```

- Todos aceitam `MaybeRefOrGetter<string | number | Date | null | undefined>` (refs/getters funcionam direto).
- `diffInDays`/`diffInHours`/`diffInMinutes` (e afins) retornam sempre a diferença **absoluta**, nunca negativa — não use o sinal do resultado para saber qual data é maior; use `isPast`/`isFuture`/`isSameDay` para isso.
- `addTime` retorna `Date | null` (null se a data base for inválida).
- Recorra ao Day.js cru (`.add`, `.diff`, `.isBefore`, `.isAfter`, `.isSame`) só para o que esses helpers não cobrem (timezone, durations, parsing estrito).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
- **Comentários de código em pt-BR.**
- **Prefira `@maxvue/max-use`:** não crie composables novos embrulhando Day.js para formatação/tempo relativo — `useDateFormat` e `useTimeAgo` já cumprem esse papel. Recorra ao Day.js direto só para o que elas não cobrem.
- **Não misture bibliotecas:** nada de Moment.js, date-fns ou Luxon. Toda lógica de data no frontend fica em Day.js ou nos wrappers de `@maxvue/max-use`.
- **Sem mutação global dispersa:** ver seção 3.
- **Sempre valide:** rode `.isValid()` antes de exibir datas parseadas dinamicamente de entrada do usuário ou da API.
