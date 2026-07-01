# PROPOSTA DE SKILL: laravel-pail-realtime-logging

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when debugging application logs in real-time, tailing logs via Laravel Pail, filtering logs by context, tags, or exceptions in the console, and debugging backend execution issues.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui múltiplos fluxos assíncronos (Jobs, WebSockets, consumo de APIs externas e webhooks). A inspeção manual de arquivos em `storage/logs/laravel.log` é lenta e ineficiente em ambiente de desenvolvimento. O Laravel Pail resolve isso permitindo o streaming e a filtragem de logs em tempo real diretamente no console.
* **Recursos:** Execução e monitoramento com `php artisan pail`, uso estratégico de filtros por tag/User ID (`--user`), filtros por tipo de exceção (`--filter`), controle de níveis de verbosidade no terminal, e integração com logs estruturados do Laravel.
* **Objetivo:** Estabelecer diretrizes consistentes e práticas recomendadas para o monitoramento ativo e depuração rápida de falhas em tempo real usando o Laravel Pail no desenvolvimento do backend Engeapp.
* **Casos de uso:** Rastrear falhas de disparos de Jobs ou consumo de webhooks em tempo real, monitorar respostas de integrações de API locais e capturar stack traces sem a necessidade de abrir arquivos físicos de log.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará as definições de logs estruturados e exceções personalizadas para filtrar e exibir informações ricas e contextuais no terminal com o Laravel Pail.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Agilidade extrema no diagnóstico de falhas em desenvolvimento local, redução no tempo de depuração e melhor visualização do fluxo de execução do backend.
