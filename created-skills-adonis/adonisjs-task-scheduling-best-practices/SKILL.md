---
name: adonisjs-task-scheduling-best-practices
description: Use when designing, creating, editing, or debugging periodic background tasks, cron jobs, task schedulers, or running persistent Ace Commands with loop intervals (like scheduler:run) in AdonisJS. Triggers on cron expressions, setInterval schedulers, and graceful process shutdowns.
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas para Agendamento de Tarefas no AdonisJS

## Objetivo
Estabelecer diretrizes de codificação, padrões de arquitetura e padrões de implementação para o agendamento e a execução resiliente de tarefas em segundo plano ou periódicas em aplicações AdonisJS v6, sem depender de ferramentas externas pesadas de terceiros quando um loop interno limpo do Node.js com tratamento de sinais do sistema operacional é suficiente.

## Instruções

### 1. Criando o Comando Ace
* Sempre use o gerador de comandos Ace do AdonisJS para criar um comando de agendamento dedicado:
  ```bash
  node ace make:command scheduler/run
  ```
* Defina um nome e descrição descritivos para o comando:
  ```typescript
  static commandName = 'scheduler:run'
  static description = 'Executa tarefas de agendamento periódicas em segundo plano'
  ```
* Sempre ative a inicialização completa do framework e mantenha o processo vivo definindo `static options: CommandOptions = { startApp: true, staysAlive: true }` (importe o tipo com `import type { CommandOptions } from '@adonisjs/core/types/ace'`). `startApp` é necessário para acessar Models do Lucid, serviços, configs e o container de IoC; `staysAlive` é a flag documentada pelo framework que impede a aplicação de terminar após o retorno de `run()` num comando de longa duração.

### 2. Implementando Loops de Intervalo
* Defina funções de execução assíncronas distintas dentro do método `run` para cada tarefa agendada (ex: `publishDueEvents`, `fetchNews`).
* Envolva toda a execução de cada função em um bloco `try/catch`. Exceções não tratadas dentro de timers podem derrubar todo o processo Node.js.
* Agende a execução usando `setInterval(workerFunction, intervalInMs)`.
* Mantenha a thread principal responsiva, liberando o fluxo com operações assíncronas não bloqueantes.

### 3. Encerramento Gracioso (Graceful Shutdown) e Resiliência
* Um processo scheduler precisa liberar recursos de forma limpa quando for finalizado, reiniciado ou durante novos deploys.
* Mantenha o processo vivo com `staysAlive: true` nas `options` do comando — não dependa de uma `new Promise<void>` infinita para bloquear o retorno de `run()`.
* Registre a limpeza dos timers com `this.app.terminating(() => { ... })`. O AdonisJS invoca esse hook ao encerrar (incluindo nos sinais `SIGTERM`/`SIGINT`), então limpe todos os intervalos ativos com `clearInterval()` ali dentro.

### 4. Integração com Filas
* Para tarefas pesadas ou com duração variável, não execute a lógica de negócios diretamente dentro do loop do scheduler.
* Em vez disso, use o scheduler apenas para consultar trabalhos pendentes e despachá-los para um sistema de filas como o BullMQ.
* Isso separa o disparo das tarefas (agendamento) de sua execução (carga de trabalho), mantendo o processo do scheduler leve.

## Examples

### Padrão de Comando Scheduler Resiliente
Abaixo está a estrutura padrão para um comando scheduler robusto e persistente no AdonisJS v6:

```typescript
import { BaseCommand } from '@adonisjs/core/ace'
import type { CommandOptions } from '@adonisjs/core/types/ace'
import { DateTime } from 'luxon'
import CalendarEvent from '#models/calendar/event'
import PublishEventJob from '#jobs/publish_event_job'
import FetchNewsJob from '#jobs/fetch_news_job'

export default class SchedulerRun extends BaseCommand {
  static commandName = 'scheduler:run'
  static description = 'Executa tarefas periódicas em segundo plano com encerramento gracioso'
  static options: CommandOptions = { startApp: true, staysAlive: true }

  async run() {
    this.logger.info('Scheduler iniciado')

    // 1. Definição de funções executoras isoladas e seguras
    const publishDue = async () => {
      try {
        const now = DateTime.now().toSQL()!
        const events = await CalendarEvent.query()
          .where('status', 'scheduled')
          .where('start_at', '<=', now)
        
        for (const event of events) {
          // Passe apenas o id como payload do job. Serializar um model Lucid
          // inteiro num job (ex: BullMQ) é frágil; o handler recarrega o registro.
          await PublishEventJob.dispatch({ eventId: event.id })
          this.logger.info(`Scheduler: publicação despachada para o evento ${event.id}`)
        }
      } catch (error) {
        this.logger.error(`Scheduler: erro em publishDue - ${error.message}`)
      }
    }

    const fetchNews = async () => {
      try {
        await FetchNewsJob.dispatch()
        this.logger.info('Scheduler: job fetch-news despachado')
      } catch (error) {
        this.logger.error(`Scheduler: erro em fetchNews - ${error.message}`)
      }
    }

    // Executa imediatamente na inicialização
    await publishDue()
    await fetchNews()

    // 2. Agenda execuções recorrentes
    const publishInterval = setInterval(publishDue, 60_000) // 1 minuto
    const newsInterval = setInterval(fetchNews, 6 * 60 * 60 * 1000) // 6 horas

    // 3. Registra a limpeza dos timers no encerramento gracioso da aplicação.
    // Com `staysAlive: true`, o processo permanece vivo após o retorno de run();
    // o AdonisJS chama este hook ao terminar (incluindo SIGTERM/SIGINT).
    this.app.terminating(() => {
      this.logger.info('Scheduler encerrando graciosamente...')
      clearInterval(publishInterval)
      clearInterval(newsInterval)
    })
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Não** escreva lógicas complexas de negócios dentro do arquivo do comando caso elas demorem mais do que alguns segundos. Despache-as para uma fila ou serviço separado.
* **Não** omita o bloco `try/catch` dentro dos métodos auxiliares chamados pelo `setInterval`. Qualquer rejeição não tratada derrubará o processo do scheduler.
* **Não** deixe timers pendentes na memória. Você deve limpar todas as referências a `setInterval` e `setTimeout` na sequência de desligamento.
* **Não** omita a opção `startApp: true` se o comando interagir com modelos de banco de dados, provedores de email, sistemas de arquivos, configurações ou serviços de terceiros.
