---
name: laravel-code-generators-best-practices
description: >-
  Use when generating or reviewing Laravel backend code (Models, Migrations,
  Controllers, Form Requests, Rules, Observers, Enums, DTOs, Middleware, Events,
  Mailables, Artisan Commands). Enforces strict typing, separation of concerns,
  correct routing, and database conventions for the Engeapp ecosystem. Triggers
  on make:* Artisan generators, schema design, and backend scaffolding reviews.
---

# Laravel Code Generators & Best Practices

## Objetivo

Estabelecer convenções, diretrizes e padrões rígidos para criar, modificar e manter os diversos componentes de backend do Laravel no projeto Engeapp. Isso garante uma arquitetura unificada, separação de responsabilidades adequada, tipagem forte e aderência às boas práticas do Laravel moderno (v13+).

## Instruções

### 1. Models & Migrations

- **Models**:
  - **Reliese Model Generator**: Para gerar models Eloquent a partir do schema do banco de dados, veja as regras específicas em [Reliese Models Generator Best Practices](references/reliese-models-generator.md). Ele explica como separar os arquivos Base (gerados) dos arquivos App (a sua lógica de negócio).
  - Inclua PHPDocs concisos em nível de classe em Português Brasileiro (pt-BR) e a anotação `@mixin IdeHelper[ModelName]`.
  - Execute `php artisan ide-helper:models -M --nowrite` em vez de escrever manualmente as propriedades geradas automaticamente.
  - Defina explicitamente `$fillable`, `$hidden` e `$casts`.
  - Sempre declare os tipos de retorno para os relacionamentos Eloquent (ex.: `: BelongsTo`).
  - Use casts customizados (ex.: mapeando para classes do Spatie Data) e registre-os em `$casts`.
- **Geração de Migrations (`kitloong/laravel-migrations-generator`)**:
  - Ignore tabelas temporárias/de log com `--ignore`. Use `--squash` para consolidar schemas legados.
  - Execute com `--default-index-names --default-fk-names` para forçar os padrões.
- **Criação de Migrations**:
  - Sempre envolva a lógica de criação em `if (Schema::hasTable('table_name')) { return; }`.
  - Use ULID `char('id', 26)->primary()` para chaves primárias por padrão.
  - Separe as chaves estrangeiras em seus próprios arquivos de migration (`..._add_foreign_keys_to_table.php`) envolvidos em um try-catch.
  - Forneça uma rotina de rollback válida no `down()`.
- **Seeders & Factories**:
  - Coloque as factories em `database/factories/` e os seeders em `database/seeders/`.
  - Use o helper `fake()` e defina relacionamentos via bindings padrão de factory.
  - Defina estados explícitos de factory com `$this->state()` e tipos de retorno `static`.
- **Observers**:
  - Gere via `php artisan make:observer {Name}Observer --model={Name}` e registre no `AppServiceProvider`.
  - Evite executar lógica pesada ou requisições HTTP externas de forma síncrona; despache Jobs em background (com `afterCommit()`).
  - Evite loops infinitos durante `updated`/`saved` usando `$model->saveQuietly()`.
- **Casts Customizados**:
  - Implemente `Illuminate\Contracts\Database\Eloquent\CastsAttributes`.
  - Garanta o tratamento gracioso de valores nulos do banco no método `get`. Sem queries ao banco de dados dentro de casts.

### 2. Controllers

- **API Controllers**:
  - Para padrões detalhados sobre criação e refatoração de API Controllers (garantindo Controllers enxutos, Form Requests e Resources), consulte o guia de referência: [API Controller Best Practices](references/api-controller-creator.md).
  - Mantenha os controllers enxutos. Eles devem apenas rotear requisições, chamar services/actions e retornar respostas.
  - Use Form Requests para validação; nunca use `$request->validate([...])` dentro dos controllers.
  - Use API Resources (`JsonResource`) ou DTOs para respostas. Não retorne models/collections brutos.
- **API Controllers (SPA)**:
  - O front Vue é uma SPA pura servida por rota catch-all; o Laravel **não** renderiza páginas. Os controllers expõem apenas dados em JSON, em `app/Http/Controllers/Api/` (ou na convenção de API do projeto), consumidos no Vue por stores `@maxvue/max-pinia` (MaxPinia).
  - Retorne os dados de página (incluindo dados de sub-page/tabs e itens de menu) como JSON via API Resources/DTOs. **NÃO** renderize páginas no backend nem use wrappers de renderização server-side.
  - "Container pages", "sub-page tabs" e "active menu states" são responsabilidade do front: a navegação e as URLs são resolvidas no Vue Router (com Ziggy via `route()`), e o estado de tab/menu ativo vive na store MaxPinia — o backend só fornece os dados.
  - Garanta que os dados sejam carregados via eager-loading (para evitar queries N+1) e trate fallbacks/redirects quando os dados estiverem ausentes.

### 3. Form Requests & Regras de Validação

