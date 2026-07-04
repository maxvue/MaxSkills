---
name: laravel-pulse-custom-recorders-and-cards
description: Use when designing, building, or modifying Laravel Pulse custom recorders, custom telemetry dashboards, or custom Pulse cards. Triggers on extending Pulse Recorder, creating custom Pulse blade components, customizing storage endpoints, and configuring Pulse recorders in pulse.php.
---

# Recorders e Cards Customizados do Laravel Pulse

## Objetivo
Estabelecer diretrizes, padrões e exemplos de implementação para estender o Laravel Pulse com recorders de telemetria customizados e cards visuais de dashboard dentro do ecossistema Engeapp.

## Instruções
1. **Criação de Recorders Customizados:**
   - Crie uma classe de recorder customizado simples (o Pulse NÃO possui uma classe base `Laravel\Pulse\Recorders\Recorder` para estender). Um recorder declara quais eventos ele escuta por meio de uma propriedade pública `$listen` (array de classes de evento) ou de um método `register(callable $record, Application $app)`, e chama `Pulse::record()` a partir daí.
   - Implemente o método listener/`record` para interceptar eventos (ex.: usando listeners de evento do Laravel ou middleware).
   - Use os métodos da facade `Laravel\Pulse\Pulse`, como `Pulse::record()` ou `Pulse::set()`, para armazenar métricas.
   - Por exemplo, para registrar custos de agentes de IA, registre um tipo (ex.: `ai_cost`), uma chave (ex.: ID do usuário ou nome do modelo do agente), um valor (custo ou tokens usados) e um timestamp opcional.
   - Use tipos de coluna e chaves de banco de dados apropriados.
   - Garanta que o recorder esteja registrado no array `recorders` em `config/pulse.php`.

2. **Cards Customizados (Componentes de Dashboard):**
   - Crie um componente Livewire representando o card do Pulse.
   - Use a classe base `Laravel\Pulse\Livewire\Card`.
   - Injete os dados do Pulse na view usando o serviço `Pulse`. Use `Pulse::aggregate()` ou outros métodos de consulta de telemetria.
   - Crie uma view Blade correspondente usando os helpers de layout nativos do Pulse e classes do Tailwind (ex.: `<x-pulse::card>`, `<x-pulse::card-header>`, etc.).
   - Garanta que os cards customizados sigam o estilo visual dos cards nativos do Pulse (temas claro/escuro, tipografia, espaçamento).
   - Registre o componente Livewire customizado dentro de um service provider ou renderize-o diretamente na view do dashboard.

3. **Gerenciamento de Performance e Armazenamento:**
   - Defina políticas de retenção de dados em `config/pulse.php` (ex.: configurações de `trim`).
   - Configure limpezas agendadas usando `pulse:clear` ou `pulse:work` se necessário.
   - Adicione índices de banco de dados apropriados em tabelas customizadas caso drivers de armazenamento customizados sejam usados.
   - Garanta que registros de alta frequência sejam amostrados adequadamente usando a opção de configuração `sample_rate`.

4. **Segurança e Autorização:**
   - Configure um Gate de autorização customizado no `AuthServiceProvider` (ou `AppServiceProvider`) usando `Pulse::auth()`.
   - Restrinja o acesso à rota `/pulse` em produção apenas a administradores autorizados.

## Exemplos
Veja os seguintes exemplos no diretório `examples/`:
- [custom-recorder.php](examples/custom-recorder.php): Código boilerplate para criar um recorder customizado do Pulse (monitorando latência de API externa e custos de IA).
- [pulse-card.blade.php](examples/pulse-card.blade.php): Template Blade usando Livewire para renderizar um card customizado de dashboard do Pulse.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill esteja escrito.
- NÃO consulte as tabelas do banco de dados do Pulse diretamente a partir do código da aplicação; sempre use as APIs de consulta da facade `Pulse`.
- NÃO execute escritas pesadas no banco de dados ou chamadas externas síncronas bloqueantes dentro de recorders customizados. Use enfileiramento assíncrono ou armazenamento leve em memória (ex.: driver de ingest do Redis) se alto desempenho for necessário.
- NÃO exponha o dashboard do Pulse publicamente; sempre proteja-o atrás de um Gate.
- NÃO duplique recorders nativos do Pulse (ex.: não reescreva métricas de slow queries ou de saúde do servidor).
