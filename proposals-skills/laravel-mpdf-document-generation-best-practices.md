# PROPOSTA DE SKILL: laravel-mpdf-document-generation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when generating, configuring, or debugging PDF documents using mPDF or custom HTML-to-PDF templates in Laravel. Triggers on custom font registers, header and footer setups, page numbering patterns, temporary folder permissions, and large tables styling.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O Engeapp gera relatórios analíticos, contratos de adesão de clientes e propostas comerciais densas que exigem renderização de HTML/CSS avançada, tabelas complexas com cabeçalhos repetidos e fontes personalizadas. O mPDF é ideal para isso, mas requer configurações específicas de memória, diretórios temporários compatíveis com Docker/Octane, e tags HTML específicas do mPDF (ex: `<htmlpageheader>`) que os desenvolvedores costumam esquecer.
* **Recursos:** Configuração do construtor mPDF no Laravel, definição de fontes TrueType personalizadas, cabeçalhos e rodapés dinâmicos via tags proprietárias, controle de quebra de páginas em tabelas longas (`page-break-inside`), e manipulação de arquivos temporários seguros.
* **Objetivo:** Estabelecer diretrizes consistentes e seguras para a geração de documentos PDF altamente estilizados usando mPDF no ecossistema Engeapp.
* **Casos de uso:** Contratos de prestação de serviços, Propostas comerciais personalizadas, Relatórios técnicos de vistoria, e Recibos de pagamento estruturados.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os dados estruturados de models para injetar informações dinâmicas nos templates Blade que serão compilados para PDF.
* **Skills auxiliares:** php-best-practices, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Geração de relatórios e contratos visualmente impecáveis, suporte correto a tipografia local, redução de problemas de estouro de memória e compatibilidade total com os ambientes de execução Octane/Docker.
