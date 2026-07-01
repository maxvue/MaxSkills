# PROPOSTA DE SKILL: laravel-correios-api-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, refactoring, reviewing, or debugging integrations with the official Correios API. Triggers on authentication token management, caching strategies for postal codes (CEP), parcel tracking, shipping rate calculations, and handling Correios network timeouts or authentication failures.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp se integra com a API oficial dos Correios para consulta de endereços (CEP) e gerenciamento de envios. O serviço atual apresenta inconsistências na renovação do token de acesso, cacheamento inadequado que gera erros de execução e falta de políticas de expiração e tolerância a falhas temporárias nas requisições.
* **Recursos:** Fluxo de autenticação e renovação automática de token no cache, estratégias robustas de cache de CEPs para evitar requisições redundantes, padronização da estrutura de retorno, tratamento de exceções com logs detalhados e mecanismos de timeout.
* **Objetivo:** Estabelecer diretrizes sólidas e padrões consistentes para o consumo seguro, performático e resiliente da API oficial dos Correios.
* **Casos de uso:** Validação e preenchimento de endereço por CEP, cálculo de frete e prazos de entrega, rastreamento de encomendas e gerenciamento de credenciais de autenticação da API.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Para estruturar o CorreiosService de acordo com os princípios de responsabilidade única e injeção de dependências.
  - `laravel-cache-best-practices` — Para gerenciar de forma eficiente o cache do token de acesso e das respostas da API de CEP.
  - `laravel-exception-handling-logging` — Para implementar um sistema tolerante a falhas with logs informativos das requisições e renovação de token.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-base-api-integration-patterns` — Beneficiará o modelo geral de consumo de APIs governamentais e de serviços com autenticação dinâmica baseada em token no ecossistema Engeapp.
* **Benefícios:** Eliminação de falhas em tempo de execução ao ler dados cacheados, redução do consumo desnecessário de endpoints dos Correios através de cacheamento resiliente de 24 horas, e tratamento adequado de instabilidades na API dos Correios.
