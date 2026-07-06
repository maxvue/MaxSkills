---
name: laravel-livekit-server-sdk-best-practices
description: Use ao criar, atualizar ou depurar serviços de áudio/vídeo WebRTC com o LiveKit Server SDK (agence104/livekit-server-sdk) no Laravel — gerar AccessToken JWT com VideoGrant para salas e gerenciar salas via RoomServiceClient (createRoom com RoomCreateOptions, deleteRoom, listParticipants) com tratamento de exceções. Acione em LiveKitService, geração de token e RoomServiceClient.
---

# Boas Práticas do LiveKit Server SDK no Laravel

## Objetivo
Fornecer diretrizes sólidas e padrões consistentes para integrar o LiveKit Server SDK (`agence104/livekit-server-sdk`) a um backend Laravel, cobrindo geração segura de access tokens, gerenciamento do ciclo de vida de salas e tratamento robusto de exceções.

## Instruções

### 1. Setup e Integração do Serviço
* **Instalação do Pacote:** A integração do backend deve usar o pacote composer `agence104/livekit-server-sdk`.
* **Configuração de Ambiente:** Configure suas variáveis `.env` com o host, key e secret do LiveKit:
  ```env
  LIVEKIT_API_KEY=your-api-key
  LIVEKIT_API_SECRET=your-api-secret
  LIVEKIT_WS_URL=wss://your-livekit-server-url
  ```
  Garanta que essas chaves estejam mapeadas em `config/services.php`:
  ```php
  'livekit' => [
      'api_key' => env('LIVEKIT_API_KEY'),
      'api_secret' => env('LIVEKIT_API_SECRET'),
      'ws_url' => env('LIVEKIT_WS_URL'),
  ],
  ```
* **Injeção de Dependência:** Centralize todas as operações do LiveKit Server em uma classe de serviço especializada (`LiveKitService`), injetando suas dependências via constructor property promotion ou referências de config.

### 2. Geração Segura de AccessToken
* **Configuração dos VideoGrants:** Sempre gere tokens com grants estritos. Para usuários padrão:
  - Chame `setRoomJoin()` e `setRoomName($roomName)`.
  - Chame `setCanPublish(true)` para permitir publicar tracks (áudio/tela).
  - Chame `setCanSubscribe(true)` para permitir assinar as tracks de outros participantes.
* **Identity e Display Name:** Sempre defina identificadores únicos para `setIdentity()` (ex: o ID do usuário como string) e `setName()` (ex: o nome de exibição do usuário) para garantir auditoria e a representação correta do estado no client.

### 3. Gerenciamento de Salas via RoomServiceClient
* **Inicialização do Client:** O `RoomServiceClient` requer um schema HTTP/HTTPS para chamadas REST, enquanto a conexão do client usa WebSocket (`ws://` / `wss://`). Limpe a URL antes de instanciar o client:
  ```php
  $host = str_replace(['ws://', 'wss://'], ['http://', 'https://'], $wsUrl);
  ```
* **Operações:** Use os métodos do `RoomServiceClient` para criar (`createRoom`), deletar/encerrar (`deleteRoom`) e listar participantes (`listParticipants`) dinamicamente no servidor.
* **Assinatura de `createRoom`:** O SDK declara `createRoom(RoomCreateOptions $createOptions): Room`. **Nunca** passe um array — isso causa `TypeError`. Construa as opções via fluent setters: `(new RoomCreateOptions)->setName($roomName)->setMaxParticipants($maxParticipants)`.

### 4. Tratamento de Exceções e Logging
* **Wrappers Robustos:** Sempre envolva as chamadas REST do LiveKit Server (ex: `createRoom`, `deleteRoom`, `listParticipants`) em blocos `try-catch`.
* **Logging de Erros:** Em caso de falhas de conexão ou exceções da API, capture o erro, registre-o usando a facade Log do Laravel com contexto descritivo e retorne uma exceção ou resposta de erro limpa e amigável ao usuário.

## Exemplos

