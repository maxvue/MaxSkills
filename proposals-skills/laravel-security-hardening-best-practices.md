# PROPOSTA DE SKILL: laravel-security-hardening-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, reviewing, or debugging Laravel application security, securing Eloquent models (encryption, mass assignment), writing secure controllers, hardening file uploads, configuring security headers, or mitigating OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR).
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp lida com informações sensíveis de clientes, concessionárias e integrações financeiras (Asaas, Efí, MercadoPago). Garantir práticas uniformes de hardening e segurança de dados impede vazamentos e fraudes.
* **Recursos:** Diretrizes de criptografia Eloquent (encrypted casts), prevenção de SQL Injection com queries seguras, sanitização de inputs contra XSS, proteção estrita contra CSRF/CORS, segurança na manipulação e armazenamento de arquivos enviados por usuários, controle de permissões de rota/IP e mitigação de IDOR.
* **Objetivo:** Estabelecer diretrizes e padrões de segurança robustos para o desenvolvimento backend no Laravel, protegendo a integridade da aplicação Engeapp contra vulnerabilidades comuns.
* **Casos de uso:** Validação de uploads de documentos de homologação; criptografia de chaves de API de terceiros no banco de dados; sanitização de dados recebidos via webhooks de pagamentos.
* **Workflows:**
  - `bug-fix-back-end`
  - `deploy`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará regras de validação estritas como defesa inicial contra payload malicioso.
  - `laravel-exception-handling-logging` — Utilizará padrões de logs seguros para auditar eventos críticos de segurança sem vazar stack traces em ambiente de produção.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-code-generators-best-practices, laravel-base-api-integration-patterns, laravel-code-generators-best-practices
* **Benefícios:** Aumento da segurança de dados da aplicação, conformidade com práticas de privacidade (LGPD), proteção contra explorações automatizadas e redução do risco de fraudes financeiras.
