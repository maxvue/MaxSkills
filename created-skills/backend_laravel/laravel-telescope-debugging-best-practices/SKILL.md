---
name: laravel-telescope-debugging-best-practices
description: Use when configuring, optimizing, or using Laravel Telescope in development or local environments to debug database queries, request payloads, jobs, exceptions, commands, or cache hits and misses. Triggers on telescope configuration, filtering entries, environment setup, and telemetry performance analysis.
---

# Objetivo
Fornecer diretrizes consistentes e boas práticas para configurar, otimizar e usar o Laravel Telescope dentro do ecossistema Engeapp. Isso garante telemetria e depuração locais eficientes sem degradar o desempenho do banco de dados ou vazar dados sensíveis.

# Instruções

## 1. Ambiente Local e Instalação
* **Restrição de Ambiente:** O Telescope foi projetado principalmente para desenvolvimento. Restrinja seu carregamento ao ambiente local dentro do método `register` do `TelescopeServiceProvider`:
  ```php
  if ($this->app->environment('local')) {
      $this->app->register(\Laravel\Telescope\TelescopeServiceProvider::class);
      $this->app->register(TelescopeServiceProvider::class);
  }
  ```
* **Controle de Chave Mestra:** Ligue/desligue o Telescope programaticamente usando a variável de ambiente `TELESCOPE_ENABLED` no `.env`.

## 2. Configurações dos Watchers (`config/telescope.php`)
* **Query Watcher (`QueryWatcher`):**
  - Defina o limite `'slow'` para `100` milissegundos para identificar gargalos de desempenho.
  - Habilite `'ignore_packages' => true` para ignorar queries do framework e de pacotes, focando exclusivamente nas operações de banco de dados da aplicação.
* **Model Watcher (`ModelWatcher`):**
  - Mantenha `'hydrations'` habilitado (`true`) apenas ao depurar vazamentos de memória ou comportamentos específicos do Eloquent, pois introduz overhead substancial durante grandes operações de banco de dados.
* **Request Watcher (`RequestWatcher`):**
  - Ajuste `'size_limit'` (padrão `64` KB) para evitar que respostas com payloads excessivamente grandes inchem o banco de dados.

## 3. Poda de Dados e Otimização de Armazenamento
* **Gestão do Tamanho do Banco:** As tabelas do Telescope (`telescope_entries`, `telescope_entries_tags`, etc.) podem crescer rapidamente.
* **Agendamento da Poda:** Sempre agende o comando de poda em `routes/console.php` (Laravel 11+):
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('telescope:prune --hours=24')->daily();
  ```
* **Descarregamento de Desempenho:** Se o overhead das queries se tornar um gargalo durante o desenvolvimento local, altere o `TELESCOPE_DRIVER` para um backend mais leve ou desabilite seletivamente watchers de alta frequência (como logs de cache ou queries).

## 4. Segurança e Privacidade de Dados
* **Sanitização de Detalhes Sensíveis:** Garanta que nenhuma chave privada, senha ou informação pessoal identificável (PII) seja armazenada nos logs de telemetria.
* **Configuração de Sanitização:** No `TelescopeServiceProvider.php`, use `hideSensitiveRequestDetails` para remover tokens e credenciais:
  ```php
  Telescope::hideRequestParameters(['_token', 'password', 'password_confirmation', 'client_secret', 'private_key']);
  Telescope::hideRequestHeaders(['cookie', 'x-csrf-token', 'x-xsrf-token', 'authorization']);
  ```
* **Restrição de Acesso via Gate:** Restrinja o acesso ao dashboard em ambientes não locais definindo o gate `viewTelescope` em `TelescopeServiceProvider::gate()` usando endereços de e-mail rigorosamente verificados ou funções específicas.

# Restrições
* Não habilite o Telescope em produção sem gates de autorização ativos e filtragem de dados sensíveis.
* Nunca registre credenciais brutas, certificados mTLS ou senhas de banco de dados nos parâmetros ou cabeçalhos de requisição do Telescope.
* Não deixe o `DumpWatcher` habilitado em ambientes de staging compartilhados e persistentes.
* Nunca execute migrations ou suítes de teste sem garantir que o Telescope esteja configurado para rodar silenciosamente ou desabilitado (`TELESCOPE_ENABLED=false`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
