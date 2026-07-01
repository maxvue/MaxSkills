# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or debugging Laravel Events that implement broadcasting (websockets), configuring private, presence or public channels, customizing broadcasted payloads, or listening to events on the Vue 3 frontend using Echo.
* **Estrutura de Diretórios:** Apenas SKILL.md.
* **Necessidade:** O Engeapp necessita de sincronização de estado em tempo real no frontend (como no Planner e chat de atendimento). A transmissão de eventos usando Laravel Reverb + Vue Echo exige padrões estritos sobre canais privados de autorização, serialização de payloads reduzidos e gerenciamento de escutas no frontend para evitar vazamentos de conexões e bugs reativos.
* **Recursos:** Configuração correta da interface `ShouldBroadcast` ou `ShouldBroadcastNow`, definição de canais via método `broadcastOn` (PrivateChannel, PresenceChannel), controle do payload enviado via `broadcastWith`, autorização de canais no arquivo `routes/channels.php` e consumo dos eventos via composables Vue 3 e Laravel Echo.
* **Objetivo:** Fornecer diretrizes e padrões consistentes para a criação de eventos com broadcasting em tempo real no Laravel e sua integração com escuta reativa no Vue 3.
* **Casos de uso:** Atualização instantânea de tarefas no Planner ao serem movidas por outro usuário, notificação push em tempo real na barra de ferramentas, encerramento de chamadas ativas e atualização de progresso de importações/exportações de relatórios.
* **Workflows:**
  - bug-fix-back-end
  - bug-fix-front-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os padrões de models para serialização otimizada de dados no método `broadcastWith`.
  - `vue-code-generators-best-practices` — Orientará a estruturação de composables dedicados no Vue 3 para inicialização e desmontagem limpa de listeners do Echo.
* **Skills auxiliares:** laravel-specialist, vue-specialist
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Melhoria significativa na experiência do usuário final com reatividade em tempo real, redução de consumo de banda por payloads de websockets otimizados e facilidade de manutenção no fluxo de canais autorizados.
