# PROPOSTA DE SKILL: laravel-gemini-php-sdk-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when interacting directly with the Gemini API using the google-gemini-php/laravel SDK, configuring GenerationConfig, utilizing structured outputs (JSON Schemas), handling multimodal inputs (Images, Audio, PDF) using Blob, or managing model calls and exceptions in Laravel.
* **Estrutura de Diretórios:**
  - `SKILL.md` (Arquivo principal de instruções)
* **Necessidade:** O ecossistema Engeapp integra ativamente inteligência artificial no atendimento ao cliente (chat e WhatsApp), processamento de boletos (OCR) e análises de documentos técnicos. Essas integrações dependem de chamadas de baixo nível da API do Gemini via SDK google-gemini-php/laravel, necessitando de padrões de estruturação de prompts, geração de respostas em JSON estruturado, tratamento robusto de exceções e mapeamento correto de arquivos multimídia (PDF, imagens, áudios) para evitar estouro de memória e erros de comunicação.
* **Recursos:**
  - Padrões de uso da Facade Gemini (Gemini::generativeModel) no Laravel.
  - Configuração de GenerationConfig e definição de schemas JSON rígidos utilizando as classes de dados nativas do SDK (Schema, DataType).
  - Mapeamento seguro de MimeTypes e codificação Base64 para envio de múltiplos arquivos (Blob) via API.
  - Estratégias de tratamento de exceções de rede e rate limiting da API do Gemini com logging estruturado.
  - Padronização do prompt corporativo do Engeapp (Persona, Manual de Boas Práticas e Exemplos orientativos).
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para o consumo e integração direta da API do Gemini utilizando o SDK google-gemini-php/laravel no backend do Engeapp.
* **Casos de uso:**
  - Geração de respostas de suporte técnico interativo (Chat/WhatsApp) baseadas no histórico do chamado.
  - OCR e extração estruturada de dados de boletos bancários (PDF e imagens).
  - Análise automática de documentos técnicos (datasheets de inversores, diagramas unifilares).
  - Transcrição e análise semântica de áudios de suporte gravados por clientes.
* **Workflows:**
  - [bug-fix-back-end](file:///home/johnattas/.gemini/config/global_workflows/bug-fix-back-end.md)
* **Skills próprias utilizadas:**
  - [laravel-exception-handling-logging](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-exception-handling-logging/SKILL.md) — Utilizará as convenções de logs estruturados e captura centralizada de exceções para tratar falhas de comunicação com as APIs do Gemini.
  - [laravel-code-generators-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-code-generators-best-practices/SKILL.md) — Para mapear de forma tipada e segura as intenções, tipos de documentos e statuses de chat de suporte do Engeapp.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - [laravel-ai-agent-creator](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-ai-agent-creator/SKILL.md) — Será beneficiada ao herdar as convenções de mapeamento de arquivos e estruturas de prompts robustas.
* **Benefícios:** Redução significativa de falhas de comunicação com a API do Gemini, prevenção de vazamentos e estouros de memória no upload de grandes volumes de mídias, garantia de respostas em formato JSON perfeitamente parseáveis e facilidade na manutenção e evolução de novos agentes integrados.
