---
name: laravel-media-library-best-practices
description: Use when defining, implementing, reviewing, or debugging file uploads and media attachments using Spatie Laravel Media Library. Triggers on model implementing HasMedia, using InteractsWithMedia trait, registering media collections, defining media conversions, uploading files from HTTP requests, and retrieving media URLs.
---

# Boas Práticas do Spatie Laravel Media Library

## Objetivo
Estabelecer padrões limpos, performáticos e seguros para gerenciar uploads de arquivos e anexos de mídia via Spatie Laravel Media Library no ecossistema Engeapp.

## Instruções

### 1. Configuração do Model
Ao implementar capacidades de mídia em um model:
- Implemente a interface `Spatie\MediaLibrary\HasMedia`.
- Use a trait `Spatie\MediaLibrary\InteractsWithMedia`.
- Sempre adicione declarações de tipo de retorno a todos os relacionamentos de mídia ou métodos auxiliares.
- Documente qualquer coleção de mídia nos docstrings do model (ou em um arquivo phpDoc separado, conforme os padrões do projeto).

```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Spatie\MediaLibrary\HasMedia;
use Spatie\MediaLibrary\InteractsWithMedia;
use Spatie\MediaLibrary\MediaCollections\Models\Media;

class ProjectContract extends Model implements HasMedia
{
    use InteractsWithMedia;

    public function registerMediaCollections(): void
    {
        $this->addMediaCollection('contracts')
            ->acceptsMimeTypes(['application/pdf'])
            ->singleFile();
    }

    public function registerMediaConversions(?Media $media = null): void
    {
        $this->addMediaConversion('thumb')
            ->width(150)
            ->height(150)
            ->sharpen(10)
            ->queued();
    }
}
```

### 2. Configuração de Coleções de Mídia
Defina suas coleções dentro de `registerMediaCollections()` para impor restrições:
- Use `singleFile()` para coleções que devem conter apenas um arquivo (por exemplo, avatares de usuário, arquivos principais de contrato). Os arquivos antigos serão substituídos automaticamente.
- Imponha os mime types no nível da coleção usando `acceptsMimeTypes(['image/jpeg', 'image/png', 'application/pdf'])`.
- Implemente a seleção de disco, se necessário, via `useDisk('s3')` ou `useDisk('public')`.

### 3. Conversões de Imagem Assíncronas
O processamento de imagens é intensivo em recursos. Nunca o execute de forma síncrona em requisições HTTP:
- Sempre encadeie `queued()` em `addMediaConversion()` para que rodem via jobs de fila em background em vez de bloquear a requisição do usuário.
- Defina imagens de fallback ou placeholders padrão caso as conversões ainda estejam sendo processadas.

### 4. Validação no Controller e na Request
Nunca confie em requisições de upload sem validação explícita. Sempre valide usando Form Requests do Laravel.
- Valide a existência do arquivo, o tamanho máximo (por exemplo, `max:10240` para 10MB) e os mime types.
- Dentro do Controller, anexe o arquivo de forma segura usando a api do media library.

Exemplo de implementação de Controller:
```php
namespace App\Http\Controllers;

use App\Http\Requests\UploadContractRequest;
use App\Models\ProjectContract;
use Illuminate\Http\JsonResponse;

class ProjectContractController extends Controller
{
    public function store(UploadContractRequest $request, ProjectContract $contract): JsonResponse
    {
        $contract->addMediaFromRequest('file')
            ->toMediaCollection('contracts');

        return response()->json([
            'message' => 'Contract uploaded successfully',
            'media_url' => $contract->getFirstMediaUrl('contracts'),
        ]);
    }
}
```

### 5. Prevenção de Problemas de Query N+1
Carregar mídia para listas de models pode disparar uma query no banco por registro para buscar a mídia.
- Sempre faça eager load da mídia usando `with('media')` ao consultar múltiplos models.
- Faça eager load das conversões se você for exibi-las imediatamente.

```php
// Ruim: Dispara N+1 queries para a mídia
$contracts = ProjectContract::all();
foreach ($contracts as $contract) {
    echo $contract->getFirstMediaUrl('contracts');
}

// Bom: Pré-carrega os registros de mídia do banco
$contracts = ProjectContract::with('media')->get();
```

### 6. Limpeza e Órfãos
- Mantenha seu storage limpo. Ao excluir models, garanta que a mídia deles seja removida (isso é tratado automaticamente pelos eventos de delete do model do Spatie, mas garanta que os soft deletes sejam gerenciados corretamente).
- Use `php artisan media-library:clean` para remover arquivos órfãos do storage.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **Não** execute conversões de imagem de forma síncrona. Sempre use `queued()` para qualquer conversão.
- **Não** faça upload de arquivos sem validá-los em uma Form Request.
- **Não** use queries brutas no banco para buscar URLs de mídia. Sempre use a API do Spatie (`getFirstMediaUrl()` ou métodos auxiliares).
- **Não** esqueça de fazer eager load da relação `media` ao listar múltiplas entidades que exibem anexos.
