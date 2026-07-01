# PROPOSTA DE SKILL: laravel-electrical-calculations-dimensioning-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when performing or validating electrical sizing, calculating circuit breakers, sizing cables, verifying voltage drop, or resolving inverter and solar module specifications. Triggers on calls to getWireSize, getCircuitBrake, getInverter, or when handling NBR 5410 electrical standards.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é focado em engenharia fotovoltaica e solar. Cálculos elétricos complexos de dimensionamento de cabos, queda de tensão e escolha de disjuntores são frequentemente executados. É essencial garantir que o agente saiba usar corretamente os helpers globais `getWireSize`, `getCircuitBrake`, `getInverter` e a tabela `WireTable` com tratamento correto de cache e parâmetros elétricos para evitar cálculos manuais incorretos.
* **Recursos:** Diretrizes de uso dos helpers `getWireSize` (NBR 5410/queda de tensão), `getCircuitBrake`, `getInverter`, conversão e normalização de tensões/fases, tratamento de exceções físicas (correntes vazias ou nulas) e boas práticas de caching de tabelas de cabos (`WireTable`).
* **Objetivo:** Fornecer regras e padrões estritos para o uso dos helpers e models de engenharia elétrica e solar no backend do Engeapp.
* **Casos de uso:** Dimensionamento automático de materiais em projetos solares, validação de memorial descritivo, cálculo automático de perdas e queda de tensão nos cabos AC/DC das usinas solares.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:** Nenhuma no momento.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Padronização nos cálculos de dimensionamento, redução de bugs em propostas de engenharia solar e memorial descritivo, e maior reuso de códigos de cálculo existentes em vez de reinventar lógica de física elétrica.
