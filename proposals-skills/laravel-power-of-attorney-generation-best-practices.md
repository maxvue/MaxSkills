# PROPOSTA DE SKILL: laravel-power-of-attorney-generation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging Power of Attorney (procurações) generation logic, formatting client or partner addresses for legal documents, or generating PDFs for solar energy project concessionaires in the backend.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** A geração de procurações no Engeapp envolve o preenchimento de dados jurídicos sensíveis de pessoas físicas (PF) e jurídicas (PJ) (como CPFs, CNPJs, dados de representantes legais e endereços) estruturados em HTML e exportados em PDF. O sistema necessita de diretrizes consistentes para evitar inconsistências nas informações, dados vazios ou erros de formatação nos documentos finais apresentados às concessionárias de energia.
* **Recursos:** Tratamento e mapeamento condicional de dados de PF e PJ, formatação de endereços amigáveis a partir do model Location, validação de dados de representantes legais, gerenciamento de status de documentos de procuração e injeção dinâmica de datas com suporte a internacionalização.
* **Objetivo:** Fornecer diretrizes e padrões sólidos para a criação, manutenção e depuração da lógica de negócio envolvida na geração de procurações de projetos fotovoltaicos.
* **Casos de uso:** Geração automática do texto de procurações para outorga de poderes a engenheiros/designers, formatação de endereços para órgãos reguladores e concessionárias, controle de minutas em estado de edição ou prontas para assinatura.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as definições estritas dos models (Project, Client, Location, ProjectPowerOfAttorneyDocument) para garantir o mapeamento e recuperação corretos de relacionamentos.
  - `laravel-services-best-practices` — Orientará na estruturação das responsabilidades e dependências do PowerAttorneyService.
  - `laravel-pest-testing-best-practices` — Ajudará no design de testes unitários e de integração para validação de dados gerados em procurações.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Eliminação de erros de preenchimento ou dados nulos em procurações digitais, formatação padronizada e legível de endereços e garantia de conformidade jurídica nas outorgas de poderes.
