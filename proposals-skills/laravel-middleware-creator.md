# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, registering, or testing custom Laravel Middleware, configuring global, group, or alias middlewares in bootstrap/app.php, or modifying request/response lifecycles.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Laravel v13 não utiliza mais o Kernel.php tradicional para gerenciamento de middlewares. É essencial estabelecer um padrão unificado no Engeapp de como estruturar, registrar em bootstrap/app.php (globais, grupos de rotas web/api e aliases) e testar unitariamente novos middlewares, garantindo a manutenibilidade do ciclo de requisições.
* **Recursos:** Padrão de geração via artisan make:middleware, assinatura de métodos de handle, injeção de dependências via construtor, manipulação de cookies/headers, registro em bootstrap/app.php e testes com Pest.
* **Objetivo:** Fornecer diretrizes e boas práticas para a criação e teste de middlewares personalizados no Laravel 13, garantindo conformidade com a arquitetura stateless e integração correta de segurança e tráfego.
* **Casos de uso:** Validação de assinaturas de API externas, logging de requisições críticas, bloqueio de acessos com base em propriedades de usuário, cabeçalhos de CORS ou segurança personalizados.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará as convenções de testes com Pest para estruturar os testes unitários e de integração de novos middlewares.
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de exceções e log estruturado para disparar e monitorar erros gerados em middlewares.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Redução de erros no ciclo de inicialização do app Laravel v13, simplificação de depuração em filtros de requisição e garantia de cobertura de testes sobre lógica de tráfego.
