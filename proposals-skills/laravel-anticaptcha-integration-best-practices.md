# PROPOSTA DE SKILL: laravel-anticaptcha-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, or debugging CAPTCHA resolution services (Anti-Captcha) in the Laravel backend, including ImageToText tasks, handling API keys, handling errors, timeouts, and logging.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp realiza consultas automatizadas em concessionárias de energia e órgãos públicos que exigem a resolução de CAPTCHAs visuais (ImageToText). É essencial padronizar essa integração usando a biblioteca base existente, garantindo tratamento correto de falhas de conexão, créditos insuficientes e logs centralizados.
* **Recursos:** Padrões para invocação do serviço de Anti-Captcha, tratamento de exceções de rede e de API, tratamento de respostas nulas, configuração de credenciais via variáveis de ambiente/configurações, e logging detalhado das transações no canal 'anticaptcha'.
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para integração, resolução e monitoramento de serviços de quebra de CAPTCHA no backend Laravel do Engeapp.
* **Casos de uso:** Robôs de consulta de faturas e dados cadastrais em sites de concessionárias (ex: Equatorial, Enel, Neoenergia), automações que utilizam php-webdriver com necessidade de quebra de CAPTCHAs baseados em imagem.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Utilizará as diretrizes de criação de Services para encapsular a lógica de chamadas ao Anticaptcha.
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de exceções personalizados e registros nos canais de Log configurados (como o canal 'anticaptcha').
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Padronização do tratamento de CAPTCHAs, maior resiliência em falhas de rede com retentativas controladas, rastreabilidade completa por meio de logs específicos e facilidade na manutenção dos serviços de integração.
