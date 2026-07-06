---
name: laravel-whatsapp-cloud-api-integration
description: Use when creating, reviewing, or debugging WhatsApp Cloud API integrations, handling WhatsApp webhooks, sending templates or interactive messages, processing incoming messages, and managing conversation states.
---

# Objetivo
Fornecer diretrizes estritas, padrões arquiteturais e convenções de código para implementar, refatorar e depurar integrações com a WhatsApp Cloud API dentro do ecossistema Laravel do Engeapp. Isso garante validação segura de webhooks, processamento assíncrono e não-bloqueante de mensagens, gerenciamento robusto de rate limit da API, resiliência a erros e armazenamento padronizado no banco de dados.

# Instruções

## 1. Verificação & Processamento de Webhooks
* **Validação de Segurança:** Verifique a assinatura da requisição de entrada usando o header `X-Hub-Signature-256` e o App Secret. Valide o Hub Verification Token durante a confirmação da subscrição.
* **Resposta Imediata:** O controller que recebe as requisições de webhook DEVE retornar uma resposta HTTP 200 OK imediata. Evite realizar operações pesadas no banco de dados ou chamadas a APIs externas de forma síncrona dentro desse controller para evitar flags de timeout do webhook da Meta.
* **Delegação Assíncrona:** Faça dispatch do payload bruto do webhook diretamente para um job assíncrono (ex.: `WebhookWhatsappJobExecuteJob`) na fila `whatsapp`:
  ```php
  WebhookWhatsappJobExecuteJob::dispatch($data)->onQueue('whatsapp');
  ```

## 2. Configurações de Job Assíncrono & Fila
* **Fila Dedicada:** Sempre execute os jobs do WhatsApp na fila `whatsapp`.
* **Estratégia de Retry & Backoff:** Configure limites de retries e backoff para lidar com erros temporários da API e rate limiting:
  ```php
  public int $tries = 5;
  public array $backoff = [30, 60, 120, 180, 300];
  ```
* **Verificação de Idempotência:** Previna entrega e processamento duplicado de mensagens verificando se uma mensagem com o `message_meta_id` fornecido já existe no início do handler do job:
  ```php
  if ($message->message_meta_id) {
      Log::channel('whatsapp')->info('Message already sent, ignoring retry', ['message_id' => $id]);
      return;
  }
  ```
* **Falhas Permanentes:** Capture exceptions específicas que representam estados irrecuperáveis (ex.: um número de telefone que não está habilitado no WhatsApp). Nesses casos, faça o job falhar imediatamente para evitar consumir tentativas desnecessárias:
  ```php
  catch (\RuntimeException $e) {
      Log::channel('whatsapp')->error('Permanent failure sending message: ' . $e->getMessage());
      $this->fail($e);
      return;
  }
  ```
* **Retry Middleware:** Aplique o `NotifyRetryingWhatsappMiddleware` aos jobs para que notificações em tempo real possam ser enviadas ao front-end via WebSockets quando as tentativas falharem, mas houver retries agendados.

## 3. Modelagem de Dados & Padrões de Helpers
* **Associação de Contato & Mensagem:** Armazene as mensagens de chat recebidas e enviadas no model `SupportMessage` e vincule-as a uma instância de `SupportContact`.
* **Estrutura de Parsing:** Percorra recursivamente os arrays `entry` -> `changes` -> `value` -> `messages`/`statuses` do payload do webhook da Meta para fazer o parsing do conteúdo das mensagens ou do status de entrega.
* **Padronização de Telefone:** Sempre utilize os helpers de `PhoneClass` para normalizar números de telefone e resolver IDs compatíveis com a Meta:
  ```php
  $phone_number = PhoneClass::getInternationalPhoneNumber($raw_phone);
  $whatsapp_id = PhoneClass::getWhatsappMetaId($phone_number);
  ```
* **Campos do Schema de Mensagens:** Garanta que as mensagens persistam os metadados-chave:
  - `message_meta_id`: O ID retornado pela Meta ou recebido do webhook.
  - `message_type`: Ex.: `text`, `template`, `image`, `document`, `audio`, `payment`.
  - `direction`: Ex.: `receive` ou `send`.
  - `status`: Ex.: `sent`, `delivered`, `read`, `failed`, `received`.
  - `meta_payload`: O payload JSON completo para rastreamento e debugging.

## 4. Envios de Saída — SDK netflie (caminho principal)
* **Use o SDK instalado:** Mensagens de saída DEVEM passar pelo SDK `netflie/whatsapp-cloud-api` (`^2.2`) instalado, não por chamadas manuais `Http::withHeaders(...)`. Isso espelha os controllers reais em `app/Http/Controllers/Api/Whatsapp/Sends/`, que importam `Netflie\WhatsAppCloudApi\...`.
* **Instancie com config, nunca com tokens hardcoded:** O construtor recebe um array associativo com apenas dois campos (`from_phone_number_id`, `access_token`). Leia o phone number id do canal (`$channel->meta_number`) e o token de `config()`:
  ```php
  use Netflie\WhatsAppCloudApi\WhatsAppCloudApi;
  use Netflie\WhatsAppCloudApi\Message\Template\Component;
  use Netflie\WhatsAppCloudApi\Response\ResponseException;

  $api = new WhatsAppCloudApi([
      'from_phone_number_id' => $channel->meta_number,
      'access_token'         => config('api.whatsapp_user_engeapp_token'),
  ]);

  try {
      // Texto simples
      $response = $api->sendTextMessage($clientMetaId, $body);

      // Template (name, language, Component opcional com header/body/buttons)
      $response = $api->sendTemplate($clientMetaId, $templateName, $language, $components);
  } catch (ResponseException $e) {
      Log::channel('whatsapp')->error('WhatsApp send failed', ['error' => $e->getMessage()]);
      throw $e;
  }
  ```
* **`Http` bruto apenas como fallback:** Recorra ao wrapper do client `Http` do Laravel apenas para endpoints que o SDK não cobre. Quando o fizer, ainda assim leia os tokens da config — nunca os deixe hardcoded:
  ```php
  Http::withHeaders([
      'Authorization' => 'Bearer ' . config('api.whatsapp_user_engeapp_token'),
  ])->post($url, $data);
  ```

## 5. Resiliência & Logging
* **Canal de Log Dedicado:** Direcione todos os logs de integração (info, warn, error) para o canal `whatsapp`:
  ```php
  Log::channel('whatsapp')->error('Integration error detail', ['context' => $data]);
  ```

# Restrições
* **NÃO** execute lógica de negócio de longa duração, notificações ou transações de banco de dados diretamente dentro do contexto da requisição HTTP do webhook. Sempre envie para a fila.
* **NÃO** tente reenviar mensagens que já contenham um `message_meta_id` válido, para evitar enviar duplicatas aos usuários.
* **NÃO** faça log de tokens de autenticação brutos ou client secrets. Garanta que sejam lidos dos arquivos `config()` e armazenados com segurança no `.env`.
* **NÃO** use os arquivos de log padrão da aplicação (`laravel.log`) para integrações do WhatsApp. Sempre use o canal de log `whatsapp`.
* **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
