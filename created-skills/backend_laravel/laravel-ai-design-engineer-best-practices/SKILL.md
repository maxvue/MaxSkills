---
name: laravel-ai-design-engineer-best-practices
description: >-
  Use when implementing, testing, or refining the AgentDesignEngineer or when working with AI-based solar inverter and module allocation, MPPT configuration, sizing calculations, or validating solar system designs. Triggers on modifications to AgentDesignEngineer, design engineering tools, or sizing validation rules.
---

# Boas Práticas do Laravel AI Design Engineer

## Objetivo

Fornecer diretrizes padronizadas e rigorosas para projetar, implementar e depurar o `AgentDesignEngineer` e suas regras de validação/alocação elétrica dentro do backend Laravel do Engeapp. Esta skill garante que os agentes de IA que realizam dimensionamento elétrico e alocações de módulos para inversores cumpram as restrições físicas e elétricas.

## Instruções

### 1. Missão e Identidade do Agente

O `AgentDesignEngineer` atua como um Engenheiro Projetista Fotovoltaico Sênior. Seu objetivo é analisar os dados da estação, realizar cálculos matemáticos precisos e alocar módulos solares aos inversores de forma segura, eficiente e em estrita conformidade com as restrições de engenharia elétrica.

### 2. Fluxo de Trabalho Obrigatório Passo a Passo

Todas as tarefas de alocação e validação devem seguir rigorosamente este fluxo de trabalho:

1.  **Coleta (Data Collection):**
    *   Chame a ferramenta `GetStationData` para buscar as especificações completas da estação, incluindo todos os inversores, módulos e conexões atuais.
2.  **Planejamento (Planning - CRÍTICO):**
    *   Antes de chamar qualquer ferramenta de conexão, você **deve** abrir uma tag no estilo XML `<planejamento>`.
    *   Escreva os cálculos matemáticos de dimensionamento dentro desta tag:
        *   Calcule os limites de Tensão Mínima e Máxima (número de módulos por string) para cada modelo de inversor e combinação de módulo.
        *   Calcule a capacidade máxima de Potência CC (limite de sobrecarga) de cada inversor.
        *   Descreva a estratégia de distribuição (quais grupos de módulos vão para quais inversores/MPPTs/Entradas).
3.  **Execução (Execution):**
    *   Use a ferramenta `ConnectOrMoveModulesToInputs` para registrar as conexões.
    *   **Otimização:** Agrupe e envie múltiplas alterações de conexão em uma única chamada de API/ferramenta (batching) para maximizar a velocidade e evitar overhead.
4.  **Correções (Corrections):**
    *   Se ocorrer algum erro de validação, use `DisconnectModuleFromInput` (suporta batching) ou mova os módulos usando `ConnectOrMoveModulesToInputs`.
5.  **Validação Final (Final Validation):**
    *   Verifique se 100% dos módulos do projeto estão conectados. Nenhum módulo deve permanecer sem alocação.

---

### 3. Regras Absolutas de Dimensionamento e Elétricas (Obrigatórias)

As restrições a seguir são limites físicos absolutos. Violá-las danificará equipamentos ou causará a rejeição do projeto:

1.  **Exhaustion (Exaustão):** Cada módulo registrado na estação deve estar conectado a uma entrada de inversor.
2.  **Homogeneity (Homogeneidade):** Um único MPPT (e todas as suas entradas conectadas) deve receber apenas módulos do mesmo modelo (`equipment_id`). Misturar diferentes modelos de módulo no mesmo MPPT é estritamente proibido.
3.  **Limite de Tensão Mínima de Entrada (Tensão Mínima):**
    *   O número mínimo de módulos em série por string (entrada) é definido por:
        $$\text{Min Modules} = \lceil \frac{\text{inverter->range\_vcc\_min}}{\text{module->vmpp}} \rceil$$
4.  **Limite de Tensão Máxima de Entrada (Tensão Máxima):**
    *   O número máximo de módulos em série por string (entrada) é definido por:
        $$\text{Max Modules} = \lfloor \frac{\text{inverter->range\_vcc\_max}}{\text{module->voc}} \rfloor$$
5.  **Limite de Potência CC Máxima (maximum_power):**
    *   A soma da potência nominal de todos os módulos conectados a um único inversor **nunca** deve exceder a potência CC máxima de entrada do inversor (`maximum_power`).
6.  **Simetria de MPPT (Regra de Ouro):**
    *   As entradas pertencentes ao mesmo MPPT podem estar completamente vazias (0 módulos) OU devem conter exatamente o mesmo número de módulos.
    *   *Exemplo:* Se o MPPT 1 tem a Entrada 1 e a Entrada 2, ter 10 módulos na Entrada 1 e 10 módulos na Entrada 2 é **válido**. Ter 10 módulos na Entrada 1 e 9 módulos na Entrada 2 é **inválido**.
7.  **Prioridade de Microinversores:**
    *   Se a estação contém microinversores, aloque os módulos a eles primeiro. Apenas os módulos restantes devem ser alocados aos inversores string.
    *   Sempre aloque os módulos aos microinversores em ordem decrescente de potência (maior potência primeiro).

---

### 4. Diretrizes de Otimização de Dimensionamento

Aplique estas boas práticas para melhorar a eficiência do sistema, desde que não entrem em conflito com as regras obrigatórias:

1.  **Compatibilidade de Equipamentos Antigos (status `old`):** Agrupe módulos e inversores que compartilham a mesma flag booleana `old` (por exemplo, conecte módulos `old=true` a inversores `old=true`).
2.  **Agrupamento por Modelo:** Mantenha os módulos do mesmo `equipment_id` agrupados no mesmo inversor sempre que possível.
3.  **Eficiência de Tensão (Strings Mais Longas):** É melhor usar menos entradas com strings mais longas (trabalhando em tensões mais altas, idealmente entre 50% e 80% do `range_vcc_max`) do que espalhar os módulos por muitas strings curtas e de baixa tensão.
    *   *Exemplo:* Distribuir 20 módulos em um MPPT de 4 entradas é melhor feito usando 2 entradas com 10 módulos cada (deixando 2 entradas vazias) do que usando 4 entradas com 5 módulos cada.
4.  **Balanceamento Entre Inversores (Sobrecarga / FDI):** Distribua uniformemente o percentual de sobrecarga entre todos os inversores string ativos. Calcule o percentual de sobrecarga (FDI) como:
    $$\text{Overload \%} = \frac{\sum(\text{Nominal Power of Connected Modules})}{\text{Nominal Output CA Power of Inverter}}$$

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
1.  **NUNCA** viole os limites de tensão mínima/máxima da faixa de string do inversor.
2.  **NUNCA** exceda a potência CC máxima de entrada (`maximum_power`) de qualquer inversor.
3.  **NUNCA** misture módulos com `equipment_id`s diferentes no mesmo MPPT.
4.  **NUNCA** prossiga para executar uma ferramenta de conexão sem antes documentar os cálculos e decisões no bloco `<planejamento>`.
5.  **NUNCA** deixe nenhum módulo sem alocação ao final do processo.
6.  **NUNCA** configure números desiguais de módulos em entradas do mesmo MPPT.
