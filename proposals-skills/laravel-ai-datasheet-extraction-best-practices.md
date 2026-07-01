# PROPOSTA DE SKILL: laravel-ai-datasheet-extraction-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when creating, modifying, reviewing, or debugging technical data extraction workflows from solar inverter and module datasheets (PDFs) using AgentDatasheetReader, defining output schemas, extracting electrical/dimensional specifications, handling OCR failures, or validating structured JSON results.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp necessita extrair com altíssima precisão dezenas de parâmetros técnicos de inversores e módulos fotovoltaicos a partir de datasheets em PDF para realizar dimensionamentos elétricos e homologações de usinas solares. A falta de padronização nas regras de OCR, normalização de unidades de medida (remoção de W, V, A, mm, etc.) e o mapeamento de colunas mescladas em tabelas complexas do PDF podem introduzir valores incorretos no banco de dados, prejudicando os cálculos de engenharia.
* **Recursos:**
  - Diretrizes para preenchimento de especificações elétricas e dimensionais de equipamentos com fallback para 0 (zero) em campos numéricos não localizados.
  - Padrão para normalização de valores e unidades de medida (garantindo o retorno estrito de números ou booleanos).
  - Abordagens para o tratamento de PDFs não pesquisáveis via OCR e manipulação correta de dados mesclados de múltiplos modelos in colunas compartilhadas.
  - Padrão de definição do schema de saída estruturada no método `schema()` do `AgentDatasheetReader` usando a interface `JsonSchema`.
  - Boas práticas para validação dos dados de fabricantes (nomes comuns, empresariais, websites, etc.) e dados elétricos em testes usando Pest.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para a extração, validação e normalização de especificações técnicas de inversores e módulos fotovoltaicos a partir de arquivos de datasheet (PDF) utilizando o AgentDatasheetReader no backend Laravel do Engeapp.
* **Casos de uso:**
  - Dissecção e extração de dados técnicos (como potência nominal, faixas de tensão MPPT, corrente máxima, dimensões e peso) de novos inversores cadastrados no sistema.
  - Extração de especificações de novos módulos fotovoltaicos (como tensão de circuito aberto - Voc, corrente de curto-circuito - Isc e coeficiente de temperatura) a partir de seus datasheets para cálculos de usinas.
  - Validação automatizada e saneamento de dados de marcas e fabricantes obtidos a partir dos metadados dos manuais técnicos.
* **Workflows:**
  - [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará as diretrizes de estrutura, atributos e ciclo de vida de agentes de IA para guiar o desenvolvimento do leitor de datasheet.
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de erros para registrar falhas no parsing de datasheets.
  - `laravel-pest-testing-best-practices` — Seguirá as boas práticas de testes automatizados com Pest para mockar os retornos estruturados do LLM e testar o leitor de datasheet.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-electrical-calculations-dimensioning-best-practices` — Será diretamente beneficiada ao receber dados técnicos limpos e precisos necessários para dimensionamento.
* **Benefícios:** Garantia de que os dados elétricos importados dos equipamentos sejam totalmente confiáveis e isentos de unidades textuais indesejadas, redução de erros de OCR e de mapeamento em tabelas complexas, melhor experiência e consistência nos cálculos físicos e de homologação da usina.
