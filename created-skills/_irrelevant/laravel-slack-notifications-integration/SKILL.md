---
name: laravel-slack-notifications-integration
description: Use when creating, reviewing, or debugging Laravel Slack notifications, configuring Slack Webhook channels, handling Slack notification routing, or custom slack block formatting. Triggers on Slack notification setup, webhooks configuration, or message layout changes.
---

# Integração de Notificações do Slack no Laravel

## Objetivo
Estabelecer diretrizes claras, padrões de configuração e boas práticas para criar, enviar, formatar e testar notificações do Slack dentro do backend Laravel do ecossistema Engeapp.

## Instruções

### 1. Configuração Inicial
Sempre armazene as credenciais do Slack e os canais padrão de forma segura dentro do arquivo `config/services.php`. Não acesse variáveis de ambiente diretamente no código da aplicação.

- **Configuração Padrão de Notificação do Slack:**
  Configure o array de services em `config/services.php`:
  ```php
  'slack' => [
      'notifications' => [
          'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
          'channel'              => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
      ],
  ],
  ```

- **Configuração Alternativa de Incoming Webhook:**
  Se a aplicação usar uma única URL de incoming webhook:
  ```php
  'slack' => [
      'webhook' => env('SLACK_WEBHOOK_URL'),
  ],
  ```

### 2. Criando uma Classe de Notificação
Gere a classe de notificação usando o Artisan CLI:
```bash
php artisan make:notification CriticalErrorSlackAlert
```

Implemente a estrutura da notificação:
- Implemente o método `via($notifiable)` para rotear através de `['slack']`.
- Implemente `toSlack($notifiable)` retornando uma instância de `Illuminate\Notifications\Messages\SlackMessage`.
- Implemente a interface `ShouldQueue` para garantir que as chamadas à API de notificação sejam executadas em filas em background.

### 3. Formatação Rica com Slack Message / Block Kit
Formate as notificações do Slack para parecerem altamente profissionais usando títulos, attachments, fields e cores customizadas:

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Slack\BlockKit\Blocks\SectionBlock;
use Illuminate\Notifications\Slack\SlackMessage;
use Illuminate\Notifications\Notification;

class CriticalErrorSlackAlert extends Notification implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;
    public int $backoff = 60;

    public function __construct(
        protected string $message,
        protected string $fileName,
        protected int $line
    ) {}

    public function via(mixed $notifiable): array
    {
        return ['slack'];
    }

    public function toSlack(mixed $notifiable): SlackMessage
    {
        return (new SlackMessage)
            ->headerBlock('🚨 Critical AI Process Failure Detected!')
            ->sectionBlock(function (SectionBlock $block) {
                $block->text("*Error Message:* {$this->message}");
            })
            ->sectionBlock(function (SectionBlock $block) {
                $block->field("*File Location:*\n{$this->fileName} (Line {$this->line})")->markdown();
                $block->field('*Environment:*\n' . config('app.env'))->markdown();
            });
    }
}
```

### 4. Tratando Falhas e Resiliência
- Sempre enfileire (queue) as notificações do Slack. As requisições à API de terceiros do Slack podem adicionar latência ou falhar temporariamente devido a rate limits ou indisponibilidade.
- Defina as propriedades de classe para as políticas de rate limiting e retry de conexão:
  - `public int $tries = 3;` — Número máximo de tentativas de execução.
  - `public int $backoff = 60;` — Tempo em segundos para aguardar antes de repetir uma tentativa que falhou.

### 5. Testes e Mocking (Pest v3)
Use os fakes nativos da facade `Notification` do Laravel nas suítes de teste para afirmar que as notificações do Slack são roteadas corretamente sem fazer requisições HTTP reais.

```php
<?php

use App\Notifications\CriticalErrorSlackAlert;
use Illuminate\Support\Facades\Notification;
use Illuminate\Notifications\AnonymousNotifiable;
use Illuminate\Notifications\Slack\SlackMessage;

it('sends a critical slack notification on process failure', function () {
    Notification::fake();

    // Dispara a lógica que lança/despacha a notificação de erro
    $errorMessage = 'API key expired';
    $file = 'AiAgent.php';
    $line = 42;

    // Simula o envio da notificação para um canal de roteamento customizado
    Notification::route('slack', config('services.slack.notifications.channel'))
        ->notify(new CriticalErrorSlackAlert($errorMessage, $file, $line));

    Notification::assertSentTo(
        new AnonymousNotifiable,
        CriticalErrorSlackAlert::class,
        function ($notification, $channels) use ($errorMessage) {
            return in_array('slack', $channels) && $notification->toSlack(null) instanceof SlackMessage;
        }
    );
});
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **Sem Valores Hardcoded:** Nunca escreva URLs de webhook, tokens do Slack ou nomes de canal padrão diretamente dentro das classes de notificação. Sempre os carregue via `config('services.slack...')`.
- **Sempre Enfileire:** Nunca envie notificações do Slack de forma síncrona em requisições de controller voltadas ao cliente. Sempre implemente `ShouldQueue`.
- **Mantenha os Payloads Limpos:** Não despeje arrays gigantescos de trace bruto de exceção diretamente no texto da mensagem do Slack. Formate apenas os resumos-chave de erro em fields de attachment estruturados.
- **Use os Fakes Nativos de Teste:** Não use Guzzle ou clientes HTTP customizados para enviar mensagens do Slack diretamente, e não escreva hooks de mock HTTP customizados nos testes quando `Notification::fake()` existe.
