# PROPOSTA DE SKILL: laravel-prompts-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or styling interactive console/CLI inputs using Laravel Prompts. Triggers on text prompts, password fields, select/confirm prompts, spinner loading screens, multi-select questions, and validation in CLI commands.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui diversos comandos Artisan para tarefas operacionais, e o uso de interações tradicionais por console (como `$this->ask()` ou `$this->confirm()`) carece de uma interface amigável, validação integrada de inputs e suporte a estados visuais como spinners de progresso.
* **Recursos:** Utilização de `text`, `password`, `select`, `confirm`, `multiselect`, `suggest`, `spin`, além de tratamento de fallbacks não interativos e validação de inputs no terminal.
* **Objetivo:** Estabelecer diretrizes sólidas e padrões consistentes para o uso da biblioteca Laravel Prompts em comandos Artisan interativos, melhorando a experiência do desenvolvedor e operador no terminal.
* **Casos de uso:** Comandos Artisan de setup inicial de projetos, importações manuais interativas, disparos pontuais de tarefas de IA com parâmetros fornecidos no terminal e confirmação de ações destrutivas (ex: limpeza de logs).
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará a estrutura básica e os atributos de definição de comandos Artisan (`#[Signature]`, `#[Description]`) para encapsular as interações do Laravel Prompts no método `handle()`.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada ao dispor de um guia especializado para interfaces CLI ricas e interativas, mantendo a responsabilidade de I/O elegante.
* **Benefícios:** Interface de console mais intuitiva e agradável, menor incidência de erros de entrada de dados via validação em tempo real no console, e melhor feedback visual durante operações demoradas (com o spinner).
