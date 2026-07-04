---
name: laravel-deployer-deployment-best-practices
description: Use when reviewing, configuring, or debugging Deployer PHP settings (deploy.php), managing server deployments, configuring shared files or directories, customizing rsync exclusions, or troubleshooting deployment/rollback issues.
---

# Boas Práticas de Deploy com Laravel Deployer

## Objetivo
Fornecer diretrizes sólidas, seguras e padronizadas para configurar, manter, depurar e executar deploys usando o Deployer CLI (deploy.php) no ecossistema Laravel do Engeapp.

## Instruções
1. **Configuração de Host**:
   - Garanta que os parâmetros de conexão SSH estejam explicitamente definidos (host, user, port, deploy_path).
   - Use chaves SSH para autenticação; nunca incorpore senhas ou tokens sensíveis diretamente no `deploy.php`.
   - Configure diferentes estágios ou labels (por exemplo, `production`, `staging`) usando os métodos de configuração de host do Deployer.

2. **Upload via Rsync e Exclusões**:
   - Como o Engeapp usa rsync para enviar as alterações ao servidor em vez de puxar do Git, mantenha uma lista precisa de arquivos e diretórios excluídos.
   - A opção `.rsync_exclude` ou `rsync` no `deploy.php` deve excluir arquivos de ambiente (`.env`), caches locais, módulos do Node (`node_modules`), dependências PHP (`vendor`, se construídas no host), configurações de IDE (`.idea`, `.vscode`) e uploads de storage local (`storage/app/*`, `storage/framework/cache/*`, etc.).
   - Certifique-se de que os diretórios de build local (como `public/build` ou assets construídos pelo Vite) sejam compilados localmente antes da execução do rsync e sejam incluídos com sucesso no upload.

3. **Arquivos e Diretórios Compartilhados**:
   - Mapeie caminhos persistentes que devem sobreviver entre releases usando `shared_dirs` e `shared_files`.
   - **Arquivos Compartilhados**: `.env` é o principal arquivo compartilhado.
   - **Diretórios Compartilhados**: Inclua `storage/app`, `storage/framework/sessions`, `storage/framework/views`, `storage/framework/cache` e `storage/logs`.
   - Nunca sobrescreva esses mapeamentos compartilhados sem aprovação explícita.

4. **Caminhos Graváveis e Permissões**:
   - Garanta que o usuário do servidor tenha permissões de escrita para as pastas compartilhadas, especialmente `storage` e `bootstrap/cache`.
   - Defina a opção `writable_dirs` para incluir esses diretórios e especifique o `writable_mode` (por exemplo, `chmod`, `chown` ou `acl`) apropriado para o ambiente do servidor de destino.

5. **Hooks de Deploy e Comandos Artisan**:
   - Configure hooks (`before`, `after`) para disparar tarefas específicas do Laravel.
   - Sempre execute a tarefa de migrations do banco durante o deploy: `after('deploy:shared', 'database:migrate');` (ou similar, dependendo da versão do Deployer).
   - Execute comandos de otimização e limpeza de cache após enviar o novo release:
     - `php artisan config:cache`
     - `php artisan route:cache`
     - `php artisan view:cache`
     - `php artisan event:cache`
     - `php artisan queue:restart` (se o Laravel Horizon ou workers de fila estiverem rodando)
   - Garanta que esses comandos sejam executados com a flag `--no-interaction`.

6. **Integração com Horizon e Reverb**:
   - Se a aplicação usa Laravel Horizon, execute `horizon:terminate` ou reinicie o serviço systemd para recarregar os processos workers com o código do novo release.
   - Se o Reverb for usado, recarregue o daemon se necessário.

7. **Troubleshooting e Rollbacks**:
   - Se uma etapa falhar, o Deployer interrompe automaticamente o deploy. Execute `dep rollback` para apontar o symlink `current` de volta ao release estável anterior.
   - Ao depurar erros de conexão SSH/rsync, verifique host keys, privilégios de usuário e rotas de rede local.
   - Use o modo verboso (`-vvv`) com o Deployer para rastrear tarefas específicas que estão falhando.

## Exemplos

### Configuração Padrão do deploy.php
```php
<?php
namespace Deployer;

require 'recipe/laravel.php';

// Nome do projeto
set('application', 'engeapp');

// Repositório do projeto (não usado se estiver usando upload via rsync)
set('repository', '');

// Arquivos/diretórios compartilhados entre deploys
add('shared_files', ['.env']);
add('shared_dirs', [
    'storage/app',
    'storage/framework/cache',
    'storage/framework/sessions',
    'storage/framework/views',
    'storage/logs',
]);

// Diretórios graváveis pelo servidor web
add('writable_dirs', [
    'bootstrap/cache',
    'storage',
    'storage/app',
    'storage/framework/cache',
    'storage/framework/sessions',
    'storage/framework/views',
    'storage/logs',
]);

// Hosts
host('production')
    ->set('hostname', 'prod.engeapp.com.br')
    ->set('remote_user', 'deploy')
    ->set('deploy_path', '/var/www/html/engeapp')
    ->set('rsync', [
        'exclude' => [
            '.git',
            '.idea',
            '.vscode',
            'node_modules',
            'vendor', // exclua se o vendor for construído no servidor, ou inclua se for enviado no upload
            '.env',
            'storage/framework/cache/*',
            'storage/logs/*',
        ],
        'exclude-file' => false,
        'include' => [],
        'include-file' => false,
        'filter' => [],
        'flags' => 'rz',
        'options' => ['delete'],
        'timeout' => 60,
    ]);

// Tarefas
task('deploy:upload', function () {
    upload('.', '{{release_path}}');
});

desc('Deploy your project');
task('deploy', [
    'deploy:info',
    'deploy:prepare',
    'deploy:lock',
    'deploy:release',
    'deploy:upload',
    'deploy:shared',
    'deploy:writable',
    'artisan:migrate',
    'artisan:config:cache',
    'artisan:route:cache',
    'artisan:view:cache',
    'deploy:symlink',
    'deploy:unlock',
    'deploy:cleanup',
    'success'
]);

// [Opcional] Caso o rollback falhe ou seja necessário um reload customizado
after('deploy:failed', 'deploy:unlock');
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** incorpore senhas ou credenciais brutas dentro do `deploy.php`. Use chaves SSH ou variáveis de ambiente.
- **NÃO** faça commit de `.env` ou logs locais nos hosts de produção.
- **NÃO** execute `artisan:migrate` ou comandos de otimização sem verificar se a conexão com o banco de dados de destino está ativa e estável.
- **NÃO** ignore o mecanismo de lock (`deploy:lock`), pois deploys paralelos corromperão os arquivos.
- **NÃO** faça upload de arquivos específicos de desenvolvimento (por exemplo, `tests/`, `.phpunit.result.cache`) para o servidor de produção.