### Implementação do Serviço LiveKit (`LiveKitService.php`)
```php
<?php

namespace App\Services;

use Agence104\LiveKit\AccessToken;
use Agence104\LiveKit\AccessTokenOptions;
use Agence104\LiveKit\RoomCreateOptions;
use Agence104\LiveKit\RoomServiceClient;
use Agence104\LiveKit\VideoGrant;
use Exception;
use Illuminate\Support\Facades\Log;

/**
 * Serviço responsável por encapsular a integração com o LiveKit Server.
 */
class LiveKitService
{
    private string $apiKey;
    private string $apiSecret;
    private string $wsUrl;

    public function __construct()
    {
        $this->apiKey = config('services.livekit.api_key', '');
        $this->apiSecret = config('services.livekit.api_secret', '');
        $this->wsUrl = config('services.livekit.ws_url', '');
    }

    /**
     * Gera um token de acesso JWT para um participante entrar em uma sala.
     *
     * @param string $roomName Nome/Slug da sala.
     * @param string $identity Identificador único do participante.
     * @param string $displayName Nome de exibição do participante.
     * @return string Token JWT assinado.
     */
    public function generateToken(string $roomName, string $identity, string $displayName): string
    {
        $tokenOptions = (new AccessTokenOptions())
            ->setIdentity($identity)
            ->setName($displayName);

        $videoGrant = (new VideoGrant())
            ->setRoomJoin()
            ->setRoomName($roomName)
            ->setCanPublish(true)
            ->setCanSubscribe(true);

        return (new AccessToken($this->apiKey, $this->apiSecret))
            ->init($tokenOptions)
            ->setGrant($videoGrant)
            ->toJwt();
    }

    /**
     * Instancia o client de controle de salas do LiveKit.
     */
    private function getRoomServiceClient(): RoomServiceClient
    {
        // Converte a URL do WebSocket para HTTP/HTTPS para as chamadas REST do SDK
        $host = str_replace(['ws://', 'wss://'], ['http://', 'https://'], $this->wsUrl);

        return new RoomServiceClient($host, $this->apiKey, $this->apiSecret);
    }

    /**
     * Retorna a URL do WebSocket do LiveKit (consumida pelo frontend).
     */
    public function getWsUrl(): string
    {
        return $this->wsUrl;
    }

    /**
     * Cria uma nova sala de videoconferência de forma segura.
     *
     * @param string $roomName Nome/Slug da sala.
     * @param int $maxParticipants Limite de participantes.
     * @return mixed Objeto contendo os dados da sala criada.
     * @throws Exception Caso ocorra erro na API do LiveKit.
     */
    public function createRoom(string $roomName, int $maxParticipants = 20): mixed
    {
        try {
            $client = $this->getRoomServiceClient();

            // A SDK exige um objeto RoomCreateOptions — passar array causa TypeError.
            $options = (new RoomCreateOptions())
                ->setName($roomName)
                ->setMaxParticipants($maxParticipants);

            return $client->createRoom($options);
        } catch (Exception $e) {
            Log::error('Erro ao criar sala no LiveKit Server', [
                'room_name' => $roomName,
                'exception' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    /**
     * Lista os participantes ativos de uma sala no servidor LiveKit.
     *
     * @param string $roomName Nome/Slug da sala.
     * @return array<int, mixed> Lista de participantes ativos.
     */
    public function listParticipants(string $roomName): array
    {
        try {
            $client = $this->getRoomServiceClient();
            return $client->listParticipants($roomName);
        } catch (Exception $e) {
            Log::error('Erro ao listar participantes no LiveKit Server', [
                'room_name' => $roomName,
                'exception' => $e->getMessage(),
            ]);

            return [];
        }
    }

    /**
     * Encerra e remove uma sala ativa no servidor LiveKit.
     */
    public function deleteRoom(string $roomName): void
    {
        try {
            $client = $this->getRoomServiceClient();
            $client->deleteRoom($roomName);
        } catch (Exception $e) {
            Log::error('Erro ao encerrar sala no LiveKit Server', [
                'room_name' => $roomName,
                'exception' => $e->getMessage(),
            ]);
        }
    }
}
```

### Controller de Geração de Token do LiveKit (`LiveTokenController.php`)
```php
<?php

namespace App\Http\Controllers\Live;

use App\Http\Controllers\Controller;
use App\Services\LiveKitService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * Controller responsável por autenticar e gerar tokens JWT para conexões LiveKit.
 */
class LiveTokenController extends Controller
{
    /**
     * Gera o token JWT para conectar à sala de videoconferência.
     */
    public function generateToken(Request $request, LiveKitService $liveKit): JsonResponse
    {
        $user = $request->user();

        // Validação e recuperação da sala a ser associada
        $request->validate([
            'room_slug' => 'required|string',
        ]);

        $roomSlug = $request->input('room_slug');

        try {
            $token = $liveKit->generateToken(
                $roomSlug,
                (string) $user->id,
                $user->name
            );

            return response()->json([
                'token' => $token,
                'ws_url' => $liveKit->getWsUrl(),
                'room_name' => $roomSlug,
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Não foi possível gerar o token de acesso à sala.',
                'message' => $e->getMessage(),
            ], 500);
        }
    }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Imponha Grants de Acesso Estritos:** Nunca deixe os VideoGrants vazios nem conceda permissões curinga (wildcard) sem especificar explicitamente os detalhes da sala (`setRoomJoin`, `setRoomName`).
* **Limpe as URLs de WS:** Sempre sanitize a URL de WebSocket usando uma substituição de string antes de instanciar o `RoomServiceClient` para evitar falhas de schema de conexão.
* **Logging Adequado de Erros:** Nunca suprima erros da API do LiveKit Server. Envolva todas as chamadas em blocos `try-catch` e registre-os usando a facade `Log` com contexto descritivo.
* **Sem Instanciação Direta do SDK nos Controllers:** Os controllers não devem instanciar `AccessToken` ou `RoomServiceClient` diretamente. Eles devem depender do `LiveKitService` injetado via injeção de dependência do Laravel.
* **Idioma dos Comentários:** Comentários de código e docstrings nos blocos de código devem ser escritos em **português brasileiro (pt-BR)**.
