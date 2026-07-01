# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 3
  - Nível 3: Requer pasta `examples/` com demonstrações de entrada/saída (input: Model Eloquent → output: Data class correspondente), garantindo correspondência de padrões para o LLM.
* **Wake Word (YAML Description):** Use when creating, modifying, reviewing, or refactoring Spatie Laravel Data classes (DTOs) in the app/Data/ directory. Triggers on creating Data transfer objects, defining constructor-promoted properties, configuring Lazy relationships, using DataCollectionOf attributes, casting Enums, Carbon dates, nested Data objects, or integrating DTOs with Controllers, API Resources, and TypeScript type generation. Also use for converting Eloquent Models to Data classes, implementing validation rules inside DTOs, and structuring data pipelines between backend and frontend.
* **Estrutura de Diretórios:**
  ```
  laravel-code-generators-best-practices/
  ├── SKILL.md
  └── examples/
      ├── input-model.php          # Exemplo de Model Eloquent de entrada
      ├── output-data-class.php    # Data class resultante esperada
      ├── input-model-nested.php   # Model com relacionamentos complexos
      └── output-data-nested.php   # Data class com Lazy e DataCollectionOf
  ```
* **Necessidade:** O ecossistema Engeapp possui **95 Data classes** (Spatie Laravel Data) distribuídas em 22 subpastas dentro de `app/Data/`, sem documentação padronizada ou skill que guie a criação consistente desses artefatos. Os DTOs são a espinha dorsal da transferência de dados entre o backend (Controllers, Jobs, Agentes IA) e o frontend (tipos TypeScript gerados automaticamente), tornando sua padronização crítica para a integridade de todo o sistema.
* **Recursos:**
  - Padrões de definição de propriedades com constructor promotion do PHP 8.
  - Uso correto de `Lazy` para carregamento condicional de relacionamentos.
  - Atributo `#[DataCollectionOf()]` para coleções tipadas.
  - Integração com Enums do projeto (ex: `Gender`, `BrowserAction`).
  - Tipagem com `Carbon` para campos de data/hora.
  - Aninhamento de Data classes (ex: `ClientData` referencia `LocationData`, `ProjectData`).
  - Convenções de nomenclatura (`{Model}Data`, `{Model}{Contexto}Data`).
  - Validação inline dentro de Data classes.
  - Mapeamento correto de colunas do banco para propriedades do DTO.
  - Integração com o workflow de geração de tipos TypeScript.
* **Objetivo:** Fornecer diretrizes padronizadas, rigorosas e com exemplos práticos para a criação, manutenção e refatoração de Data classes (DTOs) baseadas no Spatie Laravel Data, garantindo consistência entre o backend Laravel e o frontend Vue/TypeScript do Engeapp.
* **Casos de uso:**
  - Criação de novos DTOs ao adicionar funcionalidades no sistema (novo módulo, nova entidade).
  - Refatoração de DTOs existentes para incorporar relacionamentos Lazy ou coleções tipadas.
  - Geração automatizada de tipos TypeScript a partir dos DTOs via workflows existentes.
  - Integração com Agentes IA que retornam `HasStructuredOutput` e precisam de DTOs para mapear a resposta.
  - Padronização de DTOs em Controllers para substituir arrays brutos por objetos tipados.
* **Workflows:**
  - `types-update-frontend` — Workflow que atualiza os tipos TypeScript no frontend, consumindo diretamente as Data classes para gerar as interfaces.
  - `typescript-new-type` — Workflow que gera novos tipos TypeScript com base no backend, dependendo dos DTOs como fonte de verdade.
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará os padrões de `HasStructuredOutput` para alinhar os DTOs de resposta dos agentes com as convenções estabelecidas nesta skill.
* **Skills auxiliares:**
  - `laravel-specialist` — Referência para padrões gerais do Laravel.
  - `laravel-best-practices` — Boas práticas de arquitetura Laravel.
  - `php-best-practices` — Padrões modernos de PHP 8.x (constructor promotion, union types, enums).
  - `eloquent-best-practices` — Padrões de Eloquent para mapeamento correto Model → DTO.
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Terá DTOs padronizados para os agentes com `HasStructuredOutput`.
* **Benefícios:**
  - Eliminação de inconsistências entre as 95 Data classes existentes.
  - Tipagem forte end-to-end (PHP → TypeScript), reduzindo bugs de integração frontend/backend.
  - Carregamento otimizado de dados via uso correto de `Lazy` e `DataCollectionOf`.
  - Facilitação da geração automatizada de tipos TypeScript pelos workflows existentes.
  - Maior velocidade de desenvolvimento ao criar novos módulos com DTOs padronizados.
  - Documentação viva que serve como referência para todo o time e para os agentes de IA.
