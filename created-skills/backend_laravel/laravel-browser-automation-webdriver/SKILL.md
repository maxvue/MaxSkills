---
name: laravel-browser-automation-webdriver
description: "Use when creating, modifying, or debugging web browser automation tasks (Selenium WebDriver, Dusk, Puppeteer, Python RPA) in Laravel or backend microservices. Covers browser automation, driver configuration, and element interactions."
---
# Automação de Navegador com WebDriver no engeapp

## Objetivo
Padrões fiéis à implementação real de automação de navegador do backend engeapp, centrada na classe `App\Classes\Browser` sobre `php-webdriver/webdriver` (Facebook WebDriver) dirigindo **Firefox via geckodriver**. Serve web scraping, homologação de projetos e interações com portais externos. O foco é evitar o vazamento característico deste stack: **processo geckodriver órfão + porta Redis presa**.

## Arquitetura real (leia antes de mexer)

Não existe um servidor Selenium único nem `config('services.webdriver.url')`. Cada instância de `Browser` sobe **seu próprio** processo geckodriver:

*   O construtor procura uma porta livre no intervalo `44500..44599` gravando num hash Redis `geckodriver_ports` com `Redis::hsetnx('geckodriver_ports', $p, ...)`. Se nenhuma porta estiver livre, lança `Exception`.
*   Inicia o driver com `Symfony\Component\Process\Process::fromShellCommandline("geckodriver --port {$port}")` e registra `pid`+`time` no hash Redis.
*   Faz `sleep(2)` **de propósito** para o geckodriver terminar de subir antes de conectar.
*   Conecta em `http://127.0.0.1:{$port}/` (host fixo local — o driver é sempre local à instância).
*   Guarda `WebDriverWait($this->driver, 10)` em `$this->wait`.

> Observação: `config('app.webdriver_host')` e `config('app.webdriver_port')` existem em `config/app.php`, mas a classe `Browser` atual **não** os consome (usa `127.0.0.1` + porta dinâmica). Não escreva código assumindo que essas chaves controlam a conexão.

### Ciclo de vida e teardown
O teardown é feito no `__destruct()`, não em `try/finally` do chamador. Ele: chama `quit()` (fecha a sessão), faz `geckoProcess->stop(3, 9)` (SIGTERM→SIGKILL) e `Redis::hdel('geckodriver_ports', $port)`. Por isso, **descarte a instância** (`unset`/fim de escopo) para liberar porta e processo.

*   Nos serviços que orquestram vários passos (ex.: `App\Services\Browser\BrowserPlaybookExecutor`), há também um `finally { $this->browser->quit(); }` explícito para fechar a sessão cedo, além do `__destruct`.
*   Portas/processos que travam (crash, kill abrupto) são varridos pelo command `geckodriver:cleanup-ports` (`App\Console\Commands\CleanupGeckodriverPorts`): itera o hash Redis, e para entradas com mais de 5 min faz `kill -9 {pid}` + `fuser -k -n tcp {port}` + `Redis::hdel`. Agende-o para não esgotar o pool de 100 portas.

## Instruções

### 1. Instanciar o Browser
Use o construtor do helper — não monte `RemoteWebDriver` cru. As `FirefoxOptions` já vêm configuradas na classe (`binary` `/usr/bin/firefox`, `--window-size=1920,1080`, preferências de download de PDF e anti-detecção `dom.webdriver.enabled=false`/`useAutomationExtension=false`).

```php
use App\Classes\Browser;

// Abre já numa URL (opcional); sem URL, navegue depois com openUrl()
$browser = new Browser('https://portal.exemplo.com');
// ... automação ...
// Não precisa fechar manualmente: o __destruct cuida de quit + stop + hdel.
// Para liberar cedo em serviços longos:
$browser->quit();
```

*   **Headless**: no código atual a flag `-headless` está **comentada** (Firefox roda com janela). Se precisar headless, a flag correta do Firefox é `-headless` (traço único) — **não** `--headless`, `--disable-gpu` ou `--no-sandbox`, que são flags de Chrome/Chromium e não se aplicam ao Firefox.

### 2. Seletores e busca de elementos
Resolva o tipo de seletor com `resolveSelector($type, $value)`, que faz `match` de `id | name | css | xpath | class` para o `WebDriverBy` correspondente (default: `id`). Busque com `getElement()`.

```php
$by = $browser->resolveSelector('css', '#submit-btn');

// time_out = 0 → findElement direto (pode lançar NoSuchElement)
// time_out > 0 → CONTADOR DE TENTATIVAS: faz (time_out*2) tentativas consecutivas,
//                retornando null se nenhuma encontrar o elemento.
$element = $browser->getElement($by, 10);

if ($element) {
    $element->click();
}
```

