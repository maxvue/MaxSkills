---
name: laravel-vuefinder-media-library-integration
description: "Use when integrating the VueFinder file manager with Spatie MediaLibrary in the Laravel 13 / Vue 3 EngeApp stack. Triggers on upload/delete/rename/move/copy sync hooks, keeping the physical disk and media table consistent via legacy_folder custom properties, saveQuietly()/toBase() to avoid observer loops, and enriching VueFinder JSON with Spatie metadata."
---

# Objetivo
Garantir a sincronização em tempo real entre as operações do gerenciador de arquivos VueFinder (upload, delete, rename, move, copy) e os registros no banco de dados do Spatie MediaLibrary, mantendo o armazenamento físico e a tabela `media` do banco de dados perfeitamente consistentes.

# Instruções
1. **Operações do Controller & Tratamento de Ações**:
   - Resolva o diretório do projeto e os adapters do gerenciador de arquivos de forma segura.
   - Use `Ozdemir\VueFinder\VueFinderBuilder` e `VueFinderActionFactory` para tratar a execução da request.
   - Despache os hooks de sincronização imediatamente após a execução, correspondendo às ações específicas (`upload`, `delete`, `rename`, `move`, `copy`).

2. **Sincronização de Upload de Arquivo (`onUpload`)**:
   - Garanta a prevenção de duplicatas verificando registros de media existentes com o mesmo nome de arquivo e a mesma propriedade `legacy_folder`.
   - Crie um registro de Media do Spatie diretamente no model alvo utilizando `Media::create()` com os campos essenciais (`uuid`, `collection_name`, `name`, `file_name`, `mime_type`, `disk`, `size`).
   - Armazene o caminho do diretório físico em `custom_properties->legacy_folder`.
   - Despache jobs em background ou comandos artisan para regenerar thumbnails ou processar o conteúdo do documento (ex.: `ProcessMediaDocumentReaderJob`).

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
- NUNCA armazene arquivos temporários fora dos discos de armazenamento configurados.
- NUNCA dispare os eventos padrão de model do Eloquent ou os observers do MediaLibrary durante a sincronização (use queries `saveQuietly()` ou `toBase()`) para evitar disparos circulares.
- NÃO duplique registros de media para arquivos idênticos na mesma pasta virtual.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
