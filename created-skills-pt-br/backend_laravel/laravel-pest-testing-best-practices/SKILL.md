---
name: laravel-pest-testing-best-practices
description: "Use when writing, debugging, or reviewing Unit, Feature, or Architecture tests with Pest PHP in Laravel. Covers test creation, assertions, mocking dependencies, factory usage, database setup, arch() rules, and Http::fake()."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Testes com Pest e de Arquitetura no Laravel

## Objetivo
Definir diretrizes, padrões e convenções para escrever testes Unit, Feature e de Arquitetura com Pest PHP no ecossistema Engeapp, garantindo segurança transacional, uso adequado de factories, assertions limpas e limites arquiteturais estritos.

## Instruções
1. **Sintaxe dos Testes**:
   - Use a sintaxe funcional do Pest em vez de métodos de classe no estilo PHPUnit. `it()` e `test()` coexistem amplamente no engeapp (`it()` em ~88 arquivos, `test()` em ~46), então **não há convenção estabelecida**: prefira `test('description', function () { ... })` como padronização para código novo, mas mantenha o estilo já usado ao mexer em arquivos existentes.
   - Mantenha as descrições claras, concisas e em português brasileiro (ex.: `'Client gendler_name retorna Masculino para M'`).
   - Ao introduzir testes de arquitetura (ainda inexistentes no engeapp — ver seção 7), use o helper funcional `arch()` do Pest v3, ex.: `arch('controllers')->expect(...)`.

2. **Assertions (Expectations)**:
   - Use a API fluente do Pest (`expect()`) para todas as assertions, e não as assertions padrão do PHPUnit (ver Restrições).

3. **Banco de Dados & Isolamento** (regra única — as Restrições apenas referenciam esta seção):
   - `tests/Pest.php` aplica `DatabaseTransactions` tanto em `Feature` quanto em `Unit`. NÃO adicione manualmente `use DatabaseTransactions` nem `use RefreshDatabase` em arquivos individuais, e não misture os dois traits.
   - **Testes Unit**: prefira testes puros com `make()` e mocks. Mas quando o teste de Unit precisar do banco, isso é **aceito no engeapp** — é exatamente por isso que `tests/Pest.php` estende `DatabaseTransactions` também em `Unit` (ver comentário no arquivo). Exemplos reais que persistem models: `tests/Unit/Models/CallTest.php`, `tests/Unit/Services/VoipServiceDialTest.php`, `tests/Unit/Services/VoipServiceAnswerTest.php`, `tests/Unit/Services/PhoneNumberResolverTest.php`, `tests/Unit/Integrador/SolarCompanyTypeTest.php`, `tests/Unit/Integrador/UserRolesTest.php`, `tests/Unit/Events/IncomingCallEventTest.php`.

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

7. **Testes de Arquitetura (Pest v3)** — *recomendação, ainda não adotada no engeapp*:
   - **Nota de contexto:** o engeapp NÃO possui hoje nenhum teste de arquitetura (`arch()`), diretório `tests/Architecture` nem `ArchitectureTest.php`. As APIs abaixo são reais do Pest v3 e representam uma boa prática a introduzir; trate-as como orientação para novos testes, não como uma convenção já seguida pelo projeto.
   - Ao introduzir, salve os testes de arquitetura no diretório `tests/Architecture` ou em arquivos dedicados nomeados como `tests/Feature/ArchitectureTest.php`, se apropriado.
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
   - **ATENÇÃO — os dois exemplos acima falham hoje se executados como estão.** O código atual tem exceções conhecidas: `App\Http\Controllers\Support\SupportExecuteController` e `App\Http\Controllers\Settings\DateController` não têm `extends` (e são apenas dois exemplos: algumas dezenas de arquivos em `app/Http/Controllers` não têm `extends Controller`); em `app/Services` existem `Ogg.php`, `EfiPaymentStatus.php`, `InterPaymentExecute.php`, `PaymentPricing.php`, entre outros, sem o sufixo `Service`. Antes de adotar esses arch tests, acrescente `ignoring()` para essas exceções ou ajuste o código.
   - **Regras Estritas de Dependência & Qualidade de Código**:
     ```php
     arch('globals')
         ->expect('App')
         ->not->toUse(['dd', 'dump', 'ray', 'var_dump']);
     ```
   - **Resolvendo Dependências Externas / Falsos Positivos**:
     Use `ignoring()` para excluir classes que causariam falsos positivos ou que são exceções legadas conhecidas:
     ```php
     arch('services')
         ->expect('App\Services')
         ->toHaveSuffix('Service')
         ->ignoring([\App\Services\Ogg::class, \App\Services\Bank\EfiPaymentStatus::class]);
     ```

8. **Mocking do HTTP Client**:
   - Os testes reais do engeapp usam `Http::fake()` diretamente (ex.: `tests/Feature/Icons/OllamaClientTest.php`, `tests/Feature/SocialMedia/MetaIntegrationTest.php`), inclusive com o coringa `Http::fake(['*' => ...])`. Siga esse padrão existente ao mexer nesses testes.
   - Use `Http::preventStrayRequests()` no `beforeEach()` e padrões de URL específicos em `Http::fake()` — padrão já adotado no projeto: `tests/Feature/CellChargeServiceTest.php` usa a URL absoluta completa (`'https://api-sandbox.asaas.com/v3/mobilePhoneRecharges/...'`), enquanto `tests/Feature/Console/CellChargeCommandTest.php` e `tests/Feature/Console/CellChargeListTest.php` usam coringas parciais (`'*/v3/mobilePhoneRecharges/*/provider'`). Reserve o coringa `'*'` para casos em que qualquer requisição serve.
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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- NÃO use classes de teste ou declarações de método no estilo PHPUnit (ex.: `public function test_something()`). Use a sintaxe funcional do Pest e o helper `arch()`.
- Isolamento de banco: siga a seção 3 (o `tests/Pest.php` global cuida do estado transacional de `Feature` **e** de `Unit`).
- NÃO use assertions padrão do PHPUnit (como `$this->assertEquals()`) a menos que seja absolutamente necessário. Prefira a API `expect()` do Pest.
- NÃO use inglês para descrições de teste, pois o padrão do projeto usa português para os textos de descrição (ex.: `test('retorna erro se o cpf for invalido', function() { ... })`).
- NÃO consulte o banco de dados nem faça mock de facades dentro de testes de arquitetura. Mantenha-os puramente focados em análise estática e relações entre classes.
- NÃO defina testes de arquitetura com limites vazios ou escopos sobrepostos que possam deixar o test runner mais lento.
- Restringir SQL bruto / query builders de baixo nível em Controllers é **aspiracional**, não o estado atual: boa parte dos controllers do engeapp usa Eloquent/DB diretamente e há `DB::table()`/`DB::raw()` em `Calendar/CalendarDataController.php`, `Admin/AdminCompanyController.php` e `Statistics/StatisticsController.php`. Se um arch test dessa regra for introduzido, ele precisa nascer com `ignoring()` para essas exceções ou ser aplicado apenas a namespaces novos.
