# PROPOSTA DE SKILL: laravel-pennant-feature-flags-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, reviewing, testing, or removing feature flags (feature toggles) in Laravel using Laravel Pennant. Triggers on defining features, checking feature status, activating features for specific users or teams, sharing feature flags with Inertia frontend, and writing feature-flagged unit/feature tests.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp precisa de um mecanismo robusto e padronizado para liberação progressiva de funcionalidades críticas, testes em produção com usuários específicos (como beta testers) e capacidade de desativação rápida (kill switch) de recursos sem a necessidade de novos deploys de código.
* **Recursos:** Estrutura para definição de features dinâmicas (in-memory e database-backed), checagem em nível de middleware, diretivas Blade, compartilhamento com o frontend via Inertia, ativação/desativação programática e isolamento em testes automatizados.
* **Objetivo:** Estabelecer diretrizes e padrões consistentes para o gerenciamento seguro e eficiente de Feature Flags no Laravel utilizando o Laravel Pennant.
* **Casos de uso:** Lançamento gradual de novas integrações de IA, ativação experimental de recursos de faturamento, controle de funcionalidades sob demanda e testes A/B no ecossistema Engeapp.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizada para guiar a integração da trait `HasFeatures` do Pennant nos Eloquent Models.
  - `laravel-code-generators-best-practices` — Utilizada para guiar a lógica de compartilhamento das feature flags ativas para o frontend Vue via dados compartilhados do Inertia.
  - `laravel-pest-testing-best-practices` — Utilizada para guiar a escrita de testes de feature com Pest mockando ou forçando estados de feature flags.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior estabilidade nos deploys em produção, facilidade na realização de testes de novos recursos com usuários selecionados, maior segurança operacional via kill switches dinâmicos e redução no tempo de time-to-market.
