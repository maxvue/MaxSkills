# PROPOSTA DE SKILL: laravel-google-calendar-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when integrating, configuring, or debugging Google Calendar API operations in Laravel, including OAuth token management, event scheduling for technical visits, calendar sync, and webhook handling. Triggers on Spatie Google Calendar usage, API requests to Google Calendar, and event sync jobs.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp necessita de um fluxo automatizado e robusto para o agendamento de vistorias técnicas e reuniões de homologação, conectando eventos diretamente na agenda do Google Calendar dos engenheiros e integradores do ecossistema de forma resiliente e rastreável.
* **Recursos:** Configuração do SDK oficial do Google Client e pacote spatie/laravel-google-calendar, fluxo de autenticação de conta de serviço (Service Account) e OAuth do usuário, sincronização bidirecional de eventos, tratamento de limites de taxa (rate limiting), cacheamento de tokens e manipulação de erros com alertas apropriados.
* **Objetivo:** Fornecer diretrizes sólidas e padrões arquiteturais consistentes para integrar, gerenciar e depurar operações com a API do Google Calendar de forma segura e stateless no ecossistema Engeapp/Laravel.
* **Casos de uso:** Agendamento automático de vistorias técnicas no local da usina solar, agendamento de reuniões com concessionárias de energia, sincronização de prazos de homologação com agendas corporativas.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Utilizará as convenções de design de classes de serviços (Service Classes) e injeção de dependência para encapsular a lógica de comunicação com a API do Google Calendar.
  - `laravel-jobs-queues-horizon-best-practices` — Utilizará os padrões de filas para executar as chamadas de sincronização e criação de eventos em background de forma assíncrona e resiliente.
  - `laravel-exception-handling-logging` — Utilizará os padrões de log e tratamento de erros do projeto para registrar falhas de autenticação do Google e falhas de API sem causar travamentos silenciosos.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Automatização total das agendas de vistorias técnicas, redução de erros humanos de agendamento duplicado, controle centralizado de tokens de autenticação da API do Google, e garantia de operações semânticas resilientes no backend Laravel.
