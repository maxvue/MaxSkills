# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying or reviewing Laravel Artisan commands. Triggers on command generation, signature updates, console I/O, error handling in commands, and scheduled tasks configuration.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O projeto possui dezenas de comandos Artisan (ex: sincronização, rotinas de limpeza, processamentos em batch) que demandam uma padronização em relação à assinatura, tratamento de erros no console, logs de execução e interações de I/O.
* **Recursos:** Padrões para definição de assinaturas, uso correto do Prompts (I/O interativo), tratamento de exceções amigáveis no console, exit codes (sucesso/falha) e isolamento de lógica complexa em Services/Actions.
* **Objetivo:** Fornecer diretrizes consistentes para a construção e manutenção de comandos Artisan no ecossistema Laravel.
* **Casos de uso:** Comandos de sincronização de dados de terceiros (Whapi, Trello, Efi), rotinas de limpeza de banco e automações via scheduler.
* **Workflows:** []
* **Skills próprias utilizadas:** Nenhuma no momento.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-jobs-queues-horizon-best-practices
* **Benefícios:** Maior legibilidade nas assinaturas, interações de console padronizadas e seguras e retorno de códigos de erro previsíveis para integração com o SO ou schedulers externos.
