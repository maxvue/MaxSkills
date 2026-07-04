---
name: laravel-performance-and-profiling-best-practices
description: "Use when configuring, optimizing, debugging, or reviewing Laravel 13 profiling and observability tooling in the EngeApp backend: Pulse monitoring, Clockwork timelines, LaraDumps ds() debugging, Debugbar CLI, Telescope watchers/pruning, Log Viewer, and Pail log tailing. Covers production authorization/gates, sensitive-data filtering, N+1 detection, and stripping ds()/clock() markers before commit."
---

# Boas Práticas de Performance e Profiling no Laravel

## Objetivo
Estabelecer diretrizes padrão para depuração, profiling, inspeção e otimização de performance da aplicação usando diversas ferramentas dentro do ecossistema Laravel do Engeapp, garantindo segurança, produtividade do desenvolvedor e prevenindo vazamentos de dados.

## Instruções

### 1. Monitoramento de Performance com Pulse
- **Segurança e Autenticação**: Defina autorização personalizada para produção usando `Pulse::user()`. Restrinja a administradores. NÃO exponha `/pulse` publicamente sem middleware estrito.
- **Configuração**: Use o driver de ingestão `redis` em ambientes de alto tráfego para desafogar os workers. Configure uma janela de armazenamento menor se o banco de dados crescer rapidamente.
- **Recorders e Agregação**: Crie recorders personalizados para operações de negócio. Identifique queries lentas (>1000ms) e taxas de hit/miss do cache Redis pelo dashboard.

### 2. Profiling com Clockwork
- **Ambiente**: Habilite APENAS em local/staging (`CLOCKWORK_ENABLE=true`). Defina como `false` em produção. Não use em testes Pest/PHPUnit.
- **Timelines Personalizadas**: Use `clockwork()->startEvent('id', 'desc')` e `clockwork()->endEvent('id')` para medir os tempos exatos de execução de operações complexas. Feche em um bloco `finally`.
- **Telemetria e Logging**: Monitore as abas de Database (problemas de N+1), Cache e uso de Memória. Use `clock()->info('Msg')` ou `clockwork()->log()` para logging integrado. Não passe grandes volumes de dados binários.
- **Limpeza**: Remova os marcadores temporários `clock()` antes de criar um PR.

### 3. Depuração com LaraDumps
- **Ferramenta Principal**: Use `ds()` em vez de `dd()`, `dump()` ou `print_r()`. Rotule e colora a saída.
- **Recursos**: Monitore queries (`ds()->queriesOn()`), tempo (`ds()->time()`), models (`ds()->model()`).
- **Etiqueta**: Remova todas as instruções `ds()` antes de fazer commit. NUNCA faça commit de helpers `ds(...)` ativos. Use as variáveis de `config/laradumps.php` para alternar.

### 4. Laravel Debugbar CLI
- Use para inspecionar e depurar via CLI sem um navegador.
- **Comandos**: Localize requisições (`debugbar:find`), inspecione detalhes (`debugbar:get --collector=time`), inspecione queries (`debugbar:queries`) e limpe o armazenamento (`debugbar:clear`).
- **Restrição**: NÃO faça dry-run com `--result` via Debugbar para queries de mutação (`INSERT`, `UPDATE`, `DELETE`) em produção.

### 5. Laravel Telescope
- **Watchers**: Personalize o `config/telescope.php`. Defina limites (`'slow' => 100`). Desabilite `hydrations` no `ModelWatcher` localmente.
- **Pruning e Segurança**: Limpe os dados via scheduler (`telescope:prune`). Filtre dados sensíveis (senhas, tokens, CVVs) no `TelescopeServiceProvider`. Restrinja o acesso em produção usando Gates. Nunca faça commit de dumps do Telescope.

### 6. Laravel Log Viewer
- **Protegendo o Acesso**: Defina um gate personalizado (`viewLogViewer`) no `AppServiceProvider`. Exija autenticação em produção.
- **Configuração**: Exclua frames do framework nos stack traces e proteja logs sensíveis via `exclude_files`. Use `log-viewer:clear-cache` para limpar os índices.

### 7. Laravel Pail (Tailing de Log em Tempo Real)
- **Iniciando**: Execute `php artisan pail` no terminal para transmitir novas entradas de log instantaneamente conforme ocorrem.
- **Filtragem**:
  - Por classe de exceção: `php artisan pail --filter="App\Exceptions\ServiceIntegrationException"`
  - Por usuário autenticado: `php artisan pail --user=42`
  - Por mensagem/conteúdo: `php artisan pail --message="Failed to send template"`
- **Verbosidade**: `-v` (trace básico), `-vv` (contexto + stack trace), `-vvv` (stack traces completos).
- **Logs Estruturados**: Ao usar exceções personalizadas com arrays contextuais (como em `laravel-exception-handling-logging`), o Pail faz o parse e exibe o contexto estruturado de forma elegante no terminal.
- **Etiqueta**: NÃO faça `grep` ou `tail` manual no `laravel.log` físico quando o Pail pode fornecer um stream mais limpo e filtrável.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Exposição em Produção**: Nunca exponha Clockwork, LaraDumps ou Telescope globalmente em produção. O Log Viewer e o Pulse devem ser protegidos por gates de autenticação.
- **Sem Vazamento de Dados Sensíveis**: Nunca registre ou faça dump de informações sensíveis do usuário, credenciais, tokens de autorização brutos ou detalhes de pagamento. Filtre esses dados adequadamente.
- **Comentários em Português do Brasil**: Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em Português do Brasil (pt-BR).
