# PROPOSTA DE SKILL: laravel-excel-import-export-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging Excel import and export features in Laravel using the Maatwebsite/Laravel-Excel package. Triggers on model imports, exports, chunk reading, queueable imports/exports, validation rules in imports, and custom formatting.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp lida com grandes volumes de dados que precisam ser importados ou exportados em formato Excel. A falta de padronização nessas operações pode levar a problemas de estouro de memória RAM (Out of Memory), falhas silenciosas na importação de dados incorretos e duplicação de lógica nos controladores.
* **Recursos:**
  - Padrões para exports simples e com carregamento otimizado de relacionamentos (Eager Loading) para evitar N+1 queries.
  - Implementação de imports segmentados (Chunk Reading) e assíncronos (Queueable Imports) utilizando filas e Jobs gerenciados pelo Horizon.
  - Validação rigorosa dos dados importados na própria classe de importação (com suporte para falhas parciais e skipping de linhas inválidas).
  - Formatação customizada de tipos de dados (datas, moedas, CNPJ/CPF).
  - Escrita de testes automatizados com Pest para validação de fluxos de importação e exportação.
* **Objetivo:** Fornecer diretrizes e convenções sólidas e de alto desempenho para a manipulação de planilhas Excel no Engeapp com o pacote `maatwebsite/excel`.
* **Casos de uso:** Importação de planilhas de clientes/fornecedores, exportação de relatórios financeiros detalhados, importação em massa de equipamentos e histórico de medições, exportação de dados analíticos para exportadores de terceiros.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-jobs-queues-horizon-best-practices` — Utilizada para estruturar e gerenciar imports/exports queueable que devem rodar em segundo plano de forma assíncrona.
  - `laravel-code-generators-best-practices` — Utilizada para validar as linhas da planilha com as regras do Laravel.
  - `laravel-pest-testing-best-practices` — Utilizada para guiar a criação de testes de feature para os processos de importação e exportação.
* **Skills auxiliares:** laravel-specialist, php-expert
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Processamento de planilhas altamente escalável e seguro, redução drástica de erros de limite de memória no servidor, garantia de integridade dos dados importados e facilidade de manutenção.
