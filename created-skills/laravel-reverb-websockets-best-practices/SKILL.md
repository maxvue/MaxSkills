---
name: laravel-reverb-websockets-best-practices
description: Use when configuring, optimizing, debugging, or deploying the Laravel Reverb WebSocket server, managing connections, setting up Supervisor processes, or tuning performance for real-time applications.
---

# Laravel Reverb WebSockets Best Practices

## Goal
Standardize the installation, configuration, performance tuning, and production deployment of the native Laravel Reverb WebSocket server for secure (WSS) and highly-scalable real-time operations.

## Instructions

### 1. Environment Configuration (`.env`)
Configure the WebSocket environment variables correctly for local development and production.
Ensure the following variables are defined:

```env
# Reverb Server Bind Configuration (Internal)
REVERB_SERVER_HOST="0.0.0.0"
REVERB_SERVER_PORT=9000

# Reverb Public Access Configuration (Client-facing)
REVERB_HOST="engeapp.test"
REVERB_PORT=443
REVERB_SCHEME=https

# Client-side (Vite) broadcasting variables
VITE_REVERB_APP_KEY="${REVERB_APP_KEY}"
VITE_REVERB_HOST="${REVERB_HOST}"
VITE_REVERB_PORT="${REVERB_PORT}"
VITE_REVERB_SCHEME="${REVERB_SCHEME}"
```

### 2. Reverse Proxy Setup (Nginx)
To secure the WebSocket connections using TLS (WSS), configure Nginx as a reverse proxy to terminate SSL and forward traffic to the Reverb server.

Add the following location block to the server configuration file:

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

### 3. Process Management (Supervisor)
In production, the Reverb server process must run continuously. Configure Supervisor to monitor and automatically restart the Reverb command.

Create a configuration file at `/etc/supervisor/conf.d/reverb.conf`:

```ini
[program:reverb]
process_name=%(program_name)s_%(process_num)02d
command=php /home/johnattas/GitHub/engeapp/artisan reverb:start
autostart=true
autorestart=true
user=johnattas
numprocs=1
redirect_stderr=true
stdout_logfile=/home/johnattas/GitHub/engeapp/storage/logs/reverb.log
stopwaitsecs=60
minfds=10000
```

After creating the file, reload Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start reverb:*
```

### 4. Tuning Server Limits (Linux OS)
WebSocket connections are persistent and consume file descriptors. Under high traffic, default OS limits might restrict performance.

- **Check current limits:** `ulimit -n`
- **Modify Limits:** Update `/etc/security/limits.conf` to increase limits for the user running Reverb:
  ```text
  johnattas soft nofile 65536
  johnattas hard nofile 65536
  ```
- **Systemd Service Limit:** If running Reverb via systemd directly, add `LimitNOFILE=65536` in the service file.

### 5. Scaling and Redis
For horizontal scaling across multiple servers, enable Redis integration in `config/reverb.php`:

```php
'scaling' => [
    'enabled' => env('REVERB_SCALING_ENABLED', true),
    'channel' => env('REVERB_SCALING_CHANNEL', 'reverb'),
    'server' => [
        'url' => env('REDIS_URL'),
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'port' => env('REDIS_PORT', '6379'),
        ...
    ],
]
```
Ensure `REVERB_SCALING_ENABLED=true` is set in production `.env` and that Redis is configured as the cache driver.

### 6. Debugging and Troubleshooting
- **Verify Port Binding:** `netstat -plnt | grep 9000` or `ss -tulpn | grep 9000`
- **Check Server Logs:** Inspect `/home/johnattas/GitHub/engeapp/storage/logs/reverb.log` or run `tail -f storage/logs/laravel.log`.
- **Debugging Handshake Failures:** If connections fail to establish, check browser logs using `browser-logs` or inspect the Network tab for HTTP upgrade failures (403 Forbidden indicates invalid CORS/Origin settings, 502/504 Bad Gateway indicates Nginx configuration or Reverb process issues).

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do not expose raw Reverb ports** (e.g. 9000) directly to the public internet. Always route traffic through Nginx, Apache, or Caddy.
- **Never run** `reverb:start` directly in production without a process manager (Supervisor/systemd).
- **Avoid hardcoding configuration values** inside `config/reverb.php`; always resolve them using the `env()` helper.
- **Do not ignore CORS configuration.** Ensure `allowed_origins` in `config/reverb.php` includes your production domains, avoiding wildcard `['*']` in highly secure environments if possible.