> **Armadilha:** `$time_out` NÃO é segundos de espera. `getElement` chama `sleep(0.5)` (Browser.php:136) no `catch` do loop, mas `sleep()` espera um `int` — `0.5` é truncado para `0`, então cada tentativa dorme ~0s (e emite deprecation de conversão implícita float→int em PHP 8.1+). Ou seja, `getElement($by, 10)` faz 20 tentativas em milissegundos, não espera ~10s. Trate `$time_out` como contador de tentativas, não como tempo; para espera real, use `usleep()` explícito ou aceite que `time_out` alto só aumenta o número de retries, não a duração.

Atalhos por tipo: `elementById`, `elementByName`, `elementByCss`, `elementByClass`, `elementsByClass` (retorna array). Para `<select>`, use `selectByVisibleText($element, $texto)` ou variantes `selectByVisibleTextById/ByName/ByClass/ByCss`. Textos/valores: `getText($element)`, `getValue($element)`.

> **`elementByIdExist($id, $delay)` está quebrado — não o recomende como polling booleano confiável.** `elementById` delega a `getElement` com `time_out > 0` (que retorna `null` quando não acha), mas `elementById` declara retorno NÃO-nulável `: RemoteWebElement`. Elemento ausente gera `TypeError` (subclasse de `Error`, não `Exception`) — e o `catch (Exception $e)` de `elementByIdExist` não o captura, propagando um fatal em vez de retornar `false`. Prefira `getElement($by, $n) !== null`, ou `elementById($id, 0)` dentro de `try/catch (Throwable $e)`.

> Esperas: o projeto **não** usa `WebDriverExpectedCondition` nem `$driver->wait(...)->until(...)`. A convenção efetiva é **polling por retry** dentro de `getElement()` (via `time_out`) e esperas por tempo no executor (ver abaixo). Siga esse padrão para manter consistência com o código existente.

### 3. Esperas por tempo — permitidas e usadas por design
Este stack usa `sleep()`/`usleep()` deliberadamente; não são proibidos:

*   `Browser::__construct` usa `sleep(2)` (inteiro) para o geckodriver inicializar — essa espera funciona como esperado.
*   `Browser::getElement` e `elementByIdExist` chamam `sleep(0.5)` nos loops de retry, mas por `sleep()` truncar float para int, isso dorme ~0s na prática — não conte com essa chamada para introduzir espera real entre tentativas (ver armadilha na seção 2).
*   `BrowserPlaybookExecutor` usa `usleep($step->wait_before_ms * 1000)` e `usleep($step->wait_after_ms * 1000)` como **recurso configurável** de cada passo, e `actionWait`/`actionDownload` também dependem de `usleep`.

Prefira `getElement($by, $timeout)` (polling por elemento) quando o objetivo é aguardar um elemento aparecer; use `usleep`/`sleep` para pausas fixas de sincronização quando não há elemento-alvo claro (transições, downloads).

### 4. Screenshots com GD (página inteira ou recorte de elemento)
Use `Browser::screenshot()`. Assinatura real:

```php
public function screenshot(
    RemoteWebElement|string|null $element_or_file_name = null,
    $x_adjust = 0, $y_adjust = 0, $w = null, $h = null
) : ?string
```

*   Passe uma **string** para nomear o arquivo (screenshot da página inteira): `$browser->screenshot("step-1-before")`.
*   Passe um **RemoteWebElement** para recortar aquele elemento via `imagecrop` do GD: `$browser->screenshot($element)`. Retorna o caminho do PNG em `sys_get_temp_dir()`.
*   `$x_adjust`/`$y_adjust` deslocam a origem; `$w`/`$h` aceitam número absoluto ou string com `+`/`-` (ex.: `'+20'`) para ajustar largura/altura relativas ao elemento. Requer a extensão GD (a classe loga erro no canal `agent_browser` e retorna `null` se ausente).

Screenshots de elemento são usadas para Captchas, auditoria de erros e comprovação de homologação (ver `BrowserGetImage`, que devolve `file_path` + `base64`).

### 5. Alerts e diálogos
Use `aceptDialog()` — ele encapsula `switchTo()->alert()`, loga o texto no canal `agent_browser` e aceita o diálogo, retornando `bool`. Erros são capturados e logados como warning ("Continuando..."), então não interrompem o fluxo.

```php
$browser->aceptDialog();
```

### 6. Logging e auditoria de falhas
*   **Canal**: todos os logs de automação vão para o canal `agent_browser` (definido em `config/logging.php`, `storage/logs/agent_browser.log`). A própria classe `Browser` já loga início, inicialização do wait e erros de screenshot nesse canal.
*   **Em caso de falha de passo**, capture evidência: tire `screenshot()` e, se útil, `$browser->driver->getPageSource()` para diagnóstico. `BrowserPlaybookExecutor` registra a falha via `$execution->markFailed($order, $error)` e anexa screenshots com `$execution->addScreenshot($path)`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo desta skill esteja escrito. Comentários de código em pt-BR.
- **NÃO** registre credenciais ou payloads de sessão no canal `agent_browser`.
