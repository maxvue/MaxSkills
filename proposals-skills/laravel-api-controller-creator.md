# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, refactoring, or reviewing Laravel API Controllers, ensuring single responsibility, proper use of Form Requests for validation, and API Resources for response formatting.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp requer APIs consistentes e robustas, onde os Controllers devem ser enxutos (Thin Controllers), delegando validação para Form Requests e transformação de dados para API Resources ou DTOs.
* **Recursos:** Padrões para métodos de API RESTful, injeção de dependência, tratamento de exceções adequado, uso de Form Requests, e padronização de respostas HTTP e formatação JSON.
* **Objetivo:** Fornecer diretrizes e padrões sólidos para a criação e manutenção de Controllers de API no ecossistema Laravel do projeto.
* **Casos de uso:** Criação de novos endpoints de API para o frontend (Vue), refatoração de controllers legados, padronização de respostas JSON para serviços externos e integrações.
* **Workflows:** 
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os DTOs padronizados para o tráfego seguro e tipado de dados entre as requisições, os Controllers e as camadas de serviço.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior legibilidade, manutenibilidade, segurança, facilidade de testes (Pest) e consistência no desenvolvimento das APIs do Engeapp.
