---
name: laravel-media-library-best-practices
description: Use when defining, implementing, reviewing, or debugging file uploads and media attachments using Spatie Laravel Media Library. Triggers on model implementing HasMedia, using InteractsWithMedia trait, registering media collections, defining media conversions, uploading files from HTTP requests, and retrieving media URLs.
---

# Spatie Laravel Media Library Best Practices

## Goal
Establish clean, performant, and secure standards for managing file uploads and media attachments via Spatie Laravel Media Library in the Engeapp ecosystem.

## Instructions

### 1. Model Configuration
When implementing media capabilities on a model:
- Implement `Spatie\MediaLibrary\HasMedia` interface.
- Use `Spatie\MediaLibrary\InteractsWithMedia` trait.
- Always add return type declarations to all media relationships or helper methods.
- Document any media collections in model docstrings (or in a separate phpDoc file as per project standards).

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

### 2. Media Collections Setup
Define your collections inside `registerMediaCollections()` to enforce constraints:
- Use `singleFile()` for collections that should only hold one file (e.g., user avatars, main contract files). Old files will be automatically replaced.
- Enforce mime types at the collection level using `acceptsMimeTypes(['image/jpeg', 'image/png', 'application/pdf'])`.
- Implement disk selection if needed via `useDisk('s3')` or `useDisk('public')`.

### 3. Asynchronous Image Conversions
Image processing is resource-intensive. Never run it synchronously on HTTP requests:
- Always chain `queued()` to `addMediaConversion()` so that they run via background queue jobs rather than blocking the user's request.
- Define fallback images or default placeholders if conversions are still processing.

### 4. Controller & Request Validation
Never trust upload requests without explicit validation. Always validate using Laravel Form Requests.
- Validate file existence, max size (e.g., `max:10240` for 10MB), and mime types.
- Inside the Controller, securely attach the file using the media library api.

Example Controller implementation:
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

### 5. Preventing N+1 Query Problems
Loading media for lists of models can trigger a database query per record to fetch the media.
- Always eager load media using `with('media')` when querying multiple models.
- Eager load conversions if you are displaying them immediately.

```php
// Bad: Triggers N+1 queries for media
$contracts = ProjectContract::all();
foreach ($contracts as $contract) {
    echo $contract->getFirstMediaUrl('contracts');
}

// Good: Preloads media database records
$contracts = ProjectContract::with('media')->get();
```

### 6. Cleanup and Orphans
- Keep your storage clean. When deleting models, ensure their media is cleaned up (this is handled automatically by Spatie's model delete events, but ensure soft deletes are managed properly).
- Use `php artisan media-library:clean` to remove orphaned files from storage.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do not** run image conversions synchronously. Always use `queued()` for any conversion.
- **Do not** upload files without validating them in a Form Request.
- **Do not** use raw database queries to fetch media URLs. Always use Spatie's API (`getFirstMediaUrl()` or helper methods).
- **Do not** forget to eager load `media` relation when listing multiple entities that showcase attachments.
