# PROPOSTA DE SKILL: laravel-reliese-models-generator-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when generating or updating Laravel Eloquent models from the database schema using the Reliese model generator package. Triggers on running php artisan code:models, configuring config/models.php, defining custom model templates, mapping database relationships to Eloquent relations, or handling model generation for specific tables in the Engeapp database.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp opera com um banco de dados legado robusto e de grande escala (EngeApp.sql). Criar ou atualizar dezenas de Eloquent Models manualmente para sincronizar com alterações no banco de dados é altamente ineficiente e propenso a erros (como esquecimento de casts, relacionamentos incorretos ou falta de propriedades PHPDoc). O uso estruturado do Reliese Laravel Model Generator garante que a base de models permaneça fiel ao esquema do banco com mínimo esforço manual.
* **Recursos:** Configuração do arquivo `config/models.php` para definir os padrões de geração (namespaces, traits, timestamps, conexão); uso correto do comando `php artisan code:models` filtrando por tabelas específicas (`--table=...`); padrões para preservar customizações manuais nos models usando classes abstratas (Base models e App models); mapeamento de relacionamentos Eloquent a partir de chaves estrangeiras; mapeamento de tipos de colunas MySQL para Casts apropriados no Laravel.
* **Objetivo:** Fornecer diretrizes sólidas e padrões arquiteturais para a geração automatizada e segura de Eloquent Models a partir do esquema do banco de dados utilizando o pacote Reliese Laravel no ecossistema Engeapp.
* **Casos de uso:** Sincronização automatizada de novos modelos após a importação de dumps ou alteração de tabelas no banco de dados; geração em lote de modelos legados mantendo a integridade de chaves estrangeiras e relacionamentos; padronização de casts e PHPDoc de tipos estáticos para integração fluida com IDEs e análise estática (Larastan).
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as regras de tipagem estrita de relacionamentos, casts padronizados e traits contidas nesta skill para garantir que os modelos gerados pelo Reliese respeitem os padrões do Engeapp.
  - `laravel-code-generators-best-practices` — Ajudará a alinhar a estrutura das tabelas existentes com os schemas que geram os models.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-code-generators-best-practices, laravel-eloquent-relationships-loader
* **Benefícios:** Economia drástica de tempo de desenvolvimento na criação e manutenção de models; eliminação de erros de digitação e mapeamento incorreto de chaves estrangeiras; facilidade na documentação automática dos modelos através de blocos PHPDoc gerados; manutenção da separação limpa entre o esquema gerado automaticamente (Base models) e a lógica de negócios customizada (App models).
