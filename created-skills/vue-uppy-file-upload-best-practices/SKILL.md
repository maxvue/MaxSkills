---
name: vue-uppy-file-upload-best-practices
description: Use when implementing, configuring, reviewing, or debugging client-side file uploads using Uppy (@uppy/core, @uppy/xhr-upload) in Vue 3 components, and integrating them with AdonisJS backend endpoints. Triggers on Uppy initialization, upload event handlers, drag-and-drop file inputs, upload progress bars, and handling files in Vue forms.
---

## Objetivo
Fornecer diretrizes sólidas e padrões estruturados para implementar uploads de arquivos robustos, assíncronos e interativos com Uppy no Vue 3 integrado ao AdonisJS.

## Instruções

## 1. Configuração do Uppy no Frontend Vue 3
Ao configurar o Uppy em componentes Vue 3, use sempre a Composition API (`<script setup lang="ts">`) e libere os recursos no ciclo de vida de desmontagem do componente.

### Padrão Recomendado de Configuração
```typescript
import { onBeforeUnmount, ref } from 'vue';
import Uppy from '@uppy/core';
import XHRUpload from '@uppy/xhr-upload';
import pt_BR from '@uppy/locales/lib/pt_BR';
import { useFilesStore } from '@/stores/files'; // store @maxvue/max-pinia

const uppyInstance = ref<Uppy | null>(null);
const uploadProgress = ref<number>(0);
const isUploading = ref<boolean>(false);

function initUppy() {
    uppyInstance.value = new Uppy({
        id: 'file-uploader',
        autoProceed: true,
        locale: pt_BR,
        restrictions: {
            maxFileSize: 10 * 1024 * 1024, // Limite de 10MB
            allowedFileTypes: ['.pdf', '.jpg', '.jpeg', '.png'],
            maxNumberOfFiles: 5,
        },
    });

    uppyInstance.value.use(XHRUpload, {
        // O @uppy/xhr-upload precisa de uma URL STRING — NÃO chame apiPostRoute aqui
        // (ele dispararia a requisição e atribuiria uma Promise). Use o caminho string
        // (ou apiRoute('/api/files/upload').routeURL se precisar resolver via a lib).
        endpoint: '/api/files/upload',
        formData: true,
        fieldName: 'files', // Deve casar com request.files('files') no controller Adonis
        // Não defina X-CSRF-TOKEN manualmente: o AdonisJS Shield lê o token do
        // cookie XSRF-TOKEN e o front o reenvia no header X-XSRF-TOKEN automaticamente
        // em requisições com withCredentials: true.
        withCredentials: true,
    });

    uppyInstance.value.on('upload-progress', (file, progress) => {
        if (progress.bytesTotal > 0) {
            uploadProgress.value = Math.round((progress.bytesUploaded / progress.bytesTotal) * 100);
        }
    });

    uppyInstance.value.on('upload', () => {
        isUploading.value = true;
    });

    uppyInstance.value.on('complete', (result) => {
        isUploading.value = false;
        if (result.successful.length > 0) {
            // Processa uploads bem-sucedidos. O endpoint XHR cuida apenas do
            // streaming binário; os registros de arquivo retornados devem ser
            // incorporados ao estado de página via store @maxvue/max-pinia,
            // não mantidos apenas no escopo do componente.
            const responseData = result.successful.map(file => file.response?.body);
            const filesStore = useFilesStore();
            filesStore.appendUploaded(responseData); // store reflete e persiste o estado
            emit('success', responseData);
        }
        if (result.failed.length > 0) {
            console.error('Erros no upload do Uppy:', result.failed);
            emit('error', result.failed);
        }
    });
}

onBeforeUnmount(() => {
    if (uppyInstance.value) {
        uppyInstance.value.close({ keepFilesState: false });
    }
});
```

## 2. Integração com o Backend AdonisJS
O endpoint padrão do backend do Engeapp é `files/upload`, tratado por `FilesUploadController.upload`.
- Os arquivos são extraídos do corpo da requisição via `request.files('files')` do AdonisJS.
- O `fieldName` configurado no `@uppy/xhr-upload` deve casar exatamente com a chave usada em `request.files(...)`. Use `files` em ambos os lados — não use a convenção PHP `files[]`, que não corresponde ao argumento esperado por `request.files('files')` no Adonis.
- O controller AdonisJS retorna uma resposta JSON contendo os registros dos arquivos criados; esses registros devem ser hidratados na store `@maxvue/max-pinia` correspondente para alimentar a página.
- O token CSRF do AdonisJS Shield é enviado automaticamente: o Shield grava o token no cookie `XSRF-TOKEN` e o reenvia no header `X-XSRF-TOKEN` em requisições XHR com `withCredentials: true`. Não leia `meta[name="csrf-token"]` nem injete `X-CSRF-TOKEN` manualmente (padrão Laravel/Blade).

## 3. Padrões de UI e UX
- Forneça indicadores visuais claros para o estado do upload: spinner de carregamento, barra de progresso em porcentagem, ícones de sucesso e mecanismos para tentar novamente em caso de falha.
- Estilize áreas de arrastar e soltar (drop zones) com dicas visuais (ex: bordas tracejadas, mudança de cor de fundo ao arrastar o arquivo por cima) usando CSS moderno.
- Ao criar componentes personalizados de arrastar e soltar, utilize hooks como `useDropZone` e `useFileDialog` para desacoplar a lógica do template HTML.

## Restrições
- **Não** insira scripts inline ou lógica de negócio diretamente nos templates Vue. Todos os manipuladores de evento, configurações e callbacks devem residir na tag `<script setup lang="ts">`.
- **Não** esqueça de destruir e limpar a instância do Uppy no unmount usando `uppy.close()`. O esquecimento deste passo causa vazamentos de memória (memory leaks) em Single Page Applications (SPA).
- **Não** ignore a validação CSRF, mas também **não** envie o header manualmente. Mantenha `withCredentials: true` para que o AdonisJS Shield gerencie o token via cookie `XSRF-TOKEN`/header `X-XSRF-TOKEN` automaticamente.
- **Não** trate o resultado do upload apenas com `emit('success')`. Os registros de arquivo retornados são dados de página e devem ser incorporados a uma store `@maxvue/max-pinia`, que cuida do cache e do salvamento.
