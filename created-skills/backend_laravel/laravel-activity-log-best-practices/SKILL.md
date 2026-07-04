---
name: laravel-activity-log-best-practices
description: Use when configuring, implementing, or debugging user activity logs, audit trails, or model change logs using spatie/laravel-activitylog. Triggers on tracking model events, storing custom log metadata, retrieving activity history for frontend views, and cleaning up old logs.
---

# Boas Práticas de Log de Atividades no Laravel

## Objetivo
Estabelecer diretrizes, convenções e padrões para rastreamento de atividades do usuário, auditoria de mudanças em models Eloquent e registro de atividades personalizadas usando o pacote `spatie/laravel-activitylog` no ecossistema Laravel do Engeapp. Garantir conformidade com os requisitos da LGPD, evitar problemas de queries N+1 durante a recuperação de logs e tratar corretamente eventos de personificação de usuário (impersonation).

## Instruções

0. **Instale primeiro (ainda não é dependência do projeto):** O `spatie/laravel-activitylog` **não** está atualmente no `composer.json` do engeapp. Antes de usá-lo, instale-o e configure-o:
   ```bash
   composer require spatie/laravel-activitylog
   php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-migrations"
   php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-config"
   php artisan migrate
   ```

1. **Log Automático em Models Eloquent**:
   - Importe a trait `LogsActivity` e a classe `LogOptions`.
   - Implemente o método `getActivitylogOptions()` para retornar um objeto `LogOptions` configurado.
   - Sempre encadeie `logOnly(['field1', 'field2'])` para especificar os campos explicitamente em vez de usar log com wildcard, evitando impactos de performance e registro indesejado de campos sensíveis.
   - Use `logOnlyDirty()` para registrar apenas as alterações realizadas.
   - Personalize o nome do log usando `useLogName('model-name')` para facilitar a filtragem.
   - Defina `dontSubmitEmptyLogs()` para evitar inserções vazias de atividade no banco de dados.
   - Exemplo:
     ```php
     use Spatie\Activitylog\Traits\LogsActivity;
     use Spatie\Activitylog\LogOptions;

     class Client extends Model
     {
         use LogsActivity;

         public function getActivitylogOptions(): LogOptions
         {
             return LogOptions::defaults()
                 ->logOnly(['name', 'document', 'status'])
                 ->logOnlyDirty()
                 ->dontSubmitEmptyLogs()
                 ->useLogName('clients');
         }
     }
     ```

2. **Tratamento de Personificação de Usuário (Impersonation)**:
   - Integre com o pacote `lab404/laravel-impersonate` (veja `laravel-user-impersonation-best-practices`).
   - Se um administrador estiver personificando um usuário, capture o ID real do personificador usando `app('impersonate')->getImpersonatorId()` e salve-o nas propriedades personalizadas.
   - Exemplo de helper para registrar propriedades personalizadas durante o boot do model ou manualmente:
     ```php
     activity()
         ->tap(function (Activity $activity) {
             if (app('impersonate')->isImpersonating()) {
                 $activity->setExtraProperty('impersonator_id', app('impersonate')->getImpersonatorId());
                 $activity->setExtraProperty('is_impersonated', true);
             }
         });
     ```

3. **Log de Atividades Personalizado**:
   - Para eventos que não fazem parte do ciclo de vida de um model (ex: login de usuário, exportação, acesso à API), registre manualmente usando o helper `activity()`.
   - Encadeie os métodos explicitamente: `performedOn()`, `causedBy()`, `withProperties()`, `log()`.
   - Exemplo:
     ```php
     activity()
         ->causedBy(auth()->user())
         ->withProperties(['ip' => request()->ip(), 'browser' => request()->userAgent()])
         ->log('User logged in successfully.');
     ```

4. **Recuperação Otimizada de Atividades**:
   - Sempre faça eager loading das relações `causer` e `subject` ao renderizar logs de atividade para evitar problemas de queries N+1.
   - Use queries paginadas para grandes conjuntos de logs.
   - Exemplo:
     ```php
     $logs = Activity::with(['causer', 'subject'])
         ->where('log_name', 'clients')
         ->latest()
         ->paginate(15);
     ```

5. **Manutenção e Limpeza do Banco de Dados de Logs**:
   - Configure a política de retenção de logs em `config/activitylog.php` usando `delete_records_older_than_days`.
   - Registre o comando de limpeza `activitylog:clean` para rodar diariamente no scheduler (`routes/console.php` no Laravel 13).
   - Exemplo:
     ```php
     use Illuminate\Support\Facades\Schedule;

     Schedule::command('activitylog:clean')->daily()->at('03:00');
     ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO use o wildcard `logAll()` em models. Especifique os campos explicitamente usando `logOnly()`.
- NÃO registre informações sensíveis (ex: senhas, dados de cartão de crédito, tokens de autenticação) em atributos de model ou propriedades personalizadas.
- NÃO consulte logs de atividade sem fazer eager loading das relações `causer` e `subject`.
- NÃO omita os metadados de personificação ao registrar ações realizadas durante sessões de impersonation.
