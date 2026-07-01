# PROPOSTA DE SKILL: laravel-s3-minio-storage-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, implementing, or debugging cloud storage integrations in Laravel using S3, MinIO, or Cloudflare R2 drivers. Triggers on Storage facade calls, disk configuration, file uploads, pre-signed URLs, and S3-compatible testing setup.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp lida com grande volume de uploads (vistorias solares, projetos, contratos) e necessita de uma arquitetura de armazenamento em nuvem compatível com S3 para escalabilidade horizontal, com suporte a desenvolvimento local usando MinIO de forma isolada.
* **Recursos:** Configuração de discos (AWS S3, MinIO, Cloudflare R2), tratamento de uploads pesados (multipart upload), geração de URLs temporárias e seguras (pre-signed URLs), estratégias de cache de cabeçalhos de controle de cache, testes com mock de armazenamento local.
* **Objetivo:** Fornecer diretrizes e convenções de boas práticas para a integração de storage em nuvem compatível com S3 no ecossistema Engeapp/Laravel.
* **Casos de uso:** Upload de fotos de vistorias técnicas no local, geração e armazenamento de diagramas de projetos solares, disponibilização temporária de documentos de homologação para download seguro, rotinas de backup.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-media-library-best-practices` — Utilizada para integrar o driver S3/MinIO diretamente com o Spatie Media Library para gerenciamento transparente de arquivos e conversões.
  - `laravel-services-best-practices` — Utilizada para desenhar classes de serviços de upload/download otimizados.
  - `laravel-pest-testing-best-practices` — Utilizada para implementar os testes unitários e de feature mockando o driver de storage sem tocar na rede real.
* **Skills auxiliares:** laravel-specialist, php-expert
* **Skills beneficiadas:** laravel-media-library-best-practices, laravel-backup-best-practices
* **Benefícios:** Escalabilidade horizontal, desenvolvimento local isolado e fiel à produção via MinIO Docker, economia de banda e processamento via download direto com URLs assinadas e segurança de dados do cliente.
