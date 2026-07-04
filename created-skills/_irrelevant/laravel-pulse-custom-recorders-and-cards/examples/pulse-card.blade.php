{{--
    Componente Livewire correspondente (PHP):
    
    namespace App\Pulse\Livewire;

    use Laravel\Pulse\Facades\Pulse;
    use Laravel\Pulse\Livewire\Card;
    use Illuminate\Contracts\Support\Renderable;

    class ExternalApiMetrics extends Card
    {
        public function render(): Renderable
        {
            // Busca as médias de tempo de resposta armazenadas pelo Pulse nas últimas 24 horas
            $apiMetrics = Pulse::aggregate('external_api_duration', ['avg'])
                ->map(function ($row) {
                    // Busca falhas correspondentes à mesma chave de API
                    $failures = Pulse::aggregate('external_api_failure', ['count'], key: $row->key)->first()?->count ?? 0;
                    
                    // Busca tokens consumidos para esta API (se aplicável)
                    $tokens = Pulse::aggregate('ai_tokens_consumed', ['sum'], key: $row->key)->first()?->sum ?? 0;

                    return (object) [
                        'key' => $row->key,
                        'avg_duration' => $row->avg,
                        'failures' => $failures,
                        'tokens' => $tokens,
                    ];
                });

            return view('livewire.pulse.external-api-metrics', [
                'apiMetrics' => $apiMetrics,
            ]);
        }
    }
--}}

@php
use Laravel\Pulse\Facades\Pulse;
@endphp

<x-pulse::card :cols="$cols" :rows="$rows" class="col-span-full md:col-span-3">
    {{-- Cabeçalho do Cartão com estilização oficial do Pulse --}}
    <x-pulse::card-header
        name="Custos e Latência de APIs Externas"
        title="Monitora o tempo de resposta, consumo de tokens de IA e falhas da API do Autentique."
        details="Últimas 24 horas"
    >
        <x-slot:icon>
            <x-pulse::icons.circle-stack class="w-6 h-6 stroke-gray-400" />
        </x-slot:icon>
    </x-pulse::card-header>

    <x-pulse::scroll-list class="max-h-full">
        @if ($apiMetrics->isEmpty())
            <div class="flex flex-col items-center justify-center p-6 text-gray-400">
                <x-pulse::icons.no-results class="w-8 h-8 stroke-current" />
                <span class="mt-2 text-sm">Nenhuma telemetria registrada</span>
            </div>
        @else
            <x-pulse::table>
                <colgroup>
                    <col width="40%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="20%" />
                </colgroup>
                
                <x-pulse::thead>
                    <tr>
                        <x-pulse::th>API Endpoint</x-pulse::th>
                        <x-pulse::th class="text-right">Latência</x-pulse::th>
                        <x-pulse::th class="text-right">Tokens IA</x-pulse::th>
                        <x-pulse::th class="text-right">Erros</x-pulse::th>
                    </tr>
                </x-pulse::thead>

                <tbody>
                    @foreach ($apiMetrics as $metric)
                        <tr class="h-14">
                            <x-pulse::td class="max-w-[200px] truncate" title="{{ $metric->key }}">
                                <span class="font-medium text-gray-900 dark:text-gray-100 font-mono text-xs">
                                    {{ $metric->key }}
                                </span>
                            </x-pulse::td>
                            
                            <x-pulse::td class="text-right font-mono text-xs">
                                {{ number_format($metric->avg_duration, 0) }}ms
                            </x-pulse::td>
                            
                            <x-pulse::td class="text-right font-mono text-xs text-gray-600 dark:text-gray-400">
                                {{ $metric->tokens > 0 ? number_format($metric->tokens, 0) : '-' }}
                            </x-pulse::td>
                            
                            <x-pulse::td class="text-right font-mono text-xs">
                                <span class="{{ $metric->failures > 0 ? 'text-red-500 font-bold' : 'text-emerald-500' }}">
                                    {{ $metric->failures }}
                                </span>
                            </x-pulse::td>
                        </tr>
                    @endforeach
                </tbody>
            </x-pulse::table>
        @endif
    </x-pulse::scroll-list>
</x-pulse::card>
