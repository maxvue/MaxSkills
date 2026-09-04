---
name: laravel-performance-and-profiling-best-practices
description: "Use when configuring, optimizing, or debugging Laravel 13 profiling tools in Engeapp: Pulse, Clockwork, LaraDumps ds(), Debugbar, Telescope, Log Viewer, and Pail log tailing. Provides end-to-end guidance, reference architectures, and practical patterns for laravel performance and profiling best practices."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Performance e Profiling no Laravel

## Objetivo
Estabelecer diretrizes padrão para depuração, profiling, inspeção e otimização de performance da aplicação usando diversas ferramentas dentro do ecossistema Laravel do Engeapp, garantindo segurança, produtividade do desenvolvedor e prevenindo vazamentos de dados.

## Instruções

### 1. Monitoramento de Performance com Pulse
- **Segurança e Autenticação**: Defina a autorização de produção via `Gate::define('viewPulse', ...)` (é esse gate que o middleware `Authorize` do Pulse checa). Use `Pulse::user()` apenas para customizar os dados exibidos do usuário (name/email/avatar/extra) — não é mecanismo de autorização. Restrinja a administradores. NÃO exponha `/pulse` publicamente sem middleware estrito.
- **Configuração**: Use o driver de ingestão `redis` em ambientes de alto tráfego para desafogar os workers. Configure uma janela de armazenamento menor se o banco de dados crescer rapidamente.
- **Recorders e Agregação**: Crie recorders personalizados para operações de negócio. Identifique queries lentas (>1000ms) e taxas de hit/miss do cache Redis pelo dashboard.

### 2. Profiling com Clockwork
- **Ambiente**: Habilite APENAS em local/staging (`CLOCKWORK_ENABLE=true`). Defina como `false` em produção. Não use em testes Pest/PHPUnit.
- **Timelines Personalizadas**: A API de timeline do `itsgoingd/clockwork` ^5.x é fluente. Crie o evento com `clock()->event('descrição', $data)` e meça com `->begin()` / `->end()`, ou passe um closure para `->run(fn () => ...)` que abre e fecha o evento automaticamente (fecha mesmo em exceção). Não use `clockwork()->startEvent()`/`endEvent()` — esses métodos não existem nesta versão.
  ```php
  // Medição manual: garanta o ->end() num finally
  $evento = clock()->event('Processamento do boleto')->begin();
  try {
      // ...operação complexa...
  } finally {
      $evento->end();
  }

  // Ou deixe o Clockwork cuidar do begin/end via closure
  $resultado = clock()->event('Processamento do boleto')->run(fn () => processarBoleto());
  ```
- **Telemetria e Logging**: Monitore as abas de Database (problemas de N+1), Cache e uso de Memória. Use `clock()->info('Msg')` ou `clock()->log('info', 'Msg', $context)` para logging integrado. O helper global é `clock()`; `clockwork()` NÃO é uma função registrada na integração Laravel. Não passe grandes volumes de dados binários.
- **Limpeza**: Remova os marcadores temporários `clock()` antes de criar um PR.

### 3. Depuração com LaraDumps
- **Ferramenta Principal**: Use `ds()` em vez de `dd()`, `dump()` ou `print_r()`. Rotule e colora a saída.
- **Recursos**: Monitore queries (`ds()->queriesOn()`), tempo (`ds()->time()`), models (`ds()->model()`).
- **Etiqueta**: Remova todas as instruções `ds()` antes de fazer commit. NUNCA faça commit de helpers `ds(...)` ativos. O controle de ativação/estado do LaraDumps fica no arquivo `laradumps.yaml` na raiz do projeto (gerenciado pela extensão/app desktop) — `config/laradumps.php`, quando publicado, contém apenas padrões de ignore de queries/rotas, não um toggle liga/desliga.

### 4. Laravel Debugbar CLI
- Use para inspecionar e depurar via CLI sem um navegador.
- **Comandos**: Localize requisições (`debugbar:find`), inspecione detalhes (`debugbar:get --collector=time`), inspecione queries (`debugbar:queries`) e limpe o armazenamento (`debugbar:clear`).
- **Restrição**: NÃO faça dry-run com `--result` via Debugbar para queries de mutação (`INSERT`, `UPDATE`, `DELETE`) em ambientes locais/staging com bancos compartilhados. Debugbar é ferramenta de desenvolvimento (`require-dev`, `DEBUGBAR_ENABLED=false`) e não roda em produção no engeapp.

### 5. Laravel Telescope — veja a skill dedicada `laravel-telescope-debugging-best-practices` (watchers reais, Telescope::filter/night, hideSensitiveRequestDetails, gate viewTelescope, poda de telescope_entries).

### 6. Laravel Log Viewer
- **Protegendo o Acesso**: Defina um gate personalizado (`viewLogViewer`) no `AppServiceProvider`. Exija autenticação em produção.
- **Configuração**: Exclua frames do framework nos stack traces e proteja logs sensíveis via `exclude_files`. A limpeza de cache dos índices ocorre via ações da UI/rotas HTTP do Log Viewer — não existe comando artisan `log-viewer:clear-cache`.

### 7. Laravel Pail (Tailing de Log em Tempo Real)
- **Iniciando**: Execute `php artisan pail` no terminal para transmitir novas entradas de log instantaneamente conforme ocorrem.
- **Filtragem**:
  - Por classe de exceção: `php artisan pail --filter="App\Exceptions\ServiceIntegrationException"`
  - Por usuário autenticado: `php artisan pail --user=42`
  - Por mensagem/conteúdo: `php artisan pail --message="Failed to send template"`
- **Verbosidade**: por padrão a mensagem é truncada. `-v` destrunca mensagem/classe/arquivo e mostra a data completa (sem stack trace); `-vv` adiciona o stack trace. Não há comportamento adicional documentado para `-vvv`. O contexto é sempre exibido, independente da verbosidade.
- **Logs Estruturados**: Ao usar exceções personalizadas com arrays contextuais (como em `laravel-exception-handling-logging`), o Pail faz o parse e exibe o contexto estruturado de forma elegante no terminal.
- **Etiqueta**: NÃO faça `grep` ou `tail` manual no `laravel.log` físico quando o Pail pode fornecer um stream mais limpo e filtrável.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Exposição em Produção**: Nunca exponha Clockwork, LaraDumps ou Telescope globalmente em produção. O Log Viewer e o Pulse devem ser protegidos por gates de autenticação.
- **Sem Vazamento de Dados Sensíveis**: Nunca registre ou faça dump de informações sensíveis do usuário, credenciais, tokens de autorização brutos ou detalhes de pagamento. Filtre esses dados adequadamente.
- **Comentários em Português do Brasil**: Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em Português do Brasil (pt-BR).
