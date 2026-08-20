---
name: laravel-cache-best-practices
description: "Use when implementing, configuring, or debugging cache in Engeapp (Laravel 13 + Octane, phpredis store). Covers Cache::remember pattern, TTLs, invalidation via Cache::forget (Models/Observers), key conventions, tags/locks, and deploy caches."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Cache do Laravel

## Objetivo
Estabelecer diretrizes sólidas, convenções consistentes de nomenclatura de chaves e padrões estruturados para cachear dados, respostas de API e queries de banco de dados dentro do ecossistema Laravel do Engeapp. Isso garante performance ótima da aplicação, consistência de dados e compatibilidade stateless sob o Laravel Octane.

> Para a camada de driver/conexão do Redis (serialização, configuração de conexão, facade `Redis`), veja `laravel-redis-integration-best-practices`.

## Instruções

### 1. Convenções de Nomenclatura de Chaves de Cache
> **Estado atual do repositório (verdade-base):** o código hoje usa chaves *planas*, montadas por concatenação, sem prefixo estruturado. Exemplos reais:
> - `Cache::remember($this->id . '-cache-nominal-power-kw', 120, ...)` — `app/Models/Equipment/Inverter.php:126`
> - `Cache::remember('contact-contact_type-' . $this->id, ...)` — `app/Models/SupportChat/SupportContact.php:493` (com `Cache::forget` correspondente em `:489`)
> - `Cache::remember('users.channel.' . $this->id, ...)` — `app/Models/SupportChat/SupportChannel.php:73`
> - `'specs.' . $model->id` (`Module`), `'files_' . $message->id` (`SupportMessage`)
>
> Portanto, o formato abaixo é uma **convenção-alvo para código novo e refatorações**, e NÃO descreve o padrão predominante já existente. Não presuma que chaves no formato `model:...:...` existam no cache — as chaves reais seguem os padrões planos acima. Ao invalidar uma chave existente, monte-a exatamente como o código que a escreveu.

Para código novo, prefira chaves estruturadas, previsíveis e com escopo, evitando strings soltas sem contexto:
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

### 4. Invalidação de Cache
> **Estado atual do repositório (verdade-base):** hoje a invalidação é feita *inline*, de duas formas:
> - **Hooks de ciclo de vida no próprio Model**, via `static::booted()` + `static::updated()`. Ex.: `Module` limpa `'specs.' . $model->id` (`app/Models/Equipment/Module.php:241`); `SupportContact`/`SupportMessage` chamam `Cache::forget` diretamente.
> - **`Cache::forget` dentro de Controllers.** Ex.: `app/Http/Controllers/SupportContacts/ContactsDataControler.php:64` e `:118`; `app/Http/Controllers/SupportMessage/SupportMessageDataController.php:38`.
>
> Existem Observers no projeto (`app/Observers/*Observer.php`), mas **nenhum** deles invalida cache atualmente. Ou seja, a orientação abaixo é uma **convenção-alvo para centralizar/refatorar** a invalidação, não o padrão já adotado. Ao mexer em cache de um Model existente, primeiro localize onde a chave é escrita e onde já é esquecida, e mantenha a consistência.
>
> **Atenção — namespace `specs.` é compartilhado entre Module e Inverter:** a chave `'specs.{id}'` é ESCRITA por `StationModule::dataSpecs` (`app/Models/Station/StationModule.php:84`, TTL 259200) e por `StationInverter::dataSpecs` (`StationInverter.php:125`), e INVALIDADA por `Module::booted/updated` (`Module.php:241`), `Inverter::booted/updated` (`Inverter.php:186`) e `StationInverter::booted/saving` (`StationInverter.php:187`) — quem escreve e quem invalida são classes distintas. A chave usa apenas o id do equipamento, então um `Module` e um `Inverter` com o mesmo id colidem na mesma chave `specs.{id}` (um `StationModule` pode acabar lendo um `Inverter` cacheado, e vice-versa). Ao tocar nesse cache, prefira qualificar a chave por tipo (ex.: `specs.module.{id}` / `specs.inverter.{id}`) — aqui a invalidação é necessariamente multi-model, não um ponto único por Model.

Para reduzir duplicação e evitar dados obsoletos (stale), prefira concentrar a invalidação de cada Model num único ponto — seja num Observer dedicado, seja no hook `static::booted()` do Model — em vez de espalhar `Cache::forget` por vários Controllers. Dispare o `forget` nos eventos `saved`, `updated`, `deleted` e `restored`, sempre remontando a chave exatamente como ela é escrita.

```php
// Opção A — hook no próprio Model (padrão já presente no repo, ex.: Module)
protected static function booted() : void
{
    static::updated(static function (self $model) : void {
        // Remonta a chave exatamente como foi escrita ao cachear.
        Cache::forget('specs.' . $model->id);
    });
}
```

