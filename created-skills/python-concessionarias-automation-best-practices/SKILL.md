---
name: python-concessionarias-automation-best-practices
description: Use when creating, modifying, reviewing, or debugging Python RPA automation scripts (Selenium, requests) for solar utility concessionaires (Cemig, Energisa, Equatorial, Coelba) or Sinceti/TRT. Triggers on files using selenium, anticaptchaofficial/AntiCaptcha solving, Engeapp callbacks (consulta_engeapp, registra.php, normas.php), the barra()/print_dev() helpers, or web scraping utility functions from functions.py.
---

# Boas Práticas de Automação (RPA) Python para Concessionárias

> **Escopo:** scripts Python (Selenium + requests) que automatizam portais de concessionárias de energia (Cemig, Energisa, Equatorial, Coelba) e Sinceti/TRT, integrados ao backend do Engeapp. Esta skill é do ecossistema **Python/RPA** — não faz parte da stack Node/Vue (Maxdmin).

## Objetivo
Estabelecer padrões robustos de qualidade, resiliência, tratamento de exceções e integração de callback para os robôs/scripts Python que submetem projetos fotovoltaicos, consultam status e assinam TRTs, garantindo execução confiável apesar da instabilidade dos portais.

---

## Instruções

### 1. Funções Utilitárias Compartilhadas (`functions.py`)
Sempre importe e use os wrappers padrão de [functions.py](file:///home/johnattas/GitHub/Python/functions.py) (`from functions import *`) em vez de chamadas diretas do Selenium — eles já encapsulam espera de elemento, timeout e scroll:
- **Ciclo de vida do webdriver:** inicialize com `chrome(url, hide_screen, folder, time_loadpage, time_wait, nav)` (configura headless, diretório de download e timeouts).
- **Interação:** prefira `clica(By, locator)`, `digita(By, locator, valor)`, `seleciona_select(By, locator, valor)`, `seleciona_item(By, locator)`, `checkbox(By, locator, bool)`, `envia_arquivo(By, locator, filepath)`.
- **Selects resilientes:** `seleciona_select(...)` normaliza textos (remove acentos/espaços) para casar opções de forma tolerante.

### 2. Resiliência de Timeout e Carregamento
- Os portais são lentos e instáveis. **Não** use esperas estáticas (`time.sleep(10)`); configure `chrome(time_wait=...)` ou use `WebDriverWait` quando apropriado.
- Envolva navegação e etapas cruciais em `try-except`, tratando explicitamente `TimeoutException` e `NoSuchElementException`.
- Implemente loops de retentativa (até ~3 tentativas) para envio de formulários críticos.

### 3. Resolução de Captchas (API AntiCaptcha)
- **Imagem:** `captha_imagem(By, locator)` — remova o arquivo temporário gerado via `os.remove()` imediatamente após resolver, evitando lixo em disco.
- **ReCaptcha v2:** `captha_gRecaptcha(By, locator, url)` — passe a sitekey e a URL corretas.
- **Erros:** se a API falhar, registre log detalhado e aborte/refaça a etapa. Nunca submeta formulários com captcha vazio/inválido.
- **Chaves:** nunca faça hardcode da chave do AntiCaptcha — carregue de variáveis de ambiente ou de payloads de inicialização do backend.

### 4. Downloads e Operações de Arquivo
- Defina um `folder` único e isolado por execução em `chrome(folder=...)`.
- Ao baixar PDFs/diagramas unifilares/TRTs, faça loop de verificação (ex: `time.sleep(0.3)`) até que arquivos `.crdownload` (Chrome) / `.part` (Firefox) desapareçam **antes** de renomear ou processar.
- Renomeie de forma determinística (ex: `TRT_[project_id]_[timestamp].pdf`) e mova com `shutil.move()`/`os.rename()`. Normalize nomes inválidos com `unicodedata.normalize` + substituição de caracteres.

### 5. Integração e Callbacks com o Backend Engeapp
- Busque tarefas/dados com `consulta_engeapp(campos)` ou `consulta_enge_app_3(dados)`.
- Reporte progresso/resultados ao backend Laravel via `requests` para os endpoints apropriados (ex: `registra.php`, `normas.php`).
- Implemente retentativa (até ~6 tentativas) com `try-except` em **todas** as chamadas HTTP para sobreviver a falhas temporárias de rede.
- **Estrutura do payload de callback:**
  - `project_id` — identificador do projeto.
  - `status` — estado da homologação (`Submitted`, `Approved`, `Pending Corrections`, `Error`).
  - `protocol_number` — protocolo gerado pela concessionária (em sucesso).
  - `error_message` — exceção + stack trace (em falha).
  - `log_data` — etapas cruciais (timestamps, status do captcha, marcos de navegação).

### 6. Progresso, Logs e Segurança
- Informe o painel do Engeapp com `barra(porcentagem, mensagem)` (ex: `barra(10, 'Iniciando login.')`).
- Evite saída verbosa em produção; use `print_dev()` / a variável global `dev` para logs de desenvolvimento.
- Nunca faça hardcode de credenciais, senhas, chaves de API, CPF ou CNPJ — obtenha de `.env` ou dinamicamente do backend.

---

## Restrições
- **Não ignore os helpers de `functions.py`** — não escreva loops manuais de espera/clique; eles já tratam espera e erros.
- **Sem esperas estáticas indiscriminadas** — não use `time.sleep()` para checar presença de elemento.
- **Sem lixo temporário** — exclua prints/captchas locais logo após o uso.
- **Sem renomeação de download incompleto** — verifique `.crdownload`/`.part` antes.
- **Proibido credenciais/chaves fixas no código.**
- **Sem escrita direta no banco** — toda atualização de estado vai ao backend Laravel via callback HTTP.
- **Sem falhas silenciosas** — nunca silencie exceções; logue em stdout/stderr e envie relatório de erro estruturado ao callback do Engeapp.
