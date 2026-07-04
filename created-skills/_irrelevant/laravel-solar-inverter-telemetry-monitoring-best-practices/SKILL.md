---
name: laravel-solar-inverter-telemetry-monitoring-best-practices
description: Use when creating, reviewing, or debugging solar inverter telemetry integration and real-time generation monitoring in Laravel. Triggers on files modifying inverter API clients (Growatt, Fronius, Sungrow), telemetry jobs, telemetry data persistence, or alert triggers for low generation or inverter communication loss.
---

# Boas Práticas de Monitoramento de Telemetria de Inversores Solares no Laravel

## Objetivo
Estabelecer uma arquitetura resiliente e de alta performance para integrar APIs de terceiros de inversores solares (Growatt, Fronius, Sungrow), buscar dados de telemetria, cachear métricas em tempo real usando Redis, persistir o histórico de telemetria e disparar alertas para anomalias (ex.: baixa geração ou inversores offline) dentro do ecossistema Engeapp.

## Instruções
1. **Abstração do Client de Inversor**:
   - Defina uma Interface PHP `App\Services\Telemetry\Contracts\InverterClientInterface` com métodos como `fetchRealTimeMetrics(StationInverter $inverter): InverterTelemetryDto` e `checkConnection(StationInverter $inverter): bool`.
   - Implemente clients concretos (`GrowattClient`, `FroniusClient`, `SungrowClient`) estendendo uma classe base ou injetando um HTTP Client resiliente.
   - Use o HTTP Client do Laravel (`Http::withHeaders()->retry()->timeout()`) para lidar com instabilidade da API, rate limiting e falhas de rede.

2. **Data Transfer Object (DTO) de Telemetria**:
   - Use DTOs estritos para encapsular os dados de estado do inversor (potência ativa, energia diária, energia total, status, payload bruto) antes da persistência ou do cache.

3. **Jobs Agendados de Coleta de Telemetria**:
   - Crie jobs assíncronos (ex.: `FetchInverterTelemetryJob`) implementando `ShouldQueue`.
   - Agende os jobs em `routes/console.php` (via `Schedule::job(...)`) — `app/Console/Kernel.php` não existe mais no Laravel 13 — para distribuir a carga. Evite requisições em massa concorrentes à API espaçando os jobs ou usando rate limiters de fila (ex.: `Redis::throttle`).
   - Use tags de fila e filas separadas (ex.: `telemetry`) para garantir que as tarefas de telemetria não criem gargalos nos fluxos transacionais do usuário.

4. **Cache em Tempo Real (Redis)**:
   - Armazene a última leitura de telemetria no Redis (`Cache::tags(['inverters'])->put(...)`) com um TTL curto (ex.: 5-15 minutos) para recuperação instantânea no dashboard sem acessar o banco de dados.
   - Forneça lógica de fallback para queries no banco de dados caso o cache esteja vazio.

5. **Padrão de Persistência de Telemetria**:
   - Salve os dados históricos de telemetria em uma tabela estruturada do banco de dados (ex.: `station_inverter_telemetries` com os campos: `station_inverter_id`, `active_power_kw`, `daily_energy_kwh`, `total_energy_kwh`, `recorded_at`, `status`).
   - Garanta indexação em chaves estrangeiras e timestamps para queries analíticas rápidas de séries temporais.

6. **Alertas de Anomalia e Notificações**:
   - Implemente disparos de alerta usando Laravel Notifications.
   - Envie alertas (ex.: Slack, Email ou WhatsApp SMS) se:
     - A geração ativa estiver abaixo dos limites esperados (ex.: < 10% durante o horário de pico solar, 09:00 - 15:00).
     - O inversor estiver offline/com perda de comunicação por mais de 4 horas consecutivas.
   - Proteja os alertas usando flags de cache para evitar spam no cliente (ex.: permita apenas uma notificação a cada 24 horas por anomalia de inversor).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- NÃO faça chamadas HTTP brutas diretas dentro de Controllers ou Models; sempre roteie-as através de implementações abstratas de client.
- NÃO realize sincronização intensiva de dados de forma síncrona dentro dos ciclos de requisição web.
- NÃO armazene payloads grandes de telemetria a longo prazo no banco de dados principal sem compressão ou normalização estrutural.
- Evite usar queries DB raw para consultas de séries temporais sem scopes e índices apropriados.
