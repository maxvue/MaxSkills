# PROPOSTA DE SKILL: laravel-ai-design-engineer-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, testing, or refining the AgentDesignEngineer or when working with AI-based solar inverter and module allocation, MPPT configuration, sizing calculations, or validating solar system designs. Triggers on modifications to AgentDesignEngineer, design engineering tools, or sizing validation rules.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza o dimensionamento e distribuição de módulos fotovoltaicos nos inversores através do AgentDesignEngineer. A correta execução desse agente depende de regras elétricas rígidas (homogeneidade de módulos, limites de tensão mínima/máxima por string, potência máxima do inversor e simetria de MPPT). É fundamental ter regras claras para que o modelo execute este agente sem violar essas restrições elétricas e evitar falhas no dimensionamento elétrico das usinas solares.
* **Recursos:** Diretrizes de implementação de regras de restrição no agente, padronização do fluxo de trabalho (coleta, planejamento, execução via batched connections, correções e validação final), e regras elétricas mandatórias (exhaustion, homogeneity, voltage limits, maximum power, MPPT symmetry, microinverters priorities).
* **Objetivo:** Fornecer um guia robusto e diretrizes sólidas de desenvolvimento e depuração para o AgentDesignEngineer e suas ferramentas elétricas no ecossistema Engeapp/Laravel.
* **Casos de uso:** Implementação de melhorias no cálculo de dimensionamento do AgentDesignEngineer, criação de novos métodos de validação no fluxo de alocação de módulos, e escrita de testes unitários/funcionais específicos para o agente.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará os padrões estruturais de criação de agentes para garantir que as propriedades e decorators (Provider, Model, Temperature, etc.) estejam corretamente definidos.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Redução de erros de dimensionamento, maior confiabilidade do sistema nas validações elétricas e agilidade no desenvolvimento de novas ferramentas de IA ligadas a design solar.
