# PROPOSTA DE SKILL: laravel-debugbar-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when debugging, profiling, or optimizing Laravel application issues such as slow database queries, duplicate N+1 queries, memory consumption, execution time, and captured exceptions using Laravel Debugbar CLI commands. Triggers on debugging requests, performance optimization, and tracing exceptions.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp requer ferramentas eficientes e rápidas para depurar e perfilar consultas de banco de dados, detectar problemas N+1 de forma ágil e rastrear exceções em ambiente de desenvolvimento sem precisar abrir a interface web do Debugbar.
* **Recursos:** Comandos de inspeção e busca de requisições (`debugbar:find`), detalhamento de coletores (`debugbar:get`), análise aprofundada de consultas e plano EXPLAIN (`debugbar:queries`).
* **Objetivo:** Fornecer um guia rápido e padronizado para depuração e otimização de requisições no Laravel usando os comandos de CLI do Laravel Debugbar.
* **Casos de uso:** Otimização de queries N+1, investigação de gargalos de performance (tempo/memória), rastreamento do fluxo de exceções.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - Nenhuma no momento.
* **Skills auxiliares:** debug-using-debugbar, php-pro, laravel-expert
* **Skills beneficiadas:**
  - laravel-eloquent-query-optimization-best-practices
* **Benefícios:** Diagnóstico mais rápido de bugs no backend, facilidade de identificar queries redundantes e melhoria na performance das rotas do Engeapp.
