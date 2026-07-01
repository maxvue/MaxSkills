# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when generating, exporting, or reverse-engineering database migrations from an existing database schema in Laravel using the kitloong/laravel-migrations-generator package. Triggers on running migration:generate commands, specifying table exclusions, formatting generated indexes and foreign keys, or resolving schema differences between development and production.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp conta com um banco de dados de grande porte e legados de dados que precisam ser sincronizados com ambientes locais e de homologação. A criação manual de migrations para tabelas já existentes é um processo propício a erros e lento; utilizar o `laravel-migrations-generator` com diretrizes claras previne a geração de migrações desorganizadas, com nomes de chaves estrangeiras fora do padrão ou redundâncias.
* **Recursos:** Configuração do gerador no ambiente Laravel, execução do comando `php artisan migrate:generate`, tratamento de dependências de foreign keys durante a geração, seleção e exclusão de tabelas desnecessárias ou temporárias, e padronização das migrações exportadas (ex: formatação de tipos de colunas legados).
* **Objetivo:** Fornecer diretrizes consistentes e seguras para a engenharia reversa e geração automática de migrações a partir do banco de dados existente no Engeapp.
* **Casos de uso:**
  - Sincronização e exportação de migrações a partir do banco de dados local para inclusão no repositório.
  - Saneamento de bancos de dados legados por meio de migrações limpas e auto-geradas.
  - Reconstrução de tabelas específicas sem perder chaves estrangeiras ou índices existentes.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as diretrizes de nomes de tabelas, chaves primárias e estruturas para validar e corrigir eventuais inconsistências nas migrações auto-geradas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Aceleração na criação de novas tabelas a partir de mockups de banco.
* **Benefícios:** Economia de tempo no desenvolvimento, redução de falhas de sincronização de banco de dados entre ambientes, migrações auto-geradas consistentes e prontas para uso no ciclo de CI/CD.
