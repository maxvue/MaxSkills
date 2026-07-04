---
name: laravel-cloud-storage-integrations
description: Use when configuring, implementing, or debugging cloud storage integrations in Laravel. Triggers on Storage facade calls, disk configuration, file uploads, pre-signed URLs, WebDAV file streams, and AWS S3/MinIO/Cloudflare R2/WebDAV setups.
---

# Boas Práticas de Integrações com Cloud Storage no Laravel

## Objetivo
Fornecer diretrizes sólidas, padrões consistentes e padrões arquiteturais para configurar, integrar, testar e manter cloud storage (AWS S3, MinIO, Cloudflare R2 e servidores WebDAV como Nextcloud/ownCloud/Seafile) de forma segura e escalável dentro do Laravel.

## Instruções

### 1. Configuração (config/filesystems.php)
* **S3/MinIO/R2:** Use o driver nativo `s3` do Laravel. Aproveite as variáveis de ambiente. Para MinIO local, `AWS_USE_PATH_STYLE_ENDPOINT` deve ser `true`. Para Cloudflare R2, defina como `false`.
* **WebDAV:** Configure os parâmetros de conexão (URL, username, password). Registre um driver customizado em um Service Provider usando `league/flysystem-webdav` e `Sabre\DAV\Client`, encapsulando-o em `Storage::extend('webdav', ...)`.

### 2. Processamento de Arquivos Grandes e Streams
* **Nunca** carregue arquivos grandes inteiros na memória do PHP usando `file_get_contents()` ou `Storage::get()`.
* **Uploads:** Use `Storage::disk('s3')->putFile()` ou stream resources (`Storage::disk('webdav')->writeStream('path', $localStream)`).
* **Downloads:** Faça stream de arquivos remotos para arquivos locais usando `Storage::disk('disk')->readStream()`.

### 3. Incompatibilidade de Caminhos Remotos
* Drivers remotos como o WebDAV não mapeiam para caminhos de arquivo locais. `Storage::disk('webdav')->path()` lançará uma exceção.
* Se caminhos locais forem necessários (ex: para geração de PDF), baixe o arquivo localmente para um diretório temporário, processe-o e limpe depois.

### 4. Segurança de Arquivos e URLs Pré-assinadas (S3)
* Mantenha todos os buckets e arquivos privados por padrão.
* Gere URLs temporárias e pré-assinadas (`Storage::disk('s3')->temporaryUrl()`) ao conceder acesso a documentos sensíveis.

### 5. Tratamento de Exceções, Logging e Testes
* **Resiliência:** Falhas de rede e timeouts são comuns. Envolva as operações de storage em blocos try-catch e registre contextos de erro descritivos.
* **Testes:** Nunca faça chamadas HTTP reais a provedores de storage externos durante a execução da suíte de testes. Sempre use `Storage::fake('s3')` ou equivalente para fazer o mock do disco.

### 6. Integração com o Spatie Media Library
* Defina o disco de destino correto diretamente no registro das media collections do seu model (`->useDisk('s3')` ou `->useDisk('webdav')`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **SEM Credenciais no Controle de Versão:** Nunca deixe chaves ou credenciais AWS/WebDAV hardcoded. Use `env()` ou `config()`.
* **SEM Storage Local em Produção para Arquivos de Usuário:** Não armazene assets enviados por usuários nos discos `local` ou `public`. Direcione para um disco em nuvem.
* **SEM Chamadas de Rede Reais em Testes:** Faça o mock do filesystem com `Storage::fake()`.
* **NUNCA chame `Storage::disk('webdav')->path()`:** Use a resolução de arquivos temporários locais via streams.
* **NUNCA carregue arquivos grandes inteiros na memória:** Sempre implemente `readStream()` e `writeStream()`.
