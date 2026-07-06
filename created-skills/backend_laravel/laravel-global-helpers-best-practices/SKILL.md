---
name: laravel-global-helpers-best-practices
description: "Use ao criar, modificar, refatorar ou testar funções helper globais no backend Laravel do engeapp (arquivos em app/Helpers/). Cobre a convenção real do projeto: funções globais soltas em arquivos por domínio (sem namespace nem classes estáticas), nomes em camelCase, registro em composer autoload.files, design stateless para Octane e testes Pest em tests/Unit/Helpers/."
---

# Boas Práticas de Helpers Globais no Laravel (engeapp)

## Objetivo
Estabelecer padrões limpos, stateless e testados para criar, manter e refatorar funções helper globais no backend Laravel do engeapp, seguindo a convenção real já presente em `app/Helpers/`.

## Convenção real do projeto (verdade-base)
O engeapp NÃO usa classes utilitárias estáticas com namespace para helpers. Os ~18 arquivos em `app/Helpers/` são 100% arquivos de **funções globais soltas**: sem `namespace`, sem `class`, sem `public static function`. Ex.: `addBusinessDays()`, `safeDate()`, `isHoliday()`, `monthName()` (DatesHelper.php); `capitalize()`, `firstCharUpperWords()`, `abrevUPPER()` (StringsHelper.php); `getWireSize()` (ElectricalHelper.php); `checkCepValid()` (ValidationHelpers.php). Siga esse padrão; não introduza classes estáticas.

## Instruções

### 1. Escreva funções globais agrupadas por domínio
Declare funções globais diretamente no arquivo, sem namespace e sem envolvê-las em uma classe. Agrupe por domínio no arquivo correspondente (datas, strings, validação, elétrica, bancos, etc.). Isso mantém a coerência com o restante de `app/Helpers/` e o autocomplete via IDE já funciona por essas funções serem globais e autoloadadas.

### 2. Nomenclatura de funções: camelCase
Nomeie funções globais em **camelCase**, como o codebase inteiro faz (`addBusinessDays`, `safeDate`, `monthName`, `firstCharUpperWords`, `getWireSize`, `checkCepValid`). Evite snake_case para funções novas — embora existam alguns nomes legados em snake_case (ex.: `has_content()`), a convenção dominante e preferida é camelCase. Não crie nomes genéricos que colidam com helpers nativos do Laravel (`collect`, `request`, `array_get`) — consulte a doc de Helpers do Laravel antes.

### 3. Nome de arquivo por domínio
Use `app/Helpers/DominioHelper.php` em PascalCase terminando em `Helper.php` (ex.: `StringsHelper.php`, `DatesHelper.php`, `ElectricalHelper.php`, `LocationHelper.php`, `BanksHelper.php`). Alguns arquivos legados usam o sufixo plural `Helpers.php` (ex.: `ValidationHelpers.php`, `ObjectArrayHelpers.php`, `FilesHelpers.php`) — ambos os sufixos existem e contêm funções globais; não há distinção semântica entre singular e plural. Evite casing misto em arquivos novos (o legado `numbersHelper.php` é um antipadrão a não repetir).

### 4. Tipagem estrita PHP 8
Sempre declare tipos de parâmetro e de retorno explícitos, como nas funções reais (ex.: `function safeDate($date) : ?Carbon`, `function abrevUPPER(?string $valor, int $tamanho) : string`). Trate valores nulos explicitamente.

### 5. `function_exists` é defensivo e opcional (não obrigatório)
Envolver a declaração em `if (! function_exists('nome')) { ... }` é uma proteção válida contra colisões e recargas múltiplas, mas NÃO é regra do projeto: apenas 3 dos ~18 arquivos usam esse wrapper (`DataBaseHelper.php`, `FilesHelpers.php`, `ValidationHelpers.php`), e a maioria (incluindo `StringsHelper.php` e `DatesHelper.php`) declara funções sem ele. Use o wrapper quando houver risco real de colisão com um nome nativo ou de terceiros; caso contrário, seguir a maioria do codebase (declaração direta) é aceitável.
```php
if (! function_exists('checkCepValid')) {
    function checkCepValid(?string $value) : bool
    {
        // Implementação
    }
}
```

### 6. Design Stateless e compatibilidade com Octane
O engeapp roda sob Laravel Octane (FrankenPHP), que inicializa a aplicação uma vez e a mantém em memória entre requisições. Todo helper deve ser 100% stateless:
- SEM variáveis estáticas dentro de funções que preservem valores entre invocações.
- Passe o estado necessário explicitamente via argumentos.
- Se precisar de metadados contextuais vinculados à requisição, use a facade `Context` do Laravel.

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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
- **NUNCA** introduza classes utilitárias estáticas com namespace em `app/Helpers/` — a convenção do projeto é função global solta.
- **NUNCA** use snake_case para funções novas; use camelCase.
- **NUNCA** use variáveis/propriedades estáticas que preservem estado entre requisições (quebra o Octane).
- **NUNCA** use nomes genéricos que colidam com helpers nativos do Laravel; consulte a doc antes de nomear.
- **NUNCA** crie helpers sem tipagem estrita de parâmetros e retorno (PHP 8).
