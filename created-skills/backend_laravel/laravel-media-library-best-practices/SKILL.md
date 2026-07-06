---
name: laravel-media-library-best-practices
description: Use ao definir, implementar, revisar ou depurar upload e anexos de arquivos com Spatie Laravel Media Library no engeapp. Cobre models HasMedia/InteractsWithMedia, o Media model customizado (App\Models\Media\Media com HasUlids e custom properties), coleções com useDisk('projects'), conversões nonQueued, o MediaController genérico e as rotas media.* de view/download.
---

# Boas Práticas do Spatie Laravel Media Library (engeapp)

## Objetivo
Estabelecer padrões limpos, performáticos e seguros para gerenciar uploads e anexos de mídia via Spatie Laravel Media Library no engeapp, fiéis à arquitetura já existente (Media model customizado, disco `projects`, MediaController genérico e trait de compatibilidade com o antigo model `File`).

## Instruções

### 1. Configuração do Model
Ao implementar capacidades de mídia em um model:
- Implemente a interface `Spatie\MediaLibrary\HasMedia`.
- Use a trait `Spatie\MediaLibrary\InteractsWithMedia`.
- Sempre declare o tipo de retorno (`: void`) em `registerMediaCollections()` e `registerMediaConversions()`.
- Documente cada coleção em um docblock em pt-BR acima do método, seguindo o padrão do projeto.

O engeapp usa um **Media model customizado**: `App\Models\Media\Media` estende `Spatie\...\Models\Media`, adota `HasUlids` e expõe acessores para as custom properties (`data_ai`, `data_ai_b`, `hash`, etc.). Ele está registrado em `config/media-library.php` (`'media_model' => App\Models\Media\Media::class`). Não crie um segundo Media model; estenda esse quando precisar de novos acessores.

Exemplo real (baseado em `app/Models/Project/ProjectContract.php`):

```php
namespace App\Models\Project;

use Spatie\MediaLibrary\HasMedia;
use Spatie\MediaLibrary\InteractsWithMedia;

class ProjectContract extends Model implements HasMedia
{
    use HasUlids, InteractsWithMedia;

    /**
     * Registra as coleções de mídia disponíveis para contratos.
     */
    public function registerMediaCollections() : void
    {
        $this->addMediaCollection('contracts')
            ->useDisk('projects');
    }
}
```

### 2. Configuração de Coleções de Mídia
No engeapp as coleções são **enxutas por padrão**: apenas `addMediaCollection(<nome>)->useDisk('projects')`, sem `singleFile()` nem `acceptsMimeTypes()` (ver `ProjectContract`, `Module`, `Inverter`). Siga esse padrão salvo requisito real em contrário.

- Disco: use `useDisk('projects')`, que é o disco padrão dos arquivos de projeto no engeapp. O disco default do pacote é definido por `MEDIA_DISK` (`public`) em `config/media-library.php` — não presuma `s3`.
- Só adicione `singleFile()` quando a regra de negócio exigir substituição automática (ex.: um único arquivo principal). Isso não está em uso hoje.
- Só adicione `acceptsMimeTypes([...])` quando quiser restringir tipos no nível da coleção. Hoje a validação de tipo/tamanho vive no controller (ver seção 4), não na coleção.

### 3. Conversões de Imagem
As conversões reais do projeto rodam **síncronas** com `nonQueued()`. Ver `Module::registerMediaConversions()` e `Inverter::registerMediaConversions()`:

```php
public function registerMediaConversions(?Media $media = null) : void
{
    $this->addMediaConversion('thumb')
        ->width(300)
        ->height(300)
        ->sharpen(10)
        ->format('png')
        ->nonQueued();
}
```

Regra prática (não absoluta):
- Para thumbnails leves (como o `thumb` 300x300 acima) use `nonQueued()` — é o padrão do projeto e evita depender da fila para exibir a miniatura logo após o upload. **Não** "corrija" código existente que usa `nonQueued()`.
- Reserve `->queued()` para conversões realmente pesadas (imagens grandes, múltiplas variações) onde bloquear a requisição seria inaceitável. Nesse caso, garanta que a fila esteja processando e trate o estado "conversão ainda não gerada" (ver `MediaController::conversion`, que retorna 404 quando `hasGeneratedConversion()` é falso).
- Observação de config: `queue_conversions_by_default` está `true`; `nonQueued()` sobrescreve isso por conversão. `queue_connection_name` segue `QUEUE_CONNECTION` (default `sync`).

