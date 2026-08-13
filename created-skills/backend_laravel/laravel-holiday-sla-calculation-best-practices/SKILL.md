---
name: laravel-holiday-sla-calculation-best-practices
description: "Use when implementing or debugging SLA tracking, business-day calculations, or deadlines in Engeapp backend. Covers DatesHelper globals (addBusinessDays, isHoliday, isBusinessHours, businessMinutesBetween). Covers objectives and core workflows."
---
# Laravel Holiday & SLA Calculation Best Practices

## Objetivo
Estabelecer diretrizes sólidas e padrões de código consistentes para calcular dias úteis, prazos de SLA e gerenciar feriados nacionais e estaduais no backend Laravel do ecossistema Engeapp, especialmente para as homologações de projetos solares.

## Instruções

### 1. Usando os Helpers Globais de Data (DatesHelper)
Sempre prefira usar as funções helper globais definidas em `DatesHelper.php` em vez de reimplementar a lógica de cálculo de datas:
- **`addBusinessDays($data, $dias) : DateTime`**: Adiciona um número específico de dias úteis a uma data inicial, pulando automaticamente fins de semana e feriados. Retorna um `\DateTime` nativo (via `Carbon::toDate()`), não um objeto `Carbon` — se for encadear métodos Carbon (`->lt()`, `->diffInDays()`, etc.) no resultado, reenvolva com `Carbon::instance()`/`Carbon::parse()` antes.
- **`isHoliday(string|Carbon|int|null $date = null) : ?bool`**: Verifica se uma dada data é um feriado (nacional ou estadual). Aceita o argumento omitido (default: agora, resolvido via `Carbon::now()`) e pode retornar `null`. Também exposta como método estático `isHoliday()` via a trait `App\Traits\HasHoliday` em Models, e via o endpoint utilitário `Settings\DateController::businessDay` (calcula uma data futura/passada somando dias úteis).
- **`isBusinessHours($date, $after = 8, $before = 17, $interval = ['start' => 12, 'end' => 14]) : bool`**: Verifica se a data e a hora fornecidas caem dentro do horário comercial (segunda a sexta, excluindo o intervalo de almoço e os feriados).
- **`businessMinutesBetween($start, $end, $dayStart = '08:30', $dayEnd = '17:30', ...)`**: Calcula o número exato de minutos úteis entre dois timestamps, aplicando o timezone `America/Sao_Paulo`, pulando fins de semana, feriados e horários de almoço. Útil para auditar tempos exatos de resposta de API e de processos.

### 2. Verificação & Sincronização de Feriados (`HolidayService`)
Entenda como os feriados são buscados, cacheados e sincronizados:
- `HolidayService::isHoliday(Carbon $date)` verifica se a data existe na tabela do banco de dados mapeada por `App\Models\Address\Holiday`.
- Se não existirem registros para o ano da consulta, ele dispara uma chamada à API externa da Invertexto (`https://api.invertexto.com/v1/holidays/{year}`) filtrada pelo estado configurado via `INVERTEXTO_DEFAULT_STATE`. Atenção: `config/api.php` já define a chave `invertexto_default_state` com fallback `env('INVERTEXTO_DEFAULT_STATE', false)` — como a chave sempre existe (retorna `false`, não ausência), o segundo argumento `'go'` do `config('api.invertexto_default_state', 'go')` em `HolidayService.php` nunca é aplicado. Sem `INVERTEXTO_TOKEN`/`INVERTEXTO_DEFAULT_STATE` setadas no `.env` (não estão, no projeto atual), o token e o estado enviados à API são ambos `false`.
- **Estado real quando não configurado (sem token/seed):** sem token, a chamada HTTP falha e `fetchHolidays()` retorna `[]` — mas esse array vazio é gravado **dentro** do `Cache::rememberForever`, congelando a falha permanentemente para aquele ano. Como a tabela nunca é populada (`Holiday::upsert([])` com array vazio é no-op), `isHoliday()` sempre retorna `false`/`null` para anos não semeados manualmente, e `addBusinessDays()` acaba pulando apenas fins de semana. Não existe seeder de feriados no projeto. Trate a configuração de `INVERTEXTO_TOKEN`/`INVERTEXTO_DEFAULT_STATE` (ou o seeding manual da tabela `holidays`) como pré-requisito antes de confiar nesses helpers em produção.
- A resposta da API, quando bem-sucedida, é cacheada usando `Cache::rememberForever` e persistida via `upsert` no banco de dados.
- Qualquer validação manual ou seeding deve delegar ao `HolidayService`.

### 3. Implementando Regras de SLA para Homologação
As homologações de projetos solares junto às concessionárias de energia exigem rastreamento preciso de SLA:
- Ao calcular os prazos legais de resposta (ex.: Parecer de Acesso, que normalmente leva 15 dias úteis), calcule o prazo usando:
  ```php
  $deadline = addBusinessDays($submittalDate, 15);
  ```
- Para identificar tarefas atrasadas em queries no banco de dados, calcule a data limite em dias úteis usando o Carbon no PHP e compare-a com o horário atual, em vez de tentar uma lógica complexa de feriados em SQL bruto. Atenção: `addBusinessDays` retorna `\DateTime` nativo (não `Carbon`, veja seção 1) — envolva o retorno com `Carbon::instance()`/`Carbon::parse()` antes de encadear métodos de comparação Carbon.

### 4. Testando Cálculos de SLA
- Escreva testes unitários e de feature usando Pest.
- Sempre congele/mocke o horário atual do sistema nos testes usando `Carbon::setTestNow('2026-06-20 10:00:00')` para verificar as condições de fronteira (ex.: envios nas noites de sexta-feira, fins de semana, feriados ou viradas de ano).
- Verifique se `addBusinessDays` desloca a data corretamente ao longo de múltiplos feriados consecutivos (ex.: Carnaval ou Natal/Ano Novo).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **NÃO** escreva loops customizados (`while`) para pular fins de semana ou calcular dias úteis diretamente em Controllers ou Services. Use `addBusinessDays`.
- **NÃO** consulte a API da Invertexto diretamente a partir de services ou commands customizados. Todas as buscas de feriados devem passar pelo `HolidayService`.
- **NÃO** escreva feriados diretamente no banco de dados sem passar pelo `HolidayService`: `isHoliday()` consulta a tabela `Holiday` diretamente (o banco, não o cache, é a fonte de verdade da leitura); o `Cache::rememberForever` só entra em `fetchHolidays()`, quando o ano ainda não está no banco e é preciso buscar na API externa antes do `upsert`.
- **NÃO** use timezones diferentes de `'America/Sao_Paulo'` ao calcular minutos úteis ou horário comercial.
- **NÃO** use dias corridos para prazos legalmente definidos como dias úteis.
