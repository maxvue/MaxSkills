# PROPOSTA DE SKILL: laravel-dompdf-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, configuring, rendering, or debugging PDF documents using barryvdh/laravel-dompdf. Triggers on Pdf::loadHTML, Pdf::loadView, page setup, custom fonts, styling/CSS in PDF, and saving/streaming PDF outputs.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp gera documentos essenciais em PDF como Procurações e contratos via Dompdf. Estabelecer padrões de formatação HTML/CSS compatíveis com Dompdf evita quebras de layout, erros de memória e problemas de codificação de caracteres.
* **Recursos:**
  - Padrões de renderização usando a Facade `Pdf` do `barryvdh/laravel-dompdf`.
  - Diretrizes para CSS compatível com Dompdf (limitações de float, flexbox, suporte a fontes UTF-8/Noto Sans).
  - Injeção de imagens convertidas para Base64 para garantir carregamento em ambientes locais e de produção.
  - Otimização de memória em relatórios e PDFs longos.
  - Tratamento de quebras de página controladas (`page-break-after`, `page-break-inside`).
* **Objetivo:** Garantir a geração robusta, performática e visualmente consistente de arquivos PDF usando o Dompdf no backend Laravel.
* **Casos de uso:**
  - Emissão de Procurações Digitais e em Branco.
  - Relatórios executivos de projetos.
  - Contratos de prestação de serviços com assinatura digital.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — A lógica de geração e persistência de PDFs deve ser encapsulada em classes de Serviço (Services) separadas, aplicando o princípio de responsabilidade única.
  - `laravel-exception-handling-logging` — Utilizada para capturar, tratar e registrar erros de compilação de HTML e falhas no renderizador do Dompdf.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Layouts consistentes entre ambientes de homologação e produção, carregamento correto de imagens locais e fontes tipográficas, prevenção de vazamentos de memória em PDFs grandes e facilidade na manutenção dos templates HTML.
