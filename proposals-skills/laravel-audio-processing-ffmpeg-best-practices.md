# PROPOSTA DE SKILL: laravel-audio-processing-ffmpeg-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or debugging audio conversion routines, utilizing FFMpeg via Symfony/Laravel Process component, handling audio files formats (Opus, AAC, OGG, MP3), or configuring execution timeouts and error logging for system processes.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp suporta gravação de áudio no frontend Vue e transcrição ou consumo no backend. É vital ter um padrão robusto para execução de binários externos (FFMpeg) usando a API Process do Laravel/Symfony, evitando gargalos de CPU, falhas silenciosas, problemas de timeout e falhas de segurança por injeção de comandos.
* **Recursos:** Configuração de processos do Symfony/Laravel (`Symfony\Component\Process\Process`), tratamento de timeouts, verificação de existência do binário ffmpeg no sistema, logs detalhados de erros de processo, limpeza de arquivos temporários pós-conversão e validação de codecs.
* **Objetivo:** Estabelecer diretrizes sólidas e seguras para a execução de processos de conversão e processamento de áudio com FFMpeg no backend Laravel do Engeapp.
* **Casos de uso:** Conversão de arquivos de áudio gravados pelo usuário (.ogg/Opus) para formatos compatíveis com APIs de transcrição e navegadores (.aac ou .mp3), processamento e compressão de áudio e segurança em comandos do sistema executados via PHP.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — A skill proposta utilizará os padrões de encapsulamento de lógica de negócio e injeção de dependências em classes de serviço no diretório `app/Services/`.
  - `laravel-exception-handling-logging` — Utilizará as práticas de logging estruturado e try-catch para capturar falhas no binário do FFMpeg (como `ProcessFailedException`) sem causar falhas silenciosas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Processamento de mídias seguro contra command injection, controle de recursos do sistema via timeouts corretos, facilidade na manutenção dos helpers/serviços de conversão e logs detalhados para rápida resolução de bugs.
