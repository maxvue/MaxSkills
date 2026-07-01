# PROPOSTA DE SKILL: laravel-authorization-policies-gates

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or reviewing Laravel authorization logic, including Policies, Gates, role-based access control, route protection, and sharing user permissions with Inertia/Vue front-end. Triggers on gate definitions, policy classes, authorize calls, and 'can' middleware.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é um sistema corporativo multiusuário complexo. Para garantir a segurança dos dados e evitar falhas de escalada de privilégios (IDOR), é fundamental padronizar o uso de Policies e Gates do Laravel, bem como a forma como essas permissões são propagadas para o frontend Vue via Inertia.
* **Recursos:** Estrutura padrão de classes Policy ligadas a Eloquent Models, registro de Gates globais em Service Providers, uso correto do middleware `can` em rotas, métodos de autorização nos controllers do Laravel (Inertia e API), compartilhamento de permissões com o front-end Vue (Inertia shared data ou DTOs), tratamento de exceções de autorização (403 Forbidden) e convenções de testes para Policies e Gates usando Pest PHP.
* **Objetivo:** Fornecer diretrizes e padrões de projeto claros para a implementação de segurança e controle de acessos (autorização) robustos no Laravel e Vue/Inertia no Engeapp.
* **Casos de uso:** Proteger rotas e ações de edição/exclusão de recursos (como Projetos, Usuários, Integrações), controlar a visibilidade de botões e links no front-end Vue com base nas permissões do usuário logado, e validar se um usuário ou token tem permissão para realizar ações em Jobs/background processings.
* **Workflows:**
  - bug-fix-back-end
  - bug-fix-front-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — As Policies são mapeadas diretamente aos Eloquent Models do projeto.
  - `laravel-pest-testing-best-practices` — As Policies e Gates devem ser testados utilizando Pest PHP.
  - `laravel-code-generators-best-practices` — Os Controllers do Inertia devem injetar e autorizar as requisições antes de renderizar as Views.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Garantia de segurança da informação, facilidade de auditoria de permissões, consistência na UX ao ocultar elementos não autorizados, e facilidade em testar regras de negócio ligadas a acesso.
