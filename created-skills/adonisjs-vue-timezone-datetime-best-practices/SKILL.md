---
name: adonisjs-vue-timezone-datetime-best-practices
description: Use when handling timezone conversions, datetime formatting, scheduling future events (ex.: manutenções, visitas técnicas, geração de relatórios), or managing date calculations across the backend (AdonisJS with Luxon) and frontend (Vue 3 with Day.js). Triggers on datetime database storage, timezone settings per client/tenant, and datepicker formatting.
---

## Objetivo
Estabelecer diretrizes e padrões de código rigorosos para garantir a integridade e consistência de datas, horários e fusos horários (formatos IANA) entre o backend (AdonisJS com Luxon) e o frontend (Vue 3 com Day.js).

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

## 3. Manipulação e Exibição de Datas no Frontend (Vue 3 e Day.js)
* **Configuração:** O Day.js deve ser configurado com os plugins `utc` e `timezone` no ponto de entrada do frontend (ex: `app.ts` ou um arquivo utilitário de datas).
  ```typescript
  import dayjs from 'dayjs'
  import utc from 'dayjs/plugin/utc'
  import timezone from 'dayjs/plugin/timezone'

  dayjs.extend(utc)
  dayjs.extend(timezone)
  ```
* **Exibição Reativa:** Formate as datas em UTC recebidas da API para o fuso horário preferencial do cliente ao renderizar dentro de templates ou tabelas.
  ```vue
  <template>
    <span>{{ formatEventDate(event.scheduledAt, tenantTimezone) }}</span>
  </template>

  <script setup lang="ts">
  import dayjs from 'dayjs'

  // ex.: agendamento de manutenção/visita técnica numa usina fotovoltaica
  defineProps<{
    event: { scheduledAt: string }
    tenantTimezone: string
  }>()

  const formatEventDate = (dateStr: string, tz: string) => {
    return dayjs(dateStr).tz(tz).format('DD/MM/YYYY HH:mm')
  }
  </script>
  ```
* **Formatação de Seletores de Data (Datepicker) e Payloads:** Garanta que qualquer data e hora selecionada nos pickers do frontend seja convertida para uma string ISO 8601 em UTC (`.toISOString()`) antes de enviar para a API.

## Restrições
* **Sem Objetos Date Nativos do JS:** Nunca utilize o objeto bruto `new Date()` ou métodos nativos de data do JavaScript para formatação ou cálculos. Sempre prefira Luxon no backend e Day.js no frontend.
* **Sem offsets fixos (Hardcoded):** Não defina offsets fixos no código (ex: `-03:00`). Sempre utilize strings de fuso horário IANA (ex: `America/Sao_Paulo`) para lidar corretamente com mudanças de horário de verão (DST).
* **Sem Formatação no Backend:** Nunca formate datas como strings localizadas dentro dos controllers ou serviços do backend ao enviar respostas nas APIs. O backend deve responder apenas com strings ISO 8601 em UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`).
* **Sem Adivinhação de Fuso Horário:** Não tente adivinhar o fuso horário do usuário usando APIs locais do navegador (`Intl.DateTimeFormat().resolvedOptions().timeZone`) para fluxos críticos de agendamento. Sempre consulte e respeite a configuração de fuso horário armazenada no perfil do cliente/tenant.
