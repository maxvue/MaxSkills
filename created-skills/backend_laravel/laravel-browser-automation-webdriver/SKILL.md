---
name: laravel-browser-automation-webdriver
description: Use when creating, reviewing, or debugging browser automation logic in Laravel backend using Facebook WebDriver, managing browser instances, handling pages, solving selectors, taking element screenshots, or using the custom Browser helper class.
---

# Browser Automation with WebDriver in Laravel

## Goal
Establish robust patterns, coding conventions, and exception handling guidelines for browser automation using Facebook WebDriver (GeckoDriver/Firefox) in the Laravel backend. This ensures stable web scraping, automatic homologation processes, and reliable interactions with external portals, preventing resource leaks and untraceable failures.

## Instructions

### 1. Connection & Lifecycle Management
*   **Preventing Zombie Processes**: Always wrap your WebDriver interactions in a `try...finally` block. The `$driver->quit()` method **must** be executed to kill the browser instance and GeckoDriver process on the server.
    ```php
    use Facebook\WebDriver\Remote\RemoteWebDriver;
    use Facebook\WebDriver\Remote\DesiredCapabilities;
    use Facebook\WebDriver\Firefox\FirefoxOptions;

    $options = new FirefoxOptions();
    $options->addArguments(['--headless', '--disable-gpu', '--no-sandbox']);
    $options->setPreference('dom.webdriver.enabled', false); // Help bypass simple anti-bot flags
    $options->setPreference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0');

    $capabilities = DesiredCapabilities::firefox();
    $capabilities->setCapability(FirefoxOptions::CAPABILITY, $options);

    $driver = null;
    try {
        $driver = RemoteWebDriver::create(config('services.webdriver.url'), $capabilities);
        // Automation logic here
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
*   **Concurrence and Port Management**: When scaling browser workers, manage concurrent instance limits using Laravel's Redis/Cache Lock system:
    ```php
    use Illuminate\Support\Facades\Cache;

    $lock = Cache::lock('webdriver_instance_limit', 60); // 60 seconds TTL

    if ($lock->get()) {
        try {
            // Run WebDriver process
        } finally {
            $lock->release();
        }
    }
    ```

### 2. Robust Selectors & Explicit Waits
*   **NO Hardcoded Sleeps**: Never use `sleep($seconds)` or `usleep()`. It causes slow executions and flaky processes.
*   **Explicit Waits**: Use `WebDriverWait` to wait dynamically for elements.
    ```php
    use Facebook\WebDriver\WebDriverBy;
    use Facebook\WebDriver\Support\WebDriverExpectedCondition;

    // Wait until an element is visible (max 10 seconds)
    $element = $driver->wait(10)->until(
        WebDriverExpectedCondition::visibilityOfElementLocated(WebDriverBy::cssSelector('#submit-btn'))
    );
    $element->click();
    ```
*   **Handling State Transitions**: When submitting a form or clicking a link, wait explicitly for the new page state or a success indicator:
    ```php
    $driver->wait(15)->until(
        WebDriverExpectedCondition::titleContains('Protocol Homologated')
    );
    ```

### 3. Capture and Element Screenshots
*   **Cropping Element Screenshots**: Use PHP GD library to crop an element out of a full-page screenshot. This is essential for Captchas, error audits, and proof of homologation:
    ```php
    use Facebook\WebDriver\WebDriverElement;

    public function captureElementScreenshot(RemoteWebDriver $driver, WebDriverElement $element, string $outputPath): void
    {
        // 1. Take full screenshot
        $tempPath = storage_path('app/temp_screenshot.png');
        $driver->takeScreenshot($tempPath);

        // 2. Get Element location and dimensions
        $location = $element->getLocation();
        $size = $element->getSize();

        $x = $location->getX();
        $y = $location->getY();
        $width = $size->getWidth();
        $height = $size->getHeight();

        // 3. Crop using GD
        $src = imagecreatefrompng($tempPath);
        $dest = imagecreatetruecolor($width, $height);
        
        imagecopy($dest, $src, 0, 0, $x, $y, $width, $height);
        imagepng($dest, $outputPath);

        // 4. Cleanup
        imagedestroy($src);
        imagedestroy($dest);
        @unlink($tempPath);
    }
    ```

### 4. Alert & Dialog Interactions
*   Handle javascript alerts or confirmations using the `switchTo()->alert()` interface:
    ```php
    try {
        $alert = $driver->switchTo()->alert();
        Log::channel('agent_browser')->info('Accepting alert: ' . $alert->getText());
        $alert->accept();
    } catch (\Facebook\WebDriver\Exception\NoAlertOpenException $e) {
        // No alert was present, continue normal execution
    }
    ```

### 5. Logging and Error Audits
*   **Logging Channel**: All browser automation logs should be directed to the `agent_browser` channel, as defined in `laravel-exception-handling-logging`.
*   **Save Page HTML on Failure**: In case of selectors failure or timeout, save the page source HTML and screenshot for troubleshooting.
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

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
*   **NEVER** use `sleep()` or `usleep()` for synchronization; always implement explicit `WebDriverWait` with conditions.
*   **NEVER** forget to close the webdriver sessions in a `finally` block; orphan processes will crash the application server due to memory leaks.
*   **DO NOT** log user credentials or session payloads in the `agent_browser` log channel.
*   **DO NOT** hardcode browser binary paths or selenium server URLs; use Laravel config files or `.env` parameters.
