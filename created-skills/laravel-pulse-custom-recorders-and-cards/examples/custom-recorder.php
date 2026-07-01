<?php

namespace App\Pulse\Recorders;

use Laravel\Pulse\Pulse;
use Illuminate\Http\Client\Events\ResponseReceived;
use Illuminate\Http\Client\Events\ConnectionFailed;

class ExternalApiRecorder
{
    /**
     * Os eventos a serem escutados.
     *
     * @var array<int, string>
     */
    public array $listen = [
        ResponseReceived::class,
        ConnectionFailed::class,
    ];

    /**
     * Registra o evento de resposta da API externa no Laravel Pulse.
     *
     * @param  \Illuminate\Http\Client\Events\ResponseReceived  $event
     * @param  \Laravel\Pulse\Pulse  $pulse
     * @return void
     */
    public function record(ResponseReceived $event, Pulse $pulse): void
    {
        $url = $event->request->url();

        // Filtra para capturar apenas APIs de IA (Gemini/OpenAI) ou Autentique
        if (! $this->shouldRecord($url)) {
            return;
        }

        // Obtém o tempo de resposta em milissegundos
        $duration = $event->transferStats?->getTransferTime() * 1000 ?? 0;

        // Registra o tempo de resposta (latência média) no Pulse
        $pulse->record(
            type: 'external_api_duration',
            key: $this->sanitizeUrl($url),
            value: (int) $duration,
            timestamp: now()
        )->avg()->count();

        // Registra a falha se o status HTTP for de erro
        if ($event->response->failed()) {
            $pulse->record(
                type: 'external_api_failure',
                key: $this->sanitizeUrl($url),
                value: 1,
                timestamp: now()
            )->count();
        }

        // Se for uma requisição para OpenAI ou Gemini, extrai e registra tokens
        if (str_contains($url, 'api.openai.com') || str_contains($url, 'generativelanguage.googleapis.com')) {
            $this->recordAiTokens($event, $pulse);
        }
    }

    /**
     * Registra falha de conexão na API externa.
     *
     * @param  \Illuminate\Http\Client\Events\ConnectionFailed  $event
     * @param  \Laravel\Pulse\Pulse  $pulse
     * @return void
     */
    public function recordConnectionFailed(ConnectionFailed $event, Pulse $pulse): void
    {
        $url = $event->request->url();

        if (! $this->shouldRecord($url)) {
            return;
        }

        // Registra o erro de conexão como falha
        $pulse->record(
            type: 'external_api_failure',
            key: $this->sanitizeUrl($url),
            value: 1,
            timestamp: now()
            )->count();
    }

    /**
     * Verifica se a URL deve ser monitorada.
     */
    protected function shouldRecord(string $url): bool
    {
        return str_contains($url, 'api.openai.com') ||
               str_contains($url, 'generativelanguage.googleapis.com') ||
               str_contains($url, 'autentique.com.br');
    }

    /**
     * Remove parâmetros dinâmicos da URL para agrupamento correto.
     */
    protected function sanitizeUrl(string $url): string
    {
        $parsed = parse_url($url);
        $host = $parsed['host'] ?? '';
        $path = $parsed['path'] ?? '';

        // Simplifica o path substituindo UUIDs e IDs numéricos
        $path = preg_replace('/\/[0-9a-fA-F-]{36}(\/|$)/', '/{uuid}$1', $path);
        $path = preg_replace('/\/\d+(\/|$)/', '/{id}$1', $path);

        return $host . $path;
    }

    /**
     * Registra estatísticas de tokens de IA consumidos.
     */
    protected function recordAiTokens(ResponseReceived $event, Pulse $pulse): void
    {
        $responseBody = $event->response->json();
        $tokens = 0;

        if (str_contains($event->request->url(), 'api.openai.com')) {
            // Estrutura de resposta padrão da OpenAI
            $tokens = $responseBody['usage']['total_tokens'] ?? 0;
        } elseif (str_contains($event->request->url(), 'generativelanguage.googleapis.com')) {
            // Estrutura de resposta padrão do Google Gemini
            $tokens = $responseBody['usageMetadata']['totalTokenCount'] ?? 0;
        }

        if ($tokens > 0) {
            // Registra a soma de tokens consumidos para a API
            $pulse->record(
                type: 'ai_tokens_consumed',
                key: $this->sanitizeUrl($event->request->url()),
                value: $tokens,
                timestamp: now()
            )->sum()->count();
        }
    }
}
