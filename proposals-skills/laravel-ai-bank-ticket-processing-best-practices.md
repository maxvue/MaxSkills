# PROPOSTA DE SKILL: laravel-ai-bank-ticket-processing-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when creating, modifying, reviewing, or debugging AI-driven bank ticket (boleto) processing workflows in Laravel, orchestrating AgentBankTicketProcessor or AgentAiBilletReader, validating billet data, executing payments via Efí (Gerencianet) SDK, verifying TRT/tax eligibility, or saving payment receipts to projects.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp automatiza o processamento e o faturamento de taxas de homologação solar de projetos (boletos de concessionárias e taxas TRT). Como esse fluxo envolve movimentação financeira real, é essencial haver uma skill que padronize a validação das linhas digitáveis/códigos de barra de boletos, o fluxo de orquestração via agentes de IA (`AgentBankTicketProcessor` e `AgentAiBilletReader`), o uso seguro do SDK da Efí (Gerencianet) para pagamentos e o arquivamento automático de comprovantes nos projetos correspondentes, mitigando riscos de pagamentos indevidos ou duplicados.
* **Recursos:**
  - Padronização no fluxo de validação e consulta de boletos (`CheckBankTicket`) antes da efetivação de pagamentos.
  - Regras de filtragem estritas para permitir apenas o pagamento de taxas válidas (ex: taxas de concessionárias de energia e TRT) por parte do agente de IA.
  - Orquestração segura com a ferramenta `PayBankTicket` e tratamento de erros do SDK da Efí (Gerencianet) para mitigar falhas de concorrência ou dupla cobrança.
  - Padrões para arquivamento e associação de comprovantes aos projetos solares no banco de dados e no storage (`SaveBankTicketToProject`).
  - Lógica de fallback para notificação humana e intervenção manual em caso de divergência de valores ou falha de pagamento.
  - Boas práticas para escrita de testes com Pest para simular cenários de pagamento com mocking das APIs financeiras.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para o processamento, validação e pagamento seguro de boletos bancários (taxas de homologação e TRT) utilizando agentes de IA no backend Laravel do Engeapp.
* **Casos de uso:**
  - Leitura e preenchimento de campos de boletos de concessionárias de energia carregados no sistema.
  - Pagamento automático e arquivamento de guias de taxas TRT em projetos solares em andamento.
  - Consulta de status de boletos nas instituições bancárias para sincronização e auditoria financeira do Engeapp.
* **Workflows:**
  - [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará as diretrizes de estrutura, atributos e ciclo de vida de agentes de IA para guiar o desenvolvimento do processador.
  - `laravel-base-api-integration-patterns` — Utilizará os padrões de integração e autenticação segura com as APIs de pagamento.
  - `laravel-efi-payments-integration` — Consumirá as diretrizes de integração com o SDK oficial da Efí (Gerencianet) para executar as chamadas de pagamento de forma segura.
  - `laravel-media-library-best-practices` — Seguirá os padrões do Spatie Media Library para associar os comprovantes aos projetos de forma consistente.
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de erros para capturar falhas em transações bancárias críticas.
  - `laravel-pest-testing-best-practices` — Seguirá as boas práticas de testes automatizados para mockar as consultas e respostas de pagamento de boletos.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Será beneficiada com um caso de uso avançado de agentes dotados de ferramentas de automação financeira.
* **Benefícios:** Eliminação de pagamentos manuais propensos a erros humanos, conformidade com regras estritas de auditoria financeira no Engeapp, prevenção contra fraudes de boletos fraudulentos ou pagamentos duplicados, e registro completo e auditável de cada movimentação financeira efetuada pela IA.
