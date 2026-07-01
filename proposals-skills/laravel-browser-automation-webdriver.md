# PROPOSTA DE SKILL: laravel-browser-automation-webdriver

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging browser automation logic in Laravel backend using Facebook WebDriver, managing browser instances, handling pages, solving selectors, taking element screenshots, or using the custom Browser helper class.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza homologações automáticas de projetos fotovoltaicos acessando sites de concessionárias de energia. Isso exige automações robustas no backend que evitem falhas de conexão, tratem erros de seletores, capturem evidências visuais (screenshots de elementos) e gerenciem o ciclo de vida do driver WebDriver (GeckoDriver/Firefox).
* **Recursos:** Ciclo de vida da conexão do WebDriver (gerenciamento de portas e processos com GeckoDriver), tratamento robusto de seletores e esperas explícitas, captura de screenshots recortadas de elementos para logs e auditorias, interação com caixas de alerta/diálogos e boas práticas para evitar detecção.
* **Objetivo:** Estabelecer padrões de boas práticas e convenções para a implementação e depuração de rotinas de automação Web com Facebook WebDriver e Firefox/GeckoDriver no ecossistema Laravel do Engeapp.
* **Casos de uso:** Robôs de consulta de viabilidade técnica em concessionárias, submissão automática de documentos de homologação solar, monitoramento de status de processos de engenharia fotovoltaica.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Para o registro padronizado de logs específicos do navegador (`agent_browser`) e manipulação de exceções de WebDriver.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Automações de browser mais estáveis e fáceis de depurar, com controle de concorrência de portas no Redis e mitigação de processos zumbis do GeckoDriver no servidor.
