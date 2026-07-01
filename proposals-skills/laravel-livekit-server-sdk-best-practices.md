# PROPOSTA DE SKILL: laravel-livekit-server-sdk-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or debugging LiveKit WebRTC audio/video services, generating access tokens for rooms, managing LiveKit rooms, or handling room events and Webhooks. Triggers on LiveKit SDK integration, AccessToken generation, and RoomServiceClient usage.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp oferece suporte a videoconferências em tempo real integradas com o LiveKit. É crucial ter diretrizes estruturadas sobre como inicializar o client, instanciar tokens seguros com as grants apropriadas e manipular erros HTTP ou de conexão ao interagir com o LiveKit Server.
* **Recursos:** Geração segura de AccessToken com VideoGrants adequadas, gerenciamento do ciclo de vida das salas com RoomServiceClient, tratamento de exceções do SDK, padronização do Service Wrapper de LiveKit e segurança nas rotas de token.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para a integração do LiveKit Server SDK no backend Laravel.
* **Casos de uso:** Criação e encerramento de salas de aula/reunião ao vivo, geração de tokens temporários de participante e recuperação de participantes ativos.
* **Workflows:**
  - bug-fix-back-end
  - bug-fix-front-end
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — A integração com o LiveKit deve ser encapsulada em uma classe Service que siga o Single Responsibility Principle (SRP) e injeção de dependências.
  - `laravel-exception-handling-logging` — Para capturar erros de conexão ou falhas de requisição na comunicação com o LiveKit Server e registrá-los corretamente nos logs.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Padronização da geração de tokens de videoconferência, maior segurança contra geração indevida de tokens, tratamento robusto de falhas de comunicação com o servidor LiveKit e facilidade de manutenção de integrações em tempo real.
