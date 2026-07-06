---
name: laravel-ai-datasheet-extraction-best-practices
description: >-
  Use when creating, modifying, reviewing, or debugging technical data extraction workflows from solar inverter and module datasheets (PDFs) using AgentDatasheetReader, defining output schemas, extracting electrical/dimensional specifications, handling OCR failures, or validating structured JSON results.
---

# Boas Práticas para Extração de Datasheets com IA no Laravel

## Objetivo

Fornecer diretrizes estruturadas e padrões consistentes para extração, validação e normalização de dados técnicos a partir de arquivos PDF de datasheets de inversores solares e módulos fotovoltaicos usando o `AgentDatasheetReader` no backend Laravel do Engeapp.

## Instruções

### 1. Fonte de Dados e Regras de Grounding
- **Grounding**: Extraia todas as especificações exclusivamente do arquivo PDF fornecido (datasheet/manual). Não busque informações ausentes online nem invente valores (hallucinate).
- **Fallback para Zero**: Se um campo técnico não estiver presente, identificável ou aplicável a um modelo específico no PDF, faça fallback para `0` (zero) em campos numéricos e `false` em campos booleanos. Nunca os deixe null ou vazios.

### 2. Normalização de Unidades
- **Saídas Estritamente Numéricas**: Todos os campos elétricos e dimensionais (tensões, correntes, dimensões, pesos, eficiência, etc.) devem retornar números crus (inteiros ou floats).
- **Remover Unidades Textuais**: Remova todas as unidades textuais (ex: "W", "V", "A", "mm", "kg", "%", "°C", "years", "anos") dos valores.
- **Exemplo**:
  - Entrada: `550W` -> Saída: `550`
  - Entrada: `22.2 A` -> Saída: `22.2`
  - Entrada: `21.5%` -> Saída: `21.5`
  - Entrada: `380mm` -> Saída: `380`

### 3. Extração de Múltiplos Modelos e Dados Compartilhados
- **Isolamento de Modelo**: Datasheets frequentemente contêm tabelas com múltiplos modelos. Garanta que os dados sejam mapeados com cuidado para o modelo correto.
- **Colunas/Células Mescladas**: Se uma tabela tiver colunas mescladas (ex: um único valor de Tensão CA compartilhado por 4 modelos), copie/propague esse valor para todos os modelos correspondentes.
- **Mapeamento Inequívoco**: Preste atenção extra ao alinhamento das colunas para evitar que valores de um modelo vazem para outro.

### 4. Falhas de OCR e Parsing
- **PDFs Não Pesquisáveis**: Realize OCR (Reconhecimento Óptico de Caracteres) em PDFs escaneados ou apenas de imagem antes da extração técnica.
- **Tratamento de Sinônimos**: Trate corretamente os sinônimos de terminologia:
  - "MPP Trackers", "MPP" e "MPPT" são equivalentes.
  - "DADOS FV", "FV", "DADOS CC", "DADOS DE INPUT", "DADOS DE ENTRADA" e "DADOS DE ENTRADA CC" (e equivalentes em inglês como "DC Data", "Input Data") são equivalentes.
- **Faixas de Saída CA do Inversor**: Frequentemente os limites de tensão vêm agrupados com a tensão nominal (ex: `127/220V (188.6-237.7V)`). Separe-os corretamente em:
  - Nominal: `220` (ou `127`)
  - Min: `188.6`
  - Max: `237.7`

### 5. Definição de Schema usando `JsonSchema`
Todas as definições de schema em `AgentDatasheetReader::schema()` devem definir tipos estritos com anotações de descrição.

O schema retornado tem, no nível de topo, os campos `type_equipment` (string), `inverters` (array) e `modules` (array).

#### Campo Raiz de Discriminação (`type_equipment`)
- `type_equipment`: String obrigatória (`->string()->required()`) que discrimina o tipo de equipamento do datasheet. Ex: `"inverter"` ou `"module"`. É o primeiro campo do schema e define se a extração deve popular o array `inverters` ou `modules`.

#### Schema de Marca (`brand`)
Um objeto contendo:
- `name`: Nome comum do fabricante, tipicamente uma palavra (ex: "Jinko", "Deye").
- `alternative_name`: Nome de marca padrão/conhecido (ex: "Jinko Solar").
- `company_name`: Nome oficial da entidade corporativa (ex: "Jinko Solar Holding Co., Ltd.").
- `address`: Endereço físico do fabricante.
- `country`: País de origem (ex: "China", "Brasil").
- `about_en`: Descrição em inglês.
- `about_br`: Descrição em português brasileiro.
- `phone_number`: Número de telefone.
- `web_site`: Site oficial.
- `email`: Email de contato.

