# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or debugging Laravel Mailables, Markdown emails, system Notifications (database, mail, custom channels), or configuring queueing behavior for emails and notifications. Triggers on new Mailable, Mailable envelope/content config, Notification class creation, database notifications, and queueing notifications.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp necessita de padrões modernos para o envio de e-mails (ex: recuperação de senha, alertas de sistema) e notificações internas no banco de dados, alinhados com o Laravel v13 (Envelope/Content, PHP 8 Constructor Property Promotion) e processamento assíncrono seguro.
* **Recursos:**
  - Convenções para Mailables modernos usando as classes `Envelope` e `Content` da API atual do Laravel.
  - Configuração do comportamento assíncrono via `ShouldQueue` com definição correta de filas dedicadas.
  - Estruturação de Notifications multicanais (principalmente `database` e `mail`).
  - Utilização rigorosa de `Constructor Property Promotion` do PHP 8.5 para injeção de dependências.
  - Criação de templates responsivos e limpos com Blade e Markdown.
* **Objetivo:** Estabelecer diretrizes e padrões claros para o desenvolvimento e manutenção de Mailables e Notifications no ecossistema Engeapp/Laravel.
* **Casos de uso:**
  - Envio de e-mail de recuperação de senha ou confirmação de conta.
  - Notificação em tempo real salva no banco de dados para exibição no painel da aplicação (Inertia/Vue).
  - Alertas automáticos do sistema disparados por eventos.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizada para garantir a injeção e tipagem correta de instâncias Eloquent nos e-mails e notificações, aplicando a trait `SerializesModels`.
  - `laravel-jobs-queues-horizon-best-practices` — Utilizada para garantir que o enfileiramento dos disparos de e-mail/notificação siga as regras de retry, backoff e controle de concorrência.
  - `laravel-code-generators-best-practices` — Utilizada para padronizar constantes de canais de notificação ou status de leitura.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Modernização do código legado de envio de e-mail (substituição do método `build` legado), garantia de performance ao descarregar envios pesados de SMTP para filas de background, facilidade de depuração e consistência visual nas comunicações geradas pela plataforma.
