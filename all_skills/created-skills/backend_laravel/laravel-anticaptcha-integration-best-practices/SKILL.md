---
name: laravel-anticaptcha-integration-best-practices
description: "Use when implementing or debugging CAPTCHA resolution services (Anti-Captcha) in Laravel, including ImageToText tasks, API keys, error handling, timeouts, and logging. Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Integração com Anti-Captcha no Laravel

## Objetivo
Fornecer diretrizes claras e estruturadas e padrões de código para integrar, resolver e monitorar serviços de resolução de CAPTCHA (especificamente o Anti-Captcha) no backend Laravel do ecossistema Engeapp, garantindo resiliência, configuração segura, tratamento robusto de erros e logging dedicado.

## Instruções

### 1. Configuração e Gerenciamento de Chaves
- Sempre use variáveis de ambiente para armazenar a chave de API do Anti-Captcha.
- A configuração deve ser lida via `config('app.anticaptcha')`, que aponta para `env('ANTICAPTCHA_KEY')` em `config/app.php`.
- NÃO fixe a chave de API diretamente em classes, controllers ou services.
- Sempre verifique se a chave de API está configurada antes de iniciar uma requisição de captcha. Se estiver vazia, falhe de forma controlada ou lance uma exceção de configuração.

### 2. Utilizando as Classes do App
O Engeapp possui classes wrapper para o Anti-Captcha em `App\Classes\Anticaptcha`:
- **`App\Classes\Anticaptcha\Anticaptcha`**: Use o helper estático `image(string $path, array $options = [])` para tarefas rápidas de ImageToText. Ele cuida da instanciação, criação da tarefa e polling automaticamente.
- **`App\Classes\Anticaptcha\ImageToText`**: Instanciação direta para CAPTCHAs visuais mais customizados.
  - Defina o arquivo de imagem usando `$api->setFile($filePath)`.
  - Defina flags opcionais booleanas (ex.: `$api->phrase = true`, `$api->numeric = true` para exigir apenas dígitos, `$api->case = true` para diferenciar maiúsculas/minúsculas). Para restringir tamanho use os inteiros `$api->minLength` / `$api->maxLength`.
  - Chame `$api->createTask()` para submeter.
  - Chame `$api->waitForResult()` para fazer polling da solução.
  - Recupere o texto resolvido com `$api->getTaskSolution()`.

### 3. Tratamento de Erros e Resiliência
- A resolução de captcha depende de APIs externas e está sujeita a falhas de rede, timeouts ou saldo insuficiente.
- Verifique os valores de retorno:
  - Se `createTask()` retornar `false` ou `null`, ocorreu um erro na criação da tarefa. Inspecione `$api->errorMessage` ou `$api->errorCode`.
  - Se `waitForResult()` retornar `false`, o processamento da tarefa expirou (timeout) ou falhou.
- Implemente retries com backoff caso a conexão de rede caia, mas limite o tempo total de execução (o timeout padrão da API é de 30s por requisição, o polling leva até 300s por padrão).
- Falhas de rede/HTTP já são capturadas dentro de `AnticaptchaBase::jsonPostRequest()` e chegam ao chamador como `createTask() === null` e `waitForResult() === false`, com o detalhe em `$api->errorMessage` — não envolva as chamadas em `try`/`catch` de `ConnectionException`/`RequestException`.

### 4. Logging de Transações
- Todas as transações de captcha devem ser registradas no canal dedicado `anticaptcha` (`Log::channel('anticaptcha')`).
- O canal `anticaptcha` já é alimentado automaticamente pelos property hooks de `AnticaptchaBase` (`$errorMessage` → `error`, `$successMessage` → `info`, `$debugMessage` → `debug`) sempre que essas propriedades são atribuídas. Log manual do chamador deve trazer apenas contexto extra (ex.: `taskId` + solução), nunca repetir `$api->errorMessage` — ele já foi logado no set do hook.
- Registre avisos ou erros com contexto: inclua o arquivo de origem, a descrição do erro, o ID da tarefa e metadados relevantes (excluindo chaves secretas).
- Os logs são roteados para o canal `anticaptcha` (driver `daily`), que grava arquivos diários como `storage/logs/anticaptcha-YYYY-MM-DD.log` (retenção padrão de 15 dias via `LOG_DAILY_DAYS`). Ao depurar, procure o arquivo do dia correspondente, não um `anticaptcha.log` fixo.

## Exemplos

### Exemplo 1: Resolvendo uma Imagem de CAPTCHA usando o Wrapper Estático
> **Cuidado com `'case'` no wrapper estático:** `Anticaptcha::image()` (`App\Classes\Anticaptcha\Anticaptcha::image`) trata a chave `case` (e variações `casesensitive`/`case_sensitive`/`caseSensitive`) chamando `$api->setCaseFlag(...)` — método que **não existe** em `ImageToText` nem em `AnticaptchaBase`, e por isso lança um `Error` em tempo de execução. Até esse bug ser corrigido no código, evite passar `'case'` via `Anticaptcha::image()`; use a classe `ImageToText` diretamente (Exemplo 2), que aceita a propriedade `$api->case` sem problema.

```php
use App\Classes\Anticaptcha\Anticaptcha;
use Illuminate\Support\Facades\Log;

$imagePath = storage_path('app/captchas/temp_captcha.png');

if (!file_exists($imagePath)) {
    Log::channel('anticaptcha')->error("Captcha image file not found at: {$imagePath}");
    return null;
}

// Resolve usando o helper estático com opções customizadas (apenas números)
// Evite a chave 'case' aqui — ver aviso acima sobre o bug em setCaseFlag().
$solution = Anticaptcha::image($imagePath, [
    'numeric' => true,
]);

// Falhas já foram logadas automaticamente pelos property hooks de AnticaptchaBase.
if ($solution !== null) {
    Log::channel('anticaptcha')->info("Captcha resolved successfully: {$solution}");
}
```

### Exemplo 2: Fluxo Detalhado usando a Classe ImageToText Diretamente
```php
use App\Classes\Anticaptcha\ImageToText;
use Illuminate\Support\Facades\Log;

$api = new ImageToText();
$imagePath = storage_path('app/captchas/temp_captcha.png');

if (!$api->setFile($imagePath)) {
    // A falha já foi logada automaticamente pelo hook de errorMessage.
    return null;
}

// Configura as opções
$api->phrase = false;
$api->numeric = true; // flag booleana: exige que a solução contenha apenas dígitos
$api->minLength = 4;
$api->maxLength = 6;

// Cria a tarefa
$taskCreated = $api->createTask();
if ($taskCreated === null || $taskCreated === false) {
    // A falha já foi logada automaticamente pelo hook de errorMessage.
    return null;
}

Log::channel('anticaptcha')->info("Captcha task created. Task ID: {$api->taskId}");

// Faz polling do resultado (máximo de 120 segundos)
$solved = $api->waitForResult(120);

if (!$solved) {
    // A falha já foi logada automaticamente pelo hook de errorMessage.
    return null;
}

$solution = $api->getTaskSolution();
Log::channel('anticaptcha')->info("Captcha solved successfully. Task ID: {$api->taskId}, Result: {$solution}");
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** faça commit da chave de API (`ANTICAPTCHA_KEY`) no Git. Mantenha-a no arquivo `.env`.
- **NÃO** use canais de log padrão para logs de captcha; sempre escreva em `Log::channel('anticaptcha')`.
- **NÃO** fixe períodos longos de sleep ou loops de polling infinitos. Use `$api->waitForResult($maxSeconds)` com um timeout sensato para evitar travar processos worker do Laravel ou threads do Octane.
