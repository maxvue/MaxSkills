# PROPOSTA DE SKILL: laravel-sanctum-api-authentication

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, implementing, securing, or debugging API authentication using Laravel Sanctum. Triggers on Sanctum token creation, SPA cookie authentication, Sanctum middleware, and API token guard configurations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp se comunica de forma assíncrona com o front-end via SPA (Inertia e APIs externas). É fundamental ter diretrizes de segurança rígidas e bem estruturadas para autenticação baseada em tokens (para integrações e API) e cookies com estado (stateful para SPA/Inertia), evitando falhas de segurança e vazamento de chaves ou sessões.
* **Recursos:**
  - Padrões de configuração e ativação do middleware Sanctum no bootstrap/app.php ou Http Kernels do Laravel v13.
  - Padrões de emissão e revogação de tokens de acesso pessoal (Personal Access Tokens) com habilidades (abilities).
  - Configuração de autenticação baseada em cookies SPA (Stateful domains, CORS, session configuration).
  - Métodos padronizados para autenticação de requisições de teste usando o Pest helper do Sanctum (`Sanctum::actingAs`).
  - Tratamento correto de exceções e erros de autenticação em APIs.
* **Objetivo:** Estabelecer diretrizes e melhores práticas para implementação de autenticação de APIs e SPAs utilizando Laravel Sanctum, visando segurança robusta, performance e consistência em testes e produção.
* **Casos de uso:**
  - Autenticação de rotas de API para integrações de terceiros.
  - Controle de login e sessões de usuários no front-end Vue com Inertia.
  - Mocks de autenticação de usuários em testes automatizados com Pest.
* **Workflows:**
  - `bug-fix-back-end`
  - `bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os padrões de controle de requisições e respostas de API nos endpoints de login e tokens.
  - `laravel-pest-testing-best-practices` — Utilizará as boas práticas de testes com Pest para garantir rotas de autenticação confiáveis.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Garantia de segurança nas requisições, fluxos de login/logout claros e seguros, uniformidade de autenticação SPA e por Tokens de API, e facilidade na escrita de testes de integração autenticados.
