# PROPOSTA DE SKILL: laravel-ide-helper-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when setting up autocomplete, configuring Barryvdh Laravel IDE Helper, generating meta files, updating helper models declarations, running ide-helper commands (generate, models, meta), or maintaining phpdocs in separate files for Laravel models to ensure IDE integration without polluting source code.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** Garantir que a autocompletação da IDE funcione perfeitamente no ecossistema Engeapp/Laravel sem poluir o código-fonte dos models com blocos extensivos de PHPDoc gerados automaticamente, em conformidade com as regras globais do projeto.
* **Recursos:**
  - Padrões de execução dos comandos do `laravel-ide-helper` (geração de helpers para Facades, meta-arquivos e classes helpers de models).
  - Configuração e geração de comentários PHPDocs em arquivos separados de metadados (`_ide_helper_models.php`) usando a opção `php artisan ide-helper:models -M --nowrite`.
  - Integração automatizada da atualização do autocompletação no fluxo de desenvolvimento e pós-dump do Composer.
  - Instruções de prevenção para evitar commits acidentais de comentários de modelos embutidos nos arquivos `.php` originais de models.
* **Objetivo:** Estabelecer diretrizes e comandos padronizados para o uso do Laravel IDE Helper de forma a enriquecer a experiência de desenvolvimento com autocompletação precisa na IDE, mantendo os Eloquent Models limpos e em total conformidade com as regras arquiteturais do projeto.
* **Casos de uso:**
  - Configuração inicial do ambiente de desenvolvimento local.
  - Atualização do helper de autocompletação após a criação ou modificação de Eloquent Models no backend.
  - Correção de alertas de tipo não reconhecido ou indefinições de propriedades mágicas dos models.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os padrões de criação de models para assegurar que PHPDocs automáticos não sejam incluídos diretamente neles.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada ao manter os arquivos de models limpos e focados apenas na lógica de negócios e relacionamentos.
* **Benefícios:** Melhora na legibilidade dos Eloquent Models, facilitação do desenvolvimento com autocompletação e tipagem corretas e conformidade estrita com as diretrizes do projeto.
