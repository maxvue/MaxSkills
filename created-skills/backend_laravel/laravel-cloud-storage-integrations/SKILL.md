---
name: laravel-cloud-storage-integrations
description: "Use when configuring or debugging remote storage in Laravel. Covers Seafile WebDAV driver in AppServiceProvider, Seafile filesystems config, and Spatie Media Library projects disk."
---
# Boas Práticas de Integrações com Cloud Storage no Laravel

## Objetivo
Configurar, integrar, testar e manter armazenamento remoto de forma segura no engeapp. A stack real de nuvem do projeto é **Seafile via WebDAV** (driver customizado `seafile`, sobre `league/flysystem-webdav` + `Sabre\DAV\Client`). S3/MinIO/Cloudflare R2 aparecem aqui apenas como orientação genérica — o bloco `s3` em `config/filesystems.php` é o exemplo padrão do Laravel e não é usado no código.

## Contexto real do projeto (verifique antes de agir)
- `FILESYSTEM_DISK` default é `local` (`config/filesystems.php`). Quase todos os discos usam `driver => 'local'`.
- O driver customizado `seafile` é registrado em `App\Providers\AppServiceProvider::registerSeafileDriver()` via `Storage::extend('seafile', ...)`. Ele monta um `WebDAVAdapter` a partir de um `Sabre\DAV\Client`.
- As credenciais WebDAV ficam centralizadas em `config('filesystems.seafile')` (`SEAFILE_WEBDAV_URL/USERNAME/PASSWORD`). Cada disco que usar `driver => 'seafile'` herda essas credenciais e define seu próprio `root` como pathPrefix.
- Hoje o disco `projects` (usado pelo model `Project` e pelas media collections) tem `driver => 'local'` (`storage_path('app/private/projects')`). A infraestrutura Seafile está pronta, mas a migração dos discos para `driver => 'seafile'` é o alvo — leia os pontos de `path()` abaixo antes de migrar.

## Instruções

### 1. Configuração de discos (config/filesystems.php)
* **Seafile/WebDAV (caso real):** Não crie um disco chamado `webdav`. Registre o driver customizado uma única vez em um Service Provider com `Storage::extend('seafile', ...)`, encapsulando `league/flysystem-webdav` (`WebDAVAdapter`) sobre `Sabre\DAV\Client`. Nos discos, use `driver => 'seafile'` e um `root` próprio; mantenha as credenciais em `config('filesystems.seafile')`, nunca por disco.
* **S3/MinIO/R2 (genérico):** Se algum dia forem adotados, use o driver nativo `s3`. Para MinIO local, `AWS_USE_PATH_STYLE_ENDPOINT` = `true`; para Cloudflare R2, `false`. Não trate o bloco `s3` atual como integração ativa.

### 2. Processamento de Arquivos Grandes e Cópia Local
* **Padrão real do projeto:** use as helpers globais `resolveLocalDiskPath($diskName, $fileName)` e `saveToRemoteDisk($diskName, $relativePath, $content)` de `app/Helpers/FilesHelpers.php` em vez de chamar `->path()`/`file_get_contents()`/`file_put_contents()` diretamente ou reimplementar download temporário. Elas já fazem o branch por driver (`local` vs remoto), cache estático por requisição (`$_resolvedDiskPaths`) e limpeza (`cleanupResolvedDiskPaths()`).
* O caminho real para disco remoto hoje lê o conteúdo inteiro via `Storage::disk($diskName)->get($fileName)` (é assim que `resolveLocalDiskPath()` e `App\Classes\PdfEdit` — linhas 89-94 — funcionam). `readStream()`/`writeStream()` são recomendação genérica de streaming para arquivos muito grandes, ainda não adotada no código — não os apresente como padrão vigente do projeto.

### 3. Incompatibilidade de path() em discos remotos
* Enquanto um disco usa `driver => 'local'` (como o `projects` hoje), `Storage::disk(...)->path()` funciona — e o código depende disso: `Project::getPathAttribute()` (`app/Models/Project/Project.php:414`), `hash_file('sha512', ...->path($file))` (linha 503) e `pathinfo(...->path($file), PATHINFO_EXTENSION)` (linha 526) são os 3 call sites reais a revisar antes de migrar.
* Ao migrar um disco para `driver => 'seafile'` (WebDAV), `path()` **não lança exceção** — todos os discos têm `'throw' => false` em `config/filesystems.php`, e o adapter (`FilesystemAdapter::path()`) apenas devolve `$this->prefixer->prefixPath($path)` sem checar o driver. O resultado é um caminho prefixado sem sentido para o WebDAVAdapter: um bug silencioso, mais perigoso que uma exceção. Antes de migrar, substitua cada `->path()` pelas helpers da seção 2 (`resolveLocalDiskPath()` para leitura, `saveToRemoteDisk()` para escrita).

### 4. Segurança de Arquivos e URLs Temporárias
* Mantenha arquivos de projeto privados por padrão (os discos de projeto vivem em `app/private/...`).
* `temporaryUrl()` já é usado hoje em disco arbitrário: `File::getTempUrlAttribute()` (`app/Models/File/File.php:326`) chama `Storage::disk($this->disk)->temporaryUrl($this->relative_path, now()->addMinutes(10))`, o que funciona em discos locais com `'serve' => true` (ex.: os discos `image` e `images` em `config/filesystems.php`). Atenção ao migrar esse disco para `driver => 'seafile'`: o `WebDAVAdapter` não implementa `temporaryUrl()`, quebrando esse acessor — nesse caso, sirva o arquivo pela aplicação após autorização em vez de gerar URL pré-assinada.

### 5. Tratamento de Exceções, Logging e Testes
* **Resiliência:** Falhas de rede e timeouts são comuns em WebDAV. Envolva operações de storage em try-catch e registre contexto de erro descritivo.
* **Testes:** Nunca faça chamadas HTTP reais ao Seafile/S3 na suíte. Use `Storage::fake('projects')` (ou o disco alvo) para mockar o disco.

### 6. Integração com o Spatie Media Library
* Defina o disco de destino no registro das media collections do model. No engeapp, `Project` usa `->useDisk('projects')` para as collections `documents`, `photos` e `inspections` (`App\Models\Project\Project::registerMediaCollections()`).
* Ao apontar collections para um disco `seafile`, revise conversões que dependam de caminho local (ver seção 3).
* Para regras aprofundadas de media library (conversões, responsividade, coleções), consulte a skill dedicada **laravel-media-library-best-practices** em vez de duplicar aqui.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
* **SEM Storage Local em Produção para Arquivos de Usuário:** O alvo é migrar arquivos de projeto para Seafile. Evite deixar assets de usuário apenas em `local`/`public` a longo prazo.
