---
name: python-concessionarias-automation-best-practices
description: "Use when creating, modifying, or debugging Python RPA scripts (Selenium + requests) for energy concessionaire portals (Cemig, Energisa, Equatorial, Coelba), automation scripts, and TRT submissions. Covers concessionaire regulations, RPA automation, and portal scripts."
---
# Boas Práticas de Automação (RPA) Python para Concessionárias

## Objetivo
Use when creating, modifying, or debugging Python RPA scripts (Selenium + requests) for energy concessionaire portals (Cemig, Energisa, Equatorial, Coelba), automation scripts, and TRT submissions. Covers concessionaire regulations, RPA automation, and portal scripts.

> **Escopo:** scripts Python (Selenium + requests) que automatizam portais de concessionárias de energia (Cemig, Energisa, Equatorial, Coelba) e Sinceti/TRT — submeter projetos fotovoltaicos, consultar status e emitir/assinar TRTs —, integrados ao Engeapp. Esta skill é do ecossistema **Python/RPA** — não faz parte da stack Node/Vue (Maxdmin).

---

## Instruções

### 1. Geração atual: `engeapp3/functions_engeapp.py`
Scripts novos de RPA vivem em `engeapp3/` e começam com `from functions_engeapp import *` (ex.: `sinceti_submit.py`, `criar_excel_energisa.py`); utilitários não-RPA da pasta, como `script.py` (PySide6) e `test.py`, não importam esses helpers. Use os helpers de lá em vez dos equivalentes legados:
- **Dados do projeto:** `get_data(dados, withs, appends)` (GET em `https://beta.engeapp.com.br/api/project/data`) no lugar de `consulta_engeapp` / `consulta_enge_app_3`. Ex.: `get_data({'project_id': project_id}, None, ['power', 'value_art'])`. **Atenção — o backend ignora `dados` e `withs`:** o `ProjectDataController::getProjectDataApi` seleciona o projeto exclusivamente pela flag `python_requested = true` (não pelo `project_id` enviado) e o eager-load é fixo no servidor (`client.solar_company`, `station`, `location.address`, `location.coordinates`, `electrical_specs`, `concessionaire`, `designer`, `shares`). Só `appends` tem efeito real. O default `withs` do cliente Python é apenas decorativo.
- **Progresso:** `status_bar(valor, title)` no lugar de `barra(...)` — `barra` não existe em `functions_engeapp.py`.
- **Retentativa:** `repeat(function, attempts=3, delay=2)` em vez de escrever loops de retentativa à mão; ele reexecuta a função e levanta exceção após esgotar as tentativas.

`functions.py` (raiz) continua sendo a referência apenas para os **scripts legados da raiz** — não a use como base para código novo.

