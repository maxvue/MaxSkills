# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when creating, modifying, or auditing Laravel Enums. Triggers on requests to generate backed enums, document enum cases with PHPDoc, or export enums to TypeScript using Spatie TypeScript Transformer.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecessistema Engeapp faz uso intenso de TypeScript no frontend (Vue) integrado com o backend Laravel. Os Enums precisam ser definidos com suporte à tipagem e exportação automática via Spatie, além de documentação adequada no PHP.
* **Recursos:** Padrões de definição de enums tipados (string/int backed enums), aplicação do atributo `#[TypeScript]` do Spatie TypeScriptTransformer, regras de nomenclatura (TitleCase para cases), e documentação PHPDoc para cada enum e seus casos de uso.
* **Objetivo:** Padronizar a criação de Enums no ecossistema Engeapp, garantindo que as definições no backend reflitam perfeitamente no frontend via TypeScript de forma automática.
* **Casos de uso:** Criação de novos estados de modelos Eloquent (ex: status de tarefas, tipos de ação, coordenadas) e tipagem de campos em DTOs (Data Transfer Objects).
* **Workflows:**
  - `typescript-new-type`
  - `types-update-frontend`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models para alinhar a tipagem e os casts dos enums nos atributos do model.
  - `laravel-code-generators-best-practices` — Utilizará as convenções de DTOs para alinhar o uso de enums como tipos de campos nos DTOs que são enviados para o Vue.
* **Skills auxiliares:** laravel-specialist, typescript-specialist
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Obterá suporte a enums consistentes para casts de atributos.
  - `laravel-code-generators-best-practices` — Obterá suporte a enums estritamente tipados nos DTOs.
* **Benefícios:** Tipagem consistente de ponta a ponta entre backend e frontend, redução de erros de digitação de valores estáticos, código autodocumentado e automatização na sincronização de tipos.
