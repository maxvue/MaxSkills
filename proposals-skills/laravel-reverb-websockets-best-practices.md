# PROPOSTA DE SKILL: laravel-reverb-websockets-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, optimizing, debugging, or deploying the Laravel Reverb WebSocket server, managing connections, setting up Supervisor processes, or tuning performance for real-time applications.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp faz uso intenso de comunicação em tempo real (como no Planner e chat de atendimento). O Laravel Reverb oferece uma alternativa nativa e extremamente rápida ao Pusher/Soketi, mas requer diretrizes claras de configuração de infraestrutura, segurança com TLS e monitoramento de conexões ativas para garantir estabilidade sob alta carga.
* **Recursos:** Configurações do arquivo `.env` para produção (host, porta, SSL), parametrização do Supervisor/systemd, segurança com TLS e proxy reverso Nginx/Caddy, monitoramento e comandos CLI do Reverb (como `reverb:start`), e depuração de desconexões.
* **Objetivo:** Padronizar a configuração, implantação e manutenção do servidor Laravel Reverb para conexões seguras, estáveis e de alta performance.
* **Casos de uso:** Instalação do Reverb em ambiente de produção, diagnóstico de quedas de conexões websocket, configuração de TLS/SSL para canais wss:// seguros.
* **Workflows:**
  - bug-fix-back-end
  - deploy
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Para estruturação e monitoramento de logs de falhas de handshake e erros do WebSocket.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada por rodar sobre uma infraestrutura Reverb otimizada e estável.
* **Benefícios:** Infraestrutura WebSocket totalmente integrada e gratuita (reduzindo dependência de terceiros como Pusher), menor latência nas transmissões e maior facilidade de escalabilidade horizontal.
