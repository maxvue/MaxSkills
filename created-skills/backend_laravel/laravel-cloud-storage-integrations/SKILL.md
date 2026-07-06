---
name: laravel-cloud-storage-integrations
description: Use ao configurar, implementar ou depurar integrações de armazenamento remoto no Laravel. O caso concreto do engeapp é Seafile via WebDAV (driver customizado 'seafile' em AppServiceProvider, credenciais em config('filesystems.seafile'), disco 'projects' do Spatie Media Library). Cobre streams de arquivos grandes, incompatibilidade de path() em discos remotos e S3/MinIO/R2 como orientação genérica.
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

### 2. Processamento de Arquivos Grandes e Streams
* **Nunca** carregue arquivos grandes inteiros na memória com `file_get_contents()` ou `Storage::get()`.
* **Uploads:** Use stream resources — `Storage::disk('projects')->writeStream('caminho', $streamLocal)` — ou `putFile()`.
* **Downloads:** Faça stream do arquivo remoto para um arquivo local com `Storage::disk($disk)->readStream()`.

### 3. Incompatibilidade de path() em discos remotos
* Enquanto um disco usa `driver => 'local'` (como o `projects` hoje), `Storage::disk(...)->path()` funciona — e o código depende disso (ex.: `Project::getPathAttribute()`, `hash_file`, `pathinfo`).
* Ao migrar um disco para `driver => 'seafile'` (WebDAV), `path()` deixa de fazer sentido e lançará exceção — o adapter remoto não mapeia caminhos locais. Antes de migrar, substitua cada `->path()` por uma cópia temporária local: baixe via `readStream()` para um diretório temporário, processe (ex.: geração de PDF, hashing) e limpe depois.

### 4. Segurança de Arquivos e URLs Temporárias
* Mantenha arquivos de projeto privados por padrão (os discos de projeto vivem em `app/private/...`).
* Se e quando usar S3, conceda acesso a documentos sensíveis via `temporaryUrl()` (URLs pré-assinadas), nunca tornando o bucket público. WebDAV/Seafile não oferece URL pré-assinada — sirva o arquivo pela aplicação após autorizar.

### 5. Tratamento de Exceções, Logging e Testes
* **Resiliência:** Falhas de rede e timeouts são comuns em WebDAV. Envolva operações de storage em try-catch e registre contexto de erro descritivo.
* **Testes:** Nunca faça chamadas HTTP reais ao Seafile/S3 na suíte. Use `Storage::fake('projects')` (ou o disco alvo) para mockar o disco.

### 6. Integração com o Spatie Media Library
* Defina o disco de destino no registro das media collections do model. No engeapp, `Project` usa `->useDisk('projects')` para as collections `documents`, `photos` e `inspections` (`App\Models\Project\Project::registerMediaCollections()`).
* Ao apontar collections para um disco `seafile`, revise conversões que dependam de caminho local (ver seção 3).
* Para regras aprofundadas de media library (conversões, responsividade, coleções), consulte a skill dedicada **laravel-media-library-best-practices** em vez de duplicar aqui.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
* **SEM Credenciais no Controle de Versão:** Nunca deixe credenciais Seafile/AWS hardcoded. Use `env()`/`config()`, centralizadas em `config('filesystems.seafile')`.
* **SEM Storage Local em Produção para Arquivos de Usuário:** O alvo é migrar arquivos de projeto para Seafile. Evite deixar assets de usuário apenas em `local`/`public` a longo prazo.
* **SEM Chamadas de Rede Reais em Testes:** Mocke o filesystem com `Storage::fake()`.
* **path() em disco remoto:** Não chame `->path()` em discos `driver => 'seafile'`; resolva via arquivo temporário local a partir de `readStream()`.
* **NUNCA carregue arquivos grandes inteiros na memória:** Sempre use `readStream()`/`writeStream()`.
