# PROPOSTA DE SKILL: laravel-holiday-sla-calculation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, implementing, or debugging SLA tracking, business days calculation, holiday management, or date-based deadline services in the Laravel backend of the Engeapp ecosystem.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** A homologação de projetos solares fotovoltaicos exige o controle estrito de prazos legais e operacionais das concessionárias. O cálculo incorreto de dias úteis e o desconhecimento dos feriados nacionais, estaduais e municipais podem causar erros no cálculo de SLA, afetando o monitoramento de prazos e gerando prejuízos na execução de projetos.
* **Recursos:** Métodos para cálculo avançado de dias úteis (considerando sábados, domingos e feriados), integração com o HolidayService para sincronização e cache de feriados, e estruturação de regras para contagem de SLAs de concessionárias.
* **Objetivo:** Estabelecer diretrizes sólidas e padrões de código consistentes para o cálculo de dias úteis, prazos de SLA e gerenciamento de feriados no Laravel do Engeapp.
* **Casos de uso:** Cálculo de data limite para resposta de concessionárias (ex: parecer de acesso em 15 dias úteis), identificação automática de atrasos nas etapas do fluxo de homologação, e verificação regionalizada de feriados.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Utilizará as convenções de encapsulamento de lógica de negócio em classes Service para manter o HolidayService and o SlaCalculatorService limpos e testáveis.
  - `laravel-code-generators-best-practices` — Utilizará as convenções de Models para a correta estruturação e relacionamento entre a entidade Holiday e as demais entidades.
  - `laravel-pest-testing-best-practices` — Utilizará as boas práticas de teste com Pest para criar testes de unidade robustos validando o cálculo de dias úteis em finais de semana e feriados.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-engeapp-project-homologation-best-practices` — Será beneficiada pelo cálculo preciso de prazos de protocolos de homologação.
* **Benefícios:** Garantia de conformidade com os prazos regulatórios da ANEEL, redução do retrabalho por perda de prazos de concessionárias, e otimização de performance pelo cache inteligente de feriados locais.
