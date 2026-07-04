---
name: laravel-php-code-quality-tooling
description: Use when formatting, statically analyzing, or automatically refactoring PHP code in the Engeapp backend. Triggers on running Laravel Pint before commits, resolving Larastan/PHPStan type errors, configuring phpstan.neon, running Rector dry-runs, upgrading code to PHP 8.4+ or Laravel 13 conventions, or setting up IDE autocomplete with Barryvdh IDE Helper.
---

# Ferramentas de Qualidade de Código PHP no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões de execução seguros para o pipeline de qualidade de código PHP do backend Engeapp: formatação com Laravel Pint, análise estática com Larastan/PHPStan, refatoração automatizada com Rector e configuração de autocomplete de IDE com Barryvdh IDE Helper. Essas ferramentas formam o toolchain padrão de pré-commit e de upgrade.

## Instruções

### 1. Laravel Pint — Formatação de Código
- **Execução**: Sempre execute antes de finalizar as alterações:
  ```bash
  vendor/bin/pint --dirty --format agent
  ```
- **Flag `--dirty`**: Formata apenas arquivos com alterações não commitadas no Git. Protege commits históricos e evita diffs em massa em arquivos não relacionados. Use-a sempre.
- **Ordem do pipeline**: Execute o Pint **depois** do Rector (para limpar irregularidades de formatação da refatoração automatizada) e **antes** do Larastan (para garantir que correções de estilo não introduzam problemas de sintaxe).
- **Preset de estilo**: Siga as regras em `pint.json`. NÃO sobrescreva a menos que instruído pelo usuário.
- **Restrições**: Nunca execute o Pint sem `--dirty` em toda a base de código. Nunca commite arquivos PHP modificados sem executar o Pint primeiro.

### 2. Larastan/PHPStan — Análise Estática
- **Configuração (`phpstan.neon`)**:
  ```neon
  parameters:
      level: 1
      paths:
          - app/
      tmpDir: bootstrap/cache/phpstan
      scanFiles:
          - _ide_helper_models.php
      excludePaths:
          - vendor/*
      ignoreErrors:
          - '#has no type specified in iterable type#'
  ```
- **Execução**: `vendor/bin/phpstan analyse`
- **Integração com IDE Helper**: NÃO injete anotações PHPDoc diretamente nas classes de model. Sempre gere-as em um arquivo separado:
  ```bash
  php artisan ide-helper:models -M --nowrite
  ```
  Adicione `@mixin IdeHelperUser` no bloco PHPDoc do model para que IDEs e Larastan consigam vincular ao helper gerado.
- **Generics de relacionamento**: Tipe explicitamente os tipos de retorno dos relacionamentos:
  ```php
  /** @return HasMany<PlannerCard, $this> */
  public function cards(): HasMany { ... }
  ```
- **Correções comuns**:
  - Propriedade/método indefinido em models → garanta que `@mixin IdeHelper[Model]` esteja presente e que `_ide_helper_models.php` esteja atualizado.
  - Incompatibilidade de tipo vinda de `$request->input()` → faça o cast explicitamente: `/** @var string $email */ $email = $request->input('email');`
- **Restrições**: Nunca rebaixe abaixo do `level` `1`. Nunca adicione `@phpstan-ignore` inline sem primeiro tentar corrigir a estrutura de tipos. Se a supressão for necessária, adicione-a a `ignoreErrors` em `phpstan.neon` com um regex exato.

### 3. Rector — Refatoração Automatizada
- **Configuração (`rector.php`)**:
  ```php
  return static function (RectorConfig $rectorConfig): void {
      $rectorConfig->paths([__DIR__ . '/app', __DIR__ . '/routes', __DIR__ . '/database', __DIR__ . '/tests']);
      $rectorConfig->ruleWithConfiguration(RemoveFuncCallRector::class, ['ds']);
      $rectorConfig->sets([SetList::DEAD_CODE, SetList::CODE_QUALITY, SetList::TYPE_DECLARATION]);
      $rectorConfig->skip([
          __DIR__ . '/_ide_helper.php',
          __DIR__ . '/_ide_helper_models.php',
          Rector\TypeDeclaration\Rector\Property\TypedPropertyFromAssignsRector::class,
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
- **Segurança com Eloquent**: NÃO deixe o Rector adicionar propriedades tipadas a models para relações ou atributos dinâmicos. Preserve as anotações `@property` e `@mixin`.
- **DTOs do Spatie Data**: Mantenha a constructor property promotion intacta — não permita que o Rector decomponha construtores que mapeiam para models TypeScript.
- **Segurança com Octane**: Evite refatorações do Rector que introduzam propriedades `static` ou caches estáticos dentro de serviços ou controllers (causa vazamentos de memória entre requisições).
- **Sempre execute o Pint depois do Rector** para manter a consistência de estilo.

### 4. Barryvdh IDE Helper — Configuração de Autocomplete
- **Gere os metadados de autocomplete** (execute após quaisquer alterações significativas de model/facade):
  ```bash
  php artisan ide-helper:generate       # Helpers de facade
  php artisan ide-helper:models -M --nowrite  # PHPDocs de model em arquivo separado
  php artisan ide-helper:meta           # Bindings do container para o PhpStorm
  ```
- **Script composer unificado**: `composer run format` executa o Pint, todos os comandos ide-helper e as transformações de tipo TypeScript em uma única etapa.
- **Git**: Garanta que `_ide_helper.php`, `_ide_helper_models.php` e `.phpstorm.meta.php` estejam no `.gitignore`, a menos que haja uma razão específica do projeto para compartilhá-los.
- **Restrições**: NUNCA execute `php artisan ide-helper:models` sem `-M --nowrite`. NUNCA commite models populados com comentários PHPDoc autogerados. Sempre passe `--no-interaction` em ambientes automatizados.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Execute as ferramentas nesta ordem: **Rector → Pint → Larastan**.
- NÃO aplique o Rector a `bootstrap/cache/`, `storage/`, `vendor/` ou `node_modules/`.
- NÃO deixe o Rector alterar propriedades de construtor de DTOs que mapeiam para models TypeScript no frontend.
- NÃO commite nenhum arquivo PHP sem executar o Pint primeiro.
- Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em Português Brasileiro (pt-BR).