### 4. Upload e Validação no Controller
O upload genérico do engeapp vive em `app/Http/Controllers/Media/MediaController.php`, que aceita qualquer model `HasMedia` resolvido por um mapa curto→classe (`resolveModelClass()`), e valida diretamente na request:

```php
public function upload(Request $request, string $modelType, string $modelId) : MediaResource | JsonResponse
{
    $request->validate([
        'file'       => 'required|file|max:102400', // 100 MB
        'collection' => 'nullable|string',
    ]);

    $fullClass = $this->resolveModelClass($modelType);
    $model = $fullClass::findOrFail($modelId);

    $collection = $request->input('collection', 'documents');

    set_time_limit(120);

    $media = $model->addMediaFromRequest('file')
        ->toMediaCollection($collection);

    return new MediaResource($media);
}
```

Diretrizes:
- Sempre valide `file` (`required|file|max:...`). Para upload de vários arquivos use `files` como array e `files.*` com `file|max:...`, iterando com `$model->addMedia($file)->toMediaCollection(...)` (ver `uploadMultiple`).
- Ao expor os itens para o front, retorne via `MediaResource` (ou pela trait de compatibilidade, seção 5) — não monte payloads de mídia à mão.
- Se for adicionar um novo model ao fluxo genérico, registre o mapeamento curto→FQCN em `resolveModelClass()`.
- Ao criar Form Requests dedicados para fluxos específicos, mantenha as mesmas regras (`required|file|max:...`, mime types quando aplicável).

### 5. Recuperação de Mídia e Compatibilidade com o front
Não retorne `getFirstMediaUrl()` cru quando o consumidor for o front do engeapp. O projeto serve os binários por **rotas nomeadas próprias**, não por URL pública direta:
- `route('media.view', $media->id)` — visualização inline (`GET /media/{mediaId}/view`).
- `route('media.download', $media->id)` — download (`GET /media/{mediaId}/download`).
- `route('media.conversion', [$media->id, $conversion])` — serve uma conversão (ex.: `thumb`).

Para manter o front consumindo o formato do antigo model `File` (`DBFile`), use a trait `App\Traits\HasMediaAsLegacyFiles::getMediaAsLegacyFiles()`. Ela mapeia cada mídia Spatie para o shape esperado pelos componentes Vue, lendo custom properties com `getCustomProperty()`:
- `label_file_name`, `document_type`, `thumbnail`, `hash`, `tags`, `data_ai`/`data_ai_b`/`data_ai_c`, `pdf_count_pages`, `image_inspection`, `is_send_to_project`.
- `url` = `route('media.view', $item->id)`; `download_url` = `route('media.download', $item->id)`.

Ao anexar mídia, grave metadados via custom properties (`->withCustomProperties([...])` ou os acessores do Media model customizado) para que a trait os exponha depois. Não crie colunas novas na tabela `media` para isso.

### 6. Prevenção de N+1
Carregar mídia para listas dispara uma query por registro.
- Faça eager load com `->with('media')` ao listar múltiplos models que exibem anexos.
- No `MediaController::index`, a consulta já filtra por `model_type`/`model_id` e ordena por `order_column`; ao expor mídia dentro de um recurso maior, prefira eager loading a chamadas repetidas de `getMedia()`.

### 7. Limpeza e Órfãos
- A exclusão de arquivos é tratada pelos eventos de delete do model do Spatie; com soft deletes, garanta a estratégia correta de remoção física.
- Use `php artisan media-library:clean` para remover conversões/arquivos órfãos.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), sem exceção, independentemente do idioma do corpo desta skill. Comentários de código também em pt-BR.
- **Não** transforme a escolha `queued()`/`nonQueued()` em regra cega: o padrão do projeto para thumbnails é `nonQueued()`. Use `queued()` apenas para conversões pesadas justificadas.
- **Não** faça upload sem validar o arquivo (`required|file|max:...`) na request ou em uma Form Request.
- **Não** monte URLs de mídia manualmente nem use queries brutas: use as rotas nomeadas `media.view`/`media.download`/`media.conversion` ou a trait `HasMediaAsLegacyFiles`.
- **Não** presuma discos como `s3`/`public` para arquivos de projeto: as coleções usam `useDisk('projects')`.
- **Não** crie um segundo Media model: estenda `App\Models\Media\Media`, já registrado em `config/media-library.php`.
- **Não** esqueça de fazer eager load da relação `media` ao listar múltiplas entidades com anexos.
