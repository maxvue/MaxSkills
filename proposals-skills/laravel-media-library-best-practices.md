# PROPOSTA DE SKILL: laravel-media-library-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when defining, implementing, reviewing, or debugging file uploads and media attachments using Spatie Laravel Media Library. Triggers on model implementing HasMedia, using InteractsWithMedia trait, registering media collections, defining media conversions, uploading files from HTTP requests, and retrieving media URLs.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp gerencia uma vasta gama de arquivos e uploads anexados a diferentes entidades (como contratos em `ProjectContract`, imagens e comprovantes em `Payments`, fotos e chats de suporte em `SupportMessage`, e manuais de equipamentos em `Module` e `Inverter`). É crucial ter um padrão claro de implementação do Spatie Media Library para evitar consultas N+1 ao carregar mídias, conversões ineficientes que sobrecarregam o servidor, e inconsistências no armazenamento (arquivos órfãos).
* **Recursos:**
  - Padrões de implementação da interface `HasMedia` e uso correto da trait `InteractsWithMedia` nos models.
  - Registro de coleções de mídia (`registerMediaCollections()`) especificando regras de validação física (como aceitar arquivo único por coleção).
  - Configuração de conversões de imagens responsivas (`registerMediaConversions()`) usando filas em background para não travar a requisição do usuário.
  - Métodos padronizados para salvar arquivos enviados via Form Request, tratando a validação de MIME types e dimensões.
  - Boas práticas para o carregamento otimizado de mídias (prevenção de query N+1) usando eager loading (`with('media')`).
  - Limpeza de arquivos temporários e tratamento de mídias órfãs.
* **Objetivo:** Estabelecer diretrizes consistentes e seguras para a implementação, manipulação e otimização de uploads de arquivos via Spatie Laravel Media Library no ecossistema Engeapp.
* **Casos de uso:**
  - Criação de novos anexos de mídia em models (ex: comprovantes de pagamento).
  - Configuração de conversões automáticas (redimensionamento e otimização) para uploads de fotos de vistorias.
  - Otimização do carregamento de mídias em listagens de projetos para reduzir o consumo de memória e consultas ao banco.
* **Workflows:**
  - `bug-fix-back-end` — Auxiliará na correção de bugs relacionados a uploads de arquivos, permissões de escrita, e erros em conversões de imagens.
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Para estruturar a injeção do Spatie nos models de forma limpa e com tipagem estrita de relacionamentos.
  - `laravel-code-generators-best-practices` — Para a validação robusta de payloads contendo arquivos no Request antes da associação ao model.
* **Skills auxiliares:**
  - `laravel-specialist`
  - `laravel-best-practices`
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Enriquecendo a modelagem com as melhores práticas de manuseio de arquivos e mídias anexadas.
* **Benefícios:** Padronização completa na gestão de mídias, redução no consumo de disco por meio de conversões/compressões adequadas, otimização de performance no carregamento de listagens com eager loading e prevenção de vulnerabilidades de segurança ligadas a upload de arquivos maliciosos.
