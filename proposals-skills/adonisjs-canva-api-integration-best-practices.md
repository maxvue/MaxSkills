# PROPOSTA DE SKILL: adonisjs-canva-api-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, reviewing, or debugging integrations with the Canva API in an AdonisJS application, managing Canva OAuth 2.0 flows, uploading media assets to Canva, exporting or publishing designs created on Canva directly to the social media calendar, or handling Canva webhook notifications for design updates.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp (SocialMediaApp) gera ideias de conteúdo e imagens com IA, porém os profissionais de marketing e designers frequentemente precisam ajustar essas mídias no Canva. Esta integração permite exportar assets de imagem e vídeo diretamente para as pastas do Canva dos clientes e também importar os designs finalizados de volta ao SocialMediaApp para agendamento automático nas redes.
* **Recursos:**
  - Fluxo de autenticação OAuth 2.0 seguro para conexões com a API do Canva por cliente/tenant.
  - Envio de assets de imagem gerados no backend diretamente para pastas de projetos no Canva (Upload Media API).
  - Listagem e importação de designs (imagens, PDFs) do Canva para uso no calendário editorial.
  - Endpoint de Webhook para processar eventos do Canva (design atualizado, etc.) mantendo as mídias em sincronia.
  - Lógica de resiliência e controle de limites de taxa (Rate Limiting) da API do Canva.
* **Objetivo:** Estabelecer diretrizes e padrões de desenvolvimento seguros e eficientes para integrar a API do Canva a projetos AdonisJS, cobrindo autenticação, sincronia bidirecional de mídias e tratamento robusto de erros.
* **Casos de uso:**
  - Envio automático de uma imagem de post gerada por IA (pelo graphic_editor) para a pasta do Canva do cliente para que o designer finalize a arte.
  - Sincronização automática no SocialMediaApp da imagem finalizada no Canva para publicação no Instagram.
  - Atualização automática de mídias no calendário de posts com base no webhook de designs alterados do Canva.
* **Workflows:**
  - `/bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `adonisjs-best-practices` — Convenções gerais de estrutura de comandos Ace e injeção de dependência.
  - `adonisjs-ally-oauth-best-practices` — Configuração e extensão de drivers do Ally para autenticação OAuth 2.0 segura com o Canva.
  - `adonisjs-exception-handling-logging-best-practices` — Tratamento e reporte robusto de falhas na comunicação com a API.
  - `adonisjs-drive-file-uploads-best-practices` — Gestão local e remota das mídias recuperadas da API.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `adonisjs-editorial-calendar-event-workflow-best-practices` — Otimização no fluxo de atualização e disponibilidade de imagens para posts agendados.
* **Benefícios:** Automação do ciclo de vida das artes visuais, eliminando o upload/download manual entre o Canva e o SocialMediaApp, melhorando a integridade dos metadados das postagens e otimizando o tempo dos designers.
