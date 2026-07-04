---
name: laravel-global-helpers-best-practices
description: Use when creating, modifying, refactoring, or testing global helper functions (Helpers) or utility classes in the Laravel backend. Triggers on helper autoload, global function declarations, and custom utility utilities.
---

# Boas Práticas de Helpers Globais e Classes Utilitárias no Laravel

## Objetivo
Estabelecer padrões limpos, modulares, stateless e totalmente testados para criar, manter e refatorar funções helper globais e classes utilitárias estáticas no backend Laravel do ecossistema Engeapp.

## Instruções

### 1. Escolha Arquitetural: Classe Utilitária Estática vs. Função Helper Global
Para manter um namespace global limpo e garantir um excelente autocomplete na IDE, priorize:
- **Classes Utilitárias Estáticas** sob um namespace (ex.: `App\Helpers\StringHelper::capitalize()`) para lógica complexa, utilitários específicos de domínio ou coleções de métodos relacionados.
- **Funções Helper Globais** (ex.: `capitalize()`) apenas quando o utilitário for altamente genérico, usado com frequência em múltiplos contextos (Views, Controllers, classes de Service) e melhorar diretamente a legibilidade.

### 2. Convenções de Nomenclatura e Estrutura de Diretórios
- **Classes Utilitárias Estáticas**:
  - Caminho do arquivo: `app/Helpers/ClassUtilityName.php` (singular, PascalCase, terminando em `Helper` ou `Utility`, ex.: `App\Helpers\MathUtility.php`).
  - Nome da classe: `ClassUtilityName` correspondendo ao nome do arquivo.
  - Nomes dos métodos: camelCase (ex.: `public static function formatBrl()`).
- **Arquivos de Funções Helper Globais**:
  - Caminho do arquivo: `app/Helpers/DomainHelpers.php` (plural, PascalCase, terminando em `Helpers.php`, ex.: `app/Helpers/StringHelpers.php`).
  - Nomes das funções: snake_case (ex.: `format_cnpj()`).
  - Observação: Inconsistências como `numbersHelper.php` (casing misto) são estritamente proibidas para novos arquivos.

### 3. Proteção Contra Colisões
Todas as declarações de funções globais **DEVEM** ser envolvidas em uma verificação `function_exists` para prevenir erros fatais devido a colisões de nomes ou carregamentos múltiplos de arquivos:
```php
if (! function_exists('format_cnpj')) {
    /**
     * Formats a raw string into a standard CNPJ format (99.999.999/9999-99).
     *
     * @param string|null $cnpj
     * @return string
     */
    function format_cnpj(?string $cnpj): string
    {
        // Implementação
    }
}
```

### 4. Design Stateless e Compatibilidade com Laravel Octane
Como o Laravel Octane (FrankenPHP) inicializa a aplicação uma vez e a mantém em memória entre as requisições, todo o código de helper deve ser 100% stateless:
- **SEM** propriedades estáticas que armazenam estado dentro de classes utilitárias.
- **SEM** variáveis estáticas dentro de funções helper que preservam valores entre invocações.
- Não injete instâncias de service com estado ou requests no construtor nem mantenha referência em variáveis estáticas.
- Passe o estado necessário explicitamente via argumentos da função, ou use a facade `Context` do Laravel se metadados contextuais vinculados à requisição forem necessários.

### 5. Registrando Helpers Globais via Composer
Para registrar novos arquivos contendo funções globais, adicione-os ao array `autoload.files` no `composer.json`:
```json
"autoload": {
    "files": [
        "app/Helpers/MyNewHelpers.php"
    ]
}
```
Após modificar o `composer.json`, execute `composer dump-autoload` para atualizar o autoloader.

### 6. Testando Helpers com Pest
Toda função helper e método utilitário estático deve ter cobertura total de testes unitários:
- Crie testes unitários em `tests/Unit/Helpers/` (ex.: `tests/Unit/Helpers/StringHelpersTest.php`).
- Agrupe as asserções de teste usando blocos `test()` ou `it()` do Pest.
- Verifique tanto formatos de entrada válidos, casos de borda, valores nulos quanto formatos incorretos (robustez).
Exemplo:
```php
test('format_cnpj formats raw numbers correctly', function () {
    expect(format_cnpj('12345678000199'))->toBe('12.345.678/0001-99');
});
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **NUNCA** defina uma função helper global sem envolvê-la em um bloco `if (! function_exists(...))`.
- **NUNCA** use variáveis de estado estáticas ou propriedades estáticas de classe para preservar estado entre requisições.
- **NUNCA** use nomes genéricos que possam colidir com as funções helper nativas do Laravel (ex.: `array_get`, `collect`, `request`). Sempre consulte a documentação de Helpers do Laravel antes de criar.
- **NUNCA** crie arquivos de helper sem tipagem estrita de parâmetros do PHP 8 e tipos de retorno explícitos.
