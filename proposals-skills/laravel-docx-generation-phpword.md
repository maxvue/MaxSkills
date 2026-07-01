# PROPOSTA DE SKILL: laravel-docx-generation-phpword

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 2
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when generating, formatting, or exporting Word documents (.docx) using PhpWord, managing templates, injecting variables, or configuring headers/footers in Laravel.
* **Estrutura de Diretórios:**
  - `SKILL.md` (Arquivo principal de instruções)
  - `resources/` (Templates base `.docx` e configurações de estilo de tabelas)
* **Necessidade:** O ecossistema Engeapp lida com relatórios técnicos de engenharia fotovoltaica, laudos de vistoria, contratos e propostas comerciais. A geração desses arquivos em formato Word (`.docx`) requer manipulação precisa da biblioteca [phpoffice/phpword](https://github.com/PHPOffice/PHPWord), formatação de tabelas complexas, injeção de imagens dinâmicas e preenchimento de variáveis sem corromper o arquivo XML subjacente.
* **Recursos:**
  - Padrões de uso do `TemplateProcessor` para substituição segura de variáveis.
  - Formatação corporativa de tabelas com células mescladas, larguras relativas e alinhamento preciso.
  - Injeção proporcional e posicionamento de imagens nos documentos.
  - Manipulação avançada de seções, quebras de página, cabeçalhos e rodapés com paginação dinâmica.
  - Sanitização de strings para evitar quebra do XML do arquivo `.docx`.
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para criação, leitura e edição de documentos Word (`.docx`) usando a biblioteca PhpWord no Laravel.
* **Casos de uso:**
  - Geração de laudos técnicos de vistoria com tabelas de medições elétricas e fotos de satélite.
  - Exportação automática de contratos de prestação de serviços com dados cadastrais e cronogramas financeiros.
  - Criação de relatórios executivos mensais de geração fotovoltaica.
* **Workflows:**
  - [bug-fix-back-end](file:///home/johnattas/.gemini/config/global_workflows/bug-fix-back-end.md)
* **Skills próprias utilizadas:**
  - [laravel-exception-handling-logging](file:///home/johnattas/GitHub/Skills/created-skills/laravel-exception-handling-logging/SKILL.md) — Para capturar e logar de forma estruturada as falhas de processamento de arquivos físicos no disco.
  - [laravel-media-library-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/laravel-media-library-best-practices/SKILL.md) — Para carregar caminhos de mídias anexadas a models e injetá-las em documentos Word.
* **Skills auxiliares:** laravel-specialist, php-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Padronização visual dos relatórios Word gerados pelo sistema, desenvolvimento acelerado por meio de templates reutilizáveis, prevenção de estouro de memória no processamento de arquivos grandes e redução de erros de XML corrompido em variáveis dinâmicas.
