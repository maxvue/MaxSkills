# PROPOSTA DE SKILL: laravel-socialite-oauth-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, refactoring, or debugging OAuth authentication via Laravel Socialite. Triggers on Socialite driver config, callback routing, user provisioning, state validation, and OAuth testing.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp necessita de um fluxo seguro e sem fricção para autenticação externa (Google e Microsoft Azure AD), permitindo o login ágil de clientes e parceiros integradores. A implementação inadequada pode gerar falhas de segurança críticas como sequestro de contas por falta de verificação de e-mail e falhas na validação de State CSRF.
* **Recursos:** Configuração de múltiplos drivers no services.php, estruturação de rotas de redirecionamento e callback, provisionamento seguro de usuários a partir do payload OAuth, prevenção de Account Hijacking, tratamento correto de exceções de State, e mocking do Socialite para testes consistentes com Pest.
* **Objetivo:** Fornecer diretrizes sólidas e seguras para a integração de autenticação OAuth com Laravel Socialite no backend do Engeapp.
* **Casos de uso:** Login corporativo com Microsoft Azure Active Directory para engenheiros e parceiros, autenticação ágil de clientes através do Google Sign-In, e associação de múltiplas contas de redes sociais ao mesmo perfil de usuário de forma segura.
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de Controllers para padronizar os endpoints de callback e as respostas de token JWT/Sanctum.
  - `laravel-code-generators-best-practices` — Utilizará os padrões de controladores Inertia para realizar redirecionamentos fluidos na interface gráfica.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Aceleração do onboarding de usuários, segurança mitigando hijacking de contas e ataques CSRF, e padrões homogêneos para suporte a novos provedores OAuth futuramente.
