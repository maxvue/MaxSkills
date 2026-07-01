# PROPOSTA DE SKILL: laravel-engeapp-project-homologation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when managing solar project homologation flows, tracking concessionaire submittals, managing concessionaire rules/requirements, or tracking protocol statuses for solar integration projects in the Engeapp ecosystem.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp é um sistema de gestão de clientes e projetos fotovoltaicos, sendo a homologação de projetos junto às concessionárias um de seus fluxos mais críticos. Falhas, atrasos e falta de validação nas exigências de cada concessionária e subsidiária regional comprometem a operação. É necessário padronizar as regras de homologação, transição de status dos protocolos e validação dos documentos regulatórios.
* **Recursos:** Estrutura para gerenciamento de fluxo de homologação, transições de status de protocolos de homologação, validações de documentos obrigatórios vinculados a regulamentações de subsidiárias (`ConcessionaireSubsidiaryRegulation`) e padronização do serviço de homologação (`HomologationService`).
* **Objetivo:** Estabelecer diretrizes sólidas e padrões consistentes para o desenvolvimento, manutenção e validação dos fluxos de homologação de projetos solares fotovoltaicos junto às concessionárias no ecossistema Engeapp.
* **Casos de uso:** Cadastro de regulamentações específicas de subsidiárias de concessionárias, upload e verificação automatizada de documentos de homologação (Procurações, memoriais descritivos), transição e auditoria do histórico de status de protocolos de homologação, e alertas automatizados sobre prazos das distribuidoras.
* **Workflows:**
  - `bug-fix-back-end`
  - `bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Para garantir a correta definição e relacionamento entre as entidades de projetos, clientes, concessionárias e regulamentos.
  - `laravel-services-best-practices` — Para estruturar o serviço `HomologationService` com baixo acoplamento e injeção de dependências adequada.
  - `laravel-code-generators-best-practices` — Para garantir que as novas tabelas de log e histórico de protocolos sigam o padrão estrito de integridade do banco de dados.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Redução do índice de rejeição de homologações junto às concessionárias por falta de documentos, maior controle operacional sobre os prazos de resposta das distribuidoras, rastreabilidade completa das ações e padronização do código-fonte.