#### Schema de Inversor (`inverters`)
Um array de objetos representando os modelos de inversores, contendo:
- `brand`: Objeto de marca.
- `model`: Identificador do modelo (ex: "X1000").
- `grid`: Tipo de conexão ("On-Grid", "Off-Grid", "Hybrid").
- `size_type`: "Micro" (microinversores) ou "String" (convencional).
- `inmetro`: Número do certificado Inmetro (ex: "035820/2025").
- `nominal_power`: Potência CA nominal em W.
- `maximum_power`: Potência CC de entrada máxima em W.
- `phases`: Número de fases (ex: 1, 3).
- `voltage`: Tensão CA nominal em V.
- `ac_current`: Corrente CA nominal em A.
- `strings`: Array de números (entradas por MPPT).
- `max_in_group`: Máximo de inversores por cabo tronco CA (apenas Micro).
- `max_in_line`: Máximo de inversores por circuito CA (apenas Micro).
- `min_voltage_ca`: Tensão de saída CA mínima em V.
- `max_voltage_ca`: Tensão de saída CA máxima em V.
- `mppts`: Número de MPPTs.
- `inputs_per_mppt`: Entradas por MPPT.
- `total_inputs`: Total de entradas CC.
- `v_start`: Tensão de partida em V.
- `max_vcc`: Tensão de entrada CC máxima em V.
- `min_vcc`: Tensão de entrada CC mínima em V.
- `efficiency_max`: Percentual de eficiência máxima (ex: 98.3).
- `range_vcc`: Objeto com tensões CC de operação `min` e `max`.
- `max_icc`: Corrente de entrada CC máxima por MPPT em A.
- `max_icc_sc`: Corrente de curto-circuito CC máxima por MPPT em A.
- `module_per_mppt`: Módulos por MPPT (apenas Micro).
- `warranty_product`: Garantia do produto em anos.
- `descriptive_summary`: Descrição curta em linguagem simples (até 200 palavras).

#### Schema de Módulo (`modules`)
Um array de objetos representando os modelos de módulos fotovoltaicos, contendo:
- `brand`: Objeto de marca.
- `model`: Nome do modelo.
- `nominal_power`: Potência nominal em W.
- `bifacial`: Booleano.
- `n_type`: Booleano (tecnologia N-Type).
- `half_cell`: Booleano (tecnologia half-cell).
- `voc`: Tensão de circuito aberto em V.
- `isc`: Corrente de curto-circuito em A.
- `vmpp`: Tensão no MPP em V.
- `impp`: Corrente no MPP em A.
- `height`: Altura em mm.
- `width`: Largura em mm.
- `weight`: Peso em kg.
- `efficiency`: Percentual de eficiência do módulo (ex: 21.5).
- `temperature_coefficient`: Coeficiente de temperatura Pmax em %/°C.
- `maximum_system_voltage`: Tensão máxima do sistema em V (ex: 1500).
- `fuse_rated_current`: Corrente nominal do fusível série em A.
- `warranty_linear_power`: Garantia de potência linear em anos.
- `warranty_product`: Garantia do produto em anos.
- `warranty_linear_power_percent`: Percentual de potência garantida no ano limite.
- `annual_degradation`: Percentual de degradação anual.
- `wire_length`: Comprimento do cabo em mm.
- `descriptive_summary`: Descrição curta em linguagem simples (até 200 palavras).

### 6. Boas Práticas de Testes com Pest
- Sempre escreva testes dentro de `tests/Feature/` ou `tests/Unit/` usando Pest para validar a lógica de extração.
- Faça mock das chamadas à API do LLM Gemini usando as capacidades de teste do Laravel AI SDK: `Ai::fakeAgent(AgentDatasheetReader::class, [...])` (não existe um `Ai::fake()` genérico), e então faça asserções com `assertAgentWasPrompted`.
- Verifique:
  - O parsing exato dos campos sem unidades.
  - O fallback correto para `0` quando os campos estão ausentes na resposta crua mockada.
  - A separação correta dos modelos e o mapeamento dos metadados de marca.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** retorne unidades (V, A, W, mm, kg, %, etc.) em campos numéricos do schema.
- **NUNCA** use `null` ou strings vazias como padrão para campos numéricos ausentes; sempre use `0`.
- **NUNCA** pesquise na internet nem use conhecimento externo para detalhes técnicos ausentes. Baseie todas as extrações no PDF fornecido (grounding).
- **NUNCA** agrupe modelos distintos em um único objeto de saída; cada modelo deve ser uma entrada separada no array de saída.
- **NUNCA** use prompts HereDoc com aspas duplas (`<<<INSTRUCTIONS`) no `AgentDatasheetReader`. Sempre use HereDocs com aspas simples.
