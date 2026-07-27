---
name: laravel-php-code-quality-tooling
description: "Use when formatting, statically analyzing, or automatically refactoring PHP code in the Engeapp backend. Triggers on running Laravel Pint before commits, resolving Larastan/PHPStan type errors, configuring phpstan.neon, running Rector dry-runs, upgrading code to PHP 8.4+ or Laravel 13 conventions, or setting up IDE autocomplete with Barryvdh IDE Helper."
---

# Ferramentas de Qualidade de Código PHP no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões de execução seguros para o pipeline de qualidade de código PHP do backend Engeapp: formatação com Laravel Pint, análise estática com Larastan/PHPStan, refatoração automatizada com Rector e configuração de autocomplete de IDE com Barryvdh IDE Helper. Essas ferramentas formam o toolchain padrão de pré-commit e de upgrade.

## Instruções

### 1. Laravel Pint — Formatação de Código
- **Execução (edições pontuais)**: Ao finalizar alterações num subconjunto de arquivos, formate só o que mudou:
  ```bash
  vendor/bin/pint --dirty
  ```
- **Execução (pipeline canônico do projeto)**: O script `composer run format` roda Pint na base inteira seguido do pipeline de IDE Helper (ver seção 4). Use-o quando quiser normalizar tudo de uma vez; use `--dirty` apenas para diffs focados.
- **Flag `--dirty`**: Formata apenas arquivos com alterações não commitadas no Git. Protege commits históricos e evita diffs em massa em arquivos não relacionados. Prefira-a em edições pontuais.
- **Ordem do pipeline**: Execute o Pint **depois** do Rector (para limpar irregularidades de formatação da refatoração automatizada) e **antes** do Larastan (para garantir que correções de estilo não introduzam problemas de sintaxe).
- **Preset de estilo**: Siga as regras em `pint.json`. NÃO sobrescreva a menos que instruído pelo usuário.
- **Restrições**: Em edições pontuais, evite formatar a base inteira sem necessidade (veja flag `--dirty` acima; o script `composer run format` roda a base inteira de propósito). Nunca commite arquivos PHP modificados sem executar o Pint primeiro.

### 2. Larastan/PHPStan — Análise Estática
- **Configuração (`phpstan.neon`)**:
  ```neon
  parameters:
      level: 1
      paths:
          - app/
      tmpDir: bootstrap/cache/phpstan
      parallel:
          maximumNumberOfProcesses: 8
          minimumNumberOfJobsPerProcess: 2
      scanFiles:
          - _ide_helper_models.php
      excludePaths:
          - vendor/*
      ignoreErrors:
          - '#has no type specified in iterable type#'
  ```
- **Execução**: `vendor/bin/phpstan analyse`
- **Integração com IDE Helper**: NÃO injete anotações PHPDoc diretamente nas classes de model. Sempre gere-as em um arquivo separado, com `-M --nowrite` (ver seção 4). Adicione `@mixin IdeHelperUser` no bloco PHPDoc do model para que IDEs e Larastan consigam vincular ao helper gerado.
- **Generics de relacionamento**: Tipe explicitamente os tipos de retorno dos relacionamentos (recomendação aspiracional — nenhum model do projeto usa esse padrão de generics hoje):
  ```php
  /** @return HasMany<Model, $this> */
  public function items(): HasMany { ... }
  ```
- **Correções comuns**:
  - Propriedade/método indefinido em models → garanta que `@mixin IdeHelper[Model]` esteja presente e que `_ide_helper_models.php` esteja atualizado.
  - Incompatibilidade de tipo vinda de `$request->input()` → faça o cast explicitamente: `/** @var string $email */ $email = $request->input('email');`
- **Restrições**: Nunca rebaixe abaixo do `level` `1`. Nunca adicione `@phpstan-ignore` inline sem primeiro tentar corrigir a estrutura de tipos. Se a supressão for necessária, adicione-a a `ignoreErrors` em `phpstan.neon` com um regex exato.

### 3. Rector — Refatoração Automatizada
- **Configuração (`rector.php`)**: O projeto usa uma configuração minimalista e deliberadamente enxuta — apenas os `paths` a varrer e uma única regra `RemoveFuncCallRector` para remover chamadas `ds()` (função de debug do pacote `laradumps/laradumps`) esquecidas. NÃO há `SetList` nem bloco `skip()`. Mantenha assim, a menos que o usuário peça explicitamente para ampliar o escopo:
  ```php
  use Rector\Config\RectorConfig;
  use Rector\Removing\Rector\FuncCall\RemoveFuncCallRector;

  return static function (RectorConfig $rectorConfig): void {
      // 1. Defina as pastas onde o Rector vai procurar o ds()
      $rectorConfig->paths([
          __DIR__ . '/app',
          __DIR__ . '/routes',
          __DIR__ . '/database',
          __DIR__ . '/tests',
      ]);

      // 2. Regra que remove chamadas da função ds()
      $rectorConfig->ruleWithConfiguration(RemoveFuncCallRector::class, [
          'ds',
      ]);
  };
  ```
- **Execução — sempre faça dry-run primeiro**:
  ```bash
  vendor/bin/rector process --dry-run   # verificação read-only
  vendor/bin/rector process             # aplica as alterações
  vendor/bin/rector process --clear-cache
  vendor/bin/rector process app/Http/Controllers/UserController.php --dry-run
  ```
- **Segurança do Rector** (não deixe o Rector): adicionar propriedades tipadas a models para relações/atributos dinâmicos — preserve `@property`/`@mixin`; decompor construtores de DTOs do Spatie Data que mapeiam para models TypeScript — mantenha a constructor property promotion intacta; introduzir propriedades `static`/caches estáticos em serviços ou controllers (vazamento de memória entre requisições sob Octane).
- **Sempre execute o Pint depois do Rector** para manter a consistência de estilo.

### 4. Barryvdh IDE Helper — Configuração de Autocomplete
- **Gere os metadados de autocomplete** (execute após quaisquer alterações significativas de model/facade):
  ```bash
  php artisan ide-helper:generate       # Helpers de facade
  php artisan ide-helper:models -M --nowrite  # PHPDocs de model em arquivo separado (flags obrigatórias — ver Restrições)
  php artisan ide-helper:meta           # Bindings do container para o PhpStorm
  ```
- **Script composer unificado**: `composer run format` executa, nesta ordem, `php ./vendor/bin/pint`, `php artisan ide-helper:generate`, `php artisan ide-helper:models -M --nowrite`, `php artisan ide-helper:meta` e `php artisan typescript:transform`.
- **Git**: No engeapp os arquivos de IDE helper (`_ide_helper.php`, `_ide_helper_models.php`, `_ide_helper_spatie.php` e `.phpstorm.meta.php`) são **rastreados no repositório** (commitados), não ignorados — regere-os com `composer run format` e commite as mudanças junto. Ignorá-los no `.gitignore` é uma convenção comum de outros projetos, mas contraria a deste.
- **Restrições**: NUNCA execute `php artisan ide-helper:models` sem `-M --nowrite`. NUNCA commite models populados com comentários PHPDoc autogerados. Sempre passe `--no-interaction` em ambientes automatizados.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito. Todos os comentários dentro dos exemplos de código também em pt-BR.
- NÃO aplique o Rector a `bootstrap/cache/`, `storage/`, `vendor/` ou `node_modules/`.
