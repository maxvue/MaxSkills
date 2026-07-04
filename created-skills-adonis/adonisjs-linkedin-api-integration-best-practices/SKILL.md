---
name: adonisjs-linkedin-api-integration-best-practices
description: Use when implementing, reviewing, or debugging LinkedIn API integrations, managing LinkedIn OAuth v2 authentication flows, posting text/image/link shares (UGC Posts or Share API), retrieving organization or member profiles, handling LinkedIn webhooks, or processing rate limit responses in AdonisJS v6. Triggers on files modifying LinkedInService, LinkedInController, or LinkedIn OAuth drivers.
---

## Objetivo
Estabelecer padrões robustos e boas práticas para integrar a API do LinkedIn, gerenciar a autenticação OAuth 2.0 (3-legged), publicar conteúdo de texto/mídia, implementar validação segura de webhooks e tratar rate limits no AdonisJS v6.

## Instruções
Ao implementar ou modificar a integração com a API do LinkedIn ou os fluxos OAuth, siga os seguintes princípios:

1. **LinkedIn OAuth 2.0 (Autenticação 3-Legged)**
   - Use o driver oficial LinkedIn do AdonisJS Ally ou uma classe customizada que estenda `Oauth2Driver` se scopes específicos ou atributos de troca de token forem necessários.
   - Configure as credenciais de forma segura em `config/ally.ts` usando variáveis validadas em `start/env.ts` (ex.: `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_CALLBACK_URL`).
   - Solicite os scopes mínimos necessários: `r_liteprofile` e `r_emailaddress` (ou `openid`, `profile`, `email` para OpenID Connect), e `w_member_social` (para postar como membro) ou `w_organization_social` (para postar como página).
   - Criptografe e armazene os access tokens, refresh tokens e expirações de forma segura no banco de dados utilizando o serviço `Encryption` do AdonisJS.
   - Implemente um comando cron automatizado ou um job do BullMQ para renovar os tokens antes que expirem usando o fluxo de refresh token do LinkedIn.

2. **Publicando Conteúdo (UGC Post API / Share API)**
   - Distinga corretamente entre postar em nome de um Membro (`urn:li:person:{id}`) e de uma Organização (`urn:li:organization:{id}`).
   - Construa as requisições UGC Post (`POST /v2/ugcPosts`) ou Share API (`POST /v2/shares`) com a formatação JSON correta.
   - Para publicação de imagem/vídeo, implemente o processo de upload em múltiplas etapas:
     1. Registre o asset de upload (`POST /v2/assets?action=registerUpload`).
     2. Faça o upload dos dados binários para a `uploadUrl` fornecida via requisição HTTP PUT (sem headers de Authorization, usando um cliente HTTP limpo).
     3. Monitore o status do upload (especialmente para vídeos).
     4. Referencie a URN do asset criado (`urn:li:digitalmediaAsset:{id}`) no payload do post.
   - Envolva o cliente da API em métodos helper dentro do `LinkedInService`.

3. **Resiliência, Rate Limiting e Filas**
   - Nunca dispare posts do LinkedIn ou uploads de mídia diretamente de controllers ou fluxos de request síncronos. Use um job dedicado do BullMQ (ex.: `PublishLinkedInPostJob`).
   - Implemente a detecção de rate-limit verificando o código de status HTTP `429` (Too Many Requests).
   - Configure políticas de backoff exponencial e retry no BullMQ (ex.: `backoff: { type: 'exponential', delay: 10000 }, attempts: 5`) para tratar os limites de cota da API do LinkedIn de forma graciosa.
   - Limpe os arquivos temporários localmente após o upload.

4. **Webhooks e Verificação de Assinatura**
   - Implemente a verificação segura de webhooks para os Push Events do LinkedIn validando a assinatura criptográfica.
   - Extraia o corpo bruto (raw body) da request antes do parsing para computar a assinatura HMAC-SHA256 e compará-la com o header de assinatura enviado pelo LinkedIn.
   - Processe os webhooks de forma assíncrona inserindo os eventos em um model `Webhook` e enfileirando um job para fazer o parse deles.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- Não armazene access tokens ou refresh tokens em texto puro. Sempre criptografe as credenciais no banco de dados.
- Não execute chamadas à API do LinkedIn ou uploads de mídia de forma síncrona em HTTP Controllers. Use workers do BullMQ.
- Evite fazer hardcode de URLs ou prefixos de URN. Recupere-os de configs ou de respostas dinâmicas.
