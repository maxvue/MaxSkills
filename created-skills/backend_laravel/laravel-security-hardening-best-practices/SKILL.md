---
name: laravel-security-hardening-best-practices
description: "Use when designing, reviewing, or debugging Laravel application security. Covers Eloquent encryption, mass assignment protection, SQLi/IDOR mitigation, secure controllers, file upload hardening, security headers, and OWASP Top 10."
---
# Boas Práticas de Hardening de Segurança no Laravel

## Objetivo
Estabelecer diretrizes robustas de segurança e práticas de hardening para o desenvolvimento backend no ecossistema Laravel do Engeapp. Isso previne vazamentos de dados, mitiga vulnerabilidades do OWASP Top 10, protege integrações e garante o manuseio seguro de arquivos.

## Instruções

### 1. Segurança de Models Eloquent
- **Criptografia de Campos Sensíveis**: Use o cast `'encrypted'` embutido do Laravel ou casting criptografado customizado para PII (Informações Pessoais Identificáveis) e chaves/tokens de APIs de terceiros. Sempre oculte essas colunas usando `$hidden` no model.
- **Proteção contra Mass Assignment**: Para models novos ou que recebem entrada direta do usuário, prefira declarar explicitamente os atributos seguros no array `$fillable` — isso limita a superfície de mass assignment ao mínimo necessário. Realidade do engeapp: a maioria dos models usa `$fillable`, mas `protected $guarded = [];` é uma convenção amplamente adotada em um número relevante deles, então NÃO exija `$fillable` de forma cega. Quando o model usa `guarded = []`, o controle compensatório obrigatório é validar/filtrar a entrada em um Form Request dedicado (ver secao 4), nunca passar `$request->all()` sem validação prévia para `create`/`update`.
- **Strict Loading e Prevenção de Lazy Loading** (opt-in, não configurado hoje): O engeapp NÃO configura `Model::shouldBeStrict()` / `preventLazyLoading()` / `preventSilentlyDiscardingAttributes()` no `AppServiceProvider` atualmente. Se decidir adotar esse hardening, ative-o no `boot()` do `AppServiceProvider` (idealmente apenas fora de produção via `!app()->isProduction()`) — isso ajuda a detectar N+1 e atribuições silenciosamente descartadas em desenvolvimento. Trate como recomendação genérica opcional, não como estado atual do projeto.

### 2. Prevenção de SQL Injection (SQLi)
- **Consultas Parametrizadas**: Sempre use os bindings de parâmetro do Eloquent ou do query builder, inclusive em `whereRaw`, `selectRaw`, `orderByRaw` e `DB::statement`.
- **Expressões Raw Seguras**: Se o SQL bruto for inevitável, use métodos que de fato façam bind dos parâmetros: `DB::select('select * from users where id = ?', [$id])` para um SELECT bruto, ou bindings em array em uma condição do query builder: `->whereRaw('id = ?', [$id])`. Note que `DB::raw()` é apenas um fragmento de SQL sem escape — ele **não** aceita bindings e **não** parametriza, então a entrada do usuário NUNCA deve ser passada diretamente para ele.

### 3. Mitigação de IDOR (Insecure Direct Object References)
- **Scoped Route Model Binding**: NÃO assuma que `Route::get('/projects/{project}/documents/{document}', ...)` valida o vínculo pai→filho. Com `{document}` puro o filho é resolvido pela própria PK, sem relação com o pai. O scoping implícito só ocorre quando o parâmetro filho usa chave customizada (`{document:slug}`, que popula `bindingFields()`) ou quando a rota/grupo chama `->scopeBindings()`. No engeapp não há nenhum uso de `scopeBindings()` hoje, portanto o vínculo pai-filho precisa ser feito explicitamente: consulte o filho a partir da relação do pai (`$project->documents()->findOrFail($id)`) ou aplique uma Policy.
- **Autorização Estrita via Policies e Gates**: Valide as permissões em cada requisição de acesso a recurso. Use `$this->authorize('view', $model)` ou `Gate::authorize()` dentro das actions do controller. No engeapp a cobertura por Policy é pequena (apenas `ClientPolicy` e `ProjectPolicy`, com 7 chamadas a `authorize(` nos controllers) — a camada de autorização efetiva é o `spatie/laravel-permission` (trait `HasRoles` em `App\Models\User`), via `hasRole()`/`hasPermissionTo()`, gates de permissão e middleware `can:`. Ao endurecer um endpoint, verifique qual das duas camadas realmente protege aquele recurso.
- **Endpoints públicos**: Audite rotas sem middleware de auth. Exemplo concreto a proteger: `routes/api.php` expõe `Route::post('project/data', ...)` e a versão GET equivalente sem nenhum middleware `auth`, permitindo leitura de dados de projeto por qualquer chamador.
- **UUIDs/ULIDs para Identificadores Públicos**: Evite expor IDs inteiros auto-incrementais nas URLs. Prefira ULIDs/UUIDs (como a trait `HasUlids`) para as chaves primárias/de rota dos models.

