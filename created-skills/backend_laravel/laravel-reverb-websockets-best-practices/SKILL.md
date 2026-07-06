---
name: laravel-reverb-websockets-best-practices
description: "Use when configuring, optimizing, debugging, or deploying the Laravel Reverb WebSocket server for real-time features in the EngeApp backend. Covers .env server/public bind variables, Vite client broadcasting vars, Nginx reverse proxy for secure WSS/TLS termination, Supervisor process management, connection handling, and performance tuning for scalable real-time broadcasting."
---

# Boas Práticas de WebSockets com Laravel Reverb

## Objetivo
Padronizar a instalação, configuração, ajuste de performance e deploy em produção do servidor WebSocket nativo Laravel Reverb para operações em tempo real seguras (WSS) e altamente escaláveis.

## Instruções

### 1. Configuração de Ambiente (`.env`)
Configure corretamente as variáveis de ambiente do WebSocket para desenvolvimento local e produção.
Garanta que as seguintes variáveis estejam definidas:

```env
# Reverb Server Bind Configuration (Internal)
REVERB_SERVER_HOST="0.0.0.0"
REVERB_SERVER_PORT=9000

# Reverb Public Access Configuration (Client-facing)
REVERB_HOST="dev.engeapp.com.br"
REVERB_PORT=443
REVERB_SCHEME=https

# Client-side (Vite) broadcasting variables
VITE_REVERB_APP_KEY="${REVERB_APP_KEY}"
VITE_REVERB_HOST="${REVERB_HOST}"
VITE_REVERB_PORT="${REVERB_PORT}"
VITE_REVERB_SCHEME="${REVERB_SCHEME}"
```

### 2. Configuração de Reverse Proxy (Nginx)
Para proteger as conexões WebSocket usando TLS (WSS), configure o Nginx como um reverse proxy para terminar o SSL e encaminhar o tráfego para o servidor Reverb.

Adicione o seguinte bloco `location` ao arquivo de configuração do servidor:

```nginx
location /app {
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
    proxy_connect_timeout 60s;
}
```

### 3. Gerenciamento de Processos (Supervisor)
Em produção, o processo do servidor Reverb deve rodar continuamente. Configure o Supervisor para monitorar e reiniciar automaticamente o comando do Reverb.

Crie um arquivo de configuração em `/etc/supervisor/conf.d/reverb.conf`. Substitua `/caminho/para/app` pelo caminho real de deploy da aplicação (ex.: `/var/www/engeapp`) e `www-data` pelo usuário do processo em produção:

```ini
[program:reverb]
process_name=%(program_name)s_%(process_num)02d
command=php /caminho/para/app/artisan reverb:start
autostart=true
autorestart=true
user=www-data
numprocs=1
redirect_stderr=true
stdout_logfile=/caminho/para/app/storage/logs/reverb.log
stopwaitsecs=60
minfds=10000
```

Após criar o arquivo, recarregue o Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start reverb:*
```

### 4. Ajuste de Limites do Servidor (SO Linux)
Conexões WebSocket são persistentes e consomem file descriptors. Sob alto tráfego, os limites padrão do SO podem restringir a performance.

- **Verifique os limites atuais:** `ulimit -n`
- **Modifique os Limites:** Atualize `/etc/security/limits.conf` para aumentar os limites do usuário que executa o Reverb:
  ```text
  # Substitua "www-data" pelo usuário que executa o Reverb em produção
  www-data soft nofile 65536
  www-data hard nofile 65536
  ```
- **Limite do Serviço Systemd:** Se estiver rodando o Reverb via systemd diretamente, adicione `LimitNOFILE=65536` no arquivo do serviço.

### 5. Escalonamento e Redis
Para escalonamento horizontal em múltiplos servidores, habilite a integração com Redis em `config/reverb.php`:

```php
'scaling' => [
    'enabled' => env('REVERB_SCALING_ENABLED', false),
    'channel' => env('REVERB_SCALING_CHANNEL', 'reverb'),
    'server' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'port' => env('REDIS_PORT', '6379'),
        ...
    ],
]
```
No engeapp o padrão é `env('REVERB_SCALING_ENABLED', false)` — ou seja, scaling desligado por padrão, adequado a instância única. Só defina `REVERB_SCALING_ENABLED=true` no `.env` quando houver **mais de uma** instância do Reverb e um Redis provisionado e acessível; caso contrário, habilitar sem Redis quebra o servidor. Ao ligar, garanta também que o Redis esteja configurado como driver de cache/broadcasting.

### 6. Depuração e Troubleshooting
- **Verifique o Binding da Porta:** `netstat -plnt | grep 9000` ou `ss -tulpn | grep 9000`
- **Verifique os Logs do Servidor:** Inspecione o `stdout_logfile` configurado no Supervisor (ex.: `storage/logs/reverb.log`) ou execute `tail -f storage/logs/laravel.log`.
- **Depurando Falhas de Handshake:** Se as conexões não se estabelecerem, verifique os logs do navegador usando `browser-logs` ou inspecione a aba Network em busca de falhas de HTTP upgrade (403 Forbidden indica configurações inválidas de CORS/Origin, 502/504 Bad Gateway indica problemas na configuração do Nginx ou no processo do Reverb).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **Não exponha portas brutas do Reverb** (ex.: 9000) diretamente à internet pública. Sempre roteie o tráfego através de Nginx, Apache ou Caddy.
- **Nunca execute** `reverb:start` diretamente em produção sem um gerenciador de processos (Supervisor/systemd).
- **Evite valores de configuração hardcoded** dentro de `config/reverb.php`; sempre resolva-os usando o helper `env()`.
- **Atenção à configuração de CORS.** Hoje o engeapp usa `allowed_origins => ['*']` em `config/reverb.php` (intencional, aceita qualquer origem). Isso é aceitável em dev; em produção altamente sensível, prefira restringir `allowed_origins` aos domínios reais (ex.: `['dev.engeapp.com.br', 'engeapp.com.br']`). Não trate o `['*']` atual como bug a ser "corrigido" sem antes confirmar o requisito de segurança com o time.