- **Form Requests**:
  - Gere via `php artisan make:request`.
  - Declare os tipos de retorno explicitamente: `public function authorize(): bool` e `public function rules(): array`.
  - Use objetos de regra fluentes em notação de array (ex.: `['required', 'email', Rule::unique('users')->ignore($this->route('user'))]`). Nada de strings delimitadas por pipe (`|`).
  - Prepare os dados dentro de `prepareForValidation()` e transforme-os posteriormente via `passedValidation()`.
- **Regras de Validação Customizadas**:
  - Gere via `php artisan make:rule RuleName`. Implemente `Illuminate\Contracts\Validation\ValidationRule`.
  - O tratamento de falha usa a closure `$fail` com chaves de tradução (ex.: `$fail('validation.custom.key')->translate();`). Não retorne booleanos.
  - Escreva testes unitários e de feature dedicados (ex.: Pest) para as regras.

### 4. Enums & DTOs

- **Enums**:
  - Armazene em `app/Enums`. Defina como backed enums (`: string` ou `: int`).
  - Use o atributo `#[TypeScript]` do Spatie TypeScript Transformer para integração com o frontend.
  - Execute `php artisan typescript:transform` ao modificar Enums ou DTOs para sincronizar os tipos do frontend.
- **Data Transfer Objects (Spatie Laravel Data)**:
  - Para entender como lidar com declarações Lazy, DataCollectionOf, validações de DTO e tipagem TypeScript, consulte o guia completo: [Data DTO Best Practices](references/data-dto-creator.md).
  - Mantenha os DTOs em `app/Data/` com o sufixo `Data`.
  - Use Constructor Promotion do PHP 8.
  - Para relacionamentos Eloquent, use `Spatie\LaravelData\Lazy` para evitar problemas de N+1. Use `#[DataCollectionOf(RelatedData::class)]` para coleções.
  - Não inclua lógica de persistência no banco de dados dentro de DTOs.

### 5. Middleware

- **Criação & Registro**:
  - Gere via `php artisan make:middleware`.
  - Injete dependências via constructor promotion do PHP 8. Mantenha o middleware stateless para compatibilidade com o Octane.
  - Registre middleware global, de grupo ou de alias em `bootstrap/app.php` (abordagem do Laravel 13) em vez de `Kernel.php`.

### 6. Events & Broadcasting

- **Criação & Conexões**:
  - Events que usam broadcasting devem implementar `ShouldBroadcast` ou `ShouldBroadcastNow`.
  - Implemente `broadcastConnections(): array` retornando `['reverb']`.
- **Channels & Payloads**:
  - Defina `broadcastOn()` retornando um array de Channels (prefira `PrivateChannel`).
  - Restrinja o payload em `broadcastWith()` em vez de enviar os models completos.
  - Autorize private channels em `routes/channels.php` com o tipo `User $user` e retornos `: bool`.
- **Frontend**:
  - Use o composable `useEcho` do `@laravel/echo-vue` na Composition API do Vue 3 para tratar automaticamente a escuta e a limpeza (cleanup).

### 7. Mailables & Notifications

- **Mailables**:
  - Use a sintaxe moderna: implemente `envelope()` e `content()`. Evite o legado `build()`.
  - Injete dependências no construtor via property promotion. Use a trait `SerializesModels`.
  - Para e-mail assíncrono, implemente `ShouldQueue` e especifique uma fila (ex.: `public $queue = 'emails';`).
- **Notifications**:
  - Retorne os canais em `via()`. Use `ShouldQueue`.
  - Defina `toDatabase()`, `toMail()`, etc., retornando arrays serializáveis e limpos ou objetos `MailMessage`.

### 8. Artisan Commands

- **Criação & Práticas**:
  - Para guias de I/O de console (usando Laravel Prompts), injeção de dependência via container e formatação de saída, consulte a referência dedicada: [Artisan Command Creator](references/artisan-command-creator.md).
- **Definição & Atributos**:
  - Use atributos do PHP 8 para `#[Signature]` e `#[Description]`.
  - Use `:` para agrupar comandos relacionados.
- **Lógica & Execução**:
  - O método `handle()` deve retornar um código de saída `int` (`self::SUCCESS`, `self::FAILURE`, `self::INVALID`).
  - Mantenha o `handle()` focado em I/O. Extraia a lógica de negócio para Jobs, Services ou Actions.
  - Use os helpers de console (`$this->info()`, `$this->error()`, `$this->table()`, `createProgressBar()`) para saída formatada ao usuário.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **NÃO** use funções PHP simples como `echo`, `print_r`, `$request->validate()`, queries brutas inline ou validações com pipe `|`.
- Mantenha controllers, rotas e observers enxutos. Evite executar APIs externas de forma síncrona sem jobs.
- Comentários de código e PHPDocs **DEVEM** ser escritos em Português Brasileiro (pt-BR) conforme as regras globais do usuário.
