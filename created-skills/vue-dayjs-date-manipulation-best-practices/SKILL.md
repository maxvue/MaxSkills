---
name: vue-dayjs-date-manipulation-best-practices
description: Use when manipulating, formatting, parsing, or comparing dates and times in the Vue 3 frontend using Day.js. Triggers on date formatting, timezone handling, duration calculation, and date validation.
---

# Boas Práticas de Manipulação de Datas com Day.js no Vue 3

## Objetivo
Estabelecer diretrizes padrão, padrões de código e restrições para a execução segura, reativa e localizada de operações de data e hora no frontend Vue 3 do Engeapp utilizando a biblioteca Day.js. Isso garante consistência, evita desvios de fuso horário entre backend/frontend e fornece padrões de helpers comuns.

## Instruções

### 1. Inicialização Centralizada
A biblioteca Day.js é altamente modular e permite tree-shaking. Para usar recursos avançados (como timezone, formatos personalizados, durações), você deve carregar os plugins explicitamente.
Inicialize e configure o Day.js em um ponto de entrada central (ex: `resources/Vue/app.ts` ou um helper compartilhado `resources/Vue/Helpers/date.ts`):

```typescript
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import relativeTime from 'dayjs/plugin/relativeTime';
import duration from 'dayjs/plugin/duration';
import 'dayjs/locale/pt-br';

// Estende o Day.js com os plugins necessários
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(customParseFormat);
dayjs.extend(relativeTime);
dayjs.extend(duration);

// Define o idioma padrão para Português do Brasil
dayjs.locale('pt-br');

export default dayjs;
```

### 2. Formatos Padrão
Sempre use as seguintes strings de formato para representação visual no padrão brasileiro:
- **Apenas Data:** `DD/MM/YYYY` (ex: `20/06/2026`)
- **Apenas Hora:** `HH:mm` (ex: `14:30`)
- **Data e Hora:** `DD/MM/YYYY HH:mm` (ex: `20/06/2026 14:30`)
- **Formato do Banco de Dados / Payload de API:** `YYYY-MM-DD HH:mm:ss` (ex: `2026-06-20 14:30:00`)

### 3. Análise de Datas com Segurança (Parsing)
- **Strings Apenas com Data (Proteção de Fuso Horário)**:
  Ao analisar datas ISO padrão que não contêm informações de hora (ex: `'2026-06-20'`), os navegadores podem interpretá-las como fuso horário UTC. Converter essas datas para o horário local pode deslocar o dia para o dia anterior (ex: exibindo `19/06/2026` dependendo do fuso do usuário).
  *Padrão de Segurança*: Adicione `'T00:00:00'` antes de analisar, ou faça a análise com formato explícito:
  ```typescript
  // Evite
  const data = dayjs('2026-06-20'); // Pode sofrer desvio dependendo do fuso horário local

  // Recomendado
  const dataLocal = dayjs('2026-06-20' + 'T00:00:00');
  ```
- **Análise de Formatos Customizados**:
  Se receber strings de data em formatos personalizados (como `DD/MM/YYYY`), especifique o formato explicitamente usando o plugin `customParseFormat`:
  ```typescript
  const dataAnalisada = dayjs('20/06/2026', 'DD/MM/YYYY');
  ```

### 4. Fuso Horário (Timezones)
- **Conversão de Timezone**:
  Ao lidar com timestamps vindos de APIs backend (que tipicamente estão em UTC), analise-os em UTC e converta para o fuso horário local do usuário:
  ```typescript
  // Converte timestamp UTC da API para a representação do fuso horário local do usuário
  const horaLocal = dayjs.utc(apiTimestamp).local().format('DD/MM/YYYY HH:mm');
  ```
- **Preservação de Fuso Horário**:
  Se a aplicação exigir a execução de operações sob um fuso horário específico (ex: America/Sao_Paulo):
  ```typescript
  const horaSP = dayjs().tz('America/Sao_Paulo');
  ```

### 5. Utilitários Reativos de Datas (Vue 3 Composition API)
Ao criar composables ou propriedades computadas para formatar datas, encapsule a lógica do Day.js de forma reativa:

```typescript
import { computed, MaybeRefOrGetter, toValue } from 'vue';
import dayjs from 'dayjs';

/**
 * Formata reativamente uma data usando o Day.js
 * @param dateRef - Valor reativo da data (Date, string, timestamp, ou null)
 * @param formatStr - Formato de saída desejado (padrão: 'DD/MM/YYYY')
 */
export function useFormattedDate(
  dateRef: MaybeRefOrGetter<Date | string | number | null | undefined>,
  formatStr: string = 'DD/MM/YYYY'
) {
  return computed(() => {
    const val = toValue(dateRef);
    if (!val) return '';
    const parsed = dayjs(typeof val === 'string' && !val.includes('T') && !val.includes(' ') ? val + 'T00:00:00' : val);
    return parsed.isValid() ? parsed.format(formatStr) : '';
  });
}
```

### 6. Aritmética e Comparação de Datas
- **Cálculos**:
  ```typescript
  // Adiciona dias
  const proximaSemana = dayjs().add(7, 'day');
  // Diferença em dias
  const diferencaDias = dayjs('2026-06-30').diff(dayjs('2026-06-20'), 'day');
  ```
- **Comparação Segura**:
  Use `isBefore`, `isAfter`, ou `isSame` em vez de operadores matemáticos puros:
  ```typescript
  const expirado = dayjs().isAfter(dataVencimento);
  ```

## Restrições
- **Não Misture Bibliotecas**: Não importe Moment.js, date-fns ou Luxon. Mantenha toda a lógica de data da interface unificada usando Day.js ou os wrappers existentes em `@maxvue/max-use` (ex: `useDateFormat`, `useTimeAgo`).
- **Sem Mutação Global**: Evite modificar a configuração global do `dayjs` dentro de componentes. Mantenha as extensões e locales centralizados.
- **Sempre Valide**: Sempre execute `.isValid()` antes de exibir valores de entrada do usuário ou da API que foram analisados dinamicamente e que não têm garantia de ser uma data válida.
- **Garanta o Idioma pt-BR**: Ao calcular tempos relativos ou nomes de calendários, garanta que o locale esteja explicitamente definido como `pt-br`.
