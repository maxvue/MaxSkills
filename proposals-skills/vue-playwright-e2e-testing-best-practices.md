# PROPOSTA DE SKILL: vue-playwright-e2e-testing-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when setting up, writing, debugging, or configuring End-to-End (E2E) tests with Playwright in Vue 3 frontends. Triggers on configuring playwright.config.ts, writing test specs for page navigation, simulating user interactions, intercepting and mocking API network requests, testing responsiveness across mobile/desktop viewports, and integrating E2E tests into CI/CD pipelines.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O frontend do SocialMediaApp possui fluxos complexos como agendamento de posts no calendário editorial, visualização de prévias de mídias e painel interativo de IA. Testes unitários comuns não conseguem validar o comportamento real do navegador, renderização de layouts, tratamento de cookies, fluxos de autenticação completos e interceptação de chamadas de API externas em tempo real.
* **Recursos:**
  - Configuração do Playwright (`playwright.config.ts`) integrada ao servidor de desenvolvimento local (Vite/AdonisJS).
  - Estruturação de Page Object Model (POM) para reutilizar seletores e interações dos componentes customizados (`MaxComponentsUi`).
  - Técnicas de autenticação global para compartilhar o estado de login (armazenamento de cookies e localStorage) entre múltiplos specs.
  - Interceptação, monitoramento e simulação (mocking) de requisições de rede (APIs de redes sociais como Meta Graph, Instagram e WhatsApp).
  - Testes de regressão visual e captura de tela (screenshots/snapshots) para garantir a consistência das prévias de posts.
  - Simulação de interações ricas como arrastar e soltar (drag and drop) no calendário editorial e upload de arquivos grandes.
* **Objetivo:** Estabelecer diretrizes consistentes e eficientes para escrever e executar testes de ponta a ponta (E2E) com Playwright no frontend Vue 3, assegurando robustez e estabilidade em todos os fluxos críticos do SocialMediaApp.
* **Casos de uso:**
  - Validar o fluxo completo de login e alternância de layouts dinâmicos (Guest e Default).
  - Testar o comportamento do calendário editorial ao arrastar e soltar eventos entre dias diferentes.
  - Simular uma falha na API do Gemini para garantir que a interface apresente amigavelmente a mensagem de erro ao usuário.
* **Workflows:**
  - /bug-fix-front-end
* **Skills próprias utilizadas:**
  - `vue-vitest-testing-best-practices` — Para diferenciar quando uma funcionalidade deve ser validada via teste de unidade (Vitest) ou por fluxo E2E real (Playwright).
  - `vue-max-components-ui-development-best-practices` — Para mapear e interagir corretamente com componentes personalizados da biblioteca Max, como seletores e inputs acessíveis.
  - `vue-router-best-practices` — Para guiar o setup de rotas e guards de navegação a serem validados nos testes de fluxo de rotas.
* **Skills auxiliares:** vue-specialist, modern-web-guidance
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior confiabilidade nas entregas de fluxos complexos, detecção precoce de quebras de layout e regressões visuais, testes mais rápidos que emulam o comportamento real dos usuários de forma automatizada.
