---
name: laravel-pest-testing-best-practices
description: "Use when writing, debugging, or reviewing Unit, Feature, or Architecture tests with Pest PHP in Laravel. Triggers on test creation, assertions, mocking dependencies, factory usage, database test setup, enforcing code standards and architectural boundaries via arch(), or faking HTTP client calls (Http::fake, Http::sequence, Http::assertSent) for external API tests."
---

# Boas Práticas de Testes com Pest e de Arquitetura no Laravel

## Objetivo
Definir diretrizes, padrões e convenções para escrever testes Unit, Feature e de Arquitetura com Pest PHP no ecossistema Engeapp, garantindo segurança transacional, uso adequado de factories, assertions limpas e limites arquiteturais estritos.

## Instruções
1. **Sintaxe dos Testes**:
   - Use a sintaxe `test('description', function () { ... })` em vez de `it('description')` ou métodos de classe no estilo PHPUnit.
   - Mantenha as descrições claras, concisas e em português brasileiro (ex.: `'Client gendler_name retorna Masculino para M'`), seguindo a convenção do Engeapp.
   - Use o helper funcional `arch()` do Pest v3 para definir suítes de testes de arquitetura, ex.: `arch('controllers')->expect(...)`.

2. **Assertions (Expectations)**:
   - Use a API fluente do Pest (`expect()`) para todas as assertions.
   - Exemplos comuns de expectation:
     - `expect($value)->toBe($expected)`
     - `expect($value)->toBeTrue()` / `expect($value)->toBeFalse()`
     - `expect($value)->toBeInstanceOf(ClassName::class)`
     - `expect($collection)->toHaveCount($count)`
     - `expect($value)->not->toBe($other)`

3. **Banco de Dados & Isolamento**:
   - **Testes Feature**: Todos os testes dentro do diretório `tests/Feature` usam automaticamente o trait `DatabaseTransactions` (conforme configurado em `tests/Pest.php`). NÃO adicione manualmente `use DatabaseTransactions` ou `use RefreshDatabase` em arquivos individuais.
   - **Testes Unit**: Mantenha os testes unitários puros. Não consulte o banco de dados nem dependa do estado do banco em `tests/Unit`.

4. **Factories & Criação de Models**:
   - Use Laravel Model Factories para instanciar models.
   - Use `Model::factory()->make()` para instanciar models em memória quando a persistência no banco não for necessária (ex.: testar accessors/mutators ou lógica que não lê/grava no banco). Isso acelera a execução dos testes.
   - Use `Model::factory()->create()` apenas quando o banco de dados precisar ser consultado, relacionamentos precisarem ser persistidos ou hooks do ciclo de vida do model (`booted` / `created` / etc.) precisarem rodar.

5. **Requisições HTTP (Testes Feature de Controller)**:
   - Use os helpers de request de teste do Pest/Laravel: `$this->get($uri)`, `$this->post($uri, $data)`, `$this->actingAs($user)`.
   - Sempre faça assertion do status da resposta HTTP (ex.: `$response->assertOk()`, `$response->assertStatus(200)`, `$response->assertRedirect()`).

6. **Mocking & Fakes**:
   - Faça mock de chamadas a APIs externas, envio de emails, jobs ou notificações pesadas.
   - Use os Fakes padrão do Laravel para facades: `Queue::fake()`, `Event::fake()`, `Http::fake()`.

7. **Testes de Arquitetura (Pest v3)**:
   - Salve os testes de arquitetura no diretório `tests/Architecture` ou em arquivos de teste dedicados nomeados como `tests/Feature/ArchitectureTest.php`, se apropriado.
   - **Impondo Herança de Classe**:
     ```php
     arch('controllers')
         ->expect('App\Http\Controllers')
         ->toExtend('App\Http\Controllers\Controller');
     ```
   - **Impondo Convenções de Nomenclatura**:
     ```php
     arch('services')
         ->expect('App\Services')
         ->toHaveSuffix('Service');
     ```
   - **Isolamento de Camadas & Restrições de Acoplamento**:
     ```php
     arch('domain')
         ->expect('App\Domain')
         ->not->toUse('App\Http');
     ```
   - **Regras Estritas de Dependência & Qualidade de Código**:
     ```php
     arch('globals')
         ->expect('App')
         ->not->toUse(['dd', 'dump', 'ray', 'var_dump']);
     ```
   - **Resolvendo Dependências Externas / Falsos Positivos**:
     Exclua classes de terceiros, models ou código de vendor que possam causar falsos positivos ao testar limites de arquitetura usando `ignoring()`:
     ```php
     arch('domain')
         ->expect('App\Domain')
         ->not->toUse('App\Infrastructure')
         ->ignoring('App\Infrastructure\Traits\SharedTrait');
     ```

8. **Mocking do HTTP Client**:
   - Sempre chame `Http::preventStrayRequests()` no `beforeEach()` para garantir que nenhuma requisição de rede real escape. Ela lança imediatamente em chamadas não mockadas.
   - Use `Http::fake(['domain.com/*' => Http::response([...], 200)])` para padrões de URL específicos. Evite o coringa `*` — ele mascara requisições não intencionais.
   - Use `Http::sequence()` para código que faz múltiplas requisições ao mesmo endpoint (lógica de retry, APIs paginadas):
     ```php
     Http::fake(['api.service.com/send' => Http::sequence()->push('Error', 500)->push(['id' => 'abc'], 200)]);
     ```
   - Use `Http::failedConnection()` para verificar a resiliência da aplicação durante quedas.
   - Sempre faça assertion com `Http::assertSent()`, `Http::assertNotSent()` ou `Http::assertNothingSent()` — verifique URL, método, payload, headers e query params.
   - Para integrações baseadas no `BaseApi` do Engeapp: faça mock das URLs de destino definidas em `EndPoints.json`.
   - NÃO use mocks do PHPUnit/Mockery para interceptar métodos da classe `Http`. Use apenas o `Http::fake()` nativo.
   - NÃO use credenciais reais, tokens de sandbox ou API keys em mocks — use placeholders fake (ex.: `'fake-token'`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- NÃO use classes de teste ou declarações de método no estilo PHPUnit (ex.: `public function test_something()`). Use a sintaxe funcional do Pest e o helper `arch()`.
- NÃO misture `DatabaseTransactions` com `RefreshDatabase` dentro de arquivos de teste. Deixe o `tests/Pest.php` global cuidar do estado transacional para a suíte `Feature`.
- NÃO consulte o banco de dados dentro de `tests/Unit`. Use objetos mock ou factories com `make()` no lugar.
- NÃO use assertions padrão do PHPUnit (como `$this->assertEquals()`) a menos que seja absolutamente necessário. Prefira a API `expect()` do Pest.
- NÃO use inglês para descrições de teste, pois o padrão do projeto usa português para os textos de descrição (ex.: `test('retorna erro se o cpf for invalido', function() { ... })`).
- NÃO consulte o banco de dados nem faça mock de facades dentro de testes de arquitetura. Mantenha-os puramente focados em análise estática e relações entre classes.
- NÃO defina testes de arquitetura com limites vazios ou escopos sobrepostos que possam deixar o test runner mais lento.
- NÃO permita SQL bruto ou query builders de baixo nível em Controllers; force que passem por Services ou DTOs verificando violações de dependência.
