---
name: laravel-browser-automation-webdriver
description: Use when creating, reviewing, or debugging browser automation logic in Laravel backend using Facebook WebDriver, managing browser instances, handling pages, solving selectors, taking element screenshots, or using the custom Browser helper class.
---

# Automação de Navegador com WebDriver no Laravel

## Objetivo
Estabelecer padrões robustos, convenções de código e diretrizes de tratamento de exceções para automação de navegador usando Facebook WebDriver (GeckoDriver/Firefox) no backend Laravel. Isso garante web scraping estável, processos de homologação automáticos e interações confiáveis com portais externos, prevenindo vazamentos de recursos e falhas não rastreáveis.

## Instruções

### 1. Gerenciamento de Conexão e Ciclo de Vida
*   **Prevenindo Processos Zumbis**: Sempre envolva suas interações com o WebDriver em um bloco `try...finally`. O método `$driver->quit()` **deve** ser executado para encerrar a instância do navegador e o processo GeckoDriver no servidor.
    ```php
    use Facebook\WebDriver\Remote\RemoteWebDriver;
    use Facebook\WebDriver\Remote\DesiredCapabilities;
    use Facebook\WebDriver\Firefox\FirefoxOptions;

    $options = new FirefoxOptions();
    $options->addArguments(['--headless', '--disable-gpu', '--no-sandbox']);
    $options->setPreference('dom.webdriver.enabled', false); // Ajuda a contornar flags simples de anti-bot
    $options->setPreference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0');

    $capabilities = DesiredCapabilities::firefox();
    $capabilities->setCapability(FirefoxOptions::CAPABILITY, $options);

    $driver = null;
    try {
        $driver = RemoteWebDriver::create(config('services.webdriver.url'), $capabilities);
        // Lógica de automação aqui
    } catch (\Throwable $e) {
        Log::channel('agent_browser')->error('WebDriver automation failed', [
            'exception' => $e->getMessage(),
            'trace' => $e->getTraceAsString(),
        ]);
        throw $e;
    } finally {
        if ($driver instanceof RemoteWebDriver) {
            $driver->quit();
        }
    }
    ```
*   **Concorrência e Gerenciamento de Portas**: Ao escalar workers de navegador, gerencie os limites de instâncias concorrentes usando o sistema de Lock do Redis/Cache do Laravel:
    ```php
    use Illuminate\Support\Facades\Cache;

    $lock = Cache::lock('webdriver_instance_limit', 60); // TTL de 60 segundos

    if ($lock->get()) {
        try {
            // Executa o processo do WebDriver
        } finally {
            $lock->release();
        }
    }
    ```

### 2. Seletores Robustos e Esperas Explícitas
*   **SEM Sleeps Fixos**: Nunca use `sleep($seconds)` ou `usleep()`. Isso causa execuções lentas e processos instáveis (flaky).
*   **Esperas Explícitas**: Use `WebDriverWait` para aguardar dinamicamente por elementos.
    ```php
    use Facebook\WebDriver\WebDriverBy;
    use Facebook\WebDriver\Support\WebDriverExpectedCondition;

    // Aguarda até que um elemento esteja visível (máximo de 10 segundos)
    $element = $driver->wait(10)->until(
        WebDriverExpectedCondition::visibilityOfElementLocated(WebDriverBy::cssSelector('#submit-btn'))
    );
    $element->click();
    ```
*   **Lidando com Transições de Estado**: Ao enviar um formulário ou clicar em um link, aguarde explicitamente pelo novo estado da página ou por um indicador de sucesso:
    ```php
    $driver->wait(15)->until(
        WebDriverExpectedCondition::titleContains('Protocol Homologated')
    );
    ```

### 3. Captura e Screenshots de Elementos
*   **Recortando Screenshots de Elementos**: Use a biblioteca PHP GD para recortar um elemento de uma screenshot de página inteira. Isso é essencial para Captchas, auditorias de erros e comprovações de homologação:
    ```php
    use Facebook\WebDriver\WebDriverElement;

    public function captureElementScreenshot(RemoteWebDriver $driver, WebDriverElement $element, string $outputPath): void
    {
        // 1. Tira a screenshot completa
        $tempPath = storage_path('app/temp_screenshot.png');
        $driver->takeScreenshot($tempPath);

        // 2. Obtém a localização e as dimensões do elemento
        $location = $element->getLocation();
        $size = $element->getSize();

        $x = $location->getX();
        $y = $location->getY();
        $width = $size->getWidth();
        $height = $size->getHeight();

        // 3. Recorta usando o GD
        $src = imagecreatefrompng($tempPath);
        $dest = imagecreatetruecolor($width, $height);
        
        imagecopy($dest, $src, 0, 0, $x, $y, $width, $height);
        imagepng($dest, $outputPath);

        // 4. Limpeza
        imagedestroy($src);
        imagedestroy($dest);
        @unlink($tempPath);
    }
    ```

### 4. Interações com Alerts e Diálogos
*   Trate alerts ou confirmações javascript usando a interface `switchTo()->alert()`:
    ```php
    try {
        $alert = $driver->switchTo()->alert();
        Log::channel('agent_browser')->info('Accepting alert: ' . $alert->getText());
        $alert->accept();
    } catch (\Facebook\WebDriver\Exception\NoAlertOpenException $e) {
        // Nenhum alert estava presente, continua a execução normal
    }
    ```

### 5. Logging e Auditorias de Erro
*   **Canal de Logging**: Todos os logs de automação de navegador devem ser direcionados ao canal `agent_browser`, conforme definido em `laravel-exception-handling-logging`.
*   **Salvar o HTML da Página em Caso de Falha**: Em caso de falha de seletores ou timeout, salve o HTML fonte da página e a screenshot para diagnóstico.
    ```php
    catch (\Throwable $e) {
        if ($driver instanceof RemoteWebDriver) {
            $html = $driver->getPageSource();
            Storage::put('webdriver/failures/' . now()->timestamp . '.html', $html);
            $driver->takeScreenshot(storage_path('app/webdriver/failures/' . now()->timestamp . '.png'));
        }
        throw $e;
    }
    ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
*   **NUNCA** use `sleep()` ou `usleep()` para sincronização; sempre implemente `WebDriverWait` explícito com condições.
*   **NUNCA** esqueça de fechar as sessões do webdriver em um bloco `finally`; processos órfãos vão travar o servidor da aplicação devido a vazamentos de memória.
*   **NÃO** registre credenciais de usuário ou payloads de sessão no canal de log `agent_browser`.
*   **NÃO** deixe caminhos de binários de navegador ou URLs de servidor selenium fixos no código (hardcode); use arquivos de config do Laravel ou parâmetros do `.env`.
