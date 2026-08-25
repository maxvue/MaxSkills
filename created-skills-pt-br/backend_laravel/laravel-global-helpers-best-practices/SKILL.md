---
name: laravel-global-helpers-best-practices
description: "Use when creating, modifying, or testing global helper functions in Engeapp (app/Helpers/). Covers domain helper files, camelCase naming, composer autoload registration, Octane statelessness, and Pest unit tests."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Helpers Globais no Laravel (engeapp)

## Objetivo
Estabelecer padrões limpos, stateless e testados para criar, manter e refatorar funções helper globais no backend Laravel do engeapp, seguindo a convenção real já presente em `app/Helpers/`.

## Convenção real do projeto (verdade-base)
O engeapp NÃO usa classes utilitárias estáticas com namespace para helpers. Há 20 arquivos em `app/Helpers/`, dos quais 18 estão registrados em `composer.json` `autoload.files`; todos os 20 são 100% arquivos de **funções globais soltas**: sem `namespace`, sem `class`, sem `public static function`. Ex.: `addBusinessDays()`, `safeDate()`, `isHoliday()`, `monthName()` (DatesHelper.php); `capitalize()`, `firstCharUpperWords()`, `abrevUPPER()` (StringsHelper.php); `getWireSize()` (ElectricalHelper.php); `checkCepValid()` (ValidationHelpers.php). Siga esse padrão; não introduza classes estáticas.

## Instruções

### 1. Escreva funções globais agrupadas por domínio
Declare funções globais diretamente no arquivo, sem namespace e sem envolvê-las em uma classe. Agrupe por domínio no arquivo correspondente (datas, strings, validação, elétrica, bancos, etc.). Isso mantém a coerência com o restante de `app/Helpers/` e o autocomplete via IDE já funciona por essas funções serem globais e autoloadadas.

### 2. Nomenclatura de funções: camelCase
Nomeie funções globais em **camelCase**, como o codebase inteiro faz (`addBusinessDays`, `safeDate`, `monthName`, `firstCharUpperWords`, `getWireSize`, `checkCepValid`). Evite snake_case para funções novas — embora existam alguns nomes legados em snake_case (ex.: `has_content()`), a convenção dominante e preferida é camelCase. Não crie nomes genéricos que colidam com helpers nativos do Laravel (`collect`, `request`, `array_get`) — consulte a doc de Helpers do Laravel antes.

### 3. Nome de arquivo por domínio
Use `app/Helpers/DominioHelper.php` em PascalCase terminando em `Helper.php` (ex.: `StringsHelper.php`, `DatesHelper.php`, `ElectricalHelper.php`, `LocationHelper.php`, `BanksHelper.php`). Alguns arquivos legados usam o sufixo plural `Helpers.php` (ex.: `ValidationHelpers.php`, `ObjectArrayHelpers.php`, `FilesHelpers.php`) — ambos os sufixos existem e contêm funções globais; não há distinção semântica entre singular e plural. Evite casing misto em arquivos novos (o legado `numbersHelper.php` — registrado no `composer.json` — é um antipadrão a não repetir). Pior ainda: existe também `NumbersHelpers.php` (função `arred()`) com casing conflitante e que NÃO está no `autoload.files`, ou seja, não é carregado automaticamente. O mesmo vale para `OldDBHelper.php` (10 funções, ex. `exportDB()`), também ausente do `autoload.files` — não é um caso isolado do `NumbersHelpers.php`. Não replique esse tipo de arquivo não-autoloadado.

### 4. Tipagem: retorno sempre, parâmetro quando possível
A prática real do codebase é mista: o tipo de **retorno** é tipado de forma consistente (ex.: `: ?Carbon`, `: bool`, `: string`), mas a maioria das funções em `app/Helpers/` NÃO tipa os parâmetros — nenhum arquivo usa `declare(strict_types=1)`. Ex.: `abrevUPPER(?string $valor, int $tamanho) : string` tipa os parâmetros, mas `safeDate($date) : ?Carbon`, `addBusinessDays($data, $dias) : DateTime` e `capitalize($string, $encoding = 'UTF-8') : string` não tipam parâmetros. Declare ao menos o tipo de retorno; tipar parâmetros é recomendado, mas não é praticado de forma consistente no codebase existente. Trate valores nulos explicitamente.

### 5. `function_exists` é defensivo e opcional (não obrigatório)
Envolver a declaração em `if (! function_exists('nome')) { ... }` é uma proteção válida contra colisões e recargas múltiplas, mas NÃO é regra do projeto: apenas 3 dos 20 arquivos usam esse wrapper (`DataBaseHelper.php`, `FilesHelpers.php`, `ValidationHelpers.php`), e a maioria (incluindo `StringsHelper.php` e `DatesHelper.php`) declara funções sem ele. Use o wrapper quando houver risco real de colisão com um nome nativo ou de terceiros; caso contrário, seguir a maioria do codebase (declaração direta) é aceitável.
```php
// Padrão real de wrapper: veja ValidateCpf/ValidateCnpj em ValidationHelpers.php.
if (! function_exists('ValidateCpf')) {
    function ValidateCpf($cpf) : bool
    {
        // Implementação
    }
}
```
Atenção: nem toda função em arquivos wrapeados usa o wrapper — no mesmo `ValidationHelpers.php`, `checkCepValid()` é declarada diretamente, sem `function_exists`. O wrapper é aplicado função a função, não ao arquivo inteiro.

### 6. Design Stateless e compatibilidade com Octane
O engeapp roda sob Laravel Octane (FrankenPHP), que inicializa a aplicação uma vez e a mantém em memória entre requisições. Todo helper deve ser 100% stateless:
- SEM variáveis estáticas dentro de funções que preservem valores entre invocações.
- Passe o estado necessário explicitamente via argumentos.

### 7. Registrando helpers via Composer
Arquivos de funções globais precisam estar no array `autoload.files` do `composer.json` para serem carregados (os existentes já estão lá, ex.: `app/Helpers/StringsHelper.php`, `app/Helpers/DatesHelper.php`):
```json
"autoload": {
    "files": [
        "app/Helpers/StringsHelper.php"
    ]
}
```
Após editar o `composer.json`, execute `composer dump-autoload`.

### 8. Testando com Pest
Cubra cada função com testes unitários em `tests/Unit/Helpers/` (ex.: `StringsHelperTest.php`, `DatesHelperTest.php`, `ValidationHelpersTest.php` já existem). Use blocos `test()` do Pest, com descrições em pt-BR, cobrindo entradas válidas, casos de borda, nulos e entradas incorretas:
```php
test('capitalize mantém preposições em minúsculo', function () {
    expect(capitalize('joão da silva'))->toBe('João da Silva');
});
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** introduza classes utilitárias estáticas com namespace em `app/Helpers/` — a convenção do projeto é função global solta.
- **NUNCA** use snake_case para funções novas; use camelCase.
- **NUNCA** use variáveis/propriedades estáticas que preservem estado entre requisições (quebra o Octane).
- **NUNCA** use nomes genéricos que colidam com helpers nativos do Laravel; consulte a doc antes de nomear.
- **NUNCA** crie helpers sem tipagem estrita de parâmetros e retorno (PHP 8).
