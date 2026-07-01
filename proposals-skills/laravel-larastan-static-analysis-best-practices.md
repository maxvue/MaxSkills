# PROPOSTA DE SKILL: laravel-larastan-static-analysis-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, running, or resolving static analysis errors with Larastan/PHPStan, updating phpstan.neon configurations, raising the analysis level, or fixing type mismatches in Laravel controllers, models, and services.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é um ecossistema complexo com integração de APIs e processamento assíncrono. Erros de tipagem, chamadas a métodos inexistentes e retornos incorretos podem passar despercebidos. O uso consistente do Larastan previne bugs em tempo de desenvolvimento.
* **Recursos:** Configurações recomendadas para phpstan.neon, níveis de análise ideais, tratamento de tipagem genérica, annotations PHPDoc para o Eloquent e integração com ferramentas de IDE.
* **Objetivo:** Estabelecer diretrizes e boas práticas para análise estática de código com Larastan, ajudando a elevar a qualidade e confiabilidade do backend Laravel no ecossistema Engeapp.
* **Casos de uso:** Resolução de erros comuns de análise estática, configuração do nível do PHPStan em novos módulos, anotação correta de tipos em models e DTOs, e prevenção de regressions na tipagem do Laravel.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as regras de declaração de models para mapear propriedades do Eloquent para o Larastan.
  - `laravel-ide-helper-best-practices` — Utilizará arquivos de helper gerados (`_ide_helper_models.php`) para guiar a análise estática do Larastan em métodos mágicos do Eloquent.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices`
  - `laravel-services-best-practices`
  - `laravel-code-generators-best-practices`
* **Benefícios:** Detecção precoce de bugs de tipagem, redução de erros em tempo de execução, facilidade de refatoração segura e código de backend mais limpo e legível em pt-BR.
