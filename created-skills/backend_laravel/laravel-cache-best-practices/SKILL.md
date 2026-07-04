---
name: laravel-cache-best-practices
description: Use when implementing, configuring, or debugging caching mechanisms in Laravel. Triggers on Cache facade usage, Cache::remember, Cache::forget, Cache::put, cache configuration, TTL definitions, and cache-aside patterns.
---

# Boas Práticas de Cache do Laravel

## Objetivo
Estabelecer diretrizes sólidas, convenções consistentes de nomenclatura de chaves e padrões estruturados para cachear dados, respostas de API e queries de banco de dados dentro do ecossistema Laravel do Engeapp. Isso garante performance ótima da aplicação, consistência de dados e compatibilidade stateless sob o Laravel Octane.

> Para a camada de driver/conexão do Redis (serialização, configuração de conexão, facade `Redis`), veja `laravel-redis-integration-best-practices`.

## Instruções

### 1. Convenções de Nomenclatura de Chaves de Cache
Sempre use chaves de cache estruturadas, previsíveis e com escopo. Evite usar strings simples ou IDs gerados dinamicamente sem contexto.
- **APIs Externas:** Use o formato `api:{provider}:{endpoint_or_resource}:{unique_identifier}`
  - Exemplo: `api:correios:zipcode:01001000`
  - Exemplo: `api:cnpj:company:12345678000199`
- **Models Eloquent:** Use o formato `model:{table_name}:{id}:{attribute_or_relation}`
  - Exemplo: `model:inverters:45:nominal_power`
  - Exemplo: `model:support_contacts:12:channel_users`
- **Contextos de Aplicação:** Use o formato `app:{context}:{identifier}`
  - Exemplo: `app:support_template:welcome_message`

### 2. Especificações de Time-To-Live (TTL)
Sempre defina um TTL preciso e apropriado. Evite cachear dados para sempre (`rememberForever`), a menos que sejam verdadeiramente estáticos e imutáveis.
- Use helpers do Carbon explícitos ou inteiros em segundos para representar a duração.
- TTLs recomendados:
  - APIs Externas de Endereço (CEP, CNPJ): 3 a 6 meses (`now()->addMonths(6)`).
  - APIs Externas de Token (ex: Correios, CRM): Até a expiração do token (`now()->addHours(24)`).
  - Relações/atributos Eloquent: 10 minutos a 3 dias, dependendo da frequência de atualizações.

### 3. Padrão Cache-Aside
Prefira usar `Cache::remember` em vez de blocos manuais de `Cache::has` e `Cache::put` para prevenir condições de corrida e garantir código limpo.

```php
// Padrão recomendado para buscar dados com fallback e cacheamento automático
$inverterPower = Cache::remember(
    "model:inverters:{$this->id}:nominal_power",
    now()->addMinutes(120),
    fn () => $this->nominal_power / 1000
);
```

### 4. Invalidação de Cache via Observers
Para evitar estados de dados obsoletos (stale), sempre invalide os caches de model usando Observers do Eloquent. Evite colocar lógica de invalidação de cache dentro de Controllers ou Models.
- Crie um Observer usando `php artisan make:observer {ModelName}Observer --model={ModelName}`.
- Dispare `Cache::forget` nos eventos `saved`, `deleted` e `restored`.

```php
namespace App\Observers;

use App\Models\Inverter;
use Illuminate\Support\Facades\Cache;

class InverterObserver
{
    /**
     * Limpa o cache quando o inversor é salvo ou atualizado.
     */
    public function saved(Inverter $inverter): void
    {
        Cache::forget("model:inverters:{$inverter->id}:nominal_power");
    }

    /**
     * Limpa o cache quando o inversor é deletado.
     */
    public function deleted(Inverter $inverter): void
    {
        Cache::forget("model:inverters:{$inverter->id}:nominal_power");
    }
}
```

Para entradas relacionadas que devem expirar juntas (ex: todas as páginas cacheadas de uma listagem), marque-as com uma tag na escrita e limpe o grupo inteiro de uma vez. Apenas drivers com suporte a tags (Redis, Memcached) suportam isso.

```php
// Agrupa entradas relacionadas sob uma tag para invalidação em bloco
Cache::tags(['inverters'])->remember('inverters:index:page:1', now()->addMinutes(5), fn () => Inverter::paginate(50));

// Invalida todas as entradas da tag de uma só vez
Cache::tags(['inverters'])->flush();
```

Documente o gatilho de invalidação próximo ao código que escreve o cache, e sempre inclua qualquer dimensão de escopo (tenant, locale, página) na chave.

### 5. Condições de Corrida e Concorrência
Para tarefas de alta concorrência ou recálculos pesados, use locks atômicos (`Cache::lock`) para prevenir Cache Stampede (múltiplos processos consultando os mesmos dados do banco simultaneamente quando o cache expira).

```php
use Illuminate\Support\Facades\Cache;

// Adquire uma trava atômica por até 10 segundos para processar dados de API pesados
$lock = Cache::lock('api:processing:heavy_report', 10);

if ($lock->get()) {
    // Processamento seguro sem concorrência concorrente
    
    $lock->release();
}
```

### 6. Compatibilidade com Octane (Stateless)
- Evite usar o driver de cache `array` em ambientes de produção, pois ele é em memória e não sincronizará entre múltiplos workers do Octane.
- Não armazene estado diretamente em propriedades estáticas de classe, pois elas persistem entre requisições no worker do Octane. Sempre use a facade `Cache` ou a facade `Context` do Laravel para rastreamento de metadados com escopo de requisição.

### 7. Caches do Framework (Deploy)
Cacheie a config, as rotas e as views do próprio framework durante o deploy para reduzir o custo de boot por requisição. Sempre limpe (ou re-cacheie) esses itens a cada deploy, e nunca rode `config:cache` localmente enquanto edita o `.env`.

```
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

Use os comandos correspondentes `config:clear` / `route:clear` / `view:clear` quando os valores mudarem.

---

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **SEM Chaves Simples:** Nunca use chaves de cache sem prefixos estruturados (ex: não use apenas `$this->id`, use `"model:inverters:{$this->id}"` em vez disso).
- **SEM Invalidação de Cache Inline:** Não coloque código de invalidação de cache inline dentro de controllers; delegue-o a Observers.
- **SEM Singletons com Estado:** Nunca armazene valores cacheados em propriedades de instância de singleton, a menos que você implemente explicitamente um mecanismo de limpeza ou os vincule usando resolver closures.
- **Comentários em Português Brasileiro:** Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em português brasileiro (pt-BR).
