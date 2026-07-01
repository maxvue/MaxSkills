---
name: laravel-livekit-server-sdk-best-practices
description: Use when creating, updating, or debugging LiveKit WebRTC audio/video services, generating access tokens for rooms, managing LiveKit rooms, or handling room events and Webhooks. Triggers on LiveKit SDK integration, AccessToken generation, and RoomServiceClient usage.
---

# Laravel LiveKit Server SDK Best Practices

## Goal
Provide solid guidelines and consistent patterns for integrating the LiveKit Server SDK (`agence104/livekit-server-sdk`) into a Laravel backend, covering secure access token generation, room lifecycle management, and robust exception handling.

## Instructions

### 1. Setup and Service Integration
* **Package Installation:** The backend integration must use the `agence104/livekit-server-sdk` composer package.
* **Environment Configuration:** Configure your `.env` variables with the LiveKit host, key, and secret:
  ```env
  LIVEKIT_API_KEY=your-api-key
  LIVEKIT_API_SECRET=your-api-secret
  LIVEKIT_WS_URL=wss://your-livekit-server-url
  ```
  Ensure these keys are mapped in `config/services.php`:
  ```php
  'livekit' => [
      'api_key' => env('LIVEKIT_API_KEY'),
      'api_secret' => env('LIVEKIT_API_SECRET'),
      'ws_url' => env('LIVEKIT_WS_URL'),
  ],
  ```
* **Dependency Injection:** Centralize all LiveKit Server operations into a specialized service class (`LiveKitService`), injecting its dependencies via constructor property promotion or config references.

### 2. Secure AccessToken Generation
* **VideoGrants Configuration:** Always generate tokens with strict grants. For standard users:
  - Call `setRoomJoin()` and `setRoomName($roomName)`.
  - Call `setCanPublish(true)` to allow publishing tracks (audio/screen).
  - Call `setCanSubscribe(true)` to allow subscribing to other participants' tracks.
* **Identity and Display Name:** Always set unique identifiers for `setIdentity()` (e.g., User ID as a string) and `setName()` (e.g., User Display Name) to guarantee auditing and correct state representation in the client.

### 3. Room Management via RoomServiceClient
* **Client Initialization:** The `RoomServiceClient` requires an HTTP/HTTPS schema for REST calls, whereas the client connection uses WebSocket (`ws://` / `wss://`). Clean the URL before instantiating the client:
  ```php
  $host = str_replace(['ws://', 'wss://'], ['http://', 'https://'], $wsUrl);
  ```
* **Operations:** Use the `RoomServiceClient` methods to create (`createRoom`), delete/close (`deleteRoom`), and list participants (`listParticipants`) dynamically on the server.

### 4. Exception Handling & Logging
* **Robust Wrappers:** Always wrap LiveKit Server REST calls (e.g., `createRoom`, `deleteRoom`, `listParticipants`) in `try-catch` blocks.
* **Logging Errors:** In case of connection failures or API exceptions, catch the error, log it using Laravel's Log facade with descriptive context, and return a clean, user-friendly exception or error response.

## Examples

### LiveKit Service Implementation (`LiveKitService.php`)
```php
<?php

namespace App\Services;

use Agence104\LiveKit\AccessToken;
use Agence104\LiveKit\AccessTokenOptions;
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
            return $client->createRoom([
                'name' => $roomName,
                'max_participants' => $maxParticipants,
            ]);
        } catch (Exception $e) {
            Log::error('Erro ao criar sala no LiveKit Server', [
                'room_name' => $roomName,
                'exception' => $e->getMessage(),
            ]);
            throw $e;
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

### LiveKit Token Generation Controller (`LiveTokenController.php`)
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

## Constraints
* **Enforce Strict Access Grants:** Never leave VideoGrants empty or grant wildcard permissions without explicitly specifying the room details (`setRoomJoin`, `setRoomName`).
* **Clean WS URLs:** Always sanitize the WebSocket URL using a string replacement before instantiating `RoomServiceClient` to avoid connection scheme failures.
* **Proper Error Logging:** Never suppress errors from the LiveKit Server API. Wrap all calls in `try-catch` blocks and log them using the `Log` facade with descriptive context.
* **No Direct SDK Instantiation in Controllers:** Controllers must not instantiate `AccessToken` or `RoomServiceClient` directly. They must rely on `LiveKitService` injected via Laravel dependency injection.
* **Language of Comments:** Code comments and docstrings in code blocks must be written in **Brazilian Portuguese (pt-BR)**.
