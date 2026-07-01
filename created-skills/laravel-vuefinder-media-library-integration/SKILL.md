---
name: laravel-vuefinder-media-library-integration
description: Use when integrating VueFinder file manager with Spatie MediaLibrary in Laravel/Vue 3 projects. Triggers on file upload, delete, rename, move, copy mutations, and database metadata synchronization.
---

# Goal
Ensure real-time synchronization between VueFinder file manager operations (upload, delete, rename, move, copy) and Spatie MediaLibrary database records, keeping the physical storage and the `media` database table perfectly consistent.

# Instructions
1. **Controller Operations & Action Handling**:
   - Resolve the project directory and file manager adapters securely.
   - Use `Ozdemir\VueFinder\VueFinderBuilder` and `VueFinderActionFactory` to handle request execution.
   - Dispatch synchronization hooks immediately after execution, matching specific actions (`upload`, `delete`, `rename`, `move`, `copy`).

2. **File Upload Synchronization (`onUpload`)**:
   - Ensure you prevent duplicates by checking for existing media records with the same file name and `legacy_folder` property.
   - Create a Spatie Media record directly on the target model utilizing `Media::create()` with essential fields (`uuid`, `collection_name`, `name`, `file_name`, `mime_type`, `disk`, `size`).
   - Store the path to the physical directory in `custom_properties->legacy_folder`.
   - Dispatch background jobs or artisan commands to regenerate thumbnails or process document content (e.g. `ProcessMediaDocumentReaderJob`).

3. **File Deletion Synchronization (`onDelete`)**:
   - If a directory is deleted, recursively delete all matching media items whose `legacy_folder` matches the deleted folder path prefix.
   - Use direct database query execution (`toBase()->delete()`) to prevent dispatching Spatie model deletion events, since VueFinder has already physically deleted the files.

4. **File Rename (`onRename`)**:
   - Retrieve the media record matching the old name and legacy folder.
   - Update both `$media->file_name` and `$media->name` using `saveQuietly()` to prevent triggering observers.

5. **File Relocation / Move (`onMove`)**:
   - Update the `legacy_folder` custom property of the moved media record to point to the destination folder using `saveQuietly()`.

6. **File Copy (`onCopy`)**:
   - Replicate the media record inside the destination folder, mapping properties and avoiding duplicates in the target location.

7. **Metadata Enrichment (`enrichWithSpatieMetadata`)**:
   - Enrich VueFinder's index or search JSON responses with Spatie Media library attributes (`media_id`, `data_ai`, `status_ai_process`, `thumbnail`, `document_type`, `tags`, etc.).

# Constraints
- NEVER store temporary files outside the configured storage disks.
- NEVER trigger default Eloquent model events or MediaLibrary observers during synchronization (use `saveQuietly()` or `toBase()` queries) to avoid circular triggers.
- DO NOT duplicate media records for identical files in the same virtual folder.
