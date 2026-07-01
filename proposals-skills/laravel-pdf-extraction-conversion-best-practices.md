# PROPOSTA DE SKILL: laravel-pdf-extraction-conversion-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when processing uploaded PDF documents, extracting raw text using spatie/pdf-to-text, converting PDF pages to images using spatie/pdf-to-image, or optimizing document parsing workflows and testing PDF processing services in Laravel.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp gerencia documentos carregados, faturas e boletos em formato PDF. É crucial ter um padrão unificado para a extração do conteúdo textual e para a geração de imagens de preview de cada página, evitando implementações duplicadas ou ineficientes que sobrecarregam o servidor.
* **Recursos:** Configuração de binários do sistema (poppler-utils e pdftotext), manipulação e leitura de arquivos temporários, conversão de páginas específicas em imagens PNG/JPG, extração estruturada de texto por página e tratamento de exceções.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para a extração de textos e conversão de páginas de arquivos PDF em imagens no Laravel utilizando as bibliotecas Spatie.
* **Casos de uso:** Leitura automatizada de dados de boletos recebidos, renderização de miniaturas (previews) de documentos no frontend Vue 3 e indexação de dados para busca local ou para consumo por agentes de IA.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará as boas práticas de escrita de testes para validar cenários de leitura com arquivos PDF falsos e reais de teste.
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de erros para reportar adequadamente falhas ao tentar abrir PDFs criptografados, corrompidos ou binários de sistema ausentes.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Agentes poderão consumir o texto extraído das páginas dos PDFs.
  - `laravel-media-library-best-practices` — Para integração das imagens geradas de pré-visualização no fluxo de mídia padrão.
* **Benefícios:** Processamento robusto e resiliente de arquivos PDF, previews dinâmicos de documentos de forma nativa e melhor legibilidade no tratamento de documentos carregados por parte da equipe e de IA.
