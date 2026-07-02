---
name: laravel-deployer-deployment-best-practices
description: Use when reviewing, configuring, or debugging Deployer PHP settings (deploy.php), managing server deployments, configuring shared files or directories, customizing rsync exclusions, or troubleshooting deployment/rollback issues.
---

# Laravel Deployer Deployment Best Practices

## Goal
Provide solid, secure, and standardized guidelines for configuring, maintaining, debugging, and executing deployments using Deployer CLI (deploy.php) in the Engeapp Laravel ecosystem.

## Instructions
1. **Host Configuration**:
   - Ensure SSH connection parameters are explicitly defined (host, user, port, deploy_path).
   - Use SSH keys for authentication; never embed passwords or sensitive tokens directly in `deploy.php`.
   - Configure different stages or labels (e.g., `production`, `staging`) using Deployer's host configuration methods.

2. **Rsync Upload and Exclusions**:
   - Since Engeapp uses rsync to push changes to the server rather than pulling from Git, maintain a precise list of excluded files and directories.
   - The `.rsync_exclude` or `rsync` option in `deploy.php` must exclude environment files (`.env`), local caches, Node modules (`node_modules`), PHP dependencies (`vendor` if built on host), IDE settings (`.idea`, `.vscode`), and local storage uploads (`storage/app/*`, `storage/framework/cache/*`, etc.).
   - Make sure local build directories (like `public/build` or assets built by Vite) are compiled locally before rsync runs and are successfully included in the upload.

3. **Shared Files and Directories**:
   - Map persistent paths that must survive across releases using `shared_dirs` and `shared_files`.
   - **Shared Files**: `.env` is the primary shared file.
   - **Shared Directories**: Include `storage/app`, `storage/framework/sessions`, `storage/framework/views`, `storage/framework/cache`, and `storage/logs`.
   - Never override these shared mappings unless explicit approval is provided.

4. **Writable Paths and Permissions**:
   - Ensure the server user has write permissions for shared folders, especially `storage` and `bootstrap/cache`.
   - Set the `writable_dirs` option to include these directories, and specify the `writable_mode` (e.g., `chmod`, `chown`, or `acl`) appropriate for the target server's environment.

5. **Deployment Hooks and Artisan Commands**:
   - Configure hooks (`before`, `after`) to trigger Laravel-specific tasks.
   - Always run the database migrations task during deployment: `after('deploy:shared', 'database:migrate');` (or similar depending on the Deployer version).
   - Run optimization and cache clear commands after uploading the new release:
     - `php artisan config:cache`
     - `php artisan route:cache`
     - `php artisan view:cache`
     - `php artisan event:cache`
     - `php artisan queue:restart` (if Laravel Horizon or queue workers are running)
   - Ensure these commands are run with the `--no-interaction` flag.

6. **Horizon and Reverb Integration**:
   - If the application uses Laravel Horizon, execute `horizon:terminate` or restart the systemd service to reload worker processes with the new release code.
   - If Reverb is used, reload the daemon if needed.

7. **Troubleshooting and Rollbacks**:
   - If a step fails, Deployer automatically stops the deployment. Run `dep rollback` to point the `current` symlink back to the previous stable release.
   - When debugging SSH/rsync connection errors, check host keys, user privileges, and local network routes.
   - Use verbose mode (`-vvv`) with Deployer to trace specific failing tasks.

## Examples

### Standard deploy.php Configuration
```php
<?php
namespace Deployer;

require 'recipe/laravel.php';

// Project name
set('application', 'engeapp');

// Project repository (unused if using rsync-based upload)
set('repository', '');

// Shared files/dirs between deploys 
add('shared_files', ['.env']);
add('shared_dirs', [
    'storage/app',
    'storage/framework/cache',
    'storage/framework/sessions',
    'storage/framework/views',
    'storage/logs',
]);

// Writable dirs by web server 
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
            'vendor', // exclude if vendor is built on server, or include if uploaded
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

// Tasks
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

// [Optional] If rollback fails or custom reload is needed
after('deploy:failed', 'deploy:unlock');
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do NOT** embed raw passwords or credentials inside `deploy.php`. Use SSH keys or environment variables.
- **Do NOT** commit `.env` or local logs to production hosts.
- **Do NOT** run `artisan:migrate` or optimization commands without verifying the target database connection is active and stable.
- **Do NOT** bypass the lock mechanism (`deploy:lock`), as parallel deployments will corrupt files.
- **Do NOT** upload development-specific files (e.g. `tests/`, `.phpunit.result.cache`) to the production server.
