---
name: adonisjs-vue-timezone-datetime-best-practices
description: Use when handling timezone conversions, datetime formatting, scheduling future events (ex.: manutenções, visitas técnicas, geração de relatórios), or managing date calculations across the backend (AdonisJS with Luxon) and frontend (Vue 3 with MaxUse date composables / Luxon). Triggers on datetime database storage, timezone settings per client/tenant, and datepicker formatting.
---

## Objetivo
Estabelecer diretrizes e padrões de código rigorosos para garantir a integridade e consistência de datas, horários e fusos horários (formatos IANA) entre o backend (AdonisJS com Luxon) e o frontend (Vue 3 usando os composables de data do MaxUse e/ou Luxon — que já é dependência do Maxdmin).

## Instruções

## 1. Banco de Dados e Lucid ORM (AdonisJS)
* **Armazenamento em UTC:** Armazene todos os valores de data e hora no PostgreSQL como `timestamp` ou `timestamp with time zone` (timestamptz) normalizados em UTC.
* **Colunas no Model:** Sempre decore os campos de data e hora nos Models do Lucid usando `@column.dateTime()` com a classe `DateTime` do Luxon.
* **Configuração de Conexão do Banco de Dados:** Certifique-se de que a configuração de conexão do driver do banco de dados (ex: em `config/database.ts`) esteja configurada para tratar a análise de datas em UTC ou dependa do ambiente de execução do Node.js configurado em UTC.
* **Timezone do Cliente/Tenant:** Salve o nome do fuso horário IANA preferencial (ex: `'America/Sao_Paulo'`, `'America/Manaus'`) como uma coluna de texto (ex: `timezone`) na tabela de configurações do cliente/tenant (ex: `Company` ou `Plant`/usina).

## 2. Parsing e Cálculos no Backend (Luxon)
* **Parsing Seguro:** Sempre faça o parsing das strings de data e hora vindas do frontend em UTC usando `DateTime.fromISO(value, { zone: 'utc' })` ou `DateTime.fromSQL(value, { zone: 'utc' })`.
* **Tarefas Agendadas e Jobs:** Ao agendar eventos (ex: jobs do BullMQ ou comandos de agendamento Ace) baseados no horário local do cliente:
  1. Recupere o fuso horário IANA preferencial do tenant no banco de dados.
  2. Faça o parsing da data/hora alvo dentro do contexto desse fuso horário.
  3. Converta o datetime localizado em UTC antes de salvá-lo ou calcular os atrasos de execução.
  ```typescript
  import { DateTime } from 'luxon'

  // Cálculo correto do horário alvo no fuso horário do tenant convertido para UTC
  const tenantTimezone = tenant.timezone // ex: 'America/Sao_Paulo'
  const localTarget = DateTime.fromISO(inputDateString, { zone: tenantTimezone })
  const utcTarget = localTarget.toUTC()
  ```

## 3. Manipulação e Exibição de Datas no Frontend (Vue 3 — MaxUse / Luxon)
> **Regra de stack:** o Maxdmin **não declara `dayjs`** como dependência (só `luxon`/`@types/luxon`; `dayjs` existe apenas como dependência transitiva do `@vueuse/core`). As House Rules proíbem importar libs de terceiros diretamente no frontend — a formatação de datas deve passar pelos composables do MaxUse (`@maxvue/max-use`) ou por Luxon para o trabalho de fuso horário.

* **Exibição simples (reativa):** Para formatar uma data para exibição, use o composable `useDateFormat` do MaxUse (wrapper reativo sobre o `useDateFormat` do vueuse), que retorna um ref formatado.
  ```typescript
  import { useDateFormat } from '@maxvue/max-use'

  const formatted = useDateFormat(event.scheduledAt, 'DD/MM/YYYY HH:mm')
  ```
  Para cálculos (adicionar tempo, comparar com agora, checar futuro/passado, horas decorridas) use os helpers de datas do MaxUse: `addTime`, `now`, `isFuture`, `isPast`, `hasPassedHours`, `diffInHours`, etc.

* **Conversão de fuso horário (IANA):** Como `useDateFormat` não recebe timezone, use **Luxon** (dependência do Maxdmin) para converter a data UTC da API para o fuso do tenant antes de exibir.
  ```vue
  <template>
    <span>{{ formatEventDate(event.scheduledAt, tenantTimezone) }}</span>
  </template>

  <script setup lang="ts">
  import { DateTime } from 'luxon'

  // ex.: agendamento de manutenção/visita técnica numa usina fotovoltaica
  defineProps<{
    event: { scheduledAt: string }
    tenantTimezone: string
  }>()

  const formatEventDate = (dateStr: string, tz: string) => {
    return DateTime.fromISO(dateStr, { zone: 'utc' }).setZone(tz).toFormat('dd/MM/yyyy HH:mm')
  }
  </script>
  ```
* **Formatação de Seletores de Data (Datepicker) e Payloads:** Garanta que qualquer data e hora selecionada nos pickers do frontend seja convertida para uma string ISO 8601 em UTC (`.toISOString()`) antes de enviar para a API.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Sem Objetos Date Nativos do JS:** Nunca utilize o objeto bruto `new Date()` ou métodos nativos de data do JavaScript para formatação ou cálculos. Sempre prefira Luxon no backend e os composables/helpers de data do MaxUse (ou Luxon, para fuso horário) no frontend. Não importe `dayjs` diretamente — ele não é dependência declarada do Maxdmin.
* **Sem offsets fixos (Hardcoded):** Não defina offsets fixos no código (ex: `-03:00`). Sempre utilize strings de fuso horário IANA (ex: `America/Sao_Paulo`) para lidar corretamente com mudanças de horário de verão (DST).
* **Sem Formatação no Backend:** Nunca formate datas como strings localizadas dentro dos controllers ou serviços do backend ao enviar respostas nas APIs. O backend deve responder apenas com strings ISO 8601 em UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`).
* **Sem Adivinhação de Fuso Horário:** Não tente adivinhar o fuso horário do usuário usando APIs locais do navegador (`Intl.DateTimeFormat().resolvedOptions().timeZone`) para fluxos críticos de agendamento. Sempre consulte e respeite a configuração de fuso horário armazenada no perfil do cliente/tenant.
