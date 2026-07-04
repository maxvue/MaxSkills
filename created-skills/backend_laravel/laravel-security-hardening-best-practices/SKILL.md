---
name: laravel-security-hardening-best-practices
description: Use when designing, reviewing, or debugging Laravel application security, securing Eloquent models (encryption, mass assignment), writing secure controllers, hardening file uploads, configuring security headers, or mitigating OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR).
---

# Boas Práticas de Hardening de Segurança no Laravel

## Objetivo
Estabelecer diretrizes robustas de segurança e práticas de hardening para o desenvolvimento backend no ecossistema Laravel do Engeapp. Isso previne vazamentos de dados, mitiga vulnerabilidades do OWASP Top 10, protege integrações e garante o manuseio seguro de arquivos.

## Instruções

### 1. Segurança de Models Eloquent
- **Criptografia de Campos Sensíveis**: Use o cast `'encrypted'` embutido do Laravel ou casting criptografado customizado para PII (Informações Pessoais Identificáveis) e chaves/tokens de APIs de terceiros. Sempre oculte essas colunas usando `$hidden` no model.
- **Proteção contra Mass Assignment**: Não use `protected $guarded = [];`. Declare explicitamente os atributos seguros no array `$fillable`.
- **Strict Loading e Prevenção de Lazy Loading**: Imponha regras estritas de segurança de model no `AppServiceProvider`.

### 2. Prevenção de SQL Injection (SQLi)
- **Consultas Parametrizadas**: Sempre use os bindings de parâmetro do Eloquent ou do query builder. Nunca concatene entrada do usuário diretamente em strings de query (por exemplo, em `whereRaw`, `selectRaw`, `orderByRaw`, `DB::statement`).
- **Expressões Raw Seguras**: Se o SQL bruto for inevitável, use métodos que de fato façam bind dos parâmetros: `DB::select('select * from users where id = ?', [$id])` para um SELECT bruto, ou bindings em array em uma condição do query builder: `->whereRaw('id = ?', [$id])`. Note que `DB::raw()` é apenas um fragmento de SQL sem escape — ele **não** aceita bindings e **não** parametriza, então a entrada do usuário NUNCA deve ser passada diretamente para ele.

### 3. Mitigação de IDOR (Insecure Direct Object References)
- **Scoped Route Model Binding**: Use scoped route model bindings quando um recurso filho pertence a um pai. Por exemplo, `Route::get('/projects/{project}/documents/{document}', ...)` garantirá automaticamente que o documento pertence ao projeto.
- **Autorização Estrita via Policies e Gates**: Valide as permissões em cada requisição de acesso a recurso. Sempre use `$this->authorize('view', $model)` ou `Gate::authorize()` dentro das actions do controller.
- **UUIDs/ULIDs para Identificadores Públicos**: Evite expor IDs inteiros auto-incrementais nas URLs. Prefira ULIDs/UUIDs (como a trait `HasUlids`) para as chaves primárias/de rota dos models.

### 4. Sanitização de Entrada e Prevenção de XSS
- **Escaping do Blade**: Confie nas chaves duplas do Blade `{{ $variable }}`, que escapam automaticamente a saída usando `htmlspecialchars`. Use `{!! $variable !!}` SOMENTE com rich text verificado e sanitizado e nunca com entrada direta do usuário.
- **Form Requests**: Filtre e sanitize a entrada dentro de Form Requests dedicadas. Defina regras de validação estritas (por exemplo, `email`, `url`, `integer`, `string`, `max`).

### 5. Uploads de Arquivo Seguros
- **Validação**: Imponha verificações de mime-type, extensão e tamanho de arquivo. Por exemplo, `required|file|mimes:pdf,jpg,png|max:10240`.
- **Armazenamento**: Nunca armazene arquivos enviados pelo usuário no diretório público com seus nomes originais. Use `$request->file('doc')->store('homologations')` para gerar automaticamente um nome de arquivo único e seguro.
- **Caminhos Não Executáveis**: Garanta que os arquivos enviados sejam armazenados em discos não executáveis (por exemplo, S3/MinIO) ou que a configuração do servidor impeça a execução de scripts na pasta de upload.

### 6. CSRF, CORS e Cabeçalhos de Segurança
- **Validação de Token CSRF**: Garanta que a proteção CSRF esteja ativa para todas as requisições que alteram estado (POST, PUT, PATCH, DELETE). Isente apenas webhooks (como callbacks de integração externa) sob correspondência estrita de URL.
- **Sessões Seguras**: Defina `'secure' => true` e `'http_only' => true` em `config/session.php`.
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
