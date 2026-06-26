# PROPOSTA DE SKILL: adonisjs-gemini-file-api-media-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, reviewing, or debugging media uploads and processing using the Google AI File API with the Gemini SDK in AdonisJS. Triggers on files managing multimodal AI requests, processing large video, audio, or PDF files for Gemini analysis, uploading temp files to the Google File API, monitoring upload state, and cleanup operations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema do SocialMediaApp precisa processar arquivos de mídia pesados (como vídeos promocionais dos clientes, gravações de áudio de briefings ou PDFs de diretrizes de marca longas) para alimentar os agentes de IA. A API tradicional em base64 do Vercel AI SDK possui limites baixos de tamanho, exigindo a integração com a File API do Google AI para upload e processamento resiliente de arquivos multimídia de grande porte.
* **Recursos:**
  - Inicialização do cliente da Google File API (usando `@google/genai` ou o SDK oficial `@google/generative-ai`).
  - Fluxo de upload de arquivos locais (resgatados via `@adonisjs/drive`) para a File API.
  - Monitoramento do status do processamento de arquivos pesados (ex: vídeos) utilizando polling assíncrono (Active Status Polling).
  - Passagem dos arquivos carregados no payload do Vercel AI SDK via referências da File API.
  - Estratégias de limpeza automática dos arquivos temporários na API da Google (cleanup hooks) para evitar vazamento de dados e custos residuais.
  - Tratamento de exceções e limites de quota para upload de mídias.
* **Objetivo:** Fornecer diretrizes robustas e seguras para fazer upload de arquivos de grande porte (vídeo, áudio, PDF) para a API de Arquivos do Google AI (Google File API) e utilizá-los em requisições de agentes de IA baseados no Gemini dentro do AdonisJS.
* **Casos de uso:**
  - Envio de áudios de briefings para transcrição e análise pelo agente `theme_extractor`.
  - Processamento de vídeos de Reels/Shorts criados para validação estética pelo agente `art_analyst`.
  - Leitura de PDFs de identidade visual extensos para alimentar o contexto do agente `graphic_editor`.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `adonisjs-ai-sdk-google-gemini-best-practices` — Utilizada para orquestrar as chamadas de geração de texto e tool calling após a mídias estarem processadas na File API.
  - `adonisjs-drive-file-uploads-best-practices` — Utilizada para obter e gerenciar os caminhos dos arquivos locais a serem enviados à File API.
  - `adonisjs-exception-handling-logging-best-practices` — Utilizada para tratar falhas de rede, limites de quota da Google API e registrar o progresso de uploads.
* **Skills auxiliares:** google-gemini-specialist, adonisjs-best-practices
* **Skills beneficiadas:**
  - `adonisjs-ai-agents-copywriter-reviewer-best-practices`
  - `adonisjs-ai-agents-graphic-editor-and-art-analyst-best-practices`
* **Benefícios:** Processamento resiliente de arquivos multimídia pesados, redução do consumo de memória do servidor (evitando conversões de base64 gigantes na RAM) e melhoria na assertividade das respostas de IA multimodal.
