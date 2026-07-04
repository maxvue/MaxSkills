---
name: laravel-backup-best-practices
description: Use when configuring, executing, testing, or debugging backups in Laravel, setting up spatie/laravel-backup, managing backup destinations, defining backup schedules, or handling backup failure alerts.
---

# Boas Práticas de Backup no Laravel

## Objetivo
Estabelecer diretrizes sólidas, seguras e automatizadas para backup de bancos de dados e arquivos da aplicação dentro do ecossistema Laravel (especificamente para o Engeapp), garantindo continuidade do negócio e capacidade de recuperação de desastres.

## Instruções

### 1. Instalação e Configuração Inicial
1. **Instale o Spatie Laravel Backup:**
   Se o pacote não estiver instalado, instale-o usando o Composer:
   ```bash
   composer require spatie/laravel-backup
   ```
2. **Publique a Configuração:**
   Publique o arquivo de configuração do pacote:
   ```bash
   php artisan vendor:publish --provider="Spatie\Backup\BackupServiceProvider"
   ```
   Isso gera o `config/backup.php`.

### 2. Configuração do Backup (`config/backup.php`)
1. **Configuração de Origem (`backup.source`):**
   - **Banco de Dados:** Garanta que todas as conexões de banco relevantes estejam selecionadas (normalmente `mysql` ou `pgsql`).
   - **Arquivos:** Limite os backups a arquivos essenciais, como uploads dinâmicos de usuários (ex: `storage/app/public`). Exclua `node_modules/`, `vendor/`, `storage/framework/` e diretórios de cache para reduzir o tamanho dos arquivos.
2. **Configuração de Destino (`backup.destination`):**
   - Configure discos para armazenamento de backups. Evite armazenar backups apenas no mesmo servidor (disco `local`).
   - Use destinos externos como AWS S3 (`s3`) ou WebDAV (`webdav`).
   - Obtenha todas as credenciais de disco estritamente a partir de variáveis de ambiente (`.env`).
3. **Políticas de Retenção (`backup.cleanup`):**
   - Defina uma estratégia de limpeza para remover automaticamente backups antigos e evitar o esgotamento do armazenamento.
   - Política recomendada: Manter backups diários por 7 dias, backups semanais por 4 semanas, backups mensais por 4 meses e backups anuais por 2 anos.

### 3. Agendamento de Backup
1. **Comandos Artisan:**
   - Executar limpeza: `php artisan backup:clean`
   - Executar backup: `php artisan backup:run` (ou `--only-db` para fazer backup apenas do banco de dados).
2. **Scheduler do Console:**
   - Registre os comandos em `routes/console.php` (Laravel 11+) ou `app/Console/Kernel.php`:
     ```php
     use Illuminate\Support\Facades\Schedule;

     // Limpa backups antigos diariamente à 1:00 da manhã
     Schedule::command('backup:clean')->daily()->at('01:00');

     // Executa backup de banco de dados e arquivos diariamente às 2:00 da manhã
     Schedule::command('backup:run')->daily()->at('02:00');
     ```
   - Alternativamente, configure essas tarefas pelo dashboard do **Laravel Totem**.

### 4. Logs e Notificações
1. **Log Estruturado de Exceções:**
   - Integre as notificações do Spatie Backup com canais de notificação (Mail, Slack, Discord ou Telegram) configurando `backup.notifications` dentro de `config/backup.php`.
   - Garanta que a configuração de logging do Laravel (`config/logging.php`) registre o status e as falhas de backup usando contexto estruturado (ex: incluindo o disco de armazenamento e o tamanho do backup).
2. **Monitoramento de Saúde:**
   - Execute `php artisan backup:monitor` periodicamente ou agende-o para garantir que os arquivos de backup estejam atualizados e os destinos acessíveis.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Segurança:** Não escreva nem faça commit de credenciais, chaves da AWS ou senhas de WebDAV diretamente em `config/backup.php` ou `config/filesystems.php`. Use o `.env` e os helpers `env()`.
- **Privacidade:** Nunca inclua arquivos de ambiente sensíveis em tempo de execução (como o `.env`) ou chaves privadas (`oauth-private.key`) no zip de backup. Exclua-os explicitamente em `config/backup.php`.
- **Localização:** Não armazene backups no diretório `public/` ou em qualquer caminho acessível pela web.
- **Gerenciamento de Recursos:** Evite executar backups completos de arquivos durante os horários de pico de uso do sistema. Prefira agendamentos na madrugada para backups completos.
