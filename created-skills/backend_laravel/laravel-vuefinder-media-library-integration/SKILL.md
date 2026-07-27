---
name: laravel-vuefinder-media-library-integration
description: "Use when integrating the VueFinder file manager with Spatie MediaLibrary in the Laravel 13 / Vue 3 EngeApp stack. Triggers on upload/delete/rename/move/copy sync hooks, keeping the physical disk and media table consistent via legacy_folder custom properties, saveQuietly()/toBase() to avoid observer loops, and enriching VueFinder JSON with Spatie metadata."
---

# Objetivo
Garantir a sincronização em tempo real entre as operações do gerenciador de arquivos VueFinder (upload, delete, rename, move, copy) e os registros no banco de dados do Spatie MediaLibrary, mantendo o armazenamento físico e a tabela `media` do banco de dados perfeitamente consistentes.

# Instruções
1. **Operações do Controller & Tratamento de Ações**:
   - Antes de listar/operar, garanta idempotentemente que a pasta do projeto exista fisicamente: se `$project->folder` ainda não estiver definido, chame `$project->createFolder(true)`; se estiver definido mas ausente no disco, recrie-a com `makeDirectory()` incluindo as subpastas padrão `Fotos` e `Vistoria`. Só então monte o adapter (`LocalFilesystemAdapter`) e o `VueFinderBuilder`/`ActionFactory` para tratar a execução da request.
   - Use `Ozdemir\VueFinder\VueFinderBuilder::create()` do vendor para montar o core, mas instancie a factory LOCAL `App\Services\VueFinder\ActionFactory` (subclasse de `VueFinderActionFactory` que exige `$basePath` e substitui `preview`/`download` por `PreviewAction`/`DownloadAction` com suporte a HTTP Range via `LocalFileStreamAction::setBasePath`), chamando `->setRequest($request)->create($action)->execute()`.
   - Envolva a chamada a `->execute()` em `try/catch` de `League\Flysystem\UnableToReadFile | UnableToRetrieveMetadata`: logue com `Log::warning()` e retorne JSON 404 (`'Arquivo não encontrado.'`) em vez de deixar a exceção subir ao handler global e gerar auto-report.
   - Despache os hooks de sincronização (`syncWithSpatie`) imediatamente após a execução, correspondendo às ações específicas (`upload`, `delete`, `rename`, `move`, `copy`). `syncWithSpatie` deve capturar `\Throwable` e apenas logar um warning, garantindo que falha de sincronização nunca quebre a resposta do file manager.

2. **Sincronização de Upload de Arquivo (`onUpload`)**:
   - Garanta a prevenção de duplicatas verificando registros de media existentes com o mesmo nome de arquivo e a mesma propriedade `legacy_folder`.
   - Crie um registro de Media do Spatie diretamente no model alvo (`model_type` = `Project::class`, `model_id` = id do projeto) usando `Media::create()`. Preencha `uuid`, `collection_name` (`'documents'`), `name`, `file_name`, `mime_type`, `disk`, `conversions_disk` (mesmo disk do projeto) e `size`. `conversions_disk` é obrigatório para a regeneração de conversões não quebrar.
   - Calcule `order_column` como `($project->media()->max('order_column') ?? 0) + 1` para manter a ordenação; sem isso os registros ficam sem ordem definida.
   - Inicialize os campos JSON exigidos pelo schema do Spatie: `manipulations`, `generated_conversions` e `responsive_images` como arrays vazios.
   - Armazene o caminho do diretório físico em `custom_properties->legacy_folder`. Marque `custom_properties->status_ai_process = true` (consumido depois no enriquecimento). Crie uma notificação para o usuário via `NotificationService::createNotification()`, então force a regeneração de conversões com `Artisan::call('media-library:regenerate', ['--ids' => [$media->id], '--force' => true])` antes de despachar `ProcessMediaDocumentReaderJob` (passando o id da notificação).

3. **Sincronização de Exclusão de Arquivo (`onDelete`)**:
   - Se um diretório for excluído, exclua recursivamente todos os itens de media correspondentes cujo `legacy_folder` corresponda ao prefixo do caminho da pasta excluída.
   - Use execução direta de query no banco de dados (`toBase()->delete()`) para prevenir o disparo de eventos de exclusão de model do Spatie, já que o VueFinder já excluiu fisicamente os arquivos.

4. **Renomear Arquivo (`onRename`)**:
   - Recupere o registro de media correspondente ao nome antigo e à legacy folder.
   - Atualize tanto `$media->file_name` quanto `$media->name` usando `saveQuietly()` para prevenir o disparo de observers.

5. **Relocação / Mover Arquivo (`onMove`)**:
   - Atualize a custom property `legacy_folder` do registro de media movido para apontar para a pasta de destino usando `saveQuietly()`.

6. **Copiar Arquivo (`onCopy`)**:
   - Replique o registro de media dentro da pasta de destino, mapeando as propriedades e evitando duplicatas no local de destino.

7. **Enriquecimento de Metadados (`enrichWithSpatieMetadata`)**:
   - Enriqueça as respostas JSON de índice ou busca do VueFinder com os atributos da media library do Spatie (`media_id`, `data_ai`, `status_ai_process`, `thumbnail`, `document_type`, `tags`, etc.).

# Restrições
- NUNCA dispare os eventos padrão de model do Eloquent ou os observers do MediaLibrary durante a sincronização (use queries `saveQuietly()` ou `toBase()`) para evitar disparos circulares.
- NÃO duplique registros de media para arquivos idênticos na mesma pasta virtual.

## Idioma
- Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
