---
name: vue-playwright-e2e-testing-best-practices
description: Use when setting up, writing, debugging, or configuring End-to-End (E2E) tests with Playwright in Vue 3 frontends. Triggers on configuring playwright.config.ts, writing test specs for page navigation, simulating user interactions, intercepting and mocking API network requests, testing responsiveness across mobile/desktop viewports, and integrating E2E tests into CI/CD pipelines.
---

## Objetivo
Estabelecer diretrizes limpas, manuteníveis e confiáveis para a escrita de testes de ponta a ponta (E2E) usando o Playwright em uma aplicação frontend Vue 3 (integrada com AdonisJS). Isso garante layouts visuais robustos, jornadas de usuário estáveis (como agendamento de postagens, visualizações de mídia e painéis interativos de IA) e comportamento resiliente sob dependências de APIs de terceiros.

## Instruções

### 1. Configuração do Playwright e Integração com Servidor Local
Integre o servidor de desenvolvimento/teste local no ciclo de vida do Playwright para que os testes rodem contra uma instância local previsível.
Configure o arquivo `playwright.config.ts` da seguinte forma:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3333',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3333',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### 2. Page Object Model (POM) para Componentes de Interface Customizados
Sempre utilize o padrão Page Object Model para encapsular seletores e ações, evitando duplicidade nos testes e simplificando a manutenção quando componentes customizados (do `MaxComponentsUi`) forem alterados.
- Busque elementos utilizando seletores resilientes, preferencialmente `data-testid` ou consultas baseadas em acessibilidade (como `role`, `label`).
- Evite depender de nomes de classes CSS que sejam autogerados ou dinâmicos.

**Exemplo de POM para uma Página de Login e Elementos do MaxComponentsUi (`tests/e2e/pages/LoginPage.ts`):**
```typescript
import { Locator, Page } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;

  constructor(page: Page) {
    this.page = page;
    // Mirando em elementos encapsulados pelo InputBase via data-testid ou atributos de acessibilidade
    this.emailInput = page.locator('input[data-testid="login-email"]');
    this.passwordInput = page.locator('input[data-testid="login-password"]');
    this.loginButton = page.locator('button[data-testid="login-submit"]');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}
```

### 3. Autenticação Global e Compartilhamento de Sessão
Para evitar fazer login antes de cada arquivo de teste individual (o que torna a execução muito lenta), use a configuração global do Playwright para se autenticar apenas uma vez, salvar o estado da sessão e reutilizá-lo em múltiplos testes.

**Passo A: Definir o projeto de setup em `playwright.config.ts`:**
```typescript
projects: [
  {
    name: 'setup',
    testMatch: /global\.setup\.ts/,
  },
  {
    name: 'chromium',
    use: { 
      ...devices['Desktop Chrome'],
      storageState: 'playwright/.auth/user.json',
    },
    dependencies: ['setup'],
  },
]
```

**Passo B: Implementar o script de setup (`tests/e2e/global.setup.ts`):**
```typescript
import { test as setup } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('http://localhost:3333/login');
  await page.locator('input[data-testid="login-email"]').fill('admin@engeapp.com.br');
  await page.locator('input[data-testid="login-password"]').fill('Secret123!');
  await page.locator('button[data-testid="login-submit"]').click();
  
  // Aguarda até o usuário ser redirecionado para a página do painel
  await page.waitForURL('**/dashboard');
  
  // Salva o estado do armazenamento contendo os cookies e localStorage da sessão
  await page.context().storageState({ path: authFile });
});
```

### 4. Interceptação de API e Mocking (Isolamento de Rede)
Não faça requisições reais para as APIs de produção de redes sociais (Meta Graph, WhatsApp, Instagram) ou serviços de IA (Gemini) durante a execução dos testes. Intercepte e simule essas chamadas usando `page.route()`.

**Exemplo: Simulando uma resposta de erro no coprocessador de IA Gemini (`tests/e2e/editorial-calendar.spec.ts`):**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Calendário Editorial - Coprocessador de IA', () => {
  test('deve exibir mensagem de erro amigável quando a API do Gemini falhar', async ({ page }) => {
    // Intercepta a rota da API do Gemini e retorna um status de erro 500
    await page.route('**/api/ai/generate-copy', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Gemini service is temporarily unavailable' }),
      });
    });

    await page.goto('/calendar');
    await page.locator('button[data-testid="ai-suggest-btn"]').click();
    
    // Valida se a interface exibe um card de erro amigável
    const errorAlert = page.locator('[data-testid="ai-error-alert"]');
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toContainText('Gemini service is temporarily unavailable');
  });
});
```

### 5. Interações Ricas: Arrastar e Soltar no Calendário
Simule movimentos complexos de mouse, como arrastar eventos editoriais entre células do calendário (ex: FullCalendar).
```typescript
test('deve arrastar e soltar um evento para reagendá-lo', async ({ page }) => {
  await page.goto('/calendar');

  const sourceEvent = page.locator('.fc-event:has-text("Draft Instagram Post")').first();
  const targetCell = page.locator('.fc-dayGridMonth-view .fc-day[data-date="2026-06-30"]').first();

  // Executa a ação de arrastar e soltar
  await sourceEvent.dragTo(targetCell);

  // Valida a alteração persistida (ex: mensagem toast ou interceptação da requisição de mock)
  const toast = page.locator('[data-testid="toast-notification"]');
  await expect(toast).toContainText('Post rescheduled successfully');
});
```

### 6. Regressão Visual e Responsividade
Utilize snapshots para realizar verificações visuais em layouts de páginas cruciais e garantir a responsividade em viewports de dispositivos móveis e desktops.
```typescript
test('a prévia de mídia deve renderizar corretamente', async ({ page }) => {
  await page.goto('/calendar/event/1');
  
  // Aguarda que os recursos de mídia sejam carregados
  await page.waitForSelector('[data-testid="media-player"] img');
  
  // Captura o screenshot e compara com o snapshot de referência
  await expect(page.locator('[data-testid="media-preview-container"]')).toHaveScreenshot('media-preview-baseline.png');
});
```

## Restrições
1. **Nenhuma Requisição Real para Terceiros**: Nunca permita que os testes acessem diretamente APIs externas reais (Meta, WhatsApp, Google Gemini). Sempre utilize `page.route()` para mockar os payloads de rede.
2. **Evitar Seletores Frágeis**: Não use classes de estilização (ex: hashes aleatórios do UnoCSS ou combinações dinâmicas de classes utilitárias) ou caminhos hierárquicos profundos (ex: `div > div > span`). Utilize funções baseadas em acessibilidade (`getByRole`), conteúdo de texto (`getByText`) ou atributos `data-testid`.
3. **Sem Contaminação do Banco de Dados**: Certifique-se de que cada teste seja executado em um estado isolado ou que as transações do banco de dados sejam limpas. Simule consultas de backend quando aplicável ou remova os registros criados durante o teste.
4. **Distinção entre Vitest e Playwright**: Não utilize o Playwright para realizar testes unitários em funções isoladas ou validação simples de props de componentes. Utilize o Playwright estritamente para renderização de layout visual, navegações cross-origin, integrações de rotas e cenários completos de usuário. Use o Vitest para componentes isolados e lógica de unidade.
