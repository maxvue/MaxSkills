---
name: laravel-ai-datasheet-extraction-best-practices
description: "Use when extracting technical specifications from solar inverter/module datasheets (PDFs) via AgentDatasheetReader, production pipeline, grounding rules, output schemas, electrical specs, and JSON validation. Covers extraction pipeline and validation rules."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas para Extração de Datasheets com IA no Laravel

## Objetivo

Fornecer diretrizes estruturadas e padrões consistentes para extração, validação e normalização de dados técnicos a partir de arquivos PDF de datasheets de inversores solares e módulos fotovoltaicos usando o `AgentDatasheetReader` no backend Laravel do Engeapp.

## Pipeline Real

`File` (PDF de datasheet) -> `GeminiDocumentService::datasheetFile()` monta `new LocalDocument($file->full_file_path, 'application/pdf')` e chama `promptWithFallback(new AgentDatasheetReader, ...)`, que tenta cada modelo de `FALLBACK_MODELS` em sequência, só trocando de modelo em erro 503/429/5xx -> persiste o JSON bruto em `$file->data_ai` -> `GeminiDatasheetProcessJob` converte `data_ai` em `Brand` + `inverters`/`modules` (`updateOrCreate` por `model`, `checked_datasheet = true`, `syncWithoutDetaching` do arquivo, `broadcast` do evento `datasheet_ai_done`). Exposto via rota nomeada `datasheet.file.ai` (`App\Http\Controllers\Api\Gemini\ApiGeminiProject`).

O atributo `#[Model('gemini-2.5-flash-lite')]` do agente é apenas o default declarativo — é sobrescrito em runtime pelo `model:` passado explicitamente em cada tentativa de `promptWithFallback`.

## Instruções

### 1. Fonte de Dados e Regras de Grounding
- **Grounding**: Extraia todas as especificações exclusivamente do arquivo PDF fornecido (datasheet/manual). Não busque informações ausentes online nem invente valores (hallucinate).
- **Fallback para Zero**: Se um campo técnico não estiver presente, identificável ou aplicável a um modelo específico no PDF, faça fallback para `0` (zero) em campos numéricos e `false` em campos booleanos. Nunca os deixe null ou vazios. Essa regra do prompt é pré-requisito para entender o filtro de persistência abaixo.
- **Fonte do prompt completo**: as instruções acima resumem `AgentDatasheetReader::instructions()` (grounding, remoção de unidades, colunas mescladas, OCR, sinônimos, faixa CA). Consulte o método diretamente como fonte de verdade ao editar o prompt — não reproduza aqui o heredoc inteiro.

### 2. Persistência descarta zeros: `has_content()` trata `0` como vazio (só nos inversores)
- O LLM deve devolver `0`/`false` no fallback (regra acima), mas `GeminiDatasheetProcessJob` filtra esses valores com `has_content($value, allow_zero: false)` (`app/Helpers/StringsHelper.php`) antes de montar o array de inversor, e o `array_filter` final **remove a chave** cujo valor é `0`. Ou seja, no `updateOrCreate` de inversores um campo zerado não é gravado: fica `null` na criação e mantém o valor anterior em uma atualização.
- Esse filtro existe **apenas no ramo de inversores**. Em `modules`, o array vindo do JSON é repassado inteiro ao `updateOrCreate` — lá o `0` é gravado normalmente.

### 3. Extração de Múltiplos Modelos e Dados Compartilhados
- **Isolamento de Modelo**: Datasheets frequentemente contêm tabelas com múltiplos modelos. Garanta que os dados sejam mapeados com cuidado para o modelo correto.
- **Colunas/Células Mescladas**: Se uma tabela tiver colunas mescladas (ex: um único valor de Tensão CA compartilhado por 4 modelos), copie/propague esse valor para todos os modelos correspondentes.
- **Mapeamento Inequívoco**: Preste atenção extra ao alinhamento das colunas para evitar que valores de um modelo vazem para outro.

### 4. Falhas de OCR e Parsing
- **PDFs Não Pesquisáveis**: Realize OCR (Reconhecimento Óptico de Caracteres) em PDFs escaneados ou apenas de imagem antes da extração técnica.
- **Tratamento de Sinônimos**: Trate corretamente os sinônimos de terminologia:
  - "MPP Trackers", "MPP" e "MPPT" são equivalentes.
  - "DADOS FV", "FV", "DADOS CC", "DADOS DE INPUT", "DADOS DE ENTRADA" e "DADOS DE ENTRADA CC" são equivalentes.
- **Faixas de Saída CA do Inversor**: Frequentemente os limites de tensão vêm agrupados com a tensão nominal (ex: `127/220V (188.6-237.7V)`). Separe-os corretamente em:
  - Nominal: `220` (ou `127`)
  - Min: `188.6`
  - Max: `237.7`

### 5. Definição de Schema usando `JsonSchema`
Todas as definições de schema em `AgentDatasheetReader::schema()` devem definir tipos estritos com anotações de descrição.

O schema retornado tem, no nível de topo, os campos `type_equipment` (string), `inverters` (array) e `modules` (array).

#### Campo Raiz de Discriminação (`type_equipment`)
- `type_equipment`: String obrigatória (`->string()->required()`) que discrimina o tipo de equipamento do datasheet. Ex: `"inverter"` ou `"module"`. É o primeiro campo do schema e define se a extração deve popular o array `inverters` ou `modules`.

#### Schema de Marca (`brand`), Inversor (`inverters`) e Módulo (`modules`)
Os três sub-schemas têm dezenas de campos elétricos/dimensionais próprios (ex.: `efficiency_max`, `range_vcc`, `voc`, `temperature_coefficient`). Não reenumere aqui campo a campo em prosa — a lista muda a cada campo novo e duplicaria as `->description()` do próprio schema. Consulte `AgentDatasheetReader::schema()` como fonte de verdade de nomes, tipos e descrições.

### 6. Boas Práticas de Testes com Pest
- Sempre escreva testes dentro de `tests/Feature/` ou `tests/Unit/` usando Pest para validar a lógica de extração.
- Não existe hoje nenhum teste de datasheet no repositório — o que segue é recomendação prescritiva, não algo já implementado.
- Forma idiomática (trait `Promptable`, usado pelo `AgentDatasheetReader`): `AgentDatasheetReader::fake([...])` e `AgentDatasheetReader::assertPrompted(fn ($prompt) => ...)`. Como alternativa equivalente e mais explícita, `Ai::fakeAgent(AgentDatasheetReader::class, [...])` + `Ai::assertAgentWasPrompted(...)` (não existe um `Ai::fake()` genérico).
- Verifique:
  - O parsing exato dos campos sem unidades.
  - O fallback correto para `0` quando os campos estão ausentes na resposta crua mockada.
  - A separação correta dos modelos e o mapeamento dos metadados de marca.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** agrupe modelos distintos em um único objeto de saída; cada modelo deve ser uma entrada separada no array de saída.
- **NUNCA** use prompts HereDoc com aspas duplas (`<<<INSTRUCTIONS`) no `AgentDatasheetReader`. Sempre use HereDocs com aspas simples.
