---
name: adonisjs-gemini-file-api-media-integration-best-practices
description: Use when implementing, reviewing, or debugging media uploads and processing using the Google AI File API with the Gemini SDK in AdonisJS. Triggers on files managing multimodal AI requests, processing large video, audio, or PDF files for Gemini analysis, uploading temp files to the Google File API, monitoring upload state, and cleanup operations.
---

## Objetivo
Fornecer diretrizes seguras, robustas e eficientes em termos de recursos para fazer upload e processar arquivos multimídia de grande porte (vídeos, áudios e PDFs pesados) na API de Arquivos do Google AI (Google File API) e utilizá-los em modelos Gemini dentro de aplicações AdonisJS v6.

## Instruções

### 1. Seleção de SDK e Inicialização do Cliente
Sempre leia as chaves de API a partir do serviço Env do AdonisJS. Use o SDK moderno `@google/genai` (recomendado) ou o SDK `@google/generative-ai`.
- **Usando `@google/genai` (Novo Padrão)**:
  ```typescript
  import { GoogleGenAI } from '@google/genai'
  import env from '#start/env'

  const ai = new GoogleGenAI({ apiKey: env.get('GEMINI_API_KEY') })
  ```
- **Usando `@google/generative-ai` (Legado/Comum)**:
  ```typescript
  import { GoogleGenAI, GoogleGenAIFileManager } from '@google/generative-ai'
  import env from '#start/env'

  const genAI = new GoogleGenAI(env.get('GEMINI_API_KEY'))
  const fileManager = new GoogleGenAIFileManager(env.get('GEMINI_API_KEY'))
  ```

### 2. Integração com o Drive do AdonisJS
Os SDKs da File API do Google exigem um caminho de arquivo local. Como o AdonisJS pode armazenar arquivos enviados em discos locais (`fs`) ou em armazenamento em nuvem (`s3` / `gcs`), você deve implementar um helper dinâmico para resolver os arquivos para um caminho local antes de fazer o upload:
```typescript
import drive from '@adonisjs/drive/services/main'
import app from '@adonisjs/core/services/app'
import { cuid } from '@adonisjs/core/helpers'
import env from '#start/env'
import fs from 'node:fs'
import path from 'node:path'
import { pipeline } from 'node:stream/promises'

/**
 * Resolve uma chave de arquivo do drive para um caminho local no sistema de arquivos.
 * Se o arquivo estiver em armazenamento na nuvem, faz o download para a pasta temporária.
 * Retorna o caminho local e um booleano indicando se é um arquivo temporário.
 */
export async function getLocalPath(fileKey: string): Promise<{ localPath: string; isTemp: boolean }> {
  const currentDisk = env.get('DRIVE_DISK')
  
  if (currentDisk === 'fs') {
    return {
      localPath: drive.use().makePath(fileKey),
      isTemp: false
    }
  }

  // Disco em nuvem: baixa para o diretório temporário
  const tempPath = path.join(app.tmpPath(), `gemini-file-${cuid()}`)
  const fileStream = await drive.use().getStream(fileKey)
  await pipeline(fileStream, fs.createWriteStream(tempPath))

  return {
    localPath: tempPath,
    isTemp: true
  }
}
```

### 3. Upload para a Google File API
Realize o upload utilizando o caminho local resolvido. Forneça o `mimeType` correto e um `displayName` semântico.
- **Usando `@google/genai`**:
  ```typescript
  const uploadResult = await ai.files.upload({
    file: localPath,
    mimeType,
    config: { displayName }
  })
  // uploadResult contém name, uri, mimeType, etc.
  ```
- **Usando `@google/generative-ai`**:
  ```typescript
  const uploadResult = await fileManager.uploadFile(localPath, {
    mimeType,
    displayName
  })
  ```

### 4. Monitoramento Ativo de Status (Processamento de Mídia)
Arquivos de mídia grandes (como vídeos ou áudios longos) passam por processamento assíncrono nos servidores do Google. Você deve implementar um loop de polling para aguardar até que o estado do arquivo mude de `PROCESSING` para `ACTIVE` antes de enviá-lo ao modelo generativo:
- **Usando `@google/genai`**:
  ```typescript
  let fileState = await ai.files.get({ name: uploadResult.name })
  while (fileState.state === 'PROCESSING') {
    await new Promise((resolve) => setTimeout(resolve, 10000)) // Espera 10s
    fileState = await ai.files.get({ name: uploadResult.name })
  }
  if (fileState.state !== 'ACTIVE') {
    throw new Error(`O processamento do arquivo falhou com o estado: ${fileState.state}`)
  }
  ```
- **Usando `@google/generative-ai`**:
  ```typescript
  let fileState = await fileManager.getFile(uploadResult.name)
  while (fileState.state === 'PROCESSING') {
    await new Promise((resolve) => setTimeout(resolve, 10000))
    fileState = await fileManager.getFile(uploadResult.name)
  }
  if (fileState.state !== 'ACTIVE') {
    throw new Error(`O processamento do arquivo falhou com o estado: ${fileState.state}`)
  }
  ```

### 5. Invocação do Gemini com Referências de Arquivo
Uma vez ativo, passe o objeto do arquivo (ou referência) no array `contents`.
- **Usando `@google/genai`**:
  ```typescript
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      uploadResult, // Referência direta ao objeto
      'Analise este arquivo de mídia'
    ]
  })
  ```
- **Usando `@google/generative-ai` ou Vercel AI SDK**:
  Passe os dados do arquivo utilizando o formato `fileData`:
  ```typescript
  const response = await model.generateContent([
    {
      fileData: {
        fileUri: uploadResult.uri,
        mimeType: uploadResult.mimeType
      }
    },
    'Analise este arquivo de mídia'
  ])
  ```

### 6. Limpeza de Recursos e Hooks de Ciclo de Vida
Os arquivos da Google File API persistem por até 48 horas, a menos que sejam excluídos. Sempre execute uma etapa de limpeza em um bloco `finally` para remover o arquivo do Google e quaisquer arquivos locais temporários criados:
```typescript
try {
  // Upload e processamento...
} finally {
  // 1. Exclui a referência na Google File API
  try {
    if (uploadResult?.name) {
      // @google/genai
      await ai.files.delete({ name: uploadResult.name })
      // Ou @google/generative-ai
      // await fileManager.deleteFile(uploadResult.name)
    }
  } catch (error) {
    logger.warn({ err: error }, 'Falha ao excluir o arquivo da Google File API')
  }

  // 2. Exclui o arquivo temporário local (se baixado do cloud storage)
  if (isTemp && localPath) {
    fs.promises.unlink(localPath).catch((error) => {
      logger.warn({ err: error }, 'Falha ao excluir o arquivo temporário local')
    })
  }
}
```

## Restrições
- **Nunca** realize conversões para Base64 em memória para payloads de vídeo/áudio grandes. Fazer isso causará esgotamento de memória RAM. Sempre envie-os através da File API.
- **Nunca** prossiga para a geração de conteúdo usando um arquivo sem antes verificar se o seu estado transitou para `ACTIVE`.
- **Nunca** deixe vazar arquivos temporários locais ou referências da Google File API. Sempre limpe os recursos dentro de blocos `finally`.
- **Não** crie protocolos personalizados de upload de arquivos. Utilize os métodos oficiais do SDK do Google (`files.upload` ou `uploadFile`).
- **Não** exponha chaves de API brutas ou configurações hardcoded. Acesse todos os parâmetros através do serviço `env` do AdonisJS.
