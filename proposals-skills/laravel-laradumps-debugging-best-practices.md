# PROPOSTA DE SKILL: laravel-laradumps-debugging-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring LaraDumps, debugging variables, database queries, HTTP requests, logs, or system states using LaraDumps in the Laravel backend. Triggers on ds() helper calls, LaraDumps configurations, and debugging setups.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é um ecossistema complexo com múltiplos serviços, integração com IA e processamento em segundo plano. O uso inconsistente de dumps e logs tradicionais dificulta a depuração ágil de bugs em desenvolvimento. O LaraDumps oferece um painel interativo em tempo real para visualizar dumps, queries e logs, mas necessita de padrões de uso para não poluir o código em produção.
* **Recursos:** Padrões de uso do helper ds(), depuração de queries SQL, monitoramento de rotas e requests, integração com comandos Artisan, e remoção segura de dumps antes do commit (evitando ds() em produção).
* **Objetivo:** Estabelecer diretrizes claras para o uso do LaraDumps como ferramenta primária de depuração local no Laravel backend do Engeapp, garantindo produtividade e segurança do código.
* **Casos de uso:** Depuração de dados de APIs, inspeção de queries Eloquent complexas, monitoramento de performance local e depuração de payloads de integração.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Integrará o fluxo de dumps com as regras gerais de log e tratamento de exceções da aplicação.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Aceleração do diagnóstico de bugs locais, redução de logs ruidosos de depuração no storage local, e prevenção de vazamento de dados sensíveis ou helpers ds() em ambientes de produção.
