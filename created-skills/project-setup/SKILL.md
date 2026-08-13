---
name: project-setup
description: Use when setting up this project from scratch on a new machine, or when onboarding steps are needed (installing dependencies, configuring .env, bootstrapping the database, starting dev services). Not needed for day-to-day work in an already-set-up environment.
---

# Setup — SocialMedia

```bash
composer install && npm install
cp .env.example .env && php artisan key:generate
# preencher DB_PASSWORD (mesma do .env do EngeApp), DB_ADMIN_* se necessário, GEMINI_API_KEY (pipeline de IA)
# e, para integrações Meta (Marco 4): META_GRAPH_VERSION (ex. 24.0, sem prefixo "v" — mas version() tolera), META_WEBHOOK_TOKEN (handshake do webhook), META_APP_SECRET (opcional — valida X-Hub-Signature-256)
# extração de conteúdo base de tema em PDF exige o binário `pdftotext` (pacote poppler) instalado no sistema
# e, para treino de LoRA por personagem (Marco 5): ONETRAINER_PYTHON, ONETRAINER_PATH (venv/instalação local do OneTrainer), ZIMAGE_BASE_MODEL (checkpoint base Z-Image), COMFYUI_URL (default http://127.0.0.1:8188), COMFYUI_LORA_DIR (pasta de LoRAs do ComfyUI), LORA_MIN_IMAGES (default 8), LORA_COOLDOWN_HOURS (default 48), LORA_EPOCHS (default 100), LORA_CHUNK_EPOCHS (default 10)
php artisan db:bootstrap   # cria role+db socialmedia e socialmedia_test (idempotente)
php artisan migrate --seed
redis-server &             # requerido pelas filas `gemini`/`lora` (QUEUE_CONNECTION=redis)
npm run dev                # Vite (:5173) — o PHP é servido pelo Caddy via PHP-FPM (ver "Ambiente de Dev" no CLAUDE.md); NÃO usar `php artisan serve`
php artisan horizon &      # manual, quando precisar das filas: Jobs de IA (clients com client_enabled=true) e filas `lora`/`lora-train` (1 processo, prioridade estrita — ver regra 16 do CLAUDE.md)
php artisan schedule:work &  # manual, quando precisar: publicação automática scheduled→published (publish-due) e refresh periódico de notícias
```

- `php artisan ai:smoke {clientId}` — smoke test manual (fora da suíte) que roda o CopywriterJob síncrono com chamada REAL ao Gemini contra um client de teste (exige `GEMINI_API_KEY` válida e client com brand positioning preenchido).
- `php artisan lora:smoke {characterId} [--generate]` — smoke test manual (fora da suíte) que roda a chain de caption+treino de LoRA real (OneTrainer) para um personagem de teste; com `--generate`, também chama o ComfyUI real para gerar uma arte com o LoRA treinado. OneTrainer e ComfyUI devem estar instalados e rodando na **mesma máquina** que o Laravel/Horizon (GPU local); substitua os templates de `resources/lora/` (`zimage-lora.template.json`, `comfyui-zimage-character.json`) pelos exports reais do OneTrainer GUI e do ComfyUI (Export API) antes de rodar este comando pela primeira vez.
