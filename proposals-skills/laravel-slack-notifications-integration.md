# PROPOSTA DE SKILL: laravel-slack-notifications-integration

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging Laravel Slack notifications, configuring Slack Webhook channels, handling Slack notification routing, or custom slack block formatting. Triggers on Slack notification setup, webhooks configuration, or message layout changes.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp necessita de uma abordagem consistente e segura para enviar notificações internas em tempo real, alertas de erro de IA e resumos operacionais automáticos para canais específicos do Slack.
* **Recursos:** Configuração segura de canais/webhooks no `config/services.php`, criação de classes de notificação usando o canal do Slack, formatação rica utilizando blocos (Slack Block Kit), tratamento de falhas de rede no envio e mocking em testes com Pest.
* **Objetivo:** Estabelecer diretrizes e padrões de melhores práticas para a integração e envio de notificações para o Slack no backend Laravel.
* **Casos de uso:** Alertas instantâneos para falhas críticas de processamento nos agentes de IA, notificações de logs operacionais de homologação com concessionárias e notificações de transações financeiras suspeitas ou falhas de pagamento.
* **Workflows:**
  - `bug-fix-back-end`
  - `deploy`
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará as diretrizes de logging para acoplar o envio de mensagens do Slack a gatilhos de exceções críticas detectadas.
  - `laravel-services-best-practices` — Utilizará as convenções de arquitetura de serviços para centralizar e padronizar chamadas e controle de notificações no Engeapp.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Monitoramento ativo e em tempo real do sistema, diminuição do tempo de resposta das equipes operacionais sobre falhas críticas de IA e centralização de alertas.
