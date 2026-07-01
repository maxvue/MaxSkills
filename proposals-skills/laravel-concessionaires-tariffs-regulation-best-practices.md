# PROPOSTA DE SKILL: laravel-concessionaires-tariffs-regulation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when creating, modifying, or querying energy concessionaires (concessionárias), subsidiaries, regional units, electrical regulations (ANEEL rules), or tariff data (group A/B, green/blue tax flags, TUSD/TE distribution tariffs) in Laravel. Triggers on calculations involving power distribution costs, energy concessionaire CRUDs, and regulation data validations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza cálculos complexos de viabilidade e dimensionamento financeiro para projetos fotovoltaicos. Esses cálculos dependem diretamente das regras de tarifa de energia da concessionária local (TUSD, TE, tarifas de ponta/fora de ponta para Grupo A, tarifas residenciais/comerciais para Grupo B) e regras de regulamentação da ANEEL (como a compensação de energia de GD). É necessário definir padrões claros para estruturar e validar esses modelos, DTOs e cálculos no backend Laravel, evitando divergências tributárias e lógicas de cálculo duplicadas.
* **Recursos:** Padrões para modelagem de distribuidoras/subsidiárias de energia, regras de validação para dados de regulamentação e tarifas via DTOs (Spatie Laravel Data), estratégias para indexação de tarifas por tipo de cliente (Grupo A vs. Grupo B), estruturação de taxas TUSD e TE, manipulação de bandeiras tarifárias e tratamento de regras de compensação vigentes (resoluções da ANEEL).
* **Objetivo:** Fornecer diretrizes sólidas e padrões para o gerenciamento de concessionárias de energia, suas subsidiárias, tarifas e regras de regulamentação (ANEEL) no backend Laravel do Engeapp.
* **Casos de uso:** Cadastro e atualização de concessionárias e suas subsidiárias no painel administrativo, cálculo do retorno financeiro (payback) e economia mensal estimada de uma usina solar no backend, validação de tarifas locais inseridas pelos usuários e fornecimento de dados consolidados de faturas de energia para a geração de propostas e memoriais descritivos em PDF.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models Eloquent para gerenciar os relacionamentos entre ConcessionaireCompany, Subsidiary, Regionals e RegulationData.
  - `laravel-code-generators-best-practices` — Utilizará os padrões de DTOs do Spatie para validar dados complexos de tarifas elétricas e regras regulatórias.
  - `laravel-brazilian-localization-best-practices` — Utilizará as boas práticas de formatação de valores brasileiros e arredondamentos para calcular corretamente os valores de TUSD, TE e impostos.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-pdf-generation-best-practices` — Será beneficiada, pois os PDFs de propostas e memoriais usarão cálculos tarifários corretos e estruturados.
* **Benefícios:** Garantia de precisão nos cálculos de payback de usinas solares, redução de retrabalho na modelagem e validação dos dados regulatórios ANEEL, código limpo e padronizado para as tarifas de distribuição e energia das concessionárias do Brasil.
