---
name: adonisjs-ace-commands-best-practices
description: Use when creating, reviewing, or debugging custom Ace commands (CLI scripts) in AdonisJS v6. Triggers on extending BaseCommand, defining command flags and arguments, setting startApp options, running interactive prompts (ask, choice, secure, confirm), using logger output in commands, or implementing command test helpers.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas para Comandos Ace do AdonisJS v6

## Objetivo
Fornecer diretrizes padrão e boas práticas para criar, modificar, depurar e executar comandos Ace personalizados (scripts CLI) dentro do ecossistema do AdonisJS v6.

## Instruções

### 1. Estrutura e Definição de Comandos
- Herdar de `BaseCommand` importado de `@adonisjs/core/ace`.
- Definir propriedades estáticas:
  - `commandName`: Nome exclusivo usando namespace delimitado por dois-pontos (ex: `namespace:nome`).
  - `description`: Um breve resumo do que o comando faz.
  - `options`: Defina `{ startApp: true }` se o comando exigir banco de dados, models ou injeção de dependência do container. Caso contrário, deixe vazio ou `{ startApp: false }` para acelerar o tempo de inicialização.

```typescript
import { BaseCommand } from '@adonisjs/core/ace'

export default class MyCustomCommand extends BaseCommand {
  static commandName = 'custom:my-command'
  static description = 'Execute my custom task'
  static options = {
    startApp: true,
  }

  async run() {
    this.logger.info('Command started')
    // A lógica do comando entra aqui
  }
}
```

### 2. Declaração de Flags e Argumentos
- Importar os decorators `flags` e `args` de `@adonisjs/core/ace`.
- Usar o modificador `declare` do TypeScript para declarações de propriedades.
- Definir flags usando decorators como `@flags.string()`, `@flags.boolean()`, `@flags.number()` ou `@flags.array()`.
- Definir argumentos posicionais usando `@args.string()` ou `@args.spread()`. Não existe `@args.number()` — argumentos posicionais só suportam `string`/`spread`; converta manualmente um valor numérico dentro do `run()` se necessário (flags numéricas existem via `@flags.number()`).

```typescript
import { BaseCommand, flags, args } from '@adonisjs/core/ace'

export default class ProcessDataCommand extends BaseCommand {
  static commandName = 'data:process'
  static description = 'Process data files'

  @args.string({ description: 'Path to the target file' })
  declare filePath: string

  @flags.boolean({ description: 'Run process in dry mode', alias: 'd' })
  declare dryRun: boolean

  async run() {
    this.logger.info(`Processing file: ${this.filePath} (Dry run: ${this.dryRun})`)
  }
}
```

### 3. Prompts Interativos
- Usar os métodos do `this.prompt` para interagir com o usuário:
  - `ask(question, options)`: Solicita uma entrada de texto simples.
  - `secure(question, options)`: Solicita uma entrada mascarada (senha).
  - `confirm(question, options)`: Solicita uma confirmação booleana sim/não.
  - `choice(question, choices, options)`: Seleciona uma única opção de uma lista.
  - `multiple(question, choices, options)`: Seleciona várias opções de uma lista.

```typescript
const confirmExecution = await this.prompt.confirm('Are you sure you want to proceed?')
if (!confirmExecution) {
  this.logger.warning('Operation cancelled by the user.')
  return
}
```

### 4. Formatação de Saída & Logs
- Sempre usar `this.logger` em vez de `console.log()` para mensagens de console.
- Utilizar métodos de log semânticos:
  - `this.logger.info(message)`: Mensagens informativas gerais.
  - `this.logger.success(message)`: Indicar que ações foram concluídas com sucesso.
  - `this.logger.warning(message)`: Avisos ou problemas que não interrompem a execução.
  - `this.logger.error(message)`: Indicar operações que falharam.
  - `this.logger.await(message)`: Iniciar processos assíncronos em progresso.

### 5. Encerramento Gracioso & Sinais
- Para comandos de longa execução (como schedulers, queue workers, listeners), registrar manipuladores para os sinais `SIGINT` e `SIGTERM`.
- Limpar recursos (limpar intervalos, fechar conexões de workers, desligar filas) para evitar processos zumbis persistentes.

```typescript
await new Promise<void>((resolve) => {
  const shutdown = async () => {
    this.logger.info('Shutting down command gracefully...')
    // Realize a limpeza de recursos aqui
    resolve()
  }
  process.once('SIGTERM', shutdown)
  process.once('SIGINT', shutdown)
})
```

### 6. Códigos de Saída e Tratamento de Erros
- Envolver a lógica do comando em blocos try-catch para capturar exceções inesperadas.
- Em caso de falha, definir `this.exitCode = 1` e registrar a mensagem de erro usando `this.logger.error(error.message)`.
- Evitar chamar `process.exit()` diretamente; deixe que o Kernel do AdonisJS cuide do encerramento com base no valor de `this.exitCode` ao final do `run()`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** use `console.log()` ou `console.error()`. Sempre use `this.logger` para impressões no console.
- **NUNCA** esqueça de declarar as opções estáticas `options = { startApp: true }` se você consultar models, executar migrações ou chamar serviços que dependam do container IoC do AdonisJS. Não fazer isso causará erros de "Application not started" ou falhas na instanciação de dependências.
- **NÃO** use `process.exit()` diretamente dentro de comandos. Em vez disso, defina `this.exitCode`.
- **NUNCA** deixe comandos de longa execução (como workers BullMQ ou Schedulers personalizados) sem registrar manipuladores `SIGINT`/`SIGTERM`. Processos zumbis remanescentes bloquearão conexões de banco de dados e outros recursos.
- **NUNCA** defina flags ou argumentos de propriedade sem a palavra-chave `declare` do TypeScript.
