---
name: laravel-prompts-best-practices
description: Use when creating, modifying, or styling interactive console/CLI inputs using Laravel Prompts. Triggers on text prompts, password fields, select/confirm prompts, spinner loading screens, multi-select questions, and validation in CLI commands.
---

# Boas Práticas do Laravel Prompts

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para utilizar a biblioteca Laravel Prompts em comandos Artisan interativos, melhorando a experiência de terminal do desenvolvedor e do operador.

## Instruções
1. **Importação de Funções**:
   - Sempre importe funções de prompt específicas usando a sintaxe `use function` em vez de chamá-las estaticamente ou por nomes totalmente qualificados.
     ```php
     use function Laravel\Prompts\text;
     use function Laravel\Prompts\select;
     use function Laravel\Prompts\confirm;
     use function Laravel\Prompts\spin;
     use function Laravel\Prompts\progress;
     ```

2. **Tipos de Prompt e Uso**:
   - **Text**: Para entradas de texto simples. Forneça um `label` claro, `placeholder` opcional e `hint`.
   - **Password**: Para entradas de dados sensíveis. Impede que os caracteres sejam exibidos.
   - **Confirm**: Para decisões booleanas. Sempre forneça um valor `default` lógico (true/false).
   - **Select**: Para escolher uma única opção de uma lista predefinida.
   - **Multiselect**: Para escolher múltiplas opções.
   - **Suggest**: Autocompleta a entrada a partir de um array de valores conforme o usuário digita.
   - **Search**: Para opções de busca conforme a digitação, ideal para consultas ao banco de dados.
   - **Spin**: Exibe um spinner de carregamento durante tarefas de longa duração.
   - **Progress**: Exibe uma barra de progresso ao iterar sobre coleções.

3. **Validação de Entrada**:
   - Use o argumento `validate` com uma closure para validar as entradas. Retorne uma string descrevendo o erro se for inválida, ou `null` se for válida.
     ```php
     $email = text(
         label: 'Qual é o seu endereço de e-mail?',
         validate: fn (string $value) => match (true) {
             ! filter_var($value, FILTER_VALIDATE_EMAIL) => 'O endereço de e-mail é inválido.',
             default => null
         }
     );
     ```

4. **Fallbacks Não Interativos**:
   - Garanta que os comandos CLI suportem execução não interativa (por exemplo, CI/CD, tarefas agendadas).
   - Faça fallback para a verificação de argumentos ou opções do comando quando a entrada não for interativa.
     ```php
     $name = $this->argument('name') ?? text('Qual é o seu nome?');
     ```

5. **Elementos de Saída Visual**:
   - Use as funções de alerta embutidas `info()`, `warning()`, `error()` e `note()` para saídas estilizadas em vez de echo bruto ou `$this->info()`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **Não** use inputs legados do Symfony Console como `$this->ask()` ou `$this->confirm()`, a menos que o Laravel Prompts seja incompatível com o ambiente.
- **Não** bloqueie o terminal com tarefas síncronas de longa duração sem usar `spin()` ou `progress()` para dar feedback.
- **Não** escreva loaders ou spinners em ASCII customizados. Use a função nativa `spin()`.
- **Não** omita validação para entradas críticas (por exemplo, IDs de banco de dados, e-mails, caminhos de arquivo).