### 2. Funções Utilitárias Compartilhadas (`functions.py`, legado)
Nos scripts legados da raiz, importe e use os wrappers de [functions.py](file:///home/johnattas/GitHub/Python/functions.py) (`from functions import *`) em vez de chamadas diretas do Selenium — eles já encapsulam espera de elemento, timeout e scroll:
- **Ciclo de vida do webdriver:** inicialize com `chrome(url, hide_screen, folder, time_loadpage, time_wait, nav)` (configura headless, diretório de download e timeouts).
- **Interação:** prefira `clica(By, locator)`, `digita(By, locator, valor)`, `seleciona_select(By, locator, valor)`, `seleciona_item(By, locator)`, `checkbox(By, locator, bool)`, `envia_arquivo(By, locator, filepath)`.
- **Selects resilientes:** `seleciona_select(...)` normaliza textos (remove acentos/espaços) para casar opções de forma tolerante.

### 3. Resiliência de Timeout e Carregamento
- Os portais são lentos e instáveis. **Não** use esperas estáticas (`time.sleep(10)`) para checar presença de elemento; configure `chrome(time_wait=...)`.
- Envolva navegação e etapas cruciais em `try-except`, tratando `NoSuchElementException` (única exceção do Selenium exposta por `from functions import *`). Se quiser usar `TimeoutException` ou `WebDriverWait`, importe-os explicitamente (`from selenium.common.exceptions import TimeoutException`, `from selenium.webdriver.support.ui import WebDriverWait`) — nenhum dos dois é importado por `functions.py` nem usado hoje no projeto, então `except TimeoutException` sem import estoura `NameError`.
- Implemente retentativa (até ~3 tentativas) para envio de formulários críticos — em `engeapp3/` use `repeat(...)`.

### 4. Resolução de Captchas (API AntiCaptcha)
- **Imagem:** `captha_imagem(by, by_value)` — retorna apenas a string da solução; o helper já tira o screenshot em arquivo temporário e o apaga com `os.remove()` internamente, então **não** tente remover o arquivo pelo chamador (o nome não é exposto).
- **ReCaptcha v2:** `captha_gRecaptcha(By, locator, url)` — passe `By`/`locator` do elemento que contém o `data-sitekey` e a `url` da página. A sitekey **não** é passada pelo chamador: o helper a lê automaticamente via `get_attribute('data-sitekey')` do próprio elemento localizado.
- **Erros:** se a API falhar, registre log detalhado e aborte/refaça a etapa. Nunca submeta formulários com captcha vazio/inválido.
- **Chaves hardcoded (dívida técnica a corrigir — regra única do projeto):** há chaves literais tanto no legado quanto na geração atual: a do AntiCaptcha em `captha_imagem` e `captha_gRecaptcha` (`chave_api` em `functions.py:54`/`:68` e, duplicada, em `engeapp3/functions_engeapp.py:57`/`:71`) e as chaves de payload do backend em `consulta_enge_app_3` (`functions.py:85`), `consulta_engeapp` (`functions.py:108`) e `get_data` (`engeapp3/functions_engeapp.py:90`). Usar `engeapp3/` **não** livra da dívida — ela vive lá também. Todas são má prática e **devem ser migradas** para variável de ambiente (`.env`). Não replique nenhuma delas — nem qualquer credencial, senha, CPF ou CNPJ — em novos scripts; leia de `.env` ou obtenha dinamicamente do backend.

### 5. Downloads e Operações de Arquivo
- Defina um `folder` único e isolado por execução em `chrome(folder=...)`.
- Ao baixar PDFs/diagramas unifilares/TRTs, faça loop de verificação (ex: `time.sleep(0.3)`) até que arquivos `.crdownload` (Chrome — é o único navegador usado no projeto) desapareçam **antes** de renomear ou processar.
- **Limite de 49 caracteres (portais Equatorial):** antes de enviar um PDF, separe `nome_base, extensao = os.path.splitext(arquivo)` e, se `len(nome_base) > 49`, trunque para `nome_base[:49]` e aplique `os.rename()` — o portal rejeita nomes mais longos no upload. Esse é o padrão real usado em `equatorial_al/ap/go/ma/pa/pi/rs`.
- Normalize nomes inválidos com `unicodedata.normalize` + substituição de caracteres.

### 6. Integração e Callbacks com o Engeapp
- **Leitura:** busque dados com `get_data(...)` (API Laravel `/api/project/data`) ou, no legado, `consulta_engeapp(campos)` / `consulta_enge_app_3(dados)`.
- **`get_data` NÃO é idempotente:** apesar de ser um GET, o controller faz `python_requested = false; save()` como acknowledge da leitura. Chamar duas vezes não devolve o mesmo projeto — a segunda chamada pega o próximo projeto com a flag ligada ou estoura `firstOrFail()` (404). Busque uma vez por execução e guarde o resultado em variável.
- **Escrita de estado:** vai por `requests.post` para os **endpoints PHP legados** hospedados em `https://engeapp.com.br/python/` (`registra.php`, `normas.php`) — eles estão **fora** da aplicação Laravel.
- **Payload real de `registra.php`** (form-encoded):
  - Formato atual (vários campos): `campos = {'id_projeto_url': url_atual, 'data_submissao_concessionaria': 1}` e `data_send = {'key': projeto['chave_publica'], 'campos': json.dumps(campos)}`.
  - Formato antigo (um campo só, ex. `submeter_trt_sinceti.py`): `data_send = {'key': projeto['chave_publica'], 'campo': 'data_emissao_trt'}`.
  - As chaves de `campos` são **nomes de coluna em pt-BR** do projeto no banco legado — confira o nome exato antes de inventar um campo novo.
- Implemente retentativa (até ~6 tentativas) com `try-except` em **todas** as chamadas HTTP para sobreviver a falhas temporárias de rede.

### 7. Progresso e Logs
- Acompanhe o progresso no console local com `status_bar(valor, title)` (`barra(valor, title)` nos scripts legados) — é local e **não** envia nada ao Engeapp; para reportar estado, use os callbacks HTTP da seção 6.
- Evite saída verbosa em produção; use `print_dev()` / a variável global `dev` para logs de desenvolvimento.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem escrita direta no banco** — a atualização de estado vai via callback HTTP ao endpoint legado `registra.php`; a API Laravel `/api/project/data` só serve para leitura de dados (a única escrita que ela faz é consumir a flag `python_requested`).
- **Sem falhas silenciosas** — nunca silencie exceções; logue em stdout/stderr e reporte o erro no callback ao Engeapp.
