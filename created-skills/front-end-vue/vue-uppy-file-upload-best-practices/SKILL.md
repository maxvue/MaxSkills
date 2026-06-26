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
        endpoint: '/files/upload',
        formData: true,
        fieldName: 'files[]', // Alinhado com a expectativa do controller
        headers: {
            'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement)?.content || '',
        },
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
            // Processa uploads bem-sucedidos
            const responseData = result.successful.map(file => file.response?.body);
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
- Certifique-se de que o nome do campo (`fieldName`) configurado no `@uppy/xhr-upload` esteja alinhado com o esperado pelo controller (`files[]` ou `file`).
- O controller AdonisJS retorna uma resposta JSON contendo os registros dos arquivos criados.
- O token CSRF do AdonisJS Shield é enviado automaticamente via cookie `XSRF-TOKEN` em requisições XHR com `withCredentials: true`.

## 3. Padrões de UI e UX
- Forneça indicadores visuais claros para o estado do upload: spinner de carregamento, barra de progresso em porcentagem, ícones de sucesso e mecanismos para tentar novamente em caso de falha.
- Estilize áreas de arrastar e soltar (drop zones) com dicas visuais (ex: bordas tracejadas, mudança de cor de fundo ao arrastar o arquivo por cima) usando CSS moderno.
- Ao criar componentes personalizados de arrastar e soltar, utilize hooks como `useDropZone` e `useFileDialog` para desacoplar a lógica do template HTML.

## Restrições
- **Não** insira scripts inline ou lógica de negócio diretamente nos templates Vue. Todos os manipuladores de evento, configurações e callbacks devem residir na tag `<script setup lang="ts">`.
- **Não** esqueça de destruir e limpar a instância do Uppy no unmount usando `uppy.close()`. O esquecimento deste passo causa vazamentos de memória (memory leaks) em Single Page Applications (SPA).
- **Não** ignore a validação CSRF. Sempre envie o cabeçalho `X-CSRF-TOKEN` nas requisições do tipo XHR.
