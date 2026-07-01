# PROPOSTA DE SKILL: laravel-deployer-deployment-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when reviewing, configuring, or debugging Deployer PHP settings (deploy.php), managing server deployments, configuring shared files or directories, customizing rsync exclusions, or troubleshooting deployment/rollback issues.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp é implantado em produção usando o Deployer CLI. É necessário garantir deploys consistentes via rsync (sem Git no servidor), gerenciar symlinks compartilhados (como logs, storage e arquivos de ambiente), manter permissões de escrita corretas e orquestrar rollbacks automáticos e seguros em caso de falha.
* **Recursos:** Configurações padronizadas para o arquivo `deploy.php`, controle de exclusões do rsync, mapeamento de `shared_dirs` e `shared_files`, definição de tarefas e ganchos (hooks) pós-deploy e rotinas de depuração.
* **Objetivo:** Fornecer diretrizes sólidas e seguras para a manutenção, depuração e evolução dos scripts e processos de deploy no ecossistema Engeapp.
* **Casos de uso:** Adição de novos diretórios e arquivos persistentes, depuração de erros de conexão ou de permissões SSH/rsync, otimização de exclusões no upload de releases e configuração de novos hosts de deploy.
* **Workflows:**
  - `deploy`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as diretrizes de execução e depuração de comandos Artisan para validar as etapas pós-deploy que utilizam Artisan (ex: migrações, limpezas de cache).
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior estabilidade nos deploys, redução de erros de configuração no ambiente remoto e segurança ao realizar deploys e rollbacks de novas versões.