```php
// Opção B — Observer dedicado (convenção-alvo para centralizar a lógica)
namespace App\Observers;

use App\Models\Equipment\Inverter;
use Illuminate\Support\Facades\Cache;

class InverterObserver
{
    /**
     * Limpa o cache do inversor quando ele é salvo ou atualizado.
     */
    public function saved(Inverter $inverter) : void
    {
        // A chave real usada em Inverter é plana; remonte-a idêntica.
        Cache::forget($inverter->id . '-cache-nominal-power-kw');
        Cache::forget($inverter->id . '-cache-maximum-power');
    }
}
```

#### Orientação única sobre Cache Tags (canônica — referida também por `laravel-redis-integration-best-practices`)
> **Ainda não usado no Engeapp:** não há nenhuma ocorrência de `Cache::tags` em `app/`. O store efetivo do projeto é `redis` (`CACHE_DRIVER=redis` / `CACHE_STORE=redis` em `.env`, via `phpredis`; `config/cache.php:18` só define `database` como fallback do `env()`), que **suporta tags** — mas `file`/`array` (e `database`, caso o store seja trocado) **não** suportam. Verifique o store efetivo antes de usar tags.

Para entradas relacionadas que devem expirar juntas (ex: todas as páginas cacheadas de uma listagem), marque-as com uma tag na escrita e limpe o grupo inteiro de uma vez com `flush()` seletivo. Regras:
- No Redis, tags são implementadas via **chaves de rastreamento adicionais**, que consomem memória. Use tags para grupos de **cardinalidade moderada**; **evite** tags ao cachear milhões de chaves. Nesses casos de altíssima cardinalidade, prefira invalidação por chave individual (Observers + `Cache::forget`) ou por prefixo determinístico embutido na própria chave.
- Faça `flush()` **seletivo por tag**, nunca limpe o cache inteiro.
- `CACHE_PREFIX` (`.env`) já compõe o namespace real de todas as chaves gravadas no Redis.

```php
// Agrupa entradas relacionadas sob uma tag para invalidação em bloco
Cache::tags(['inverters'])->remember('inverters:index:page:1', now()->addMinutes(5), fn () => Inverter::paginate(50));

// Invalida todas as entradas da tag de uma só vez (flush seletivo)
Cache::tags(['inverters'])->flush();
```

Documente o gatilho de invalidação próximo ao código que escreve o cache, e sempre inclua qualquer dimensão de escopo (tenant, locale, página) na chave.

### 5. Condições de Corrida e Concorrência
> **Padrão já presente no Engeapp:** `Cache::lock` já é usado em `app/Services/Finance/TrtPaymentSchedulingService.php:109` (`Cache::lock('trt-payment-schedule:' . $project->id . ':' . $index, 120)`) para evitar duplo envio de pagamento. Use esse caso real como referência ao introduzir locks em outros fluxos. O store `redis` suporta locks atômicos (usa `lock_connection`, default `'default'`); o driver `array` não é confiável para isso.

Para tarefas de alta concorrência ou recálculos pesados, use locks atômicos (`Cache::lock`) para prevenir Cache Stampede (múltiplos processos consultando os mesmos dados do banco simultaneamente quando o cache expira).

```php
use Illuminate\Support\Facades\Cache;

// Adquire uma trava atômica por até 120s para evitar duplo processamento (padrão real: TrtPaymentSchedulingService)
$lock = Cache::lock('trt-payment-schedule:' . $project->id . ':' . $index, 120);

if ($lock->get()) {
    // Processamento seguro sem concorrência concorrente
    
    $lock->release();
}
```

### 6. Compatibilidade com Octane (Stateless)
- Evite usar o driver de cache `array` em ambientes de produção, pois ele é em memória e não sincronizará entre múltiplos workers do Octane.
- Não armazene estado diretamente em propriedades estáticas de classe, pois elas persistem entre requisições no worker do Octane. Sempre use a facade `Cache` para estado compartilhado. Para metadados com escopo de requisição, a facade `Context` do Laravel é uma opção válida — porém note que a facade `Context` do Laravel (`Illuminate\Support\Facades\Context`) **ainda não é usada no Engeapp**; as únicas ocorrências de `Context::` em `app/` são `Twirp\Context::withHttpRequestHeaders` em `AgentCallService.php` e `VoipService.php`, que não têm relação com essa facade. Adote-a conscientemente ao introduzir esse padrão.

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
- **SEM Singletons com Estado:** Nunca armazene valores cacheados em propriedades de instância de singleton, a menos que você implemente explicitamente um mecanismo de limpeza ou os vincule usando resolver closures.
- **Comentários em Português Brasileiro:** Todos os comentários de código dentro dos exemplos PHP devem ser escritos estritamente em português brasileiro (pt-BR).
