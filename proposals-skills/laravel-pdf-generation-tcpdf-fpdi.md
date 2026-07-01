# PROPOSTA DE SKILL: laravel-pdf-generation-tcpdf-fpdi

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, editing, importing, or debugging PDF documents using TCPDF, FPDI, or the custom PdfEdit class in Laravel. Triggers on page imports, coordinate-based text rendering, load table loops, and concessionaire form outputs.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O Engeapp gera dezenas de memoriais descritivos, diagramas unifilares e fichas de inspeção oficiais de concessionárias de energia. Essas gerações importam templates PDF estáticos e inserem dados dinamicamente usando coordenadas (X, Y) precisas por meio de TCPDF, FPDI e a classe personalizada `PdfEdit`. Um padrão claro ajudará a evitar erros de posicionamento e inconsistências nos documentos.
* **Recursos:** Manipulação e conversão de coordenadas (X, Y), paginação com `PdfEdit`, inserção de textos formatados (tamanho, estilo, alinhamento), desenho de mapas estáticos e preenchimento de tabelas dinâmicas de carga.
* **Objetivo:** Estabelecer as melhores práticas e diretrizes de desenvolvimento para geração e edição de PDFs utilizando FPDI e TCPDF no ecossistema Engeapp.
* **Casos de uso:** Memoriais descritivos (Equatorial/Amazonas), Diagramas unifilares, Fichas de solicitação de acesso de concessionárias de energia.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os dados tipados de models e relacionamentos para mapear as chaves necessárias ao preenchimento do PDF.
* **Skills auxiliares:** php-best-practices, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Precisão visual no posicionamento de dados em formulários rígidos de concessionárias, redução de falhas de renderização e carregamento otimizado de arquivos temporários.
