# PROPOSTA DE SKILL: laravel-log-viewer-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when configuring, securing, viewing, or managing application logs via the web UI using the opcodesio/log-viewer package in Laravel. Triggers on log-viewer configuration, security gating, route definition, custom log paths, and log clean-up settings.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui múltiplos canais de log de integração (como whatsapp, gemini, asaas). Centralizar e analisar esses logs em uma interface web rica, segura e restrita é essencial para depuração rápida no dia a dia da equipe de desenvolvimento.
* **Recursos:** Configurações de acesso seguro (Gate), customização de visualização de logs, formatação de exceções detalhadas, otimização de performance para arquivos grandes e controle de retenção de logs.
* **Objetivo:** Estabelecer padrões de configuração e segurança no uso do pacote opcodesio/log-viewer.
* **Casos de uso:** Visualização de logs de integração com APIs externas (ex. Asaas, Gemini, Whatsapp), busca rápida por exceções e rastreamento de erros de Jobs em background.
* **Workflows:**
  - bug-fix-back-end
  - deploy
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará as práticas de estruturação de logs e canais do Laravel para garantir que o Log Viewer organize corretamente os arquivos de logs por canal e contexto.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Facilidade de depuração em tempo real, interface centralizada para múltiplos canais de logs e segurança aprimorada no acesso a dados sensíveis de log em produção.