### 4. Sanitização de Entrada e Prevenção de XSS
- **Escaping do Blade**: Confie nas chaves duplas do Blade `{{ $variable }}`, que escapam automaticamente a saída usando `htmlspecialchars`. Use `{!! $variable !!}` SOMENTE com rich text verificado e sanitizado e nunca com entrada direta do usuário.
- **Form Requests**: Filtre e sanitize a entrada dentro de Form Requests dedicadas. Defina regras de validação estritas (por exemplo, `email`, `url`, `integer`, `string`, `max`).

### 5. Uploads de Arquivo Seguros
- **Validação**: Imponha verificações de mime-type, extensão e tamanho de arquivo. Por exemplo, `['required', 'file', 'mimes:pdf,png,jpg,jpeg', 'max:20480']` (padrão de `app/Http/Requests/Integrador/StoreDocumentRequest.php`). Hoje pouquíssimos Form Requests do engeapp validam `mimes:` — ao tocar em um endpoint de upload, adicione essa validação.
- **Armazenamento (padrão real do engeapp)**: O projeto grava predominantemente com `Storage::disk($disk)->put(...)` em discos locais segmentados por domínio, definidos em `config/filesystems.php` (`public`, `bugs`, `image`, `images`, `brand`, `private`, `certificates`, `projects`, `normas`, `whatsapp`, ...), além do `spatie/laravel-medialibrary` (`InteractsWithMedia`) para models com anexos. Arquivos públicos são servidos pelo symlink `public_path('storage') => storage_path('app/public')` declarado em `'links'`. Prefira o disco de domínio correto e mantenha em disco privado tudo que não precisa ser público.
- **Nome do arquivo**: Nunca persista o nome original enviado pelo usuário. Gere o nome (hash/ULID) — `->store('pasta', 'disco')` já faz isso e é usado nos uploads do Calendar — ou passe um nome gerado explicitamente ao `put()`.
- **Caminhos Não Executáveis**: Garanta que a configuração do servidor impeça a execução de scripts (PHP) nas pastas de upload e no diretório apontado pelo symlink `storage`. Nota: o disco `s3` existe em `config/filesystems.php`, mas não é usado pelos uploads do projeto — não escreva código assumindo S3/MinIO.

### 6. CSRF, CORS e Cabeçalhos de Segurança
- **Validação de Token CSRF**: Garanta que a proteção CSRF esteja ativa para todas as requisições que alteram estado (POST, PUT, PATCH, DELETE). No engeapp as isenções ficam em `bootstrap/app.php`, no `$middleware->validateCsrfTokens(except: [...])` (estilo Laravel 11+), hoje com `'onlyoffice/callback/*'`, `'voip/webhook'` e `'voip/agent/result'`. Isente apenas webhooks de integração externa, sob correspondência estrita de URL, e adicione a isenção nesse mesmo array — nunca desabilite o middleware globalmente.
- **Sessões Seguras**: Não hardcode nada em `config/session.php` — ele já resolve os valores via `env()`. Defina no `.env` de produção `SESSION_SECURE_COOKIE=true`, `SESSION_HTTP_ONLY=true` e `SESSION_SAME_SITE=lax` (ou `strict`). O `same_site` é um controle anti-CSRF relevante: `lax`/`strict` impedem que o cookie de sessão viaje em requisições cross-site, e `none` só deve ser usado com `secure` ativo e motivo explícito.
- **Configuração de CORS**: Limite origens, cabeçalhos e métodos em `config/cors.php` apenas àqueles explicitamente necessários.

### 7. Tratamento Seguro de Exceções e Logging
- **Segurança em Produção**: Garanta que `app.debug` seja `false` em produção.
- **Logs Sanitizados**: Mascare credenciais e segredos nos logs. Não registre senhas, tokens ou identificadores pessoais em texto plano. Use padrões de logging estruturado.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- NUNCA use entrada não validada em queries de banco de dados ou caminhos do sistema de arquivos.
- NUNCA deixe `app.debug` habilitado em ambientes de produção.
- NUNCA ignore policies ou verificações de autorização por conveniência durante operações de banco de dados ou desenvolvimento de API.
- NUNCA use concatenação bruta de strings em métodos SQL raw (`DB::raw()`, `whereRaw()`, etc.).
